#!/usr/bin/env python3
"""Check package structure; native evidence is checked only by explicit request."""
import argparse
import json
import math
from collections import defaultdict
from pathlib import Path, PureWindowsPath

from native_evidence import digest as sha256, validate_native_evidence

ROLES = {"background", "animation", "panel", "graphics", "shared_graphics",
         "text", "brand", "narration", "sfx", "music"}
AUDIO_ROLES = {"narration", "sfx", "music"}
GRAPHIC_ROLES = {"graphics", "shared_graphics"}
SCALE_PROPERTIES = {"KFTypeScaleX", "KFTypeScaleY", "UNIFORM_SCALE"}


def validate_motion(segment, entry, fps, check, warn, info, claim_id):
    """Check serialized keyframes; report compatibility risks without claiming playback."""
    sid = segment['id']
    is_text = entry.get('role') in {'text', 'brand'}
    intent = entry.get('motionIntent', {})
    intent = intent if isinstance(intent, dict) else {}
    method = intent.get('visibilityMethod')
    source_scale = intent.get('scalePurpose') == 'source_animation' and method in {
        'segment_ranges', 'native_animation', 'native_alpha'}

    def scale_finding(code, detail):
        # An explicit opacity workaround remains invalid even if also called source animation.
        if method in {'zero_scale', 'scale_zero', 'alpha_to_scale'}:
            check('text.visibility_zero_scale', False, f'{sid}: {detail}; zero scale is not an opacity substitute')
        elif source_scale:
            info(code, sid, detail)
        else:
            warn(code, sid, detail)
    span = segment.get('target_timerange', {})
    duration = span.get('duration') if isinstance(span, dict) else None
    clip = segment.get('clip')
    if clip is not None and check('clip.object', isinstance(clip, dict), sid):
        for field in ('scale', 'transform'):
            values = clip.get(field)
            if values is not None and check('clip.' + field, isinstance(values, dict), sid):
                for axis in ('x', 'y'):
                    check('clip.' + field + '.' + axis, number(values.get(axis)), sid)
        for field in ('alpha', 'rotation'):
            if field in clip:
                check('clip.' + field, number(clip[field]), sid)
        if 'alpha' in clip and number(clip['alpha']):
            check('clip.alpha_range', 0 <= clip['alpha'] <= 1, sid)
        scale = clip.get('scale', {})
        if is_text and isinstance(scale, dict) and any(number(scale.get(axis)) and scale[axis] == 0 for axis in ('x', 'y')):
            scale_finding('text.static_zero_scale', 'Text has a zero base scale; inspect visibility and keyframe overrides')
    lists = segment.get('common_keyframes', [])
    if not check('keyframes.array', isinstance(lists, list), sid):
        return
    properties = set()
    for sequence in lists:
        if not check('keyframes.object', isinstance(sequence, dict), sid):
            continue
        claim_id(sequence.get('id'), 'keyframe_list')
        prop = sequence.get('property_type')
        if not check('keyframes.property', isinstance(prop, str) and bool(prop), sid):
            continue
        check('keyframes.native_property', prop != 'UNIFORM_SCALE',
              f'{sid}: UNIFORM_SCALE is an API alias; native serialization uses KFTypeScaleX and uniform_scale.on')
        check('keyframes.property_unique', prop not in properties, f'{sid}: {prop}')
        properties.add(prop)
        frames = sequence.get('keyframe_list')
        if not check('keyframes.points', isinstance(frames, list) and bool(frames), sid):
            continue
        points = []
        previous = -1
        for frame in frames:
            if not check('keyframe.object', isinstance(frame, dict), sid):
                continue
            claim_id(frame.get('id'), 'keyframe')
            offset, values = frame.get('time_offset'), frame.get('values')
            valid_time = integer(offset) and integer(duration) and 0 <= offset <= duration
            if check('keyframe.time', valid_time, f'{sid}: {offset}, duration={duration}'):
                check('keyframe.time_order', offset > previous, f'{sid}: {previous} -> {offset}')
                previous = offset
            valid_values = isinstance(values, list) and len(values) == 1 and number(values[0])
            check('keyframe.values', valid_values, f'{sid}: {prop}: {values}')
            if valid_values:
                value = values[0]
                if prop == 'KFTypeAlpha':
                    check('keyframe.alpha_range', 0 <= value <= 1, sid)
                elif prop == 'KFTypeVolume':
                    check('keyframe.volume_range', value >= 0, sid)
                if valid_time:
                    points.append((offset, value))
        if is_text and prop == 'KFTypeAlpha':
            warn('text.alpha_capability_unverified', sid,
                 'Text KFTypeAlpha support is not established by the enum or static layout evidence; record version-specific native motion evidence before claiming it works.')
        if is_text and prop in SCALE_PROPERTIES:
            if points and all(abs(value) <= 1e-9 for _, value in points):
                scale_finding('text.constant_zero_scale', {'property': prop, 'detail': 'All scale keyframes are zero'})
            for (first_time, first), (last_time, last) in zip(points, points[1:]):
                if (abs(first) <= 1e-9) == (abs(last) <= 1e-9):
                    continue
                detail = {'property': prop, 'from': first, 'to': last,
                          'startUs': span.get('start', 0) + first_time,
                          'endUs': span.get('start', 0) + last_time,
                          'withinOneFrame': number(fps) and fps > 0 and last_time - first_time <= 1000000 / fps + 1}
                scale_finding('text.zero_scale_transition', detail)
    check('keyframes.scale_exclusive', not ('UNIFORM_SCALE' in properties and properties & {'KFTypeScaleX', 'KFTypeScaleY'}), sid)
    # Native uniform scaling uses KFTypeScaleX with segment.uniform_scale.on, not the enum alias.
    uniform = segment.get('uniform_scale', {})
    if isinstance(uniform, dict) and uniform.get('on') is True:
        check('keyframes.native_uniform_scale_exclusive', 'KFTypeScaleY' not in properties, sid)


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def font_family(value):
    """Read an explicitly named family; keep path and identity separate."""
    if not isinstance(value, dict):
        return None
    for key in ('fontName', 'family', 'font_name', 'name'):
        name = value.get(key)
        if isinstance(name, str) and name.strip():
            return name.strip()
    return None


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


def validate_package(package, native_evidence=None, allow_unvalidated_test_draft=False, *,
                     structure_only=False, require_native_evidence=False):
    root = Path(package).resolve()
    result = {"status": "failed", "passed": False, "checks": [], "errors": [], "warnings": [],
              "fontWarnings": [], "fontValidation": "not_performed", "motionInfo": [],
              "nativeValidation": "not_performed", "visualValidation": "not_performed",
              "structuralValidation": "failed", "motionValidation": "not_performed",
              "audioValidation": "metadata_only",
              "packageRoot": str(root), "deliveryReady": False,
              "validationMode": "delivery" if require_native_evidence else ("test_only" if allow_unvalidated_test_draft else "structure_only")}

    def check(name, condition, detail=""):
        okay = bool(condition)
        result["checks"].append({"name": name, "passed": okay, "detail": str(detail)})
        if not okay:
            result["errors"].append(f"{name}: {detail}")
        return okay

    def warn(code, sid, detail):
        result['warnings'].append({'code': code, 'segmentId': sid, 'detail': detail})

    def info(code, sid, detail):
        result['motionInfo'].append({'code': code, 'segmentId': sid, 'detail': detail,
                                     'verification': 'source_intent_declared_only'})

    native_ids = {}

    def claim_id(value, kind):
        if not check(kind + '.id', isinstance(value, str) and bool(value.strip()), value):
            return False
        okay = check('native.id_unique', value not in native_ids, f'{kind}: {value}; first={native_ids.get(value)}')
        native_ids.setdefault(value, kind)
        return okay

    if not check('validation.mode', sum(bool(x) for x in (structure_only, require_native_evidence, allow_unvalidated_test_draft)) <= 1,
                 'structure_only, require_native_evidence and legacy test mode are mutually exclusive'):
        return result
    # Choosing an evidence file is not authorization to run the native gate.
    # No-mode callers share the explicit structure-only path.
    structure_only = not (require_native_evidence or allow_unvalidated_test_draft)

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
        check("schemaVersion", integer(manifest.get("schemaVersion")) and manifest.get("schemaVersion") == 1, "expected 1")
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
        check("draft.duration", integer(draft.get("duration")) and integer(project.get("durationUs"))
              and abs(draft["duration"] - project["durationUs"]) <= 1)
        collections = {}
        for key in ("media", "segments", "panels", "sources"):
            value = manifest.get(key)
            collections[key] = value if isinstance(value, list) else []
            check("manifest." + key, isinstance(value, list), "expected array")
        dependencies = manifest.get('fontDependencies', [])
        system_fonts = set()
        if check('fontDependencies.array', isinstance(dependencies, list)):
            for dependency in dependencies:
                if not check('fontDependencies.object', isinstance(dependency, dict)):
                    continue
                family = font_family(dependency)
                if check('fontDependencies.family', family is not None, dependency):
                    if dependency.get('redistributed') is False or dependency.get('source') == 'system':
                        system_fonts.add(family.casefold())
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
            if not check('material.collection', isinstance(items, list), category):
                continue
            for item in items:
                if not isinstance(item, dict) or not item.get("id"):
                    check("material.id", False, category)
                    continue
                mid = item["id"]
                claim_id(mid, 'material')
                if not check("material.unique", isinstance(mid, str) and mid not in material_table, mid):
                    continue
                material_table[mid], material_types[mid] = item, category
                if category in {'videos', 'audios'}:
                    check('material.local_path', isinstance(item.get('path'), str) and bool(item['path'].strip()), mid)
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
            check('segment.sourceObjectIds_unique', len(ids) == len(set(ids)), sid)
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
            if not claim_id(tid, 'track'):
                continue
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
                claim_id(sid, 'segment')
                check("draft.segment.unique", sid not in actual, sid)
                actual[sid] = segment
                check("draft.segment.manifest", sid in described, sid)
                if not check("draft.segment.material", isinstance(mid, str) and mid in material_table, f"{sid}: {mid}"):
                    continue
                refs = segment.get("extra_material_refs", [])
                if check("draft.segment.extra_refs", isinstance(refs, list), sid):
                    for ref in refs:
                        check("draft.segment.extra_ref_exists", isinstance(ref, str) and ref in material_table, f"{sid}: {ref}")
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
                validate_motion(segment, entry, project.get('fps'), check, warn, info, claim_id)
                if role in {"text", "brand"}:
                    check("text.native_material", material_types.get(mid) == "texts" and track.get("type") == "text", sid)
                    material = material_table[mid]
                    try:
                        content = json.loads(material.get('content', '{}'))
                    except (ValueError, TypeError):
                        content = None
                    if check('text.content', isinstance(content, dict) and isinstance(content.get('text'), str), sid):
                        styles = content.get('styles')
                        if check('text.styles', isinstance(styles, list) and bool(styles), sid):
                            for style in styles:
                                if not check('text.style', isinstance(style, dict), sid):
                                    continue
                                check('text.size', number(style.get('size')) and style['size'] > 0, sid)
                                font = style.get('font', {})
                                if not check('fonts.styleFont', isinstance(font, dict), sid):
                                    continue
                                path = font.get('path', '')
                                if isinstance(path, str) and path.strip():
                                    # Nonempty paths always use portable media validation above;
                                    # a system declaration cannot excuse missing packaged bytes.
                                    if result['fontValidation'] == 'not_performed':
                                        result['fontValidation'] = 'packaged_dependencies_checked'
                                else:
                                    family = font_family(font) or font_family(style) or font_family({'font_name': material.get('font_name')})
                                    explicit = isinstance(path, str) and family is not None and family.casefold() in system_fonts
                                    if check('fonts.segmentExplicit', explicit,
                                             f'{sid}: each style needs a portable font path or a matching declared system font ({family})'):
                                        result['fontValidation'] = 'system_dependency_unverified'
                                        warning = {'code': 'fonts.system_dependency_unverified', 'segmentId': sid,
                                                   'fontName': family, 'detail': 'System font dependency declared; local availability, substitution and native rendering were not verified'}
                                        if warning not in result['fontWarnings']:
                                            result['fontWarnings'].append(warning)
                elif role in AUDIO_ROLES:
                    check("audio.native_material", material_types.get(mid) == "audios" and track.get("type") == "audio", sid)
                else:
                    check("visual.native_material", material_types.get(mid) == "videos" and track.get("type") == "video", sid)
                material = material_table[mid]
                timed_media = role in AUDIO_ROLES or (material_types.get(mid) == 'videos' and material.get('type') == 'video')
                source_span = segment.get('source_timerange')
                if timed_media or source_span is not None:
                    valid_source = isinstance(source_span, dict) and integer(source_span.get('start')) and integer(source_span.get('duration'))
                    valid_source = valid_source and source_span['start'] >= 0 and source_span['duration'] > 0
                    if check('media.source_timerange', valid_source, sid):
                        source_duration = material.get('duration')
                        if timed_media:
                            check('media.duration', integer(source_duration) and source_duration > 0, sid)
                            check('media.source_within_duration', integer(source_duration) and source_span['start'] + source_span['duration'] <= source_duration + 1, sid)
                        speed = segment.get('speed', 1.0)
                        if check('media.speed', number(speed) and speed > 0, sid) and valid_span:
                            for ref in refs if isinstance(refs, list) else []:
                                if isinstance(ref, str) and material_types.get(ref) == 'speeds':
                                    recorded_speed = material_table[ref].get('speed')
                                    check('media.speed_material_consistent', number(recorded_speed) and abs(recorded_speed - speed) <= 1e-6, sid)
                            curved = any(material_types.get(ref) == 'speeds' and material_table[ref].get('curve_speed')
                                         for ref in refs if isinstance(ref, str) and ref in material_table) if isinstance(refs, list) else False
                            if curved:
                                warn('media.curved_speed_unchecked', sid, 'Source/target mapping requires curve-aware review')
                            else:
                                check('media.source_target_duration', abs(source_span['duration'] - span['duration'] * speed) <= max(1, speed), sid)
                volume = segment.get("volume", 1.0)
                if track.get('type') in {'audio', 'video'}:
                    check('audio.volume_valid', number(volume) and volume >= 0, sid)
                audible = track.get("type") == "audio" or role in AUDIO_ROLES or (
                    track.get("type") == "video" and number(volume) and volume != 0)
                if audible or "expectedVolume" in entry:
                    expected = entry.get("expectedVolume")
                    check("audio.explicit_volume", number(expected) and expected >= 0, sid)
                    check("audio.gain_applied_once", number(volume) and number(expected) and abs(volume - expected) <= 0.000001,
                          f"{sid}: actual={volume}, expected={expected}")
                if "audioGainBakedDb" in entry:
                    check("audio.baked_gain_record", number(entry["audioGainBakedDb"]), sid)
                if valid_span:
                    for ref in refs if isinstance(refs, list) else []:
                        if isinstance(ref, str) and material_types.get(ref) == 'audio_fades':
                            for field in ('fade_in_duration', 'fade_out_duration'):
                                fade = material_table[ref].get(field)
                                check('audio.fade_duration', integer(fade) and 0 <= fade <= span['duration'], f'{sid}: {field}={fade}')
                group = segment.get("group_id")
                if group:
                    if check('group.id', isinstance(group, str), sid) and isinstance(scene, str) and isinstance(owner, str):
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
    result["structuralValidation"] = "passed" if not result["errors"] else "failed"
    result['motionValidation'] = 'requires_review' if result['warnings'] else 'not_performed'
    if not result["errors"] and require_native_evidence:
        evidence = validate_native_evidence(root, manifest, draft, native_evidence, check)
        result["nativeEvidence"] = evidence
        result["nativeValidation"] = evidence["status"]
    elif allow_unvalidated_test_draft:
        result["nativeValidation"] = "bypassed_for_test_only"
    result["passed"] = not result["errors"]
    result["deliveryReady"] = result["passed"] and require_native_evidence and not result['warnings']
    result["status"] = ("structure_passed" if structure_only else ("test_only_passed" if allow_unvalidated_test_draft else "passed")) if result["passed"] else "failed"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--native-evidence", type=Path, help="Evidence JSON inside the package; default native-evidence.json")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--structure-only', action='store_true', help='Check package structure only (default); does not open Jianying or require native evidence')
    modes.add_argument('--require-native-evidence', action='store_true', help='Explicitly check existing native evidence; never capture evidence or operate Jianying')
    modes.add_argument("--allow-unvalidated-test-draft", action="store_true",
                        help="Structure-only test/calibration check; never marks delivery ready")
    args = parser.parse_args()
    report = validate_package(args.package, args.native_evidence, args.allow_unvalidated_test_draft,
                              structure_only=args.structure_only, require_native_evidence=args.require_native_evidence)
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
