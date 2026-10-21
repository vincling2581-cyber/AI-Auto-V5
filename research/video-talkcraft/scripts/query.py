"""Return a few semantic candidates without loading the entire source library."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SYNONYMS = [
    ['比较', '对比', '差异', '前后', '优劣', '对照'],
    ['汇聚', '归集', '汇总', '多对一', '合并', '整合'],
    ['筛选', '选择', '候选', '选中', '排除', '单选'],
    ['顺序', '步骤', '流程', '阶段', '递进', '接力'],
    ['比例', '占比', '百分比', '份额', '数量'],
    ['证据', '截图', '文档', '出处', '引用', '核查'],
    ['变化', '增长', '趋势', '走势', '曲线'],
    ['强调', '标注', '重点', '定位', '聚焦', '指认'],
    ['修改', '纠错', '替换', '更正', '修正'],
    ['并列', '多个', '同屏', '列表', '平行'],
    ['路线', '地图', '路径', '地理', '位置'],
]


def main():
    p = argparse.ArgumentParser(description='语义候选检索。结果需结合整段文案再判断。')
    p.add_argument('query', nargs='*')
    p.add_argument('--id')
    p.add_argument('--role')
    p.add_argument('--category')
    p.add_argument('--limit', type=int, default=5)
    p.add_argument('--json', action='store_true')
    args = p.parse_args()
    cards = json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))['cards']
    if args.id:
        selected = [x for x in cards if x['id'] == args.id]
        if not selected:
            p.error('未知卡片 ID')
    else:
        query = ' '.join(args.query).lower()
        terms = set(query.split())
        for group in SYNONYMS:
            if any(word in query for word in group):
                terms.update(group)
        scored = []
        for card in cards:
            if args.role and card['v5_role'] != args.role:
                continue
            if args.category and card['category'] != args.category:
                continue
            # Do not match negative examples or pitfalls as positive selection reasons.
            text = ' '.join([card['id'], card['title'], card['category'], card['select_when'], *card['relations']]).lower()
            score = sum(1 for term in terms if term and term in text)
            score += sum(3 for term in terms if term in card['relations'])
            if not query or score:
                scored.append((score, card['id'], card))
        selected = [x[2] for x in sorted(scored, key=lambda x: (-x[0], x[1]))[:max(1, args.limit)]]
    if args.json or args.id:
        print(json.dumps(selected, ensure_ascii=False, indent=2))
    else:
        print('候选检索，不代表自动选定或已适配；按整段文案核对关系和素材。')
        for card in selected:
            print(f'\n{card["id"]}｜{card["title"]}｜{card["role_label"]}')
            print('  适合：' + card['select_when'])
            print('  避免：' + card['avoid_when'])
            print('  详情：' + str(ROOT / f'cards/{card["id"]}.md'))
        if not selected:
            print('未找到候选，请换用关系词或直接指定 --id。')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
