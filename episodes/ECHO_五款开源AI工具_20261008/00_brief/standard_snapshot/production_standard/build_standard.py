"""Rebuild derived review documents from the current manifest and canonical JSON.
Never migrate an old SOP, inject old defaults, alter an episode, or render video.
"""
from pathlib import Path
import hashlib
import json
from standard_loader import ROOT, safe_path
HERE = Path(__file__).resolve().parent

def read_json(path, fallback=None):
    return json.loads(path.read_text(encoding='utf-8-sig')) if path.is_file() else fallback

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + '\n', encoding='utf-8')

def main():
    # Stale hashes are allowed only in this explicitly invoked revision builder.
    # The production loader always requires valid hashes.
    manifest = read_json(ROOT / 'production_standard.json')
    version = manifest['version']
    active = manifest.get('status') == 'active'
    status_text = '已启用：用户明确授权助手自检后直接使用；不表示用户亲自逐项审阅。后续本集明确要求仍可覆盖。' if active else '审阅候选：已有明确要求继续有效，其余新增与调整项仍可审阅。'
    if not safe_path(ROOT, manifest['sop']).is_file():
        raise FileNotFoundError(manifest['sop'])
    rules = read_json(safe_path(ROOT, manifest['rules']))
    prompts = read_json(safe_path(ROOT, manifest.get('prompts_data', 'production_standard/prompts.json')))
    defaults = read_json(safe_path(ROOT, manifest['defaults']))
    if defaults['version'] != version:
        raise ValueError('默认参数版本与当前入口不一致')
    for label, items in [('rules', rules), ('prompts', prompts)]:
        if not items or len({x['id'] for x in items}) != len(items):
            raise ValueError(label + ' 缺失或 ID 重复')
    conflicts = read_json(safe_path(ROOT, manifest.get('conflicts', 'production_standard/conflicts.json')), [])
    history = read_json(HERE / 'historical_prompts.json', [])
    source = read_json(safe_path(ROOT, manifest.get('source_inventory', 'production_standard/source_inventory.json')), {})
    inventory = source.get('files', [])
    extras = source.get('external', [])
    fence = chr(96) * 3
    prompt_doc = f'# 统一生产提示词 v{version}\n\n状态：{status_text}\n\n方括号为本集输入；用户最新明确要求优先。当前 JSON 是提示词唯一内容源，历史提示词仅供追溯。\n\n'
    prompt_doc += '\n\n'.join(f'## {p["id"]} · {p["title"]}\n\n{fence}text\n{p["text"]}\n{fence}' for p in prompts)
    write(safe_path(ROOT, manifest['prompts']), prompt_doc)
    rows = [f'# 全部制作规则 v{version}', '', f'共 {len(rules)} 项。{status_text}', '', '| 编号 | 类别 | 来源性质 | 条目 | 规则 | 依据 | 执行与反馈记录 |', '|---|---|---|---|---|---|---|']
    for r in rules:
        rows.append('|' + '|'.join(str(r.get(k, '')).replace('|', '／').replace('\n', '<br>') for k in ['id', 'category', 'basis', 'title', 'rule', 'source', 'decision']) + '|')
    write(HERE / f'全部制作规则_v{version}.md', '\n'.join(rows))
    write(HERE / f'冲突与取舍_v{version}.md', f'# 冲突与取舍 v{version}\n\n' + '\n\n'.join(f'## {c["id"]} {c["title"]}\n\n旧情况：{c.get("old", "")}\n\n本版处理：{c.get("new", "")}\n\n状态：{c.get("status", "")}' for c in conflicts))
    lines = ['# 来源与影响清单', '', '唯一入口是 production_standard.json。当前标准与制作基准以入口及其哈希为准；历史实例不自动成为下一集规则。剪映导入属于另行明确请求的独立任务，不在本版视频制作流程中。', '', '| 文件 | 影响类别 | 适用范围 |', '|---|---|---|']
    lines += ['|' + '|'.join(str(r.get(k, '')).replace('|', '／') for k in ['path', 'kind', 'effective']) + '|' for r in inventory]
    write(HERE / '来源与影响清单.md', '\n'.join(lines))
    for item in manifest['files']:
        if item['path'] in {'production_standard.json', manifest['review']}:
            raise ValueError('manifest/review 不能对嵌入自己的哈希建立循环依赖')
        item['sha256'] = hashlib.sha256(safe_path(ROOT, item['path']).read_bytes()).hexdigest()
    write(ROOT / 'production_standard.json', json.dumps(manifest, ensure_ascii=False, indent=2))
    from review_page import build_page
    build_page(ROOT, HERE, manifest, rules, prompts, conflicts, history, extras, inventory, defaults)
    from standard_loader import load
    load()
    print(json.dumps({'version': version, 'rules': len(rules), 'prompts': len(prompts), 'normative_files': len(manifest['files']), 'canonical_sop_and_json': 'read_only', 'video_or_editor_actions': False}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
