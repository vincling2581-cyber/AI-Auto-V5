"""Current-task boundary baseline and read-only verification for a layered export.

Only this export revision directory may receive writes. V4, original episode
(excluding its 09_revisions subtree), old V5 trials, and original MP3/SRT are read only.
No Jianying draft library or index is accessed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

REV = Path(__file__).resolve().parent
EXPECTED_REV = Path(r"D:\AI-Auto-V5（Codex+AE）\episodes\ECHO_五款开源AI工具_20261008\09_revisions\jianying_layered_20261009_v1")
V4 = Path(r"D:\AI-Auto-V4（Codex）")
V5 = Path(r"D:\AI-Auto-V5（Codex+AE）")
EP = V5 / "episodes" / "ECHO_五款开源AI工具_20261008"
ROOTS = {"v4": V4, "original_episode": EP,
         "trial_v1": V5 / "card_motion_trial_v1",
         "trial_v2": V5 / "card_motion_trial_v2_complex"}
INPUTS = [Path(r"D:\Downloads\Video\10月8日\10月8日.mp3"),
          Path(r"D:\Downloads\Video\10月8日\10月8日.srt")]
SNAPSHOT = REV / "boundary_snapshot.json"


def now():
    return datetime.now(timezone.utc).isoformat()


def require_output(path):
    if REV != EXPECTED_REV.resolve():
        raise ValueError("Verifier is outside the explicitly authorized export revision")
    resolved = path.resolve()
    if not resolved.is_relative_to(REV) or resolved == REV:
        raise ValueError("Output escapes the authorized export revision")
    return resolved


def write_json(path, data, exclusive=False):
    path = require_output(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x" if exclusive else "w", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def metadata(path):
    stat = path.stat(follow_symlinks=False)
    is_link = path.is_symlink()
    is_junction = hasattr(path, "is_junction") and path.is_junction()
    result = {"size": stat.st_size, "mtime_ns": stat.st_mtime_ns,
              "is_symlink": is_link, "is_junction": is_junction}
    if is_link or is_junction:
        result["link_target"] = os.readlink(path)
    return result


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(4 * 1024 * 1024):
            result.update(chunk)
    return result.hexdigest()


def inventory(root, exclude_revision=False):
    files, directory_links, errors = {}, {}, []
    if not root.is_dir():
        return files, directory_links, [f"Missing protected root: {root}"]
    for directory, dirs, names in os.walk(root, followlinks=False,
                                         onerror=lambda error: errors.append(str(error))):
        directory = Path(directory)
        kept = []
        for name in sorted(dirs):
            path = directory / name
            relative = path.relative_to(root).as_posix()
            if exclude_revision and relative == "09_revisions":
                continue
            try:
                info = metadata(path)
                if info["is_symlink"] or info["is_junction"]:
                    directory_links[relative] = info
                else:
                    kept.append(name)
            except OSError as error:
                errors.append(f"{path}: {error}")
        dirs[:] = kept
        for name in sorted(names):
            path = directory / name
            try:
                files[path.relative_to(root).as_posix()] = metadata(path)
            except OSError as error:
                errors.append(f"{path}: {error}")
    return files, directory_links, errors


def hash_paths(root, paths):
    hashes, errors = {}, []
    resolved_root = root.resolve()
    for relative in sorted(paths):
        path = root / relative
        try:
            before = metadata(path)
            if before["is_symlink"] or before["is_junction"]:
                # Preserve link identity without traversing outside the protected tree.
                hashes[relative] = hashlib.sha256(
                    ("symlink-target:" + before["link_target"]).encode("utf-8")).hexdigest()
            else:
                if not path.resolve().is_relative_to(resolved_root):
                    raise ValueError(f"Hash path escapes protected root: {relative}")
                hashes[relative] = digest(path)
            if metadata(path) != before:
                errors.append(f"Changed during hashing: {relative}")
        except (OSError, ValueError) as error:
            errors.append(f"{relative}: {error}")
    return hashes, errors


def input_records():
    result, errors = {}, []
    for path in INPUTS:
        try:
            before = metadata(path)
            result[str(path)] = {**before, "sha256": digest(path)}
            if metadata(path) != before:
                errors.append(f"Original input changed during hashing: {path}")
        except OSError as error:
            errors.append(str(error))
    return result, errors


def current_v4_keys(files):
    manifest_path = V4 / "production_standard.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    keys = {"production_standard.json", "AGENTS.md"}
    declared = {}
    for entry in manifest.get("files", []):
        keys.add(entry["path"])
        declared[entry["path"]] = entry.get("sha256")
    for field in ("sop", "prompts", "prompts_data", "defaults", "rules", "review",
                  "changes", "baseline_manifest", "source_inventory", "conflicts"):
        if isinstance(manifest.get(field), str):
            keys.add(manifest[field])
    for relative in files:
        path = Path(relative)
        if len(path.parts) == 1 and path.suffix.lower() in {".md", ".json"}:
            keys.add(relative)
        if len(path.parts) == 2 and path.parts[0] == "production_standard" and path.suffix.lower() in {".md", ".json"}:
            keys.add(relative)
    # A manifest can retain stale optional pointers. Record absence as current
    # state; the complete V4 inventory will detect later creation/removal.
    missing = sorted(keys - set(files))
    return manifest.get("version"), sorted(keys & set(files)), declared, missing


def snapshot():
    if SNAPSHOT.exists():
        raise RuntimeError("Refusing to replace the current-task immutable baseline")
    started = now()
    protected, errors, declared, version, missing_v4_references = {}, [], {}, None, []
    for name, root in ROOTS.items():
        files, links, root_errors = inventory(root, exclude_revision=name == "original_episode")
        if name == "v4":
            version, keys, declared, missing_v4_references = current_v4_keys(files)
            policy = "All file size/mtime/link metadata; SHA256 of current manifest targets and key rule/SOP/config files"
        else:
            keys = list(files)
            policy = "Every regular file SHA256 plus all file size/mtime/link metadata"
        hashes, hash_errors = hash_paths(root, keys)
        root_errors.extend(hash_errors)
        # Detect concurrent add/remove/metadata changes during the baseline read.
        after, after_links, after_errors = inventory(root, exclude_revision=name == "original_episode")
        root_errors.extend(after_errors)
        if files != after or links != after_links:
            root_errors.append("Protected tree changed during baseline capture; do not use this incomplete baseline")
        errors.extend(f"{name}: {error}" for error in root_errors)
        protected[name] = {"path": str(root), "file_count": len(files),
                           "total_bytes": sum(item["size"] for item in files.values()),
                           "files": files, "directory_links": links, "sha256": hashes,
                           "hash_policy": policy, "errors": root_errors,
                           "excluded_subtrees": ["09_revisions"] if name == "original_episode" else []}
    inputs, input_errors = input_records()
    errors.extend(input_errors)
    current_hashes = protected["v4"]["sha256"]
    declared_notes = [{"path": p, "manifest_declared_sha256": value,
                      "current_baseline_sha256": current_hashes.get(p)}
                     for p, value in declared.items() if value and current_hashes.get(p) != value]
    report = {"schema": "jianying_layered_export_boundary_v1",
              "task_date": "2026-10-09",
              "started_at_utc": started, "completed_at_utc": now(),
              "export_revision": str(REV),
              "baseline_basis": "Fresh reads of the current filesystem for this export; no prior-run snapshot is used for comparison.",
              "allowed_write_root": str(REV),
              "policy": "No modifications to V4, original episode outside 09_revisions, old V5 trials, or source MP3/SRT; no Jianying library/index access.",
              "v4_current_manifest_version": version,
              "v4_references_missing_at_baseline": missing_v4_references,
              "manifest_declared_hash_differences_at_baseline": declared_notes,
              "manifest_difference_policy": "Informational only: existing differences are current baseline, not export-caused changes or a failure.",
              "protected_roots": protected, "original_inputs": inputs,
              "errors": errors, "snapshot_complete": not errors,
              "limits": "V4 content hashes cover selected rules/current manifest targets; remaining V4 files have metadata protection. Episode and old V5 trials have whole-tree file hashes. Access times are excluded because reads can update them. Directory links are recorded without traversal."}
    write_json(SNAPSHOT, report, exclusive=True)
    summary = {"snapshot_complete": report["snapshot_complete"], "snapshot": str(SNAPSHOT),
               "snapshot_sha256": digest(SNAPSHOT),
               "roots": {name: {"files": item["file_count"], "hashes": len(item["sha256"]),
                                  "bytes": item["total_bytes"]} for name, item in protected.items()},
               "original_inputs": len(inputs),
               "preexisting_manifest_differences": len(declared_notes), "errors": errors}
    print(json.dumps(summary, ensure_ascii=False), flush=True)
    return 0 if report["snapshot_complete"] else 1


def verify(report_name):
    original = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    if not original.get("snapshot_complete"):
        raise ValueError("Cannot verify against an incomplete baseline")
    if Path(original["export_revision"]).resolve() != REV:
        raise ValueError("Baseline export revision does not match")
    results = {}
    for name, prior in original["protected_roots"].items():
        root = ROOTS[name]
        if Path(prior["path"]).resolve() != root.resolve():
            raise ValueError("Baseline protected root does not match")
        files, links, errors = inventory(root, exclude_revision=name == "original_episode")
        before = prior["files"]
        added, removed = sorted(set(files) - set(before)), sorted(set(before) - set(files))
        changed = [{"path": path, "before": before[path], "after": files[path]}
                   for path in sorted(set(files) & set(before)) if files[path] != before[path]]
        hashes, hash_errors = hash_paths(root, prior["sha256"])
        errors.extend(hash_errors)
        hash_changes = [{"path": path, "before": value, "after": hashes.get(path)}
                        for path, value in prior["sha256"].items() if hashes.get(path) != value]
        links_changed = links != prior.get("directory_links", {})
        after, after_links, after_errors = inventory(root, exclude_revision=name == "original_episode")
        errors.extend(after_errors)
        if files != after or links != after_links:
            errors.append("Protected tree changed during verification")
        results[name] = {"path": str(root), "file_count": len(files), "hash_count": len(hashes),
                         "added": added, "removed": removed, "metadata_changes": changed,
                         "sha256_changes": hash_changes, "directory_links_changed": links_changed,
                         "errors": errors,
                         "unchanged": not (added or removed or changed or hash_changes or links_changed or errors)}
    inputs, input_errors = input_records()
    input_changes = [{"path": path, "before": info, "after": inputs.get(path)}
                     for path, info in original["original_inputs"].items() if inputs.get(path) != info]
    passed = all(item["unchanged"] for item in results.values()) and not input_errors and not input_changes
    report = {"schema": "jianying_layered_export_boundary_verification_v1",
              "checked_at_utc": now(), "snapshot": str(SNAPSHOT), "snapshot_sha256": digest(SNAPSHOT),
              "baseline_created_at_utc": original["completed_at_utc"],
              "results": results,
              "original_inputs": {"unchanged": not (input_errors or input_changes),
                                  "changes": input_changes, "errors": input_errors},
              "passed": passed,
              "limits": original["limits"],
              "native_jianying_validation": "not_performed; boundary verifier does not access draft library/index"}
    output = REV / report_name
    if require_output(output) == SNAPSHOT.resolve():
        raise ValueError("Verification must not overwrite the baseline")
    write_json(output, report)
    print(json.dumps({"passed": passed, "report": str(output),
                      "roots": {name: {"unchanged": item["unchanged"], "files": item["file_count"],
                                        "hashes": item["hash_count"]} for name, item in results.items()},
                      "original_inputs_unchanged": report["original_inputs"]["unchanged"]}, ensure_ascii=False), flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("snapshot", "verify"))
    parser.add_argument("--report", default="boundary_verification.json")
    args = parser.parse_args()
    require_output(SNAPSHOT)
    raise SystemExit(snapshot() if args.action == "snapshot" else verify(args.report))
