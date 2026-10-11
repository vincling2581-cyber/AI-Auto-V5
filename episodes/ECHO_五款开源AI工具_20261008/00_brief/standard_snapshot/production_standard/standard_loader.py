"""Read the exact current manifest and reject incomplete or changed standards."""
from pathlib import Path
import json
import hashlib
ROOT = Path(__file__).resolve().parent.parent

def safe_path(root, relative):
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError('标准文件路径越界：' + str(relative))
    return path

def load(root=ROOT):
    root = Path(root).resolve()
    manifest = json.loads((root / 'production_standard.json').read_text(encoding='utf-8-sig'))
    paths = [x['path'] for x in manifest['files']]
    if len(set(paths)) != len(paths):
        raise ValueError('标准文件清单含重复路径')
    required = [manifest[k] for k in ['sop', 'prompts', 'defaults', 'rules']]
    required += [manifest[k] for k in ['prompts_data', 'changes', 'self_check', 'baseline_manifest', 'source_inventory', 'conflicts'] if isinstance(manifest.get(k), str)]
    if manifest.get('status') == 'active':
        approval = manifest.get('approval', {})
        if not (manifest.get('user_approved') is True and manifest.get('approval_mode') == 'delegated_self_check' and approval.get('mode') == 'delegated_self_check' and approval.get('user_personal_item_review') is False):
            raise ValueError('已启用标准缺少明确的委托自检使用授权记录')
        if not isinstance(approval.get('authorized_quote'), str) or not approval['authorized_quote'].strip():
            raise ValueError('委托自检授权缺少用户原文')
        report = manifest.get('self_check', approval.get('self_check_report'))
        if not isinstance(report, str) or approval.get('self_check_report') != report:
            raise ValueError('已启用标准的自检记录不一致')
        required.append(report)
    elif manifest.get('status') != 'review_candidate':
        raise ValueError('未知标准状态：' + str(manifest.get('status')))
    if manifest.get('baseline_manifest'):
        for key in ['prompts_data', 'changes', 'source_inventory', 'conflicts']:
            if not isinstance(manifest.get(key), str):
                raise ValueError('当前制作基准契约缺少字段：' + key)
        required += ['production_standard/' + name for name in ['build_standard.py', 'review_page.py', 'standard_loader.py', 'start_episode.py', 'verify_standard.py', 'package_standard.py', 'rule_catalog.py', 'prompt_library.py', '先读我.txt']]
    for relative in required:
        if relative not in paths:
            raise ValueError('当前标准引用未纳入哈希锁：' + relative)
    for item in manifest['files']:
        path = safe_path(root, item['path'])
        if not path.is_file():
            raise FileNotFoundError('标准文件缺失：' + str(path))
        if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('标准文件内容已变化，需同步版本记录：' + item['path'])
    defaults = json.loads(safe_path(root, manifest['defaults']).read_text(encoding='utf-8-sig'))
    if defaults['version'] != manifest['version']:
        raise ValueError('默认参数与入口版本不一致')
    if manifest.get('baseline_manifest'):
        hashes = {item['path']: item['sha256'] for item in manifest['files']}
        baseline = json.loads(safe_path(root, manifest['baseline_manifest']).read_text(encoding='utf-8-sig'))
        if baseline['standard_version'] != manifest['version']:
            raise ValueError('制作基准与入口版本不一致')
        source_record = baseline['cards_method_sources']
        if hashes.get(source_record['path']) != source_record['sha256']:
            raise ValueError('当前卡片方法来源未完整锁定')
        source_path = safe_path(root, source_record['path'])
        methods = json.loads(source_path.read_text(encoding='utf-8-sig'))
        for item in methods['files']:
            path = safe_path(source_path.parent, item['path'])
            relative = path.relative_to(root).as_posix()
            if hashes.get(relative) != item['sha256']:
                raise ValueError('当前方法资产未完整锁定：' + relative)
    return manifest

if __name__ == '__main__':
    m = load()
    print(json.dumps({'version': m['version'], 'status': m['status'], 'user_approved': m['user_approved'], 'approval_mode': m.get('approval_mode'), 'user_personal_item_review': m.get('approval', {}).get('user_personal_item_review'), 'sop': m['sop'], 'integrity': 'passed'}, ensure_ascii=False, indent=2))
