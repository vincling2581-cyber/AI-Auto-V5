"""Merge individually researched records into a small, searchable local reference."""
from __future__ import annotations
import collections
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
ROLES = {
    'card_content': '信息卡主体', 'card_emphasis': '卡内强调标注',
    'evidence_presentation': '证据与素材呈现', 'source_camera': '证据或卡片运镜',
    'transition': '转场与章节结构', 'host_interaction': '人物出镜互动',
}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    inventory = json.loads((ROOT / 'inventory.json').read_text(encoding='utf-8'))
    manifest = json.loads((ROOT / 'source_manifest.json').read_text(encoding='utf-8'))
    research = []
    for i in range(1, 4):
        research.extend(json.loads((ROOT / f'research_batches/batch_{i:02d}.json').read_text(encoding='utf-8-sig')))
    by_id = {x['id']: x for x in research}
    if len(by_id) != 108 or len(research) != 108 or set(by_id) != {x['id'] for x in inventory}:
        raise ValueError('Research records do not exactly cover 108 unique inventory IDs')
    previews = json.loads((ROOT / 'previews/capture_report.json').read_text(encoding='utf-8'))
    preview_by_id = {x['id']: x for x in previews['cards']}
    cards = []
    semantic = collections.defaultdict(list)
    categories = collections.defaultdict(list)
    hashes = {x['path']: x['sha256'] for x in manifest['files']}
    (ROOT / 'cards').mkdir(exist_ok=True)
    for item in inventory:
        slug = item['id']
        rec = by_id[slug]
        if rec['v5_role'] not in ROLES:
            raise ValueError(f'Unknown role: {slug}: {rec["v5_role"]}')
        if rec['reviewed'] != {'recipe': True, 'tsx_core': True, 'html_core': True}:
            raise ValueError('Incomplete source review: ' + slug)
        paths = {'recipe': f'references/cards/{slug}.md', 'tsx': f'template/cards/{slug}.tsx', 'html': f'demos/{slug}/index.html'}
        for evidence in rec['evidence']:
            original = evidence['file']
            kinds = [kind for kind in ('tsx', 'html') if original in (kind, paths[kind], 'upstream/' + paths[kind])]
            if len(kinds) != 1:
                raise ValueError(f'Unexpected evidence path {slug}: {original}')
            evidence['file'] = kinds[0]
        if {x['file'] for x in rec['evidence']} != {'tsx', 'html'}:
            raise ValueError('Both implementation forms must have evidence: ' + slug)
        for evidence in rec['evidence']:
            text = (ROOT / 'upstream' / paths[evidence['file']]).read_text(encoding='utf-8')
            if not evidence['needle'] or evidence['needle'] not in text:
                raise ValueError(f'Invalid source evidence {slug}: {evidence["needle"]}')
            evidence['line'] = text[:text.index(evidence['needle'])].count('\n') + 1
        fields = item['upstream_metadata']
        card = {'id': slug, 'title': item['title'], 'category': item['category'],
                'inputs': fields.get('输入', ''), 'upstream_semantic_label': fields.get('语义', ''),
                'upstream_props': fields.get('props', ''), 'upstream_demo_duration': fields.get('时长', ''),
                **rec, 'role_label': ROLES[rec['v5_role']],
                'status': {'research': 'completed', 'v5_adaptation': 'not_performed',
                           'voiceover_sync': 'not_performed', 'production_validation': 'not_performed',
                           'jianying_native_validation': 'not_performed',
                           'upstream_keyframes': preview_by_id.get(slug, {'capture': 'not_performed'})},
                'sources': {kind: {'local': 'upstream/' + p,
                                  'url': f'{manifest["repository"]}/blob/{manifest["commit"]}/{p}',
                                  'sha256': hashes[p]} for kind, p in paths.items()}}
        cards.append(card)
        for relation in rec['relations']:
            semantic[relation].append(slug)
        categories[item['category']].append(slug)
        lines = [f'# {item["title"]} · {slug}', '',
                 f'类别：{item["category"]}；研究用途：{ROLES[rec["v5_role"]]}；输入：{card["inputs"]}', '',
                 '状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。', '',
                 '## 选择条件', '', rec['select_when'], '', '语义关系：' + '、'.join(rec['relations']), '',
                 '## 避免误用', '', rec['avoid_when'], '', '## 可见过程', '']
        lines += [f'{i}. {step}' for i, step in enumerate(rec['sequence'], 1)]
        lines += ['', '配音落点：' + rec['narration_anchor'], '', '## 关键限制与适配', '']
        lines += ['- ' + value for value in rec['pitfalls']]
        lines += ['', 'V5 适配提示：' + rec['v5_adaptation'], '',
                  '上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。', '',
                  '## 源码对照', '']
        for evidence in rec['evidence']:
            source = card['sources'][evidence['file']]
            lines += [f'- [{evidence["file"]} 第 {evidence["line"]} 行]({source["url"]}#L{evidence["line"]})：{evidence["finding"]}',
                      '  对照字串：`' + evidence['needle'].replace('`', '\\`').replace('\n', ' ') + '`']
        lines += ['', '## 演示与来源', '',
                  f'![上游演示三个取样状态](../previews/{slug}.jpg)', '',
                  f'[本地静音 HTML 演示](../upstream/demos/{slug}/index.html?embed=1) · [完整配方](../upstream/references/cards/{slug}.md) · [TSX](../upstream/template/cards/{slug}.tsx)', '',
                  '关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。', '',
                  f'来源版本：`{manifest["commit"]}`。授权和来源见 [README](../README.md)。', '']
        warning = card['status']['upstream_keyframes'].get('sample_warning')
        if warning:
            lines += ['取样限制：' + warning, '']
        (ROOT / f'cards/{slug}.md').write_text('\n'.join(lines), encoding='utf-8')
    catalog = {'schema_version': 1, 'repository': manifest['repository'], 'commit': manifest['commit'],
               'purpose': '按语义检索的候选方法库；不替代任何 V5 当前制作标准或单集锁',
               'review_scope': '逐项文档重点、关键源码及 HTML 动画代码对照，附上游演示取样；不是逐行代码审计或生产适配验收',
               'cards': cards}
    write_json(ROOT / 'catalog.json', catalog)
    write_json(ROOT / 'semantic_index.json', {'relations': dict(sorted(semantic.items())), 'categories': dict(categories), 'roles': ROLES})
    payload = json.dumps(catalog, ensure_ascii=False).replace('<', '\\u003c')
    template = (ROOT / 'scripts/catalog_template.html').read_text(encoding='utf-8')
    (ROOT / 'index.html').write_text(template.replace('__CATALOG_JSON__', payload), encoding='utf-8')
    summary = {'recipes': len(cards), 'research_completed': len(cards), 'v5_adaptation_completed': 0,
               'upstream_keyframe_capture_completed': sum(x['status']['upstream_keyframes']['capture'] == 'completed' for x in cards),
               'categories': dict(collections.Counter(x['category'] for x in cards)),
               'roles': dict(collections.Counter(x['v5_role'] for x in cards))}
    write_json(ROOT / 'research_summary.json', summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
