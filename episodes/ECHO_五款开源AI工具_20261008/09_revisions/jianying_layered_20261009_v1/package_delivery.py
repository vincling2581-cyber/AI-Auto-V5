#!/usr/bin/env python3
"""Seal the finished layered-export revision; never install/register a draft.

This script is intentionally separate from rendering. All required documentation
and QC must already be complete. It preserves the revision's portable directory
layout, maps delivered layer paths to package/media, excludes duplicate renders
and caches, and creates an external receipt binding every entry plus the ZIP hash.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import sys
import zipfile

sys.dont_write_bytecode = True
REV = Path(__file__).resolve().parent
PACKAGE = REV / "package"
ZIP_NAME = "ECHO_五款AI工具_剪映分层草稿.zip"
INDEX_NAME = "package/archive_inventory.json"
PREFLIGHT_NAME = "package/archive_preflight.json"
MAPPING_NAME = "package/archive_path_mapping.json"
ROOT_REQUIRED = (
    "build_draft.py", "export_layers.py", "scan_source.py", "verify_export.py",
    "package_delivery.py", "card_layers.json", "font_calibration_evidence.json",
    "boundary_verification.json",
)
PACKAGE_REQUIRED = (
    "draft_content.json", "manifest.json", "交付说明.md",
    "按框编辑索引.md", "panel_edit_index.json",
)
TREE_ROOTS = ("package", "adapter", "source/episode", "card_text", "catalog", "delivery_tools")
ROOT_OPTIONAL = (
    "adaptation_provenance.json", "text_plan.json", "text_difference_report.json",
    "text_difference_report.md", "verify_audio.py",
)
FORBIDDEN_PARTS = {"raster_cache", "card_media", "__pycache__", ".git", "node_modules"}
FONT_SUFFIXES = {".ttf", ".ttc", ".otf", ".woff", ".woff2"}
GENERATED = {INDEX_NAME, PREFLIGHT_NAME, MAPPING_NAME}
BINARY_STORED = {".mov", ".mp4", ".mp3", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".webm", ".zip"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def safe_relative(value):
    value = str(value).replace("\\", "/")
    posix, windows = PurePosixPath(value), PureWindowsPath(value)
    require(value and not posix.is_absolute() and not windows.is_absolute() and not windows.drive,
            f"Not a portable relative path: {value}")
    require(all(part not in {"", ".", ".."} for part in value.split("/")),
            f"Unsafe relative path: {value}")
    require(not any(":" in part or "\x00" in part for part in posix.parts),
            f"Invalid path component: {value}")
    return posix.as_posix()


def inside(path):
    path = Path(path)
    require(not path.is_symlink() and not (hasattr(path, "is_junction") and path.is_junction()),
            f"Links are not accepted in archive inputs: {path}")
    resolved = path.resolve()
    require(resolved.is_relative_to(REV) and resolved != REV,
            f"Path outside this revision: {path}")
    return resolved


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def save(path, value):
    path = inside(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json_bytes(value))


def stat_key(path):
    s = path.stat()
    return s.st_size, s.st_mtime_ns


def add_file(entries, path):
    path = inside(path)
    require(path.is_file(), f"Missing archive dependency: {path}")
    relative = safe_relative(path.relative_to(REV).as_posix())
    if relative in GENERATED:
        return
    require(not any(p in FORBIDDEN_PARTS for p in PurePosixPath(relative).parts),
            f"Cache/duplicate media must not enter archive: {relative}")
    require(path.suffix.lower() not in FONT_SUFFIXES,
            f"System font redistribution is not authorized: {relative}")
    require(path.suffix.lower() not in {".pyc", ".pyo"}, f"Bytecode is not deliverable: {relative}")
    if relative in entries:
        return
    before = stat_key(path)
    digest = sha(path)
    require(stat_key(path) == before, f"File changed during inventory: {relative}")
    entries[relative] = {"path": path, "data": None, "bytes": before[0], "sha256": digest,
                         "stat": before, "kind": "unchanged_file"}


def add_data(entries, relative, data, kind):
    relative = safe_relative(relative)
    entries[relative] = {"path": None, "data": data, "bytes": len(data),
                         "sha256": hashlib.sha256(data).hexdigest(), "stat": None, "kind": kind}


def add_tree(entries, relative):
    directory = inside(REV / relative)
    require(directory.is_dir(), f"Missing archive tree: {relative}")
    for base, dirs, files in os.walk(directory, followlinks=False):
        kept = []
        for name in sorted(dirs):
            candidate = Path(base) / name
            if name in FORBIDDEN_PARTS:
                continue
            inside(candidate)
            kept.append(name)
        dirs[:] = kept
        for name in sorted(files):
            if Path(name).suffix.lower() in {".pyc", ".pyo"}:
                continue
            add_file(entries, Path(base) / name)


def report_dependencies(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from report_dependencies(item)
    elif isinstance(value, list):
        for item in value:
            yield from report_dependencies(item)
    elif isinstance(value, str):
        normalized = value.replace("\\", "/")
        if normalized.startswith("qc/") and not normalized.endswith("/"):
            yield safe_relative(normalized)


def validate_structure():
    tool = inside(REV / "delivery_tools/scripts/validate_package.py")
    require(tool.is_file(), "Bundled package validator is missing")
    spec = importlib.util.spec_from_file_location("layered_delivery_validator", tool)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.validate_package(PACKAGE)
    require(result.get("passed") is True, f"Portable draft validation failed: {result.get('errors')}")
    return result


def preconditions():
    for relative in ROOT_REQUIRED:
        require(inside(REV / relative).is_file(), f"Required file not ready: {relative}")
    for relative in PACKAGE_REQUIRED:
        path = inside(PACKAGE / relative)
        require(path.is_file() and path.stat().st_size, f"Required package document not ready: {relative}")
    encoded_path = inside(REV / "qc/encoded_export_review.json")
    require(encoded_path.is_file(), "Final encoded-graphics QC is not ready")
    encoded = load(encoded_path)
    require(encoded.get("passed") is True and encoded.get("all_information_cards") is True,
            "Encoded-graphics report must pass for all information cards")
    hashes = encoded.get("hashes", {})
    bindings = {"card_layers": REV / "card_layers.json",
                "draft": PACKAGE / "draft_content.json",
                "package_manifest": PACKAGE / "manifest.json",
                "verifier": REV / "verify_export.py"}
    for key, path in bindings.items():
        require(hashes.get(key) == sha(path), f"Encoded QC is stale for {key}")
    boundary = load(REV / "boundary_verification.json")
    require(boundary.get("passed") is True, "Boundary verification did not pass")
    require(all(x.get("unchanged") for x in boundary["results"].values()) and
            boundary["original_inputs"].get("unchanged"), "Protected inputs changed")
    require((REV / "delivery_tools/PROVENANCE.json").is_file(), "Skill provenance is missing")
    return encoded, boundary, validate_structure()


def portable_contract(entries, manifest):
    data = load(REV / "card_layers.json")
    portable = deepcopy(data)
    by_source, mappings = {}, []
    for item in manifest["media"]:
        relative = safe_relative(item["path"])
        media_path = inside(PACKAGE / relative)
        require(relative.startswith("media/"), f"Package media outside media/: {relative}")
        require(media_path.is_file(), f"Missing packaged media: {relative}")
        require(media_path.stat().st_size == item["bytes"] and sha(media_path) == item["sha256"],
                f"Manifest media integrity failure: {relative}")
        original = item.get("source")
        if original:
            by_source.setdefault(safe_relative(original), []).append(item)
    for card in portable["cards"]:
        text_path = safe_relative(card["text_frames"])
        require(text_path in entries, f"Text samples missing from archive: {text_path}")
        for layer in card["layers"]:
            original = safe_relative(layer["path"])
            original_hash = layer.get("sha256")
            candidates = [item for item in by_source.get(original, []) if item["sha256"] == original_hash]
            if not candidates and original.startswith("package/media/"):
                candidates = [item for item in manifest["media"]
                              if "package/" + safe_relative(item["path"]) == original and
                              item["sha256"] == original_hash]
            require(len(candidates) == 1,
                    f"Layer has no unique matching packaged asset: {card['id']}/{layer['id']} from {original}")
            destination = "package/" + safe_relative(candidates[0]["path"])
            require(destination in entries, f"Relocated media missing from archive: {destination}")
            layer["path"] = destination
            mappings.append({"scene": card["id"], "layer": layer["id"], "from": original,
                             "to": destination, "sha256": original_hash})
        # Incremental export_layers --cards depends on the other cards' manifests.
        add_data(entries, f"card_manifests/{card['id']}.json", json_bytes(card), "portable_card_manifest")
    before_semantic, after_semantic = deepcopy(data), deepcopy(portable)
    for collection in (before_semantic, after_semantic):
        for card in collection["cards"]:
            for layer in card["layers"]:
                layer.pop("path", None)
    require(before_semantic == after_semantic, "Portable mapping changed non-path layer data")
    payload = json_bytes(portable)
    add_data(entries, "card_layers.json", payload, "media_paths_relocated")
    return {"schemaVersion": 1, "sourceCardLayersSha256": sha(REV / "card_layers.json"),
            "portableCardLayersSha256": hashlib.sha256(payload).hexdigest(),
            "onlyLayerPathFieldsChanged": True, "mapping": mappings,
            "evidenceBridge": "Encoded QC validated the original contract. Delivered contract differs only in layer paths; every referenced media SHA256 is identical.",
            "regeneration": "scan_source.py and export_layers.py regenerate card_media locally. The delivered contract and per-card manifests can directly use package/media for build_draft.py and verify_export.py."}


def collect(encoded, boundary, structure):
    entries = {}
    for relative in TREE_ROOTS:
        add_tree(entries, relative)
    for relative in ROOT_REQUIRED + ROOT_OPTIONAL:
        if (REV / relative).is_file():
            add_file(entries, REV / relative)
    # Final JSON reports only; temporary decoded images/caches are not collected.
    for path in sorted((REV / "qc").glob("*.json")):
        add_file(entries, path)
        for relative in report_dependencies(load(path)):
            candidate = inside(REV / relative)
            if candidate.is_file():
                add_file(entries, candidate)
            elif candidate.suffix:
                raise FileNotFoundError(f"QC report references a missing artifact: {relative}")
    # Reference frames needed for rerunning verify_export, even if future report
    # schemas omit their path field. These are QC evidence, not raster_cache.
    for path in sorted((REV / "qc").glob("reference_*.png")):
        add_file(entries, path)
    manifest = load(PACKAGE / "manifest.json")
    mapping = portable_contract(entries, manifest)
    required_source = [
        "source/episode/00_brief/input/voice_original.mp3",
        "source/episode/00_brief/input/subtitles_original.srt",
        "source/episode/00_brief/effective_defaults.json",
        "source/episode/03_storyboard/cards.json",
        "adapter/classify.py", "adapter/classify_bc.py",
        "adapter/instrument.js", "adapter/groups.js", "adapter/export_page.html",
    ]
    for relative in required_source:
        require(relative in entries, f"Re-render dependency is missing: {relative}")
    for card in load(REV / "source/episode/03_storyboard/cards.json")["cards"]:
        sid = card["id"]
        require(f"catalog/{sid}.json" in entries and f"card_text/{sid}.json" in entries,
                f"Complete source scan missing for {sid}")
        if sid.startswith("A"):
            require(f"source/episode/04_assets/illustrations/{sid}.png" in entries,
                    f"Original illustration missing for {sid}")
    # These generated reports are finalized BEFORE ZIP construction.
    save(PACKAGE / "archive_path_mapping.json", mapping)
    add_data(entries, MAPPING_NAME, json_bytes(mapping), "generated_before_archive")
    report = {
        "schemaVersion": 1, "createdAtUtc": now(), "status": "ready_for_archive_integrity_check",
        "packageRootInsideArchive": "package",
        "archiveLayout": "Extract to one folder; package/, adapter/, source/, catalog/, card_text/, card_manifests/, qc/, delivery_tools/ and root scripts retain their relative positions.",
        "packageValidation": structure,
        "encodedQc": {"path": "qc/encoded_export_review.json", "sha256": sha(REV / "qc/encoded_export_review.json"),
                      "passed": encoded["passed"], "allInformationCards": encoded["all_information_cards"]},
        "boundaryQc": {"path": "boundary_verification.json", "sha256": sha(REV / "boundary_verification.json"),
                       "passed": boundary["passed"], "snapshotSha256": boundary.get("snapshot_sha256")},
        "pathMapping": {"path": MAPPING_NAME, "sha256": entries[MAPPING_NAME]["sha256"],
                        "sourceCardLayersSha256": mapping["sourceCardLayersSha256"],
                        "portableCardLayersSha256": mapping["portableCardLayersSha256"]},
        "inputBindings": {name: sha(REV / name) for name in ROOT_REQUIRED},
        "environmentDependencies": [
            "Windows Microsoft YaHei must be installed locally; no font files are redistributed.",
            "Rendering requires Python, Pillow, Playwright with Chrome, and FFmpeg; JY_EXPORT_FFMPEG may select FFmpeg.",
            "build_draft.py and manual install_draft.py require the compatible private pyJianYingDraft fork used for this export; the runtime library is not bundled.",
            "The supported render path is scan_source.py -> export_layers.py -> build_draft.py from the extracted root."
        ],
        "excluded": ["raster_cache/", "card_media/ duplicate assets", "boundary_snapshot*.json",
                     "Python bytecode/caches", "system fonts", "draft-library files or root indexes"],
        "registration": "not_performed; install_draft.py is provided for a separate explicit manual action",
        "nativeJianyingPlaybackExport": "not_performed",
        "zipIntegrity": "CRC and every entry SHA256 are checked after construction and recorded in the external receipt, never retroactively inserted into this ZIP."
    }
    save(PACKAGE / "archive_preflight.json", report)
    add_data(entries, PREFLIGHT_NAME, json_bytes(report), "generated_before_archive")
    inventory = {
        "schemaVersion": 1, "createdAtUtc": now(), "hashAlgorithm": "SHA-256",
        "selfHashPolicy": "This inventory excludes itself to avoid circular hashing. The external ZIP receipt hashes every entry, including this inventory.",
        "entries": [{"path": name, "bytes": item["bytes"], "sha256": item["sha256"], "kind": item["kind"]}
                    for name, item in sorted(entries.items())]
    }
    save(PACKAGE / "archive_inventory.json", inventory)
    add_data(entries, INDEX_NAME, json_bytes(inventory), "generated_inventory")
    folded = [name.casefold() for name in entries]
    require(len(folded) == len(set(folded)), "Case-insensitive archive path collision")
    return entries


def build_archive(entries, replace=False):
    target = inside(REV / ZIP_NAME)
    partial = inside(REV / (ZIP_NAME + ".partial"))
    receipt_path = inside(REV / (ZIP_NAME + ".receipt.json"))
    require(replace or not target.exists(), "ZIP already exists; use --replace for a deliberate rebuild")
    require(replace or not receipt_path.exists(), "Receipt already exists; use --replace for a deliberate rebuild")
    require(not partial.exists(), "An unfinished .partial archive exists; inspect it before retrying")
    with zipfile.ZipFile(partial, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6,
                         allowZip64=True, strict_timestamps=False) as archive:
        for name, item in sorted(entries.items()):
            compressed = zipfile.ZIP_STORED if PurePosixPath(name).suffix.lower() in BINARY_STORED else zipfile.ZIP_DEFLATED
            if item["data"] is not None:
                archive.writestr(name, item["data"], compress_type=compressed)
            else:
                path = item["path"]
                require(stat_key(path) == item["stat"], f"File changed before ZIP write: {name}")
                archive.write(path, arcname=name, compress_type=compressed)
                require(stat_key(path) == item["stat"], f"File changed during ZIP write: {name}")
    verified = []
    with zipfile.ZipFile(partial, "r") as archive:
        require(len(archive.infolist()) == len(entries), "ZIP entry count differs")
        require(set(archive.namelist()) == set(entries), "ZIP entries differ from inventory")
        bad = archive.testzip()
        require(bad is None, f"ZIP CRC failed: {bad}")
        for name, item in sorted(entries.items()):
            h, size = hashlib.sha256(), 0
            with archive.open(name) as stream:
                for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
                    h.update(block)
                    size += len(block)
            require(size == item["bytes"] and h.hexdigest() == item["sha256"],
                    f"ZIP content differs from final inventory: {name}")
            verified.append({"path": name, "bytes": size, "sha256": h.hexdigest()})
    os.replace(partial, target)
    receipt = {"schemaVersion": 1, "verifiedAtUtc": now(), "passed": True,
               "archive": target.name, "archiveBytes": target.stat().st_size,
               "archiveSha256": sha(target), "entryCount": len(verified),
               "zipCrc": "passed_all_entries", "allEntrySha256": "passed",
               "entries": verified, "receiptOutsideArchive": True,
               "registration": "not_performed", "nativeJianyingPlaybackExport": "not_performed"}
    save(receipt_path, receipt)
    return {"passed": True, "archive": str(target), "archiveBytes": receipt["archiveBytes"],
            "archiveSha256": receipt["archiveSha256"], "entryCount": len(verified),
            "receipt": str(receipt_path), "zipCrc": "passed_all_entries", "allEntrySha256": "passed"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replace", action="store_true", help="Rebuild the known ZIP and external receipt after all checks pass")
    args = parser.parse_args()
    encoded, boundary, structure = preconditions()
    entries = collect(encoded, boundary, structure)
    print(json.dumps(build_archive(entries, replace=args.replace), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
