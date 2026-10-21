"""Small source packets for focused research, not a substitute for interpretation."""
import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def numbered(text, start=0, end=None):
    lines = text.splitlines()
    return '\n'.join(f'{i + 1}: {lines[i]}' for i in range(start, min(len(lines), end or len(lines))))


def code_packet(text, html=False):
    if html:
        blocks = re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>', text, re.S | re.I)
        code = '\n'.join(blocks)
        if len(code) <= 3000:
            return code
        return code[:1000] + '\n[... middle omitted; open exact source if needed ...]\n' + code[-1800:]
    lines = text.splitlines()
    ranges = [(0, min(16, len(lines)))]
    for i, line in enumerate(lines):
        if re.search(r'useCurrentFrame\(|export (default|function)|export const [A-Z]|type Props|interface Props', line):
            ranges.append((max(0, i - 1), min(len(lines), i + 19)))
    seen = set()
    out = []
    for a, b in ranges:
        for i in range(a, b):
            if i not in seen:
                out.append(f'{i + 1}: {lines[i]}')
                seen.add(i)
    return '\n'.join(out)[:4300]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('ids', nargs='+')
    args = p.parse_args()
    for slug in args.ids:
        if not re.fullmatch(r'[a-z0-9-]+', slug):
            raise ValueError(slug)
        base = ROOT / 'upstream'
        doc = (base / f'references/cards/{slug}.md').read_text(encoding='utf-8')
        tsx = (base / f'template/cards/{slug}.tsx').read_text(encoding='utf-8')
        html = (base / f'demos/{slug}/index.html').read_text(encoding='utf-8')
        print('\n=== CARD ' + slug + ' ===')
        fm = re.match(r'^---\s*\n(.*?)\n---', doc, re.S)
        print(fm[1] if fm else doc[:600])
        for heading in ['意图', '动效范围', '已知坑', '复用指引']:
            m = re.search(r'^## ' + re.escape(heading) + r'[^\n]*\n(.*?)(?=^## |\Z)', doc, re.M | re.S)
            if m:
                limit = 700 if heading != '已知坑' else 1000
                body = m[1].strip()
                print('\n## ' + heading + '\n' + body[:limit])
                if len(body) > limit:
                    print('[section continues in original]')
        print('\n--- TSX CORE (numbered source excerpts) ---\n' + code_packet(tsx))
        print('\n--- HTML ANIMATION CORE ---\n' + code_packet(html, True))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
