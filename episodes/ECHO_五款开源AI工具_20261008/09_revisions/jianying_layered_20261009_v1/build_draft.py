#!/usr/bin/env python3
"""Build this revision's portable, unregistered Jianying draft.

Run with the existing pyJianYingDraft Python environment.  --prepare-only
records the proposed text mappings without copying media or writing a draft.
All source media/data must be inside this revision.  The source episode and
the installed library are read-only; this script never registers a draft.
Native visual equivalence is deliberately NOT asserted by this exporter.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import re
import shutil
import sys
import uuid


REV = Path(__file__).resolve().parent
SOURCE = REV / 'source' / 'episode'
ROLE_MAP = {'box': 'panel', 'graphics_shared': 'shared_graphics'}
GRAPHIC_ROLES = {'graphics', 'shared_graphics'}
EPS = 1e-6


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def save(path, value):
    path = contained(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def contained(path):
    path = Path(path).resolve()
    if not path.is_relative_to(REV) or path == REV:
        raise ValueError(f'Path must remain inside this revision: {path}')
    return path


def relative(path):
    return contained(path).relative_to(REV).as_posix()


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def ranges(frames):
    frames = sorted(set(frames))
    result = []
    for f in frames:
        if result and result[-1][1] == f:
            result[-1][1] += 1
        else:
            result.append([f, f + 1])
    return result


def mode(values):
    values = list(values)
    return Counter(values).most_common(1)[0][0]


def unique(values):
    return list(dict.fromkeys(values))


def finite(value, label):
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{label} must be a finite number: {value}')
    return value


def read_contract(path, require_media=True):
    data = load(contained(path))
    storyboard = load(SOURCE / '03_storyboard' / 'cards.json')
    defaults = load(SOURCE / '00_brief' / 'effective_defaults.json')
    for k in ('fps', 'width', 'height'):
        if data[k] != storyboard[k]:
            raise ValueError(f'Contract/source mismatch for {k}')
    if (data['fps'], data['width'], data['height'], storyboard['total_frames']) != (30, 1920, 1080, 2777):
        raise ValueError('This revision is scoped to the 30 fps, 1920x1080, 2777-frame episode')
    timeline = {c['id']: c for c in storyboard['cards']}
    seen = set()
    for card in data['cards']:
        sid = card['id']
        if sid in seen or sid not in timeline:
            raise ValueError(f'Duplicate or unknown scene: {sid}')
        seen.add(sid)
        original = timeline[sid]
        if (card['start_frame'], card['end_frame']) != (original['start_frame'], original['end_frame_exclusive']):
            raise ValueError(f'Timeline differs from source for {sid}')
        owners = {p['owner'] for p in card['panels']}
        if 'shared' in owners or len(owners) != len(card['panels']):
            raise ValueError(f'Invalid or duplicate panel owner in {sid}')
        for layer in card['layers']:
            if layer['owner'] not in owners | {'shared'}:
                raise ValueError(f'Unknown owner for {sid}/{layer["id"]}')
            if not card['start_frame'] <= layer['start_frame'] < layer['end_frame'] <= card['end_frame']:
                raise ValueError(f'Layer interval outside {sid}: {layer["id"]}')
            if layer.get('path'):
                contained(REV / layer['path'])
            elif require_media:
                raise ValueError(f'Layer media is not ready: {sid}/{layer["id"]}')
    missing_cards = {c['id'] for c in storyboard['cards'] if c['id'].startswith('C')} - seen
    if missing_cards:
        raise ValueError(f'Missing information cards: {sorted(missing_cards)}')
    return data, storyboard, defaults


def ownership_universe(card):
    assignments = {}
    for layer in card['layers']:
        role = ROLE_MAP.get(layer['role'], layer['role'])
        if role not in GRAPHIC_ROLES:
            continue
        ids = layer.get('source_ids', [])
        if not ids:
            raise ValueError(f'Graphics layer has no source IDs: {card["id"]}/{layer["id"]}')
        if role == 'shared_graphics' and layer['owner'] != 'shared':
            raise ValueError('A shared graphics layer must have shared ownership')
        for sid in ids:
            if sid in assignments:
                raise ValueError(f'Source object assigned twice: {card["id"]}/{sid}')
            assignments[sid] = layer['owner']
    universe = []
    declared = card['source_graphic_ids']
    for obj in declared:
        sid = obj['id'] if isinstance(obj, dict) else obj
        if sid not in assignments:
            raise ValueError(f'Source object not exported: {card["id"]}/{sid}')
        owner = obj.get('owner', assignments[sid]) if isinstance(obj, dict) else assignments[sid]
        if owner != assignments[sid]:
            raise ValueError(f'Source/export owner mismatch: {sid}')
        universe.append({'id': sid, 'owner': owner})
    if len({o['id'] for o in universe}) != len(universe) or set(assignments) != {o['id'] for o in universe}:
        raise ValueError(f'Source universe coverage mismatch: {card["id"]}')
    return universe


def font_metrics(text, defaults):
    """Measure only the system font; never copy or reference it in the draft."""
    from PIL import ImageFont
    key = 'bold_font' if text['bold'] else 'regular_font'
    path = Path(defaults['type'][key])
    if not path.is_file():
        return {'status': 'system_font_missing', 'fontName': defaults['type']['family']}
    em = 1000
    font = ImageFont.truetype(str(path), em)
    box = font.getbbox(text['text'], anchor='ls')
    ascent, descent = font.getmetrics()
    scale = text['fontSizePx'] / em
    return {'status': 'measured_system_font_only', 'fontName': defaults['type']['family'],
            'fontFileName': path.name, 'measurementEmPx': em,
            'inkBoxAtSourceSizePx': [round(v * scale, 6) for v in box],
            'advanceAtSourceSizePx': round(font.getlength(text['text']) * scale, 6),
            'ascentPx': ascent * scale, 'descentPx': descent * scale,
            'sourceFontBox': text.get('fontBox'), 'sourceSvgBaseline': text.get('svgBaseline'),
            'sourceInkCenter': text.get('inkCenter'),
            'nativeMeasured': False, 'redistributed': False}


def text_center(sample, policy):
    if policy == 'calibrated-font-box':
        # Historical real native exports measured this exact source coordinate
        # convention: transformed SVG getBBox center, not glyph/ink center.
        delta = sample['fontSizePx'] * .105 * sample['scaleY']
        angle = math.radians(sample['rotation'])
        return sample['x'] - math.sin(angle) * delta, sample['y'] + math.cos(angle) * delta
    if policy == 'ink' and sample.get('inkCenter'):
        return sample['inkCenter']['x'], sample['inkCenter']['y']
    return sample['x'], sample['y']


def calibration(data, defaults, args):
    evidence_path = REV / 'font_calibration_evidence.json'
    evidence = load(evidence_path) if evidence_path.is_file() else None
    conditions = {'canvas1080p': (data['width'], data['height']) == (1920, 1080),
                  'fontFamily': defaults['type']['family'] == 'Microsoft YaHei',
                  'fontFilesMatchHistoricalEvidence': False}
    if evidence:
        expected = evidence['systemFontSha256']
        conditions['fontFilesMatchHistoricalEvidence'] = all(
            Path(defaults['type'][key]).is_file() and digest(Path(defaults['type'][key])) == value
            for key, value in expected.items())
    historical_ok = evidence is not None and all(conditions.values())
    if args.text_center == 'calibrated-font-box' and not historical_ok:
        raise ValueError('Historical font calibration prerequisites do not match; choose an explicit theoretical mapping instead')
    factor = args.font_size_factor if args.font_size_factor is not None else (1.035 if historical_ok else 1.0)
    return {'historicalEvidenceApplicable': historical_ok, 'conditions': conditions,
            'fontSizeFactor': factor, 'fontPxPerNativeUnitBeforeFactor': args.font_px_per_unit or data['height'] / 100.0,
            'sourceCenterPolicy': args.text_center, 'nativeValidation': 'not_performed_for_this_episode',
            'fontResolutionCaveat': 'Historical exports used explicit font paths. This portable package leaves paths empty; the same system font must resolve at import.',
            'evidence': evidence, 'evidenceSha256': digest(evidence_path) if evidence else None}


def prepare_texts(data, defaults, args):
    plans, samples_by_key = [], {}
    calib = calibration(data, defaults, args)
    px_per_unit = calib['fontPxPerNativeUnitBeforeFactor'] / calib['fontSizeFactor']
    for card in data['cards']:
        ownership_universe(card)
        if not card.get('text_frames'):
            continue
        raw = load(contained(REV / card['text_frames']))
        if not isinstance(raw, list):
            raise ValueError('text_frames file must contain an array of global-frame rows')
        objects = defaultdict(dict)
        seen_frames = set()
        for row in raw:
            frame = row['frame']
            if frame in seen_frames or not card['start_frame'] <= frame < card['end_frame']:
                raise ValueError(f'Bad global text frame {card["id"]}/{frame}')
            seen_frames.add(frame)
            for t in row['texts']:
                if frame in objects[t['id']]:
                    raise ValueError(f'Duplicate text ID at {frame}: {t["id"]}')
                for field in ('x', 'y', 'width', 'height', 'fontSizePx', 'alpha', 'scaleX', 'scaleY', 'rotation', 'z'):
                    finite(t[field], f'{card["id"]}/{t["id"]}/{field}')
                objects[t['id']][frame] = t
        owner_labels = {p['owner']: p.get('owner_label', p['owner']) for p in card['panels']}
        for tid, frames in objects.items():
            states = list(frames.values())
            texts = {s['text'] for s in states}
            owners = {s['owner'] for s in states}
            if len(texts) != 1 or len(owners) != 1:
                raise ValueError(f'Logical text changes content/owner without a new ID: {card["id"]}/{tid}')
            owner = next(iter(owners))
            if owner not in set(owner_labels) | {'shared'}:
                raise ValueError(f'Unknown text owner: {card["id"]}/{tid}/{owner}')
            visible = sorted(f for f, s in frames.items() if s['alpha'] > EPS and s['scaleX'] > EPS and s['scaleY'] > EPS)
            differences = []
            def diff(kind, detail, affected_frames=None, **extra):
                affected = sorted(set(affected_frames if affected_frames is not None else visible))
                differences.append({'kind': kind, 'detail': detail, 'accepted': False,
                                    'affectedFrameRanges': ranges(affected), 'affectedObjectFrames': len(affected),
                                    'affectedObjectSeconds': len(affected) / data['fps'], **extra})
            if not visible:
                plans.append({'scene': card['id'], 'textKey': tid, 'text': states[0]['text'],
                              'owner': owner, 'exported': False, 'reason': 'never_visible_in_source',
                              'differences': []})
                continue
            # Keep every reappearance in one segment; retain adjacent zero-alpha
            # edge samples so the native fade begins/ends at the source boundary.
            first, last = visible[0], visible[-1]
            a = first - 1 if first - 1 in frames and frames[first - 1]['alpha'] <= EPS else first
            b = last + 2 if last + 1 in frames and frames[last + 1]['alpha'] <= EPS else last + 1
            peak_alpha = max(frames[f]['alpha'] for f in visible)
            peak_states = [frames[f] for f in visible if abs(frames[f]['alpha'] - peak_alpha) < 1e-5]
            style_key = mode((s['fontSizePx'], bool(s['bold']), tuple(s['color']), s.get('letterSpacingPx', 0)) for s in peak_states)
            base = next(s for s in peak_states if (s['fontSizePx'], bool(s['bold']), tuple(s['color']), s.get('letterSpacingPx', 0)) == style_key)
            if base['fontSizePx'] <= 0:
                raise ValueError(f'Nonpositive font size: {tid}')
            z_values = unique(s.get('native_z', s.get('nativeZ', s['z'])) for s in states)
            z = mode(s.get('native_z', s.get('nativeZ', s['z'])) for s in states)
            if len(z_values) > 1:
                diff('varying_dom_z', 'Native track order is fixed; use the modal exported z. Verify pairwise occlusion.', values=z_values)
            masks = unique(m for s in states for m in s.get('maskAncestors', []))
            if masks:
                diff('svg_mask', 'SVG masks are not native text masks; exported track order may emulate occlusion only.', masks=masks)
            diff('font_units', 'Use conditional historical native calibration when prerequisites match. This episode has not been rendered in Jianying.',
                 fontPxPerNativeUnit=px_per_unit, sourceFontSizePx=base['fontSizePx'], nativeSize=base['fontSizePx'] / px_per_unit)
            diff('font_anchor', 'Historical calibration uses SVG getBBox center plus the rotated local 0.105*fontSizePx*scaleY offset. Alternative center policies are uncalibrated.', policy=args.text_center)
            diff('system_font_dependency', 'Microsoft YaHei is a required local font; no font bytes are redistributed and portable font paths are empty.')
            hidden = [f for f in range(a, b) if f not in frames or frames[f]['alpha'] <= EPS or frames[f]['scaleX'] <= EPS or frames[f]['scaleY'] <= EPS]
            if hidden:
                diff('hidden_visibility', 'Fully hidden samples use zero X/Y scale within one continuous editable segment; native zero-scale behavior needs review.', affected_frames=hidden, ranges=ranges(hidden))
            for field, label in [('color', 'color'), ('bold', 'weight'), ('letterSpacingPx', 'letter_spacing')]:
                vals = unique(tuple(s[field]) if isinstance(s.get(field), list) else s.get(field, 0) for s in states)
                if len(vals) > 1:
                    affected = [f for f in visible if frames[f].get(field, 0) != base.get(field, 0)]
                    diff('dynamic_' + label, 'No supported native keyframe property; proposed mapping holds the representative visible style.', affected_frames=affected, values=vals, selected=base.get(field, 0))
            sizes = unique(s['fontSizePx'] for s in states)
            if len(sizes) > 1:
                diff('font_size_as_scale', 'Font-size changes use sampled X/Y scale ratios around a fixed editable font size; native layout metrics may differ.', affected_frames=[f for f in visible if frames[f]['fontSizePx'] != base['fontSizePx']], values=sizes)
            if base.get('letterSpacingPx', 0):
                diff('letter_spacing_units', 'Proposed em-relative spacing is serialized through the library 0.05 spacing multiplier; native metrics unverified.', sourcePx=base['letterSpacingPx'])
            alphas = [frames[f]['alpha'] if f in frames else 0 for f in range(a, b)]
            peak_frames = [f for f in range(a, b) if f in frames and abs(frames[f]['alpha'] - peak_alpha) < 1e-5]
            intro_end, outro_start = min(peak_frames), max(peak_frames)
            intro = intro_end - a if intro_end > a and all(alphas[i] <= alphas[i + 1] + EPS for i in range(intro_end - a)) else 0
            outro = b - 1 - outro_start if outro_start < b - 1 and all(alphas[i] + EPS >= alphas[i + 1] for i in range(outro_start - a, len(alphas) - 1)) else 0
            if intro or outro:
                fade_frames = [f for f in range(a, b) if (intro and f <= intro_end) or (outro and f >= outro_start)]
                diff('native_edge_fades', 'Native 渐显/渐隐 approximate edge opacity curves; no unsupported text alpha keyframes are asserted.', affected_frames=fade_frames, introFrames=intro, outroFrames=outro)
            unsupported = [f for f in range(a, b) if f in frames and EPS < frames[f]['alpha'] < peak_alpha - EPS and not (intro and f <= intro_end) and not (outro and f >= outro_start)]
            if unsupported:
                diff('internal_partial_alpha', 'Proposed mapping holds peak opacity in these internal partial-alpha intervals; visual equivalence is not accepted.', affected_frames=unsupported, ranges=ranges(unsupported))
            if peak_alpha < 1 - EPS:
                diff('static_alpha', 'Peak opacity is stored once in material global_alpha; native text opacity composition is unverified.', alpha=peak_alpha)
            plan = {'scene': card['id'], 'textKey': tid, 'text': base['text'], 'exported': True,
                    'owner': owner, 'ownerLabel': owner_labels.get(owner, '共享／跨框'), 'z': z,
                    'start_frame': a, 'end_frame': b, 'oneContinuousEditableSegment': True,
                    'sourceFramesPresent': len(frames), 'hiddenFrameRanges': ranges(hidden),
                    'sourceFontSizePx': base['fontSizePx'], 'nativeFontSize': base['fontSizePx'] / px_per_unit,
                    'bold': bool(base['bold']), 'color': base['color'], 'alpha': peak_alpha,
                    'letterSpacingPx': base.get('letterSpacingPx', 0),
                    'introFrames': intro, 'outroFrames': outro, 'fontMetrics': font_metrics(base, defaults),
                    'mappingStatus': 'proposed_not_native_verified', 'differences': differences}
            plans.append(plan)
            samples_by_key[(card['id'], tid)] = (frames, base)
    report = {'schemaVersion': 1, 'status': 'mapping_proposal', 'nativeValidation': 'not_performed',
              'visualEquivalenceAccepted': False, 'fps': data['fps'], 'fontPxPerNativeUnit': px_per_unit,
              'fontScaleCalibration': 'conditional_historical_native_evidence' if calib['historicalEvidenceApplicable'] else 'theoretical_unverified',
              'calibration': calib,
              'textCenterPolicy': args.text_center, 'fontName': defaults['type']['family'],
              'fontRedistributed': False, 'texts': plans,
              'summary': {'logicalTexts': len(plans), 'nativeSegmentsPlanned': sum(p['exported'] for p in plans),
                          'differenceCounts': dict(Counter(d['kind'] for p in plans for d in p['differences']))}}
    return report, samples_by_key


def difference_report(plan):
    """Keep exposure summed across texts separate from timeline union duration."""
    fps = plan['fps']
    categories = {}
    rows = []
    for text in plan['texts']:
        for item in text['differences']:
            kind = item['kind']
            frames = {f for a, b in item['affectedFrameRanges'] for f in range(a, b)}
            bucket = categories.setdefault(kind, {'logicalTextCount': 0, 'objectFrames': 0, '_frames': set()})
            bucket['logicalTextCount'] += 1
            bucket['objectFrames'] += len(frames)
            bucket['_frames'].update(frames)
            rows.append({'scene': text['scene'], 'textKey': text['textKey'], 'text': text['text'],
                         'owner': text['owner'], **item})
    for bucket in categories.values():
        frames = bucket.pop('_frames')
        bucket.update(objectSeconds=bucket['objectFrames'] / fps,
                      timelineUnionFrames=len(frames), timelineUnionSeconds=len(frames) / fps,
                      timelineUnionFrameRanges=ranges(frames))
    for kind in ['dynamic_color', 'dynamic_weight', 'internal_partial_alpha', 'native_edge_fades']:
        categories.setdefault(kind, {'logicalTextCount': 0, 'objectFrames': 0, 'objectSeconds': 0,
                                      'timelineUnionFrames': 0, 'timelineUnionSeconds': 0,
                                      'timelineUnionFrameRanges': []})
    return {'schemaVersion': 1, 'fps': fps, 'status': 'differences_disclosed_not_visually_approved',
            'accepted': False, 'nativeValidation': 'not_performed_for_this_episode',
            'meaningOfAcceptedFalse': 'The package is buildable and editable. Visual equivalence and these effect substitutions have not received approval.',
            'timeDefinitions': {'objectSeconds': 'sum of affected text-frame durations; simultaneous texts count separately',
                                'timelineUnionSeconds': 'union of global video frames; each frame counted once'},
            'categories': categories, 'items': rows, 'fontCalibration': plan['calibration']}


def build(data, storyboard, defaults, report, samples_by_key, package):
    import pyJianYingDraft as d
    W, H, fps = data['width'], data['height'], data['fps']
    total_frames = storyboard['total_frames']
    us = lambda f: round(f * 1_000_000 / fps)
    tr = lambda a, b: d.Timerange(us(a), us(b) - us(a))
    script = d.ScriptFile(W, H, fps, maintrack_adsorb=False)
    media_dir = package / 'media'
    media_dir.mkdir(parents=True, exist_ok=True)
    manifest = {'schemaVersion': 1, 'project': {'name': 'ECHO_五款开源AI工具_20261008_独立分层草稿',
                'width': W, 'height': H, 'fps': fps, 'durationUs': us(total_frames)},
                'media': [], 'panels': [], 'sources': [], 'segments': [],
                'fontDependencies': [{'fontName': defaults['type']['family'], 'required': True,
                                      'redistributed': False, 'portableFontPaths': 'empty',
                                      'nativeFontResolution': 'not_verified'}],
                'registered': False, 'nativeValidation': 'not_performed', 'visualValidation': 'not_performed',
                'mappingDifferencesAccepted': False, 'textPlan': 'text_plan.json'}
    entries = []
    media_names = set()

    def copy_asset(source, identity, expected_hash=None):
        source = contained(source)
        if not source.is_file():
            raise FileNotFoundError(source)
        actual_hash = digest(source)
        if expected_hash and actual_hash.lower() != expected_hash.lower():
            raise ValueError(f'Media hash mismatch: {source}')
        stem = re.sub(r'[^A-Za-z0-9_-]', '_', identity)[:100]
        short = hashlib.sha256(identity.encode('utf-8')).hexdigest()[:10]
        name = f'{stem}_{short}{source.suffix.lower()}'
        if name.casefold() in media_names:
            raise ValueError(f'Duplicate semantic media identity: {identity}')
        media_names.add(name.casefold())
        target = contained(media_dir / name)
        if not target.exists() or digest(target) != actual_hash:
            shutil.copy2(source, target)
        rel = target.relative_to(package).as_posix()
        manifest['media'].append({'path': rel, 'bytes': target.stat().st_size, 'sha256': actual_hash,
                                  'source': relative(source), 'semanticIdentity': identity})
        return target, rel

    def record(segment, scene, role, owner, label, a, b, z, kind, **extra):
        row = {'id': segment.segment_id, 'materialId': segment.material_id, 'scene': scene,
               'role': role, 'owner': owner, 'ownerLabel': label, 'startFrame': a, 'endFrame': b,
               'sourceZ': z, **extra}
        manifest['segments'].append(row)
        entries.append({'segment': segment, 'record': row, 'z': z, 'a': a, 'b': b, 'kind': kind})
        return row

    contract_ids = {c['id'] for c in data['cards']}
    for shot in storyboard['cards']:
        if shot['id'] in contract_ids:
            continue
        sid, a, b = shot['id'], shot['start_frame'], shot['end_frame_exclusive']
        if not sid.startswith('A'):
            raise ValueError(f'No export contract for {sid}')
        source = SOURCE / '06_project' / 'render' / f'{sid}.mp4'
        target, rel = copy_asset(source, sid + '_preserved_animation')
        material = d.VideoMaterial(str(target), material_name=sid + '｜原动画镜头')
        segment = d.VideoSegment(material, tr(a, b), volume=0)
        record(segment, sid, 'animation', 'shared', '原动画镜头（含原画面文字）', a, b, -1000, 'video',
               path=rel, expectedVolume=0, preservedSourceClip=True)
        manifest['sources'].append({'scene': sid, 'objects': []})

    for card in data['cards']:
        sid = card['id']
        for panel in card['panels']:
            manifest['panels'].append({'scene': sid, 'id': panel['owner'],
                                      'label': panel.get('owner_label', panel['owner']),
                                      'slot': panel.get('slot'), 'bounds': panel.get('bounds')})
        manifest['sources'].append({'scene': sid, 'objects': ownership_universe(card)})
        for layer in card['layers']:
            role = ROLE_MAP.get(layer['role'], layer['role'])
            if role not in {'background', 'animation', 'panel', 'graphics', 'shared_graphics'}:
                raise ValueError(f'Unsupported layer role: {role}')
            a, b = layer['start_frame'], layer['end_frame']
            target, rel = copy_asset(REV / layer['path'], sid + '_' + layer['id'], layer.get('sha256'))
            material = d.VideoMaterial(str(target), material_name=f'{sid}｜{layer.get("owner_label", layer["owner"])}｜{layer["id"]}')
            if (material.width, material.height) != (layer['width'], layer['height']):
                raise ValueError(f'Media dimensions differ: {sid}/{layer["id"]}')
            scale = 1 / min(W / layer['width'], H / layer['height'])
            clip = d.ClipSettings(scale_x=scale, scale_y=scale,
                                  transform_x=layer['x'] / (W / 2) - 1,
                                  transform_y=1 - layer['y'] / (H / 2))
            segment = d.VideoSegment(material, tr(a, b), volume=0, clip_settings=clip)
            extra = {'path': rel, 'sourceLayerId': layer['id'], 'expectedVolume': 0,
                     'slot': layer.get('slot'), 'pixelFootprint': [layer['width'], layer['height']],
                     'cropCenter': [layer['x'], layer['y']], 'sourceKind': layer['kind']}
            if role in GRAPHIC_ROLES:
                extra['sourceObjectIds'] = layer['source_ids']
            record(segment, sid, role, layer['owner'], layer.get('owner_label', layer['owner']),
                   a, b, layer.get('native_z', layer.get('nativeZ', layer['z'])), 'video', **extra)

    for plan in report['texts']:
        if not plan['exported']:
            continue
        frames, base = samples_by_key[(plan['scene'], plan['textKey'])]
        a, b = plan['start_frame'], plan['end_frame']
        alpha_peak = plan['alpha']

        def transform(frame):
            sample = frames.get(frame)
            # Missing interior objects remain an invisible state of the SAME text.
            if sample is None:
                sample = base
                shown = False
            else:
                shown = sample['alpha'] > EPS and sample['scaleX'] > EPS and sample['scaleY'] > EPS
            x, y = text_center(sample, report['textCenterPolicy'])
            factor = sample['fontSizePx'] / plan['sourceFontSizePx']
            return {'position_x': x / (W / 2) - 1, 'position_y': 1 - y / (H / 2),
                    'scale_x': sample['scaleX'] * factor if shown else 0,
                    'scale_y': sample['scaleY'] * factor if shown else 0,
                    'rotation': sample['rotation']}

        initial = transform(a)
        settings = d.ClipSettings(transform_x=initial['position_x'], transform_y=initial['position_y'],
                                  scale_x=initial['scale_x'], scale_y=initial['scale_y'], rotation=initial['rotation'])
        style = d.TextStyle(size=plan['nativeFontSize'], bold=plan['bold'],
                            color=tuple(v / 255 for v in plan['color']), alpha=1, align=1,
                            auto_wrapping=False,
                            letter_spacing=plan['letterSpacingPx'] / plan['sourceFontSizePx'] / .05)
        segment = d.TextSegment(plan['text'], tr(a, b), font_path='', style=style, clip_settings=settings)
        sequence = [(f, transform(f)) for f in range(a, b)]
        keyframes = 0
        for prop in initial:
            values = [s[prop] for _, s in sequence]
            if max(values) - min(values) <= 1e-9:
                continue
            for f, state in sequence:
                segment.add_keyframe(getattr(d.KeyframeProperty, prop), us(f) - us(a), state[prop])
                keyframes += 1
        if plan['introFrames']:
            segment.add_animation(d.TextIntro.渐显, duration=us(a + plan['introFrames']) - us(a))
        if plan['outroFrames']:
            segment.add_animation(d.TextOutro.渐隐, duration=us(b) - us(b - plan['outroFrames']))
        record(segment, plan['scene'], 'text', plan['owner'], plan['ownerLabel'], a, b, plan['z'], 'text',
               textKey=plan['textKey'], text=plan['text'], keyframeCount=keyframes,
               globalAlpha=alpha_peak, mappingStatus=plan['mappingStatus'],
               differenceKinds=[v['kind'] for v in plan['differences']])

    # A lane has a single absolute z and kind.  Reuse is allowed only across
    # non-overlapping intervals, preserving the source order even for text
    # below foreground graphics.  No automatic groups/compound clips.
    lanes = []
    for entry in sorted(entries, key=lambda e: (e['z'], e['kind'], e['a'], e['b'])):
        lane = next((lane for lane in lanes if lane['z'] == entry['z'] and lane['kind'] == entry['kind'] and lane['end'] <= entry['a']), None)
        if lane is None:
            label = f'{len(lanes) + 1:03d}｜z={entry["z"]}｜{entry["kind"]}'
            ref = script.append_track(d.TrackSpec(getattr(d.TrackType, entry['kind']), name=label))
            lane = {'z': entry['z'], 'kind': entry['kind'], 'end': 0, 'ref': ref}
            lanes.append(lane)
        script.add_segment(entry['segment'], lane['ref'])
        lane['end'] = entry['b']

    target, rel = copy_asset(SOURCE / '00_brief' / 'input' / 'voice_original.mp3', 'original_narration')
    voice = d.AudioMaterial(str(target), material_name='原始配音｜0 dB｜无额外 BGM/SFX')
    duration = min(voice.duration, us(total_frames))
    narration = d.AudioSegment(voice, d.Timerange(0, duration), volume=1)
    script.add_segment(narration, script.append_track(d.TrackSpec(d.TrackType.audio, name='原始配音｜音量 1')))
    manifest['segments'].append({'id': narration.segment_id, 'materialId': narration.material_id,
                                 'scene': 'episode', 'role': 'narration', 'owner': 'shared',
                                 'path': rel, 'expectedVolume': 1, 'audioGainBakedDb': 0,
                                 'sourceDurationUs': voice.duration, 'durationUs': duration,
                                 'sourceSampleModification': 'none'})

    payload = json.loads(script.dumps())
    payload['id'] = str(uuid.uuid4()).upper()
    payload['name'] = manifest['project']['name']
    payload['duration'] = us(total_frames)
    text_rows = {r['materialId']: r for r in manifest['segments'] if r['role'] == 'text'}
    path_map = {str((package / m['path']).resolve()).casefold(): m['path'] for m in manifest['media']}
    for category, materials in payload['materials'].items():
        if not isinstance(materials, list):
            continue
        for material in materials:
            if material.get('path'):
                key = str(Path(material['path']).resolve()).casefold()
                if key not in path_map:
                    raise ValueError(f'Unexpected material path: {material["path"]}')
                material['path'] = path_map[key]
            if category == 'texts':
                row = text_rows[material['id']]
                material.update(font_name=defaults['type']['family'], font_path='', global_alpha=row['globalAlpha'])
                content = json.loads(material['content'])
                for style in content['styles']:
                    style['font'] = {'id': '', 'path': ''}
                    # Alpha is applied in exactly one carrier, global_alpha.
                    style['fill']['alpha'] = 1
                    style['fill']['content']['solid']['alpha'] = 1
                material['content'] = json.dumps(content, ensure_ascii=False)
    lookup = {seg['id']: (track, seg) for track in payload['tracks'] for seg in track['segments']}
    for row in manifest['segments']:
        track, native = lookup[row['id']]
        row['trackId'] = track['id']
        row['renderIndex'] = native.get('render_index')
        native['desc'] = '｜'.join([row['scene'], row.get('ownerLabel', row['owner']), row.get('text', row.get('sourceLayerId', row['role']))])
        if native.get('group_id'):
            raise ValueError('Builder must not group editable assets')
    greatest_end = max(s['target_timerange']['start'] + s['target_timerange']['duration'] for _, s in lookup.values())
    if greatest_end != us(total_frames):
        raise ValueError(f'Draft visual timeline does not reach project end: {greatest_end}')
    manifest['builderRuntime'] = {'python': sys.version.split()[0], 'library': 'pyJianYingDraft',
                                 'version': importlib.metadata.version('pyJianYingDraft')}
    save(package / 'draft_content.json', payload)
    save(package / 'manifest.json', manifest)
    save(package / 'text_plan.json', report)
    save(package / 'text_difference_report.json', difference_report(report))
    index = {'schemaVersion': 1, 'automaticGroups': False, 'editInstruction': '按 scene 与 owner 筛选同框面板、图形和文字；各素材相互独立。共享图形须单独选择。',
             'panels': [], 'shared': [], 'nativeValidation': 'not_performed'}
    for panel in manifest['panels']:
        members = [r for r in manifest['segments'] if r['scene'] == panel['scene'] and r['owner'] == panel['id']]
        index['panels'].append({**panel, 'segments': members})
    index['shared'] = [r for r in manifest['segments'] if r['owner'] == 'shared']
    save(package / 'panel_edit_index.json', index)
    lines = ['# 按框编辑索引', '', '本包仅导出，未注册到剪映。字体依赖 Microsoft YaHei；未打包系统字体。',
             '原生播放、字体外观、透明视频解码及效果等价均待实际剪映验收。文字映射差异见 text_plan.json。', '']
    for panel in index['panels']:
        lines += [f'## {panel["scene"]} · {panel["label"]}', '', '|类型|内容|片段 ID|轨道 ID|', '|---|---|---|---|']
        for row in panel['segments']:
            label = row.get('text', row.get('sourceLayerId', row['role'])).replace('|', '／').replace('\n', ' ')
            lines.append(f'|{row["role"]}|{label}|{row["id"]}|{row["trackId"]}|')
        lines.append('')
    contained(package / '按框编辑索引.md').write_text('\n'.join(lines), encoding='utf-8')
    summary = {'status': 'built_not_native_verified', 'registered': False,
               'segments': len(manifest['segments']), 'tracks': len(payload['tracks']),
               'nativeTextSegments': len(text_rows), 'media': len(manifest['media']),
               'draftSha256': digest(package / 'draft_content.json'),
               'manifestSha256': digest(package / 'manifest.json'),
               'mappingDifferencesAccepted': False, 'nativeValidation': 'not_performed'}
    save(REV / 'qc' / 'build_report.json', summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contract', default=str(REV / 'card_layers.json'))
    parser.add_argument('--package', default=str(REV / 'package'))
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--font-px-per-unit', type=float, help='Explicit proposed native font calibration; remains unverified until editor review')
    parser.add_argument('--font-size-factor', type=float, help='Override the conditional historical 1.035 factor')
    parser.add_argument('--text-center', choices=['calibrated-font-box', 'ink', 'font-box'], default='calibrated-font-box')
    args = parser.parse_args()
    if args.font_px_per_unit is not None and (not math.isfinite(args.font_px_per_unit) or args.font_px_per_unit <= 0):
        parser.error('--font-px-per-unit must be finite and positive')
    if args.font_size_factor is not None and (not math.isfinite(args.font_size_factor) or args.font_size_factor <= 0):
        parser.error('--font-size-factor must be finite and positive')
    data, storyboard, defaults = read_contract(args.contract, require_media=not args.prepare_only)
    report, samples = prepare_texts(data, defaults, args)
    save(REV / 'text_plan.json', report)
    differences = difference_report(report)
    save(REV / 'text_difference_report.json', differences)
    lines = ['# 原生文字映射差异', '',
             '草稿可以构建和编辑；accepted:false 表示本集原生视觉效果与替代方案尚未获得视觉批准，不表示导出失败。',
             '字号与锚点使用同字体、同画布、同 SVG 测量方式的历史原生导出校准；本集未在剪映播放或导出验收。',
             '字体文件未打包，空字体路径在导入端能否正确解析微软雅黑仍需验证。', '',
             '|差异或待验证项|文字数|对象累计秒|视频时间并集秒|', '|---|---:|---:|---:|']
    for kind, values in differences['categories'].items():
        lines.append(f'|{kind}|{values["logicalTextCount"]}|{values["objectSeconds"]:.3f}|{values["timelineUnionSeconds"]:.3f}|')
    lines += ['', '对象累计秒会重复计入同一时刻的不同文字；视频时间并集秒不重复计算同一帧。',
              '具体文字、全局帧区间与替代方法见同名 JSON。动态颜色、粗细和内部透明度改变以 JSON 实测区间为准。', '']
    contained(REV / 'text_difference_report.md').write_text('\n'.join(lines), encoding='utf-8')
    if args.prepare_only:
        print(json.dumps({'status': 'text_plan_prepared', **report['summary']}, ensure_ascii=False))
        return
    package = contained(args.package)
    if package == SOURCE or package.is_relative_to(SOURCE) or SOURCE.is_relative_to(package):
        raise ValueError('Output may not overlap the copied source episode')
    print(json.dumps(build(data, storyboard, defaults, report, samples, package), ensure_ascii=False))


if __name__ == '__main__':
    main()
