"""One bounded integrity check for a completed research snapshot."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MEDIA_SUFFIXES = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif', '.svg', '.bmp',
                  '.ico', '.tif', '.tiff', '.webm', '.mp4', '.mov', '.m4v', '.avi',
                  '.mkv', '.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.opus'}


def load(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8-sig'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-only', action='store_true',
                        help='Verify the text/code distribution; do not require or verify media files')
    parser.add_argument('--no-write', action='store_true', help='Print the report without writing a report file')
    args = parser.parse_args()
    errors = []
    manifest, catalog, inventory = load('source_manifest.json'), load('catalog.json'), load('inventory.json')
    ids = {x['id'] for x in inventory}
    cards = catalog['cards']
    if len(inventory) != 108 or len(ids) != 108 or len(cards) != 108 or {x['id'] for x in cards} != ids:
        errors.append('Inventory/research coverage must be exactly 108 unique recipes')
    required_paths = {'LICENSE', 'THIRD_PARTY_NOTICES.md', 'README.md', 'references/taxonomy.md',
                      'gallery/index.html', 'demos/_lib/demo-shell.js',
                      'demos/_lib/demo-shell.css', 'demos/_lib/gsap.min.js'}
    for slug in ids:
        required_paths.update({f'references/cards/{slug}.md', f'template/cards/{slug}.tsx',
                               f'demos/{slug}/index.html'})
    source_records = {file['path']: file for file in manifest['files']
                      if Path(file['path']).suffix.lower() not in MEDIA_SUFFIXES}
    if set(source_records) != required_paths or len(manifest['files']) != len({x['path'] for x in manifest['files']}):
        errors.append('Pinned manifest must cover the 332 unique required text/code sources')
    verified_sources = 0
    skipped_media = 0
    for file in manifest['files']:
        is_media = Path(file['path']).suffix.lower() in MEDIA_SUFFIXES
        if args.source_only and is_media:
            skipped_media += 1
            continue
        path = ROOT / 'upstream' / file['path']
        if not path.is_file():
            errors.append('Missing source: ' + file['path'])
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != file['sha256'] or path.stat().st_size != file['bytes']:
            errors.append('Source integrity mismatch: ' + file['path'])
        elif not is_media and file['path'] in required_paths:
            verified_sources += 1
    if {path.stem for path in (ROOT / 'cards').glob('*.md')} != ids:
        errors.append('Readable notes must cover exactly the 108 recipe IDs')
    for card in cards:
        slug = card['id']
        for field in ['select_when', 'avoid_when', 'narration_anchor', 'v5_adaptation']:
            if not isinstance(card.get(field), str) or not card[field].strip():
                errors.append(f'{slug}: missing {field}')
        for field, low, high in [('relations', 1, 4), ('sequence', 3, 6), ('pitfalls', 2, 5)]:
            if not low <= len(card.get(field, [])) <= high:
                errors.append(f'{slug}: invalid {field}')
        if card['reviewed'] != {'recipe': True, 'tsx_core': True, 'html_core': True}:
            errors.append(slug + ': incomplete documented source review')
        note = ROOT / f'cards/{slug}.md'
        if not note.is_file():
            errors.append(slug + ': missing readable note')
        elif not re.search(r'[\u4e00-\u9fff]', note.read_text(encoding='utf-8-sig')):
            errors.append(slug + ': readable note must contain Chinese text')
        for kind, expected in [('recipe', f'references/cards/{slug}.md'),
                               ('tsx', f'template/cards/{slug}.tsx'), ('html', f'demos/{slug}/index.html')]:
            source = card['sources'].get(kind, {})
            if (source.get('local') != 'upstream/' + expected
                    or source.get('sha256') != source_records.get(expected, {}).get('sha256')):
                errors.append(f'{slug}: {kind} source does not match pinned manifest')
        if len(card['evidence']) != 2 or {x['file'] for x in card['evidence']} != {'tsx', 'html'}:
            errors.append(slug + ': incomplete source evidence')
        for evidence in card['evidence']:
            source = card['sources'].get(evidence['file'], {})
            if not source.get('local') or not (ROOT / source['local']).is_file():
                errors.append(slug + ': source evidence file missing')
                continue
            path = ROOT / source['local']
            text = path.read_text(encoding='utf-8')
            if evidence['needle'] not in text:
                errors.append(slug + ': source evidence does not match')
            elif text[:text.index(evidence['needle'])].count('\n') + 1 != evidence['line']:
                errors.append(slug + ': evidence line mismatch')
        state = card['status']
        for field in ['v5_adaptation', 'voiceover_sync', 'production_validation', 'jianying_native_validation']:
            if state[field] != 'not_performed':
                errors.append(slug + ': unsupported production acceptance state ' + field)
        preview = state['upstream_keyframes']
        if preview.get('capture') != 'completed' or len(preview.get('sample_times', [])) != 3:
            errors.append(slug + ': missing three-state upstream preview')
        if preview.get('errors') or preview.get('failed_requests'):
            errors.append(slug + ': upstream demo runtime/request error')
        if not args.source_only and not (ROOT / f'previews/{slug}.jpg').is_file():
            errors.append(slug + ': preview image missing')
    semantic = load('semantic_index.json')
    for section in ['relations', 'categories']:
        indexed = set()
        for group in semantic[section].values():
            indexed.update(group)
        if indexed != ids:
            errors.append(f'Semantic {section} index does not cover all 108 IDs')
    try:
        html = (ROOT / 'index.html').read_text(encoding='utf-8')
        payload = re.search(r'<script\b[^>]*\bid=["\']data["\'][^>]*>(.*?)</script>', html, re.S)
        if not payload or json.loads(payload.group(1)) != catalog:
            errors.append('Browser index embedded catalog does not match catalog.json')
    except (OSError, ValueError) as exc:
        errors.append('Cannot read browser index catalog: ' + str(exc))
    report = {'result': 'passed' if not errors else 'failed', 'recipes': len(cards),
              'pinned_source_files': len(manifest['files']), 'implementation_evidence_entries': sum(len(x['evidence']) for x in cards),
              'scope': ('Text/code coverage, source hashes, linked evidence and index metadata only; '
                        'historical capture metadata does not verify current media completeness' if args.source_only else
                        'Coverage, source hashes, linked evidence, metadata and captured upstream demo states only'),
              'mode': 'source_only' if args.source_only else 'full',
              'media_not_distributed': args.source_only, 'required_source_files': len(required_paths),
              'verified_source_files': verified_sources, 'skipped_media_files': skipped_media,
              'skipped_preview_files': len(cards) if args.source_only else 0,
              'normal_speed_subjective_av': 'not_performed', 'v5_adaptation': 'not_performed',
              'jianying_native_validation': 'not_performed', 'errors': errors}
    if not args.no_write:
        name = 'source_integrity_report.json' if args.source_only else 'integrity_report.json'
        dest = ROOT / 'verification' / name
        dest.parent.mkdir(exist_ok=True)
        dest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
