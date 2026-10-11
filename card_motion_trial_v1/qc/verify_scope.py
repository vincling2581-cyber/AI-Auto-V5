"""Read-only V4 audit; all reports are confined to this V5 trial's qc folder."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


QC = Path(__file__).resolve().parent
TRIAL = QC.parent
SOURCE = Path(r"D:\AI-Auto-V4（Codex）")
EPISODE_REL = Path("episodes/ECHO_开源修图工具_20261006")
SNAPSHOT = QC / "source_snapshot.json"
SCENE_REL = "06_project/cards/scene.js"
EXTRA_FILES = [
    "03_storyboard/cards.json",
    "00_brief/effective_defaults.json",
    "00_brief/standard_lock.json",
    "06_project/cards/scene.js",
    "06_project/cards/card_kit.js",
    "06_project/cards/render_cards.py",
    "06_project/cards/card_scene.html",
    "06_project/render/C04.mp4",
    "01_audio/mixed_audio.wav",
]


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            h.update(block)
    return h.hexdigest()


def save_report(path, value):
    path = path.resolve()
    if not path.is_relative_to(QC):
        raise ValueError("Reports may only be written inside this trial's qc directory")
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def inventory(root):
    result = {}
    errors = []
    def onerror(exc):
        errors.append(str(exc))
    for directory, dirs, files in os.walk(root, followlinks=False, onerror=onerror):
        dirs.sort()
        for name in sorted(files):
            path = Path(directory) / name
            try:
                stat = path.stat(follow_symlinks=False)
                result[path.relative_to(root).as_posix()] = {
                    "size": stat.st_size,
                    "mtime_ns": stat.st_mtime_ns,
                    "is_symlink": path.is_symlink(),
                }
            except OSError as exc:
                errors.append(f"{path}: {exc}")
    return result, errors


def manifest_paths():
    manifest = json.loads((SOURCE / "production_standard.json").read_text(encoding="utf-8-sig"))
    listed = {entry["path"]: entry["sha256"] for entry in manifest["files"]}
    paths = set(listed) | {"production_standard.json"}
    paths.update((EPISODE_REL / relative).as_posix() for relative in EXTRA_FILES)
    return manifest, listed, sorted(paths)


def hash_source(paths):
    hashes = {}
    errors = []
    for relative in paths:
        path = (SOURCE / relative).resolve()
        if not path.is_relative_to(SOURCE.resolve()):
            errors.append(f"Outside V4 source: {relative}")
            continue
        try:
            before = path.stat()
            value = digest(path)
            after = path.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                errors.append(f"Changed while hashing: {relative}")
            hashes[relative] = value
        except OSError as exc:
            errors.append(f"{relative}: {exc}")
    return hashes, errors


def snapshot():
    if SNAPSHOT.exists():
        raise RuntimeError("Snapshot already exists; refusing to replace the original evidence")
    manifest, expected, paths = manifest_paths()
    files, errors = inventory(SOURCE)
    hashes, hash_errors = hash_source(paths)
    errors.extend(hash_errors)
    checks = [{"path": path, "expected_sha256": value,
               "actual_sha256": hashes.get(path), "matches": hashes.get(path) == value}
              for path, value in expected.items()]
    drift = [check for check in checks if not check["matches"]]
    report = {
        "schema": "v4_read_only_trial_source_snapshot_v1",
        "created_at_utc": timestamp(),
        "source_root": str(SOURCE),
        "source_episode": str(SOURCE / EPISODE_REL),
        "policy": "Read V4 only; write audit artifacts only under this V5 trial qc directory",
        "standard_version": manifest["version"],
        "standard_revision": manifest.get("revision"),
        "file_count": len(files),
        "total_bytes": sum(item["size"] for item in files.values()),
        "files": files,
        "sha256": hashes,
        "manifest_checks": checks,
        "preexisting_standard_drift": drift,
        "errors": errors,
        "status": "snapshot_complete" if not errors else "snapshot_errors",
    }
    save_report(SNAPSHOT, report)
    print(json.dumps({key: report[key] for key in ["status", "file_count", "total_bytes", "standard_version"]}, ensure_ascii=False))
    print(json.dumps({"hash_count": len(hashes), "manifest_count": len(checks), "drift_count": len(drift), "errors": errors, "snapshot": str(SNAPSHOT)}, ensure_ascii=False))
    return 0 if not errors else 1


def c04_region(data):
    start_token = b"scenes.C04="
    end_token = b"scenes.C05="
    if data.count(start_token) != 1 or data.count(end_token) != 1:
        raise ValueError("Expected exactly one C04 and C05 scene marker")
    start = data.index(start_token)
    end = data.index(end_token, start)
    return data[:start], data[start:end], data[end:]


def trial_path(value):
    path = Path(value).resolve()
    if not path.is_relative_to(TRIAL):
        raise ValueError("Copy comparison paths must be inside this V5 trial")
    if not path.is_dir():
        raise ValueError(f"Missing copy directory: {path}")
    return path


def compare_copies(baseline, episode, ignores, shared_inputs, snapshot_hashes):
    original, before_errors = inventory(baseline)
    revised, after_errors = inventory(episode)
    def included(relative):
        return relative not in shared_inputs and not any(relative == prefix.rstrip("/") or relative.startswith(prefix.rstrip("/") + "/") for prefix in ignores)
    before = {path for path in original if included(path)}
    after = {path for path in revised if included(path)}
    added = sorted(after - before)
    missing = sorted(before - after)
    changed = []
    hashes = []
    origin_checks = []
    for relative in sorted(before & after):
        bh, eh = digest(baseline / relative), digest(episode / relative)
        hashes.append({"path": relative, "baseline_sha256": bh, "episode_sha256": eh, "equal": bh == eh})
        source_relative = (EPISODE_REL / relative).as_posix()
        expected = snapshot_hashes.get(source_relative)
        binding = "snapshot_sha256"
        if expected is None:
            expected = digest(SOURCE / EPISODE_REL / relative)
            binding = "current_unchanged_source_inventory_file"
        origin_checks.append({"path": relative, "source_sha256": expected, "baseline_sha256": bh,
                              "binding": binding, "equal": bh == expected})
        if bh != eh:
            changed.append(relative)
    shared_checks = []
    for relative in shared_inputs:
        source_relative = (EPISODE_REL / relative).as_posix()
        expected = snapshot_hashes.get(source_relative)
        actual = digest(baseline / relative) if (baseline / relative).is_file() else None
        shared_checks.append({"path": relative, "source_sha256": expected, "baseline_sha256": actual,
                              "episode_copy_required": False, "equal": expected is not None and expected == actual})
    scene_check = {"checked": False}
    if SCENE_REL in before & after:
        try:
            bp, bc, bs = c04_region((baseline / SCENE_REL).read_bytes())
            ep, ec, es = c04_region((episode / SCENE_REL).read_bytes())
            scene_check = {"checked": True, "prefix_unchanged": bp == ep,
                           "suffix_unchanged": bs == es, "c04_changed": bc != ec,
                           "baseline_c04_sha256": hashlib.sha256(bc).hexdigest(),
                           "episode_c04_sha256": hashlib.sha256(ec).hexdigest()}
        except ValueError as exc:
            scene_check = {"checked": False, "error": str(exc)}
    passed = (not before_errors and not after_errors and not added and not missing
              and all(item["equal"] for item in origin_checks + shared_checks)
              and changed == [SCENE_REL] and scene_check.get("prefix_unchanged")
              and scene_check.get("suffix_unchanged") and scene_check.get("c04_changed"))
    return {"baseline": str(baseline), "episode": str(episode), "ignored_prefixes": ignores,
            "baseline_compared_files": len(before), "episode_compared_files": len(after),
            "added_files": added, "missing_files": missing, "changed_files": changed,
            "baseline_origin_checks": origin_checks, "shared_baseline_inputs": shared_checks,
            "file_hash_comparisons": hashes, "scene_region_check": scene_check,
            "errors": before_errors + after_errors, "passed": bool(passed)}


def verify(args):
    original = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    current, errors = inventory(SOURCE)
    before = original["files"]
    added = sorted(set(current) - set(before))
    removed = sorted(set(before) - set(current))
    modified = [{"path": path, "before": before[path], "after": current[path]}
                for path in sorted(set(before) & set(current)) if before[path] != current[path]]
    hashes, hash_errors = hash_source(list(original["sha256"]))
    hash_changes = [{"path": path, "before": value, "after": hashes.get(path)}
                    for path, value in original["sha256"].items() if hashes.get(path) != value]
    source_check = {"added_files": added, "removed_files": removed, "modified_metadata": modified,
                    "changed_sha256": hash_changes, "file_count": len(current),
                    "checked_hash_count": len(hashes), "errors": errors + hash_errors,
                    "passed": not (added or removed or modified or hash_changes or errors or hash_errors)}
    report = {"schema": "v4_v5_trial_scope_verification_v1", "checked_at_utc": timestamp(),
              "snapshot": str(SNAPSHOT), "source_check": source_check,
              "preexisting_standard_drift": original["preexisting_standard_drift"]}
    if bool(args.baseline) != bool(args.episode):
        raise ValueError("Provide both --baseline and --episode")
    if args.baseline:
        report["copy_check"] = compare_copies(trial_path(args.baseline), trial_path(args.episode), args.ignore_prefix,
                                             args.shared_baseline_input, original["sha256"])
    report["passed"] = source_check["passed"] and report.get("copy_check", {"passed": True})["passed"]
    report["scope"] = "V4 integrity and V5 copied-source comparison" if args.baseline else "V4 integrity only; V5 copies not checked"
    output = QC / args.report_name
    save_report(output, report)
    print(json.dumps({"passed": report["passed"], "scope": report["scope"], "source_passed": source_check["passed"],
                      "copy_passed": report.get("copy_check", {}).get("passed"), "report": str(output)}, ensure_ascii=False))
    return 0 if report["passed"] else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["snapshot", "verify"])
    parser.add_argument("--baseline")
    parser.add_argument("--episode")
    parser.add_argument("--ignore-prefix", action="append", default=[])
    parser.add_argument("--shared-baseline-input", action="append", default=[])
    parser.add_argument("--report-name", default="scope_verification.json")
    args = parser.parse_args()
    return snapshot() if args.action == "snapshot" else verify(args)


if __name__ == "__main__":
    raise SystemExit(main())
