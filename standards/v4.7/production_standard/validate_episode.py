"""Read-only validation of the v4.7 declared main-visual production contract.

Does not render, inspect pixels, listen, open an editor, or certify semantic quality.
Run after drafting and after changing the timeline/asset mapping. Actual encoded
image holds, corner-label absence and subjective A/V have separate evidence.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

SPEC_PATH = Path(__file__).with_name('layer_contract.json')


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def is_frame(value):
    return isinstance(value, int) and not isinstance(value, bool)


def validate(episode_root, contract_path=None):
    root = Path(episode_root).resolve()
    spec = read_json(SPEC_PATH)
    path = Path(contract_path) if contract_path else root / spec['episode_contract']
    if not path.is_absolute():
        path = root / path
    errors, warnings = [], []
    report = {'schema_version': 1, 'standard_version': spec['standard_version'],
              'scope': 'declared_timeline_configuration_and_asset_identity_only',
              'contract': str(path.resolve()), 'errors': errors, 'warnings': warnings,
              'pixel_and_semantic_review': 'not_performed',
              'normal_speed_subjective_av': 'not_performed'}
    try:
        data = read_json(path)
        report['contract_sha256'] = digest(path)
        if not isinstance(data, dict):
            raise ValueError('Root must be an object')
    except (OSError, ValueError) as exc:
        errors.append('Cannot read contract: ' + str(exc))
        report['passed'] = False
        return report

    def check(condition, message):
        if not condition:
            errors.append(message)

    for key in spec['required_root_fields']:
        check(key in data, 'Missing root field: ' + key)
    check(data.get('is_template') is not True, 'Unfilled template is not a production contract')
    check(data.get('schema_version') == 1, 'Expected contract schema_version=1')
    check(data.get('standard_version') == spec['standard_version'], 'Wrong standard_version')
    scope = data.get('scope')
    check(scope in ('episode', 'sample'), 'scope must be episode or sample')
    check(data.get('corner_labels') is False, 'Fixed corner labels must be disabled')
    try:
        if isinstance(data.get('fps'), bool):
            raise ValueError('Boolean fps')
        fps = Fraction(str(data.get('fps')))
        if fps <= 0:
            raise ValueError('Nonpositive fps')
    except (ValueError, ZeroDivisionError):
        fps = None
        errors.append('fps must be a positive number or rational string')
    total = data.get('total_frames')
    check(is_frame(total) and total > 0, 'total_frames must be a positive integer')
    total = total if is_frame(total) and total > 0 else None
    clips = data.get('clips')
    if not isinstance(clips, list) or not clips:
        errors.append('clips must be a nonempty list')
        clips = []
    ids, illustration_uses = set(), []
    scene_groups, previous_scene = [], None
    cursor = 0
    counts = {'illustration': 0, 'information_card': 0}
    for index, clip in enumerate(clips):
        label = f'clips[{index}]'
        if not isinstance(clip, dict):
            errors.append(label + ' must be an object')
            continue
        for key in spec['required_clip_fields']:
            check(key in clip, label + ' missing ' + key)
        cid = clip.get('id')
        check(isinstance(cid, str) and bool(cid.strip()), label + ' needs id')
        check(isinstance(cid, str) and cid not in ids, label + ' duplicate/invalid id')
        if isinstance(cid, str):
            ids.add(cid)
        layer = clip.get('layer')
        check(isinstance(layer, str) and layer in counts, label + ' invalid main visual layer')
        if isinstance(layer, str) and layer in counts:
            counts[layer] += 1
        previous = clips[index - 1] if index else None
        previous_layer = previous.get('layer') if isinstance(previous, dict) else None
        if index and (layer == 'illustration' or previous_layer == 'illustration'):
            check(clip.get('transition') == 'hard_cut', label + ' boundary touching an illustration must use hard_cut')
        check(clip.get('corner_labels', data.get('corner_labels')) is False,
              label + ' enables fixed corner labels')
        start, end = clip.get('start_frame'), clip.get('end_frame_exclusive')
        valid_time = is_frame(start) and is_frame(end) and 0 <= start < end
        check(valid_time, label + ' needs a valid half-open frame interval')
        if valid_time:
            check(start == cursor, label + ' creates a timeline gap, overlap or unsorted interval')
            cursor = end
            if total is not None:
                check(end <= total, label + ' exceeds total_frames')
        gain = clip.get('semantic_gain')
        check(isinstance(gain, str) and bool(gain.strip()), label + ' needs semantic_gain')
        dimensions = clip.get('change_dimensions')
        check(isinstance(dimensions, list) and bool(dimensions)
              and all(isinstance(d, str) and d in spec['change_dimensions'] for d in dimensions),
              label + ' needs declared meaningful change_dimensions (quality is reviewed visually)')
        anchors = clip.get('narration_anchors')
        check(isinstance(anchors, list) and bool(anchors), label + ' needs narration_anchors')
        for anchor in anchors if isinstance(anchors, list) else []:
            good = isinstance(anchor, dict) and isinstance(anchor.get('text'), str) and bool(anchor['text'].strip())
            if good:
                a, b = anchor.get('start_frame'), anchor.get('end_frame_exclusive')
                good = is_frame(a) and is_frame(b) and 0 <= a < b
                if good and valid_time:
                    good = a < end and b > start
                if good and total is not None:
                    good = b <= total
            check(good, label + ' has an invalid or nonoverlapping narration anchor')
        relative = clip.get('asset_path')
        asset = None
        if not isinstance(relative, str) or not relative.strip():
            errors.append(label + ' needs asset_path')
        else:
            candidate = Path(relative)
            candidate = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
            if not candidate.is_relative_to(root):
                errors.append(label + ' asset escapes episode root; copy it into this episode')
            elif not candidate.is_file():
                errors.append(label + ' asset does not exist: ' + relative)
            else:
                asset = candidate
        if layer == 'illustration':
            policy = spec['illustration']
            scene = clip.get('scene_id')
            scene_valid = isinstance(scene, str) and bool(scene.strip())
            for key in policy['required_scene_fields']:
                value = clip.get(key)
                check(isinstance(value, str) and bool(value.strip()), label + ' needs ' + key)
            if scene_valid:
                if previous_scene is not None and scene != previous_scene:
                    reason = clip.get('scene_change_reason')
                    check(isinstance(reason, str) and bool(reason.strip()),
                          label + ' needs scene_change_reason when the scene changes')
                previous_scene = scene
                if valid_time:
                    if (scene_groups and scene_groups[-1]['scene_id'] == scene
                            and scene_groups[-1]['end_frame_exclusive'] == start
                            and previous_layer == 'illustration'):
                        scene_groups[-1]['end_frame_exclusive'] = end
                        scene_groups[-1]['clip_ids'].append(cid)
                    else:
                        scene_groups.append({'scene_id': scene, 'start_frame': start,
                                             'end_frame_exclusive': end, 'clip_ids': [cid]})
            check(clip.get('motion') == policy['motion'], label + ' illustration must have motion=none')
            check(clip.get('transition') == policy['transition'], label + ' illustration must use hard_cut')
            if valid_time and fps is not None:
                check(Fraction(end - start, 1) / fps <= Fraction(str(policy['max_contiguous_image_seconds'])),
                      label + ' illustration exceeds 2.0 seconds')
            if asset is not None:
                check(asset.suffix.lower() in policy['allowed_extensions'], label + ' requires a still-image asset')
                if valid_time:
                    illustration_uses.append({'id': cid, 'hash': digest(asset), 'start': start, 'end': end})
        elif layer == 'information_card':
            policy = spec['information_card']
            check(clip.get('motion') in policy['allowed_motion'], label + ' invalid information-card motion mode')
            check(clip.get('transition') in policy['allowed_transition'], label + ' invalid information-card transition')
    if total is not None:
        check(cursor == total, 'Main visual sequence must end at total_frames')
    groups = []
    for use in illustration_uses:
        if groups and use['hash'] == groups[-1]['hash'] and use['start'] == groups[-1]['end']:
            groups[-1]['end'] = use['end']
            groups[-1]['ids'].append(use['id'])
        else:
            groups.append({'hash': use['hash'], 'start': use['start'], 'end': use['end'], 'ids': [use['id']]})
    seen_hashes = set()
    for group in groups:
        check(group['hash'] not in seen_hashes, 'Narrative illustration returns after a cut: ' + ','.join(group['ids']))
        seen_hashes.add(group['hash'])
        if fps is not None:
            check(Fraction(group['end'] - group['start'], 1) / fps <= Fraction('2.0'),
                  'Same illustration split across adjacent segments exceeds 2.0 seconds: ' + ','.join(group['ids']))
    opening = data.get('opening')
    check(isinstance(opening, dict), 'opening must be an object (empty allowed for non-opening samples)')
    if scope == 'episode' and isinstance(opening, dict):
        for key in spec['opening']['required_episode_fields']:
            check(isinstance(opening.get(key), str) and bool(opening[key].strip()), 'Opening plan missing ' + key)
        if clips and isinstance(clips[0], dict):
            check(opening.get('entry_clip_id') == clips[0].get('id'), 'Opening must refer to the actual first clip')
    captions = data.get('subtitles', {'enabled': False})
    check(isinstance(captions, dict), 'subtitles must be an object when present')
    if isinstance(captions, dict) and captions.get('enabled'):
        for key, expected in spec['subtitles'].items():
            check(captions.get(key) == expected, 'Spoken caption policy mismatch: ' + key)
    warnings.extend([
        'Declared semantic_gain/change_dimensions do not prove actual semantic or visual differences.',
        'Scene groups summarize declared situations only; scene_progress/reasons do not prove narrative progress or prevent boredom. No fixed scene-duration quota is applied.',
        'Inspect actual encoded stillness, corner-label absence, source identity/anatomy and readability.',
        'This result is not normal-speed subjective A/V review or user approval.'
    ])
    for group in scene_groups:
        group['duration_seconds'] = (float(Fraction(group['end_frame_exclusive'] - group['start_frame'], 1) / fps)
                                     if fps is not None else None)
    report.update({'passed': not errors, 'clip_counts': counts, 'total_frames': total,
                   'fps': str(fps) if fps is not None else None,
                   'contiguous_illustration_scene_groups': scene_groups,
                   'distinct_illustration_source_hashes': len(seen_hashes)})
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--episode-root', type=Path, required=True)
    parser.add_argument('--contract', type=Path)
    args = parser.parse_args()
    result = validate(args.episode_root, args.contract)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
