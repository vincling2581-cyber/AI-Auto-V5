"""Focused checks for the current standard, independent new episode and review page."""
from pathlib import Path
import ast
import hashlib
import json
import subprocess
import sys
import tempfile
from standard_loader import load, ROOT, safe_path

HERE = Path(__file__).resolve().parent
CHECKS = HERE / 'checks'

def main():
    CHECKS.mkdir(exist_ok=True)
    manifest = load()
    version = manifest['version']
    rules = json.loads(safe_path(ROOT, manifest['rules']).read_text(encoding='utf-8-sig'))
    prompts = json.loads(safe_path(ROOT, manifest.get('prompts_data', 'production_standard/prompts.json')).read_text(encoding='utf-8-sig'))
    defaults = json.loads(safe_path(ROOT, manifest['defaults']).read_text(encoding='utf-8-sig'))
    assert rules and len({r['id'] for r in rules}) == len(rules)
    assert prompts and len({p['id'] for p in prompts}) == len(prompts)
    if manifest['status'] == 'active':
        assert manifest['user_approved'] is True
        assert manifest['approval_mode'] == 'delegated_self_check'
        assert manifest['approval']['user_personal_item_review'] is False
        assert manifest['approval']['authorized_quote'].strip()
    else:
        assert manifest['status'] == 'review_candidate' and manifest['user_approved'] is False
    assert defaults['version'] == version
    from rule_catalog import rules as catalog
    from prompt_library import PROMPTS
    assert catalog() == rules
    assert PROMPTS == [(p['id'], p['title'], p['text']) for p in prompts]
    assert defaults['layout']['reserved_bottom_band_px'] == 0
    assert defaults['layout']['illustration_extent'] == [0, 0, 1920, 1080]
    assert defaults['animation']['max_static_seconds'] == 3.0
    assert defaults['animation']['target_static_seconds'] <= 2.8
    assert defaults['animation']['preserve_graphic_text_scenes'] is True
    assert defaults['animation']['fixed_action_shot_ratio'] is None
    assert defaults['delivery']['project_format'] == 'source_project'
    assert defaults['delivery']['jianying_import_default'] is False
    assert defaults['delivery']['jianying_import_requires'] == 'explicit_user_request'
    sop = safe_path(ROOT, manifest['sop']).read_text(encoding='utf-8-sig')
    prompt_doc = safe_path(ROOT, manifest['prompts']).read_text(encoding='utf-8-sig')
    assert '不自动补瞳孔' not in sop
    for prompt in prompts:
        assert prompt['text'] in prompt_doc, prompt['id']
    for script in HERE.glob('*.py'):
        ast.parse(script.read_text(encoding='utf-8-sig'), filename=str(script))
    historical = []
    for script in ['storyboard/build_storyboard.py', 'reference_analysis/build_sop.py']:
        if not (ROOT / script).is_file():
            historical.append({'script': script, 'ordinary_run': 'not_applicable_historical_instance_not_shipped'})
            continue
        tree = ast.parse((ROOT / script).read_text(encoding='utf-8-sig'), filename=script)
        imports = [node for node in tree.body if isinstance(node, ast.ImportFrom) and node.module == 'historical_rebuild_guard']
        calls = [node for node in tree.body if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == 'require_historical_rebuild']
        assert imports and len(calls) == 1 and tree.body.index(imports[0]) < tree.body.index(calls[0]), script
        guard_path = HERE / 'historical_rebuild_guard.py'
        guard_tree = ast.parse(guard_path.read_text(encoding='utf-8-sig'), filename=str(guard_path))
        guard = next(node for node in guard_tree.body if isinstance(node, ast.FunctionDef) and node.name == 'require_historical_rebuild')
        assert any(isinstance(node, ast.Constant) and node.value == '--historical-rebuild' for node in ast.walk(guard))
        assert any(isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call) and isinstance(node.exc.func, ast.Name) and node.exc.func.id == 'SystemExit' for node in ast.walk(guard))
        historical.append({'script': script, 'guard_wiring': 'read_only_AST_checked', 'execution': 'not_executed'})
    with tempfile.TemporaryDirectory(prefix='entry_check_', dir=CHECKS) as folder:
        out = Path(folder) / 'new_episode'
        command = [sys.executable, '-X', 'utf8', str(HERE / 'start_episode.py'), '--name', '验证用新集', '--out', str(out)]
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        assert result.returncode == 0, result.stderr
        snap = out / '00_brief/standard_snapshot'
        assert load(snap) == manifest
        brief = json.loads((out / '00_brief/episode.json').read_text(encoding='utf-8'))
        assert brief['standard_version'] == version
        assert brief['standard_status'] == manifest['status']
        assert brief['standard_approval_mode'] == manifest.get('approval_mode')
        assert brief['standard_approval'] == manifest.get('approval', {})
        assert brief['standard_self_check'] == manifest.get('self_check')
        assert brief['project_format'] == 'source_project'
        assert brief['jianying_import_requested'] is False
        assert brief['jianying_import_authorization'] is None
        assert brief['render_status'] == 'not_started'
        assert brief['production_baseline'] == manifest.get('baseline_manifest', manifest.get('baseline'))
        assert list((out / '07_exports').iterdir()) == []
        assert list((out / '06_project').iterdir()) == []
        storyboard = json.loads((out / '03_storyboard/storyboard.json').read_text(encoding='utf-8'))
        assert len(storyboard['review_columns']) == 5 and storyboard['shots'] == []
        second = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        assert second.returncode != 0
        target = safe_path(snap, manifest['sop'])
        original = target.read_bytes()
        target.write_bytes(original + b'\nchanged\n')
        try:
            load(snap)
        except ValueError:
            pass
        else:
            raise AssertionError('tampered standard accepted')
        target.write_bytes(original)
        missing_paths = [manifest['sop'], 'production_standard/build_standard.py']
        if manifest.get('baseline_manifest'):
            baseline = json.loads(safe_path(snap, manifest['baseline_manifest']).read_text(encoding='utf-8-sig'))
            source_path = safe_path(snap, baseline['cards_method_sources']['path'])
            method_sources = json.loads(source_path.read_text(encoding='utf-8-sig'))
            missing_paths.append((source_path.parent / method_sources['files'][0]['path']).relative_to(snap).as_posix())
        for missing_path in missing_paths:
            snapshot_manifest = {**manifest, 'files': [item for item in manifest['files'] if item['path'] != missing_path]}
            (snap / 'production_standard.json').write_text(json.dumps(snapshot_manifest), encoding='utf-8')
            try:
                load(snap)
            except ValueError:
                pass
            else:
                raise AssertionError('unlocked current dependency accepted: ' + missing_path)
    from playwright.sync_api import sync_playwright
    errors = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=defaults.get('tools_local', {}).get('browser_channel', 'chrome'), headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 1050}, accept_downloads=True)
        page = context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(safe_path(ROOT, manifest['review']).as_uri())
        page.wait_for_function('window.standardReviewReady===true')
        assert page.locator('#changes').is_visible()
        if manifest['status'] == 'active':
            assert page.locator('#progress').text_content() == '已启用'
            assert page.locator('#changes').inner_text().strip()
        assert page.locator('#ruleList .rule').count() == len(rules)
        embedded = page.locator('#review-data').text_content()
        assert json.loads(embedded)['manifest'] == manifest
        page.locator('[data-tab="rules"]').click()
        category = rules[0]['category']
        page.locator('#category').select_option(category)
        assert page.locator('#ruleList .rule').count() == sum(r['category'] == category for r in rules)
        page.locator('#category').select_option('')
        rid = rules[0]['id']
        page.locator('#search').fill(rid)
        assert page.locator(f'[data-decision="{rid}"]').count() == 1
        page.locator(f'[data-decision="{rid}"]').select_option('需修改')
        page.locator(f'[data-note="{rid}"]').fill('自动验证备注，不是用户意见')
        page.reload()
        page.wait_for_function('window.standardReviewReady===true')
        assert page.locator(f'[data-note="{rid}"]').input_value() == '自动验证备注，不是用户意见'
        with page.expect_download() as download:
            page.locator('#export').click()
        feedback_path = CHECKS / '自动验证_非用户反馈.json'
        download.value.save_as(str(feedback_path))
        feedback = json.loads(feedback_path.read_text(encoding='utf-8'))
        assert feedback['standard_version'] == version
        assert feedback['standard_files'] == manifest['files']
        assert len(feedback['rules']) == len(rules)
        page.evaluate('localStorage.clear()')
        page.reload()
        page.wait_for_function('window.standardReviewReady===true')
        page.locator('#importFile').set_input_files(str(feedback_path))
        page.wait_for_function("document.querySelector('#feedback').textContent==='已导入反馈。'")
        stale = {**feedback, 'standard_files': []}
        stale_path = CHECKS / '自动验证_过期反馈.json'
        stale_path.write_text(json.dumps(stale, ensure_ascii=False), encoding='utf-8')
        page.locator('#importFile').set_input_files(str(stale_path))
        page.wait_for_function("document.querySelector('#feedback').textContent.includes('标准文件内容已变化')")
        page.evaluate('localStorage.clear()')
        page.reload()
        page.wait_for_function('window.standardReviewReady===true')
        for tab in ['changes', 'sop', 'prompts', 'params', 'sources', 'rules']:
            page.locator(f'[data-tab="{tab}"]').click()
            assert page.locator(f'#{tab}').is_visible()
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'), tab
        page.locator('[data-tab="params"]').click()
        assert page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)')
        page.locator('[data-tab="changes"]').click()
        page.screenshot(path=str(CHECKS / '审阅页_本次变化.png'), full_page=False)
        page.set_viewport_size({'width': 390, 'height': 844})
        for tab in ['changes', 'rules', 'params', 'sources']:
            page.locator(f'[data-tab="{tab}"]').click()
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'), tab
        page.locator('[data-tab="changes"]').click()
        page.screenshot(path=str(CHECKS / '审阅页_手机.png'), full_page=False)
        assert not errors, errors
        browser.close()
    result = {'standard_version': version, 'integrity': 'passed', 'rules': len(rules), 'unified_prompts': len(prompts), 'manifest_sha256': hashlib.sha256((ROOT / 'production_standard.json').read_bytes()).hexdigest(), 'historical_guards': historical, 'new_episode': 'isolated snapshot/source_project/no Jianying request/no rendering; nonempty output refused', 'tamper_rejection': 'changed content and unlocked SOP/tool/method asset rejected', 'review_ui': 'six tabs including changes; desktop/mobile; canonical content; filters; persistence; feedback hash binding; stale feedback rejected', 'browser_errors': errors, 'standard_status': manifest['status'], 'approval_mode': manifest.get('approval_mode'), 'user_personal_item_review': manifest.get('approval', {}).get('user_personal_item_review', False), 'whole_standard_approval': 'user_delegated_use_not_personal_item_review' if manifest['status'] == 'active' else 'not_performed', 'video_production': 'not_performed', 'jianying_actions': 'none'}
    (CHECKS / 'standard_qc.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
