"""Fetch a pinned, inert research snapshot; never install an upstream workflow."""
from __future__ import annotations
import concurrent.futures as cf
import hashlib
import json
from pathlib import Path
import re
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[1]
COMMIT = 'a7c29edfb2404612dde6a5a1c8aa94232e85625b'
REPO = 'https://github.com/Vincentwei1021/video-talkcraft'
RAW = f'https://raw.githubusercontent.com/Vincentwei1021/video-talkcraft/{COMMIT}/'
UPSTREAM = ROOT / 'upstream'


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def fetch(path):
    dest = UPSTREAM / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        old = PROJECT / 'experiments/talkcraft_card_study_20261020/reference/video-talkcraft' / path
        if old.is_file():
            dest.write_bytes(old.read_bytes())
        else:
            for attempt in range(3):
                try:
                    req = urllib.request.Request(RAW + path, headers={'User-Agent': 'V5-pinned-card-research'})
                    with urllib.request.urlopen(req, timeout=35) as response:
                        data = response.read()
                    dest.write_bytes(data)
                    break
                except Exception:
                    if attempt == 2:
                        raise
                    time.sleep(0.5 * (attempt + 1))
    data = dest.read_bytes()
    return {'path': path, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'url': RAW + path}


def frontmatter(text):
    match = re.match(r'^---\s*\n(.*?)\n---', text, re.S)
    fields = {}
    if match:
        for line in match[1].splitlines():
            if ':' in line:
                key, value = line.split(':', 1)
                fields[key.strip()] = value.strip()
    return fields


def main():
    records = [fetch('references/taxonomy.md'), fetch('gallery/index.html')]
    text = (UPSTREAM / 'gallery/index.html').read_text(encoding='utf-8')
    start = text.index('const CARDS = ') + len('const CARDS = ')
    cards, _ = json.JSONDecoder().raw_decode(text[start:])
    ids = sorted(card['slug'] for card in cards)
    if len(ids) != 108 or len(set(ids)) != 108:
        raise ValueError(f'Expected 108 unique pinned recipes, found {len(ids)}')
    by_id = {card['slug']: card for card in cards}
    paths = ['LICENSE', 'THIRD_PARTY_NOTICES.md', 'README.md',
             'demos/_lib/demo-shell.js', 'demos/_lib/demo-shell.css', 'demos/_lib/gsap.min.js']
    for slug in ids:
        paths.extend([f'references/cards/{slug}.md', f'template/cards/{slug}.tsx', f'demos/{slug}/index.html'])
    with cf.ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(fetch, path): path for path in paths}
        for i, fut in enumerate(cf.as_completed(futures), 1):
            records.append(fut.result())
            if i % 60 == 0:
                print(f'Fetched {i}/{len(paths)} research sources', flush=True)
    # Only the visual assets referenced by these demos; do not fetch the audio library.
    media = set()
    for slug in ids:
        html = (UPSTREAM / f'demos/{slug}/index.html').read_text(encoding='utf-8')
        media.update('demos/' + p[3:] for p in re.findall(r'\.\./_lib/media/[A-Za-z0-9_.-]+\.(?:jpg|png|webm)', html))
    media.update(['demos/pencil-sketch-draw/hand-pencil.png', 'demos/_lib/dh-host.webm'])
    with cf.ThreadPoolExecutor(max_workers=6) as pool:
        records.extend(pool.map(fetch, sorted(media)))
    inventory = []
    for n, slug in enumerate(ids):
        md = (UPSTREAM / f'references/cards/{slug}.md').read_text(encoding='utf-8')
        fields = frontmatter(md)
        inventory.append({'id': slug, 'title': fields.get('标题', by_id[slug].get('zhName', slug)),
                          'category': fields.get('类别', by_id[slug].get('category', '')),
                          'upstream_metadata': fields,
                          'gallery_metadata': by_id[slug], 'batch': n % 3 + 1})
    dump(ROOT / 'inventory.json', inventory)
    for batch in range(1, 4):
        dump(ROOT / f'research_batches/batch_{batch:02d}_assignment.json', [x['id'] for x in inventory if x['batch'] == batch])
    dump(ROOT / 'source_manifest.json', {'repository': REPO, 'commit': COMMIT,
         'license': 'PolyForm Noncommercial 1.0.0',
         'required_notice': 'Required Notice: Copyright (c) 2026 Vincent Wei (https://github.com/Vincentwei1021/video-talkcraft)',
         'scope': 'Recipe documentation, standalone TSX, demo HTML and silent demo runtime; not an installed Skill or adopted production standard',
         'files': sorted(records, key=lambda x: x['path'])})
    print(json.dumps({'recipes': len(inventory), 'source_files': len(records),
                      'bytes': sum(x['bytes'] for x in records), 'commit': COMMIT}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
