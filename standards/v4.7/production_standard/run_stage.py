"""Validate a new episode's locked inputs before running its Python stage entry.

This is an execution entry, not a renderer or a pixel/semantic acceptance tool.
Legacy episodes keep their original entry points. No files are written by the
preflight itself; only an explicitly selected child script may produce output.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType

STANDARD_VERSION = "4.7"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def contained(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError("Path leaves its declared root: " + str(relative))
    return path


def load_module(path, name):
    # Loading an episode's checks must not create files in its locked snapshot.
    module = ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def value_at(data, dotted):
    for part in dotted.split("."):
        if not isinstance(data, dict) or part not in data:
            raise ValueError("Missing effective-default field: " + dotted)
        data = data[part]
    return data


def preflight(episode_root, entry=None):
    root = Path(episode_root).resolve()
    result = {"passed": False, "errors": [], "episode_root": str(root),
              "scope": "locked_inputs_and_declared_timeline_before_execution",
              "actual_renderer_parameter_consumption": "not_proven",
              "pixel_and_subjective_review": "not_performed"}
    try:
        standard = contained(root, "00_brief/standard_snapshot")
        manifest_path = standard / "production_standard.json"
        manifest = read_json(manifest_path)
        if manifest.get("version") != STANDARD_VERSION:
            raise ValueError("This entry supports v4.7 episodes; use the legacy episode's original locked entry.")
        for lock in (root / "00_brief/standard_lock.json", standard / "standard_lock.json"):
            if lock.read_bytes() != manifest_path.read_bytes():
                raise ValueError("Episode standard lock differs from its snapshot: " + str(lock))
        locked_paths = [item["path"] for item in manifest["files"]]
        if len(locked_paths) != len(set(locked_paths)):
            raise ValueError("Duplicate locked dependency")
        for key in ("verifier", "episode_validator", "stage_runner", "layer_contract"):
            if manifest[key] not in locked_paths:
                raise ValueError("Entry is absent from the locked dependencies: " + key)
        # Verify bytes before loading the snapshot's own validation modules.
        for item in manifest["files"]:
            path = contained(standard, item["path"])
            if digest(path) != item["sha256"]:
                raise ValueError("Locked standard dependency changed: " + item["path"])
        verifier = load_module(contained(standard, manifest["verifier"]), "episode_standard_verifier")
        verifier.verify(root=standard)
        validator = load_module(contained(standard, manifest["episode_validator"]), "episode_contract_validator")
        contract_result = validator.validate(root)
        if not contract_result["passed"]:
            result["errors"].extend(contract_result["errors"])
            return result
        spec = read_json(contained(standard, manifest["layer_contract"]))
        defaults_path = contained(root, "00_brief/effective_defaults.json")
        defaults = read_json(defaults_path)
        contract_path = contained(root, spec["episode_contract"])
        contract = read_json(contract_path)
        # These are the current standard's execution invariants, not visual
        # preferences such as palette, typography or local animation durations.
        expected = {
            "version": manifest["version"],
            "animation.max_static_seconds": spec["illustration"]["max_contiguous_image_seconds"],
            "animation.target_static_seconds": None,
            "animation.fixed_cut_interval_seconds": None,
            "animation.internal_motion_allowed": False,
            "animation.camera_motion_allowed": False,
            "animation.transition": spec["illustration"]["transition"],
            "animation.corner_labels_enabled": False,
            "illustration.presentation_mode": spec["illustration"]["presentation_mode"],
            "illustration.internal_motion_allowed": False,
            "illustration.camera_motion_allowed": False,
            "illustration.transition": spec["illustration"]["transition"],
            "illustration.corner_labels_enabled": False,
            "cards.max_static_seconds": spec["information_card"]["max_contiguous_image_seconds"],
            "cards.corner_labels_enabled": False,
            "layout.corner_labels_enabled": False,
            "layout.badge_optional": False,
        }
        if contract.get("subtitles", {}).get("enabled"):
            expected.update({"layout.subtitle_independent_layer": True,
                             "layout.subtitle_fixed_position": True,
                             "layout.subtitle_alignment": "bottom_center"})
        for field, required in expected.items():
            actual = value_at(defaults, field)
            if actual != required or (isinstance(required, bool) and actual is not required):
                result["errors"].append("Effective defaults conflict with the locked contract: " + field)
        configured_fps = value_at(defaults, "video.fps")
        if isinstance(configured_fps, bool) or Fraction(str(configured_fps)) != Fraction(str(contract["fps"])):
            result["errors"].append("Effective video.fps differs from the production contract")
        selected = None
        if entry is not None:
            selected = contained(root, entry)
            if selected.suffix.lower() != ".py" or not selected.is_file():
                raise ValueError("Stage entry must be an existing Python file inside this episode")
        result.update({
            "passed": not result["errors"], "standard_version": manifest["version"],
            "standard_revision": manifest.get("revision"),
            "standard_sha256": digest(manifest_path),
            "effective_defaults": str(defaults_path), "effective_defaults_sha256": digest(defaults_path),
            "production_contract": str(contract_path), "production_contract_sha256": digest(contract_path),
            "entry": str(selected) if selected else None,
            "entry_sha256": digest(selected) if selected else None,
            "clip_counts": contract_result["clip_counts"],
        })
    except (OSError, ValueError, TypeError, KeyError, AttributeError, ZeroDivisionError) as exc:
        result["errors"].append(str(exc))
        result["passed"] = False
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episode-root", type=Path, required=True)
    parser.add_argument("--stage", choices=("render", "export"), required=True)
    parser.add_argument("--entry", type=Path, help="Explicit Python entry relative to this episode root")
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("entry_args", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if not args.check_only and args.entry is None:
        parser.error("--entry is required unless --check-only is used")
    report = preflight(args.episode_root, args.entry)
    report["stage"] = args.stage
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
    if not report["passed"]:
        return 1
    if args.check_only:
        return 0
    env = os.environ.copy()
    env.update({"V5_EPISODE_ROOT": report["episode_root"],
                "V5_EFFECTIVE_DEFAULTS": report["effective_defaults"],
                "V5_PRODUCTION_CONTRACT": report["production_contract"],
                "V5_STAGE": args.stage})
    forwarded = args.entry_args[1:] if args.entry_args[:1] == ["--"] else args.entry_args
    return subprocess.run([sys.executable, report["entry"], *forwarded],
                          cwd=report["episode_root"], env=env, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
