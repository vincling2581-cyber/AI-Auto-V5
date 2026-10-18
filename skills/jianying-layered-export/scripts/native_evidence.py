"""Validate dependency-bound native-layout evidence; never generate visual approval."""
import hashlib
import json
import math
from pathlib import Path, PureWindowsPath
import struct
import zlib


STYLE_FLAGS = ('bold', 'italic', 'underline')
FONT_SIZE_TOLERANCE = 1e-6


def certainly_hidden(segment, time_us):
    """Reject explicit hidden flags and zero scale/alpha plateaus; do not infer occlusion."""
    if segment.get('visible') is False:
        return True
    clip = segment.get('clip') or {}
    scale = clip.get('scale') or {}
    values = {'KFTypeScaleX': scale.get('x', 1), 'KFTypeScaleY': scale.get('y', 1),
              'KFTypeAlpha': clip.get('alpha', 1)}
    offset = time_us - segment['target_timerange']['start']
    for sequence in segment.get('common_keyframes', []):
        prop, frames = sequence.get('property_type'), sequence.get('keyframe_list', [])
        if prop not in values or not frames:
            continue
        points = [(frame['time_offset'], frame['values'][0]) for frame in frames]
        values[prop] = None  # Unknown between nonlinear keyframes; no visual inference.
        if offset <= points[0][0]:
            values[prop] = points[0][1]
        elif offset >= points[-1][0]:
            values[prop] = points[-1][1]
        else:
            for (left, a), (right, b) in zip(points, points[1:]):
                if offset == left:
                    values[prop] = a
                elif left < offset < right and a == b == 0:
                    values[prop] = 0
    return any(value == 0 for value in values.values())


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def media_manifest_sha256(manifest):
    items = sorted(({'path': x['path'].replace('\\', '/'), 'sha256': x['sha256'].lower(),
                     'bytes': x['bytes']} for x in manifest['media']), key=lambda x: x['path'])
    return hashlib.sha256(json.dumps(items, sort_keys=True, separators=(',', ':'),
                                    ensure_ascii=False).encode('utf-8')).hexdigest()


def font_paths(value):
    found = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(child, str) and (key == 'path' or key.endswith('_path')):
                if 'font' in key or Path(child).suffix.lower() in {'.ttf', '.otf', '.ttc', '.woff', '.woff2'}:
                    if child:
                        found.add(child.replace('\\', '/'))
            elif key == 'content' and isinstance(child, str):
                try:
                    found.update(font_paths(json.loads(child)))
                except ValueError:
                    pass
            else:
                found.update(font_paths(child))
    elif isinstance(value, list):
        for child in value:
            found.update(font_paths(child))
    return found


def raster_size(path):
    """Validate PNG scanlines / JPEG framing, not native origin or visual correctness."""
    data = path.read_bytes()
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        pos, size, compressed, ended, header = 8, None, bytearray(), False, None
        while pos + 12 <= len(data):
            count = struct.unpack('>I', data[pos:pos + 4])[0]
            kind = data[pos + 4:pos + 8]
            payload = data[pos + 8:pos + 8 + count]
            if pos + count + 12 > len(data):
                raise ValueError('Truncated PNG')
            crc = struct.unpack('>I', data[pos + 8 + count:pos + 12 + count])[0]
            if zlib.crc32(kind + payload) & 0xffffffff != crc:
                raise ValueError('PNG CRC mismatch')
            if kind == b'IHDR':
                if pos != 8 or count != 13 or header is not None:
                    raise ValueError('Invalid PNG header')
                header = struct.unpack('>IIBBBBB', payload)
                size = header[:2]
            elif kind == b'IDAT':
                compressed.extend(payload)
            elif kind == b'IEND':
                ended = True
                break
            pos += count + 12
        if not size or not ended or not compressed:
            raise ValueError('Incomplete PNG raster')
        width, height, depth, color, compression, filtering, interlace = header
        channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(color)
        valid_depths = {0: {1, 2, 4, 8, 16}, 2: {8, 16}, 3: {1, 2, 4, 8}, 4: {8, 16}, 6: {8, 16}}
        if not (width > 0 and height > 0 and channels and depth in valid_depths[color]
                and compression == filtering == 0 and interlace in {0, 1}):
            raise ValueError('Invalid PNG dimensions or encoding')
        passes = [(0, 0, 1, 1)] if interlace == 0 else [
            (0, 0, 8, 8), (4, 0, 8, 8), (0, 4, 4, 8), (2, 0, 4, 4),
            (0, 2, 2, 4), (1, 0, 2, 2), (0, 1, 1, 2)]
        rows = []
        expected = 0
        for x, y, dx, dy in passes:
            pw, ph = max(0, (width - x + dx - 1) // dx), max(0, (height - y + dy - 1) // dy)
            if pw and ph:
                stride = 1 + (pw * channels * depth + 7) // 8
                rows.append((stride, ph))
                expected += stride * ph
        if expected > 256 * 1024 * 1024:
            raise ValueError('PNG raster exceeds supported 256 MiB evidence limit')
        inflater = zlib.decompressobj()
        pixels = inflater.decompress(compressed, expected + 1)
        if len(pixels) != expected or not inflater.eof or inflater.unused_data or inflater.unconsumed_tail:
            raise ValueError('PNG scanline length does not match dimensions')
        offset = 0
        for stride, count in rows:
            if any(pixels[offset + row * stride] > 4 for row in range(count)):
                raise ValueError('Invalid PNG scanline filter')
            offset += stride * count
        return size
    if data.startswith(b'\xff\xd8') and data.endswith(b'\xff\xd9'):
        pos, size, has_scan, scan_bytes = 2, None, False, 0
        while pos < len(data):
            if data[pos] != 255:
                raise ValueError('Invalid JPEG marker')
            while pos < len(data) and data[pos] == 255:
                pos += 1
            if pos >= len(data):
                raise ValueError('Truncated JPEG marker')
            marker = data[pos]
            pos += 1
            if marker == 0xd9:
                if size and has_scan and scan_bytes > 0:
                    return size
                raise ValueError('JPEG has no complete image scan')
            if marker in {0xd8, 0x00} or 0xd0 <= marker <= 0xd7:
                raise ValueError('Unexpected JPEG standalone marker')
            if pos + 2 > len(data):
                raise ValueError('Truncated JPEG length')
            length = int.from_bytes(data[pos:pos + 2], 'big')
            if length < 2 or pos + length > len(data):
                raise ValueError('Truncated JPEG')
            if marker in {0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf}:
                height, width = struct.unpack('>HH', data[pos + 3:pos + 7])
                if width <= 0 or height <= 0 or length < 8:
                    raise ValueError('Invalid JPEG dimensions')
                components = data[pos + 7]
                if components < 1 or length != 8 + 3 * components:
                    raise ValueError('Invalid JPEG frame components')
                size = width, height
            pos += length
            if marker == 0xda:
                if size is None or length < 6:
                    raise ValueError('Invalid JPEG scan header')
                has_scan = True
                while pos < len(data):
                    if data[pos] != 0xff:
                        scan_bytes += 1
                        pos += 1
                    elif pos + 1 < len(data) and (data[pos + 1] == 0 or 0xd0 <= data[pos + 1] <= 0xd7):
                        scan_bytes += data[pos + 1] == 0
                        pos += 2
                    else:
                        break
    raise ValueError('Native/reference frame must be an actual PNG or JPEG raster')


def validate_native_evidence(root, manifest, draft, evidence_path, check):
    """Check recorded evidence and dependencies, not screenshot semantics or honesty."""
    evidence_path = Path(evidence_path) if evidence_path else root / 'native-evidence.json'
    if not evidence_path.is_absolute():
        evidence_path = root / evidence_path
    evidence_path = evidence_path.resolve()
    summary = {'status': 'failed', 'evidencePath': str(evidence_path),
               'nativePlaybackValidation': 'not_performed', 'nativeFullExportValidation': 'not_performed'}

    def require(condition, name, detail=''):
        if not check('native.' + name, condition, detail):
            raise ValueError(name + ': ' + str(detail))

    def artifact(item, label, raster=False):
        require(isinstance(item, dict), label, 'expected artifact object')
        raw = item.get('path')
        require(isinstance(raw, str) and bool(raw), label + '.path')
        portable = raw.replace('\\', '/')
        path = (root / portable).resolve()
        require(not PureWindowsPath(raw).drive and not PureWindowsPath(raw).root and ':' not in raw
                and '..' not in portable.split('/') and path.is_relative_to(root) and path != root,
                label + '.contained', raw)
        require(path.is_file(), label + '.exists', raw)
        require(isinstance(item.get('sha256'), str) and item['sha256'].lower() == digest(path),
                label + '.sha256', raw)
        return (path, raster_size(path)) if raster else path

    def nonempty(value):
        return isinstance(value, str) and bool(value.strip())

    def finite(value):
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)

    def style_flags(value, label, declaration=False):
        require(isinstance(value, dict), label, 'expected native style object')
        if declaration:
            require(set(value) <= set(STYLE_FLAGS), label + '.fields', ', '.join(STYLE_FLAGS))
        require(all(isinstance(value.get(key, False), bool) for key in STYLE_FLAGS), label + '.flags')
        return tuple(value.get(key, False) for key in STYLE_FLAGS)

    def style_description(key):
        return {'fontPath': key[0], **dict(zip(STYLE_FLAGS, key[1:]))}

    try:
        require(evidence_path.is_relative_to(root), 'evidence.contained')
        evidence = json.loads(evidence_path.read_text(encoding='utf-8-sig'))
        require(isinstance(evidence, dict) and evidence.get('schemaVersion') == 1, 'schemaVersion', 'expected 1')
        binding = evidence.get('binding', {})
        project = manifest['project']
        expected_draft_hash = digest(root / 'draft_content.json')
        require(binding.get('manifestSha256') == digest(root / 'manifest.json'), 'binding.manifestSha256',
                'stale or absent ownership/segment manifest binding')
        require(binding.get('draftSha256') == expected_draft_hash, 'binding.draftSha256', 'stale or absent draft binding')
        require(binding.get('canvas') == {k: project[k] for k in ('width', 'height')}, 'binding.canvas')
        require(binding.get('fps') == project['fps'] and binding.get('durationUs') == project['durationUs'], 'binding.timeline')
        require(binding.get('mediaManifestSha256') == media_manifest_sha256(manifest), 'binding.mediaManifestSha256')
        expected_fonts = font_paths(draft.get('materials', {}).get('texts', []))
        font_items = binding.get('fonts')
        require(isinstance(font_items, list), 'binding.fonts')
        bound_fonts = set()
        for index, item in enumerate(font_items):
            path = artifact(item, f'fonts[{index}]')
            relative = path.relative_to(root).as_posix()
            require(relative not in bound_fonts, 'fonts.unique', relative)
            bound_fonts.add(relative)
        require(bound_fonts == expected_fonts, 'fonts.coverage', f'expected {sorted(expected_fonts)}')
        text_entries = {entry['id']: entry for entry in manifest['segments'] if entry['role'] in {'text', 'brand'}}
        require(not text_entries or bool(expected_fonts), 'fonts.explicit', 'Native text needs explicit packaged font files')
        actual = {segment['id']: segment for track in draft['tracks'] for segment in track['segments']}
        text_materials = {material['id']: material for material in draft.get('materials', {}).get('texts', [])}
        final_styles = []
        for sid in text_entries:
            material = text_materials[actual[sid]['material_id']]
            require(bool(font_paths(material)), 'fonts.segmentExplicit', sid)
            content = json.loads(material.get('content', '{}'))
            styles = content.get('styles', [])
            require(isinstance(styles, list) and bool(styles) and all(isinstance(style, dict)
                    and isinstance(style.get('font'), dict) and nonempty(style['font'].get('path'))
                    and style['font']['path'].replace('\\', '/') in expected_fonts for style in styles),
                    'fonts.styleExplicit', sid)
            for style in styles:
                require(finite(style.get('size')) and style['size'] > 0, 'fonts.styleSize', sid)
                key = (style['font']['path'].replace('\\', '/'), *style_flags(style, 'fonts.styleFlags'))
                final_styles.append((sid, key, style['size']))
        runtime = evidence.get('runtime', {})
        require(runtime.get('product') == 'JianyingPro' and nonempty(runtime.get('version')), 'runtime.identity')
        executable = runtime.get('executableRelativePath', '')
        require(nonempty(executable) and not PureWindowsPath(executable).drive and not PureWindowsPath(executable).root
                and ':' not in executable and '..' not in executable.replace('\\', '/').split('/')
                and Path(executable).suffix.lower() == '.exe', 'runtime.executableRelativePath')
        exe_hash = runtime.get('executableSha256', '')
        require(isinstance(exe_hash, str) and len(exe_hash) == 64 and all(c in '0123456789abcdef' for c in exe_hash),
                'runtime.executableSha256')
        width, height = project['width'], project['height']
        covered_fonts, covered_segments = set(), set()
        calibrated_sizes = {}
        frame_hashes = set()
        for stage_name in ('calibration', 'finalLayout'):
            stage = evidence.get(stage_name, {})
            require(isinstance(stage, dict) and stage.get('status') == 'passed', stage_name + '.status')
            require(nonempty(stage.get('reviewer')) and nonempty(stage.get('reviewedAt')), stage_name + '.review')
            stage_hash = expected_draft_hash
            duration = project['durationUs']
            if stage_name == 'calibration':
                require(nonempty(stage.get('method')) and isinstance(stage.get('parameters'), dict)
                        and bool(stage['parameters']), 'calibration.parameters', 'Record measured mapping; no fixed conversion factor is assumed')
                calibration_path = artifact(stage.get('draft'), 'calibration.draft')
                calibration_draft = json.loads(calibration_path.read_text(encoding='utf-8-sig'))
                require(calibration_draft.get('canvas_config', {}).get('width') == width
                        and calibration_draft.get('canvas_config', {}).get('height') == height, 'calibration.canvas')
                require(calibration_draft.get('fps') == project['fps'], 'calibration.fps')
                duration = calibration_draft.get('duration')
                require(finite(duration) and duration > 0, 'calibration.duration')
                stage_hash = stage['draft']['sha256']
            samples = stage.get('samples')
            require(isinstance(samples, list) and bool(samples), stage_name + '.samples')
            for index, sample in enumerate(samples):
                label = f'{stage_name}.samples[{index}]'
                require(isinstance(sample, dict), label)
                time_us = sample.get('timeUs')
                require(isinstance(time_us, int) and not isinstance(time_us, bool) and 0 <= time_us < duration, label + '.timeUs')
                native_path, (image_w, image_h) = artifact(sample.get('nativeFrame'), label + '.nativeFrame', raster=True)
                _, reference_size = artifact(sample.get('referenceFrame'), label + '.referenceFrame', raster=True)
                require(reference_size == (width, height), label + '.referenceCanvas')
                require(sample['nativeFrame']['sha256'] != sample['referenceFrame']['sha256'], label + '.independentFrames',
                        'Source image cannot serve as its own native evidence')
                frame_hashes.add(sample['nativeFrame']['sha256'])
                capture = sample.get('capture', {})
                require(capture.get('method') in {'jianying_ui', 'jianying_native_export'}, label + '.nativeOrigin',
                        'SVG/PIL/browser reconstructions are not native evidence')
                require(capture.get('draftSha256') == stage_hash and nonempty(capture.get('recordedAt')), label + '.captureBinding')
                viewport = capture.get('viewport', {})
                require(isinstance(viewport, dict) and all(finite(viewport.get(k)) for k in ('x', 'y', 'width', 'height')),
                        label + '.viewport')
                x, y, vw, vh = (viewport[k] for k in ('x', 'y', 'width', 'height'))
                require(x >= 0 and y >= 0 and vw >= min(320, width) and vh > 0
                        and x + vw <= image_w and y + vh <= image_h
                        and abs(vw / vh - width / height) / (width / height) <= .01, label + '.viewportBounds')
                if capture['method'] == 'jianying_native_export':
                    export_path = artifact(capture.get('exportMedia'), label + '.exportMedia')
                    require(export_path.suffix.lower() in {'.mp4', '.mov', '.mkv', '.avi'} and export_path.stat().st_size > 32,
                            label + '.exportMediaFormat')
                review = sample.get('review', {})
                require(review.get('status') == 'passed' and all(review.get(k) is True for k in
                        ('font', 'textSize', 'position', 'lineBreaks', 'clipping')), label + '.visualReview')
                if stage_name == 'calibration':
                    paths = sample.get('fontPaths')
                    require(isinstance(paths, list) and bool(paths) and all(isinstance(p, str) and p in expected_fonts for p in paths),
                            label + '.fontPaths')
                    for key in ('sourceFontSizePx', 'nativeFontSize'):
                        require(finite(sample.get(key)) and sample[key] > 0, label + '.' + key)
                    declared_flags = style_flags(sample.get('nativeStyle', {}), label + '.nativeStyle', declaration=True)
                    # Bind the declared calibration font/size to actual active native text.
                    calibration_materials = {m['id']: m for m in calibration_draft.get('materials', {}).get('texts', [])}
                    active_styles = []
                    for track in calibration_draft.get('tracks', []):
                        if track.get('type') != 'text':
                            continue
                        for segment in track.get('segments', []):
                            span = segment.get('target_timerange', {})
                            if not (finite(span.get('start')) and finite(span.get('duration'))
                                    and span['start'] <= time_us < span['start'] + span['duration']):
                                continue
                            if certainly_hidden(segment, time_us):
                                continue
                            material = calibration_materials.get(segment.get('material_id'), {})
                            content = json.loads(material.get('content', '{}'))
                            active_styles.extend(content.get('styles', []))
                    measured_sizes = {}
                    for style in active_styles:
                        if not (isinstance(style, dict) and isinstance(style.get('font'), dict)
                                and isinstance(style['font'].get('path'), str) and finite(style.get('size'))
                                and abs(style['size'] - sample['nativeFontSize']) <= FONT_SIZE_TOLERANCE):
                            continue
                        if style_flags(style, label + '.actualStyle') == declared_flags:
                            path = style['font']['path'].replace('\\', '/')
                            measured_sizes.setdefault(path, []).append(style['size'])
                    require(set(paths) <= set(measured_sizes), label + '.calibrationDraftStyles',
                            'Claimed font/size/nativeStyle must exist in active native calibration text at sample time')
                    covered_fonts.update(paths)
                    # Other styles in the same frame are not automatically reviewed by this sample.
                    for path in paths:
                        calibrated_sizes.setdefault((path, *declared_flags), []).extend(measured_sizes[path])
                else:
                    ids = sample.get('segmentIds')
                    require(isinstance(ids, list) and bool(ids) and all(isinstance(sid, str) and sid in text_entries for sid in ids),
                            label + '.segmentIds')
                    for sid in ids:
                        span = actual[sid]['target_timerange']
                        require(span['start'] <= time_us < span['start'] + span['duration'], label + '.segmentVisibleTime', sid)
                        require(not certainly_hidden(actual[sid], time_us), label + '.segmentNotHidden', sid)
                        covered_segments.add(sid)
        require(covered_fonts == expected_fonts, 'calibration.fontCoverage')
        for sid, key, size in final_styles:
            detail = {'segmentId': sid, **style_description(key), 'nativeFontSize': size}
            require(key in calibrated_sizes, 'calibration.styleCoverage', detail)
            low, high = min(calibrated_sizes[key]), max(calibrated_sizes[key])
            require(low - FONT_SIZE_TOLERANCE <= size <= high + FONT_SIZE_TOLERANCE,
                    'calibration.sizeCoverage', {**detail, 'testedMin': low, 'testedMax': high})
        require(covered_segments == set(text_entries), 'finalLayout.textCoverage', f'missing {sorted(set(text_entries) - covered_segments)}')
        summary.update(status='evidence_verified', evidenceSha256=digest(evidence_path), runtime=runtime,
                       nativeFrameCount=len(frame_hashes), calibratedFonts=len(covered_fonts), reviewedTextSegments=len(covered_segments),
                       calibratedStyleRanges=[{**style_description(key), 'nativeMin': min(sizes), 'nativeMax': max(sizes)}
                                              for key, sizes in sorted(calibrated_sizes.items())],
                       limitation='Checks recorded provenance claims, dependency hashes, sample coverage and raster containers; does not authenticate native origin, decode JPEG pixels, or prove motion/playback/visual correctness. Actual capture and visual inspection are separate.')
    except (OSError, ValueError, TypeError, KeyError, AttributeError, IndexError, struct.error, zlib.error) as exc:
        check('native.evidence', False, f'{type(exc).__name__}: {exc}')
    return summary
