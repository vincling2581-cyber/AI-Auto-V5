#!/usr/bin/env python3
"""Check the portable editable-draft contract; no editor or visual claims."""
import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path, PureWindowsPath

ROLES = {"background", "animation", "panel", "graphics", "shared_graphics",
         "text", "brand", "narration", "sfx", "music"}
AUDIO_ROLES = {"narration", "sfx", "music"}
GRAPHIC_ROLES = {"graphics", "shared_graphics"}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def path_fields(value, label="materials"):
    """Include font references inside JSON-encoded native text content."""
    if isinstance(value, dict):
        for key, child in value.items():
            where = f"{label}.{key}"
            if (key == "path" or key.endswith("_path")) and isinstance(child, str) and child:
                yield where, child
            elif key == "content" and isinstance(child, str):
                try:
                    embedded = json.loads(child)
                except (ValueError, TypeError):
                    continue
                yield from path_fields(embedded, where)
            else:
                yield from path_fields(child, where)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from path_fields(child, f"{label}[{index}]")


def validate_package(package):
    root = Path(package).resolve()
    result = {"status": "failed", "passed": False, "checks": [], "errors": [],
              "nativeValidation": "not_performed", "visualValidation": "not_performed",
              "packageRoot": str(root)}

    def check(name, condition, detail=""):
        okay = bool(condition)
        result["checks"].append({"name": name, "passed": okay, "detail": str(detail)})
        if not okay:
            result["errors"].append(f"{name}: {detail}")
        return okay

    def portable_path(raw, label):
        if not check(label, isinstance(raw, str) and bool(raw), "path must be a nonempty string"):
            return None
        normalized = raw.replace("\\", "/")
        win = PureWindowsPath(raw)
        parts = normalized.split("/")
        candidate = (root / normalized).resolve()
        valid = not (win.drive or win.root or ":" in raw or ".." in parts)
        valid = valid and candidate.is_relative_to(root) and candidate != root
        if not check(label + ".contained", valid, raw):
            return None
        return normalized, candidate

    try:
        manifest_path, draft_path = root / "manifest.json", root / "draft_content.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        draft = json.loads(draft_path.read_text(encoding="utf-8-sig"))
        result["manifestSha256"], result["draftSha256"] = sha256(manifest_path), sha256(draft_path)
        if not check("root_objects", isinstance(manifest, dict) and isinstance(draft, dict)):
            return result
        check("schemaVersion", manifest.get("schemaVersion") == 1, "expected 1")
        project = manifest.get("project", {})
        if not check("project", isinstance(project, dict)):
            return result
        for key in ("width", "height", "durationUs"):
            check("project." + key, integer(project.get(key)) and project[key] > 0, project.get(key))
        check("project.name", isinstance(project.get("name"), str) and bool(project["name"]))
        check("project.fps", number(project.get("fps")) and project["fps"] > 0, project.get("fps"))
        check("draft.name", draft.get("name") == project.get("name"), draft.get("name"))
        canvas = draft.get("canvas_config", {})
        for key in ("width", "height"):
            check("draft.canvas." + key, isinstance(canvas, dict) and canvas.get(key) == project.get(key))
        check("draft.fps", number(draft.get("fps")) and number(project.get("fps"))
              and abs(draft["fps"] - project["fps"]) < 0.000001)
        check("draft.duration", number(draft.get("duration")) and number(project.get("durationUs"))
              and abs(draft["duration"] - project["durationUs"]) <= 1)
        collections = {}
        for key in ("media", "segments", "panels", "sources"):
            value = manifest.get(key)
            collections[key] = value if isinstance(value, list) else []
            check("manifest." + key, isinstance(value, list), "expected array")
        media = {}
        for index, entry in enumerate(collections["media"]):
            label = f"media[{index}]"
            if not check(label + ".object", isinstance(entry, dict)):
                continue
            pair = portable_path(entry.get("path"), label + ".path")
            if pair is None:
                continue
            relative, path = pair
            # Canonical path identity also detects aliases and case variants on Windows.
            key = str(path).casefold()
            check(label + ".unique", key not in media, relative)
            media[key] = entry
            if not check(label + ".exists", path.is_file(), relative):
                continue
            check(label + ".bytes", integer(entry.get("bytes")) and entry["bytes"] == path.stat().st_size, relative)
            expected_hash = entry.get("sha256", "")
            check(label + ".sha256", isinstance(expected_hash, str)
                  and expected_hash.lower() == sha256(path), relative)
        material_table = {}
        material_types = {}
        raw_materials = draft.get("materials", {})
        if not check("draft.materials", isinstance(raw_materials, dict)):
            return result
        for category, items in raw_materials.items():
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict) or not item.get("id"):
                    check("material.id", False, category)
                    continue
                mid = item["id"]
                if not check("material.unique", isinstance(mid, str) and mid not in material_table, mid):
                    continue
                material_table[mid], material_types[mid] = item, category
        for label, raw in path_fields(raw_materials):
            pair = portable_path(raw, label)
            if pair:
                check(label + ".manifest", str(pair[1]).casefold() in media, raw)
        owners = set()
        for panel in collections["panels"]:
            if not check("panel.object", isinstance(panel, dict)):
                continue
            scene, pid = panel.get("scene"), panel.get("id")
            if not check("panel.identity", isinstance(scene, str) and bool(scene)
                         and isinstance(pid, str) and bool(pid) and pid != "shared", panel):
                continue
            key = (scene, pid)
            check("panel.unique", key not in owners, key)
            owners.add(key)

        def owner_valid(scene, owner):
            return isinstance(scene, str) and bool(scene) and isinstance(owner, str) and (
                owner == "shared" or (scene, owner) in owners)

        source_objects = {}
        source_scenes = set()
        for source in collections["sources"]:
            if not check("source.object", isinstance(source, dict)):
                continue
            scene = source.get("scene")
            if not check("source.scene", isinstance(scene, str) and bool(scene) and scene not in source_scenes, scene):
                continue
            source_scenes.add(scene)
            if not check("source.objects", isinstance(source.get("objects"), list), scene):
                continue
            for obj in source["objects"]:
                if not check("source.item", isinstance(obj, dict), scene):
                    continue
                oid, owner = obj.get("id"), obj.get("owner")
                if not check("source.identity", isinstance(oid, str) and bool(oid), obj):
                    continue
                key = (scene, oid)
                check("source.unique", key not in source_objects, key)
                check("source.owner", owner_valid(scene, owner), obj)
                source_objects[key] = owner
        described = {}
        text_keys = set()
        source_usage = defaultdict(list)
        for entry in collections["segments"]:
            if not check("segment.object", isinstance(entry, dict)):
                continue
            sid, scene, owner, role = (entry.get(k) for k in ("id", "scene", "owner", "role"))
            if not check("segment.identity", isinstance(sid, str) and bool(sid), sid):
                continue
            check("segment.unique", sid not in described, sid)
            described[sid] = entry
            check("segment.role", role in ROLES, f"{sid}: {role}")
            check("segment.owner", owner_valid(scene, owner), f"{sid}: {scene}/{owner}")
            if role in {"panel", "graphics"}:
                check("segment.panel_owner", owner != "shared", sid)
            if role == "shared_graphics":
                check("segment.shared_owner", owner == "shared", sid)
            if role in {"text", "brand"}:
                text_key = entry.get("textKey")
                if check("segment.textKey", isinstance(text_key, str) and bool(text_key), sid):
                    key = (scene, text_key)
                    check("text.single_logical_segment", key not in text_keys, key)
                    text_keys.add(key)
            ids = entry.get("sourceObjectIds", [])
            if not check("segment.sourceObjectIds", isinstance(ids, list) and all(isinstance(i, str) and i for i in ids), sid):
                continue
            if role in GRAPHIC_ROLES:
                check("graphics.has_sources", bool(ids), sid)
                for oid in ids:
                    key = (scene, oid)
                    check("graphics.known_source", key in source_objects, f"{sid}: {oid}")
                    check("graphics.single_owner", source_objects.get(key) == owner, f"{sid}: {oid}")
                    source_usage[key].append(sid)
            else:
                check("nongraphics.no_sourceObjectIds", not ids, sid)
        for key in source_objects:
            check("source.coverage_once", len(source_usage[key]) == 1, f"{key}: {source_usage[key]}")
        actual, groups, material_users = {}, defaultdict(set), defaultdict(list)
        tracks = draft.get("tracks")
        if not check("draft.tracks", isinstance(tracks, list)):
            return result
        maximum_end = 0
        track_ids = set()
        for track in tracks:
            if not check("track.object", isinstance(track, dict)):
                continue
            tid = track.get("id")
            check("track.unique", isinstance(tid, str) and bool(tid) and tid not in track_ids, tid)
            track_ids.add(tid)
            segments = track.get("segments")
            if not check("track.segments", isinstance(segments, list), tid):
                continue
            intervals = []
            for segment in segments:
                if not check("draft.segment.object", isinstance(segment, dict), tid):
                    continue
                sid, mid = segment.get("id"), segment.get("material_id")
                if not check("draft.segment.id", isinstance(sid, str) and bool(sid), tid):
                    continue
                check("draft.segment.unique", sid not in actual, sid)
                actual[sid] = segment
                check("draft.segment.manifest", sid in described, sid)
                check("draft.segment.material", mid in material_table, f"{sid}: {mid}")
                refs = segment.get("extra_material_refs", [])
                if check("draft.segment.extra_refs", isinstance(refs, list), sid):
                    for ref in refs:
                        check("draft.segment.extra_ref_exists", ref in material_table, f"{sid}: {ref}")
                span = segment.get("target_timerange", {})
                valid_span = isinstance(span, dict) and integer(span.get("start")) and integer(span.get("duration"))
                valid_span = valid_span and span["start"] >= 0 and span["duration"] > 0
                if check("segment.time_range", valid_span, sid):
                    start, end = span["start"], span["start"] + span["duration"]
                    intervals.append((start, end, sid))
                    maximum_end = max(maximum_end, end)
                    check("segment.within_duration", number(project.get("durationUs")) and end <= project["durationUs"] + 1, sid)
                entry = described.get(sid)
                if not entry:
                    continue
                role, owner, scene = entry.get("role"), entry.get("owner"), entry.get("scene")
                if role in {"text", "brand"}:
                    check("text.native_material", material_types.get(mid) == "texts" and track.get("type") == "text", sid)
                elif role in AUDIO_ROLES:
                    check("audio.native_material", material_types.get(mid) == "audios" and track.get("type") == "audio", sid)
                else:
                    check("visual.native_material", material_types.get(mid) == "videos" and track.get("type") == "video", sid)
                volume = segment.get("volume", 1.0)
                audible = track.get("type") == "audio" or role in AUDIO_ROLES or (
                    track.get("type") == "video" and number(volume) and volume != 0)
                if audible or "expectedVolume" in entry:
                    expected = entry.get("expectedVolume")
                    check("audio.explicit_volume", number(expected) and expected >= 0, sid)
                    check("audio.gain_applied_once", number(volume) and number(expected) and abs(volume - expected) <= 0.000001,
                          f"{sid}: actual={volume}, expected={expected}")
                if "audioGainBakedDb" in entry:
                    check("audio.baked_gain_record", number(entry["audioGainBakedDb"]), sid)
                group = segment.get("group_id")
                if group:
                    groups[group].add((scene, owner))
                material_users[mid].append((sid, scene, owner, role))
            intervals.sort()
            furthest_end, previous = -1, None
            for start, end, sid in intervals:
                check("track.no_overlap", start >= furthest_end - 1, f"{tid}: {previous} / {sid}")
                if end > furthest_end:
                    furthest_end, previous = end, sid
        check("segments.complete", set(actual) == set(described),
              f"only draft={sorted(set(actual)-set(described))}; only manifest={sorted(set(described)-set(actual))}")
        check("timeline.nonempty", bool(actual))
        check("timeline.duration", number(project.get("durationUs")) and abs(maximum_end - project["durationUs"]) <= 1, maximum_end)
        for gid, identities in groups.items():
            check("group.no_cross_panel_link", len(identities) <= 1, f"{gid}: {sorted(identities)}")
        for mid, users in material_users.items():
            contextual = {(scene, owner) for _, scene, owner, role in users if role in {"panel", "graphics", "shared_graphics", "text", "brand"}}
            check("material.no_cross_owner_reuse", len(contextual) <= 1, f"{mid}: {users}")
            native_texts = [sid for sid, _, _, role in users if role in {"text", "brand"}]
            check("text.independent_material", len(native_texts) <= 1, f"{mid}: {native_texts}")
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        check("package.read_or_structure", False, f"{type(exc).__name__}: {exc}")
    result["passed"] = not result["errors"]
    result["status"] = "passed" if result["passed"] else "failed"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = validate_package(args.package)
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
