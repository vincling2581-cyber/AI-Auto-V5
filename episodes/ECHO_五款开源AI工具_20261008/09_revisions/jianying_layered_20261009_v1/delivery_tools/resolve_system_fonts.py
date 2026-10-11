#!/usr/bin/env python3
"""Prepare a NEW local-only draft package with explicit Windows font files.

Standard-library Python on Windows is sufficient. This is not registration:
it never opens Jianying, edits its index, or writes to an installed draft.
The original portable package stays unchanged. System fonts are copied only
from the target computer into a new local preparation directory; that local
copy is not a font-redistribution package.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def validator(path):
    path = Path(path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f'Package validator missing: {path}')
    spec = importlib.util.spec_from_file_location('layered_package_validator', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate_package


def resolve_fonts():
    if os.name != 'nt':
        raise RuntimeError('Run this preparation script on the target Windows computer')
    import winreg
    fonts_dir = (Path(os.environ.get('SystemRoot', r'C:\Windows')) / 'Fonts').resolve()
    registered = []
    key_path = r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts'
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
        for i in range(winreg.QueryInfoKey(key)[1]):
            name, value, _ = winreg.EnumValue(key, i)
            if isinstance(value, str) and ('yahei' in name.casefold() or '微软雅黑' in name):
                registered.append((name, value))
    result = {}
    for style, fallback in [('regular', 'msyh.ttc'), ('bold', 'msyhbd.ttc')]:
        candidates = [(name, value) for name, value in registered
                      if ('bold' in name.casefold() or '粗体' in name) == (style == 'bold')
                      and 'light' not in name.casefold() and '细体' not in name]
        if not candidates:
            candidates = [('Windows Fonts standard filename', fallback)]
        for registry_name, raw in candidates:
            candidate = Path(os.path.expandvars(raw))
            candidate = (candidate if candidate.is_absolute() else fonts_dir / candidate).resolve()
            if not candidate.is_relative_to(fonts_dir) or not candidate.is_file():
                continue
            result[style] = {'source': str(candidate), 'registryName': registry_name,
                             'bytes': candidate.stat().st_size, 'sha256': sha(candidate)}
            break
        if style not in result:
            raise FileNotFoundError(f'Microsoft YaHei {style} is not available in this computer\'s Windows Fonts directory')
    return result


def output_location(source, output):
    source, output = source.resolve(), output.resolve()
    if output == source or output.is_relative_to(source) or source.is_relative_to(output):
        raise ValueError('The local preparation directory must be separate from the original package')
    if output.exists():
        raise FileExistsError(f'Refusing to overwrite an existing directory. Choose a new --output: {output}')
    # This helper is deliberately not an installer, even if given a bad path.
    protected = [Path(os.environ.get('SystemRoot', r'C:\Windows'))]
    local_app = os.environ.get('LOCALAPPDATA')
    if local_app:
        protected.append(Path(local_app) / 'JianyingPro' / 'User Data')
    if any(output.is_relative_to(p.resolve()) for p in protected) or 'com.lveditor.draft' in output.parts:
        raise ValueError('Output cannot be a Windows or installed Jianying draft directory')
    return output


def prepare(source, output, fonts, check):
    source_hashes = {name: sha(source / name) for name in ['draft_content.json', 'manifest.json']}
    shutil.copytree(source, output)
    draft = read(output / 'draft_content.json')
    manifest = read(output / 'manifest.json')
    font_dir = output / 'media' / 'local_system_fonts'
    font_dir.mkdir(parents=True, exist_ok=True)
    destinations = {}
    for style, info in fonts.items():
        origin = Path(info['source'])
        destination = font_dir / f'microsoft_yahei_{style}_{info["sha256"][:12]}{origin.suffix.lower()}'
        if destination.exists():
            if sha(destination) != info['sha256']:
                raise ValueError(f'Font destination collision: {destination}')
        else:
            shutil.copy2(origin, destination)
        rel = destination.relative_to(output).as_posix()
        destinations[style] = rel
        # Any existing matching media entry is replaced, not duplicated.
        manifest['media'] = [m for m in manifest['media'] if m['path'].replace('\\', '/') != rel]
        manifest['media'].append({'path': rel, 'bytes': destination.stat().st_size,
                                  'sha256': info['sha256'], 'systemFontForLocalUseOnly': True})
    patched = []
    for material in draft.get('materials', {}).get('texts', []):
        content = json.loads(material['content'])
        styles = content.get('styles', [])
        if not styles:
            raise ValueError(f'Native text material has no styles: {material.get("id")}')
        for style in styles:
            weight = 'bold' if style.get('bold', False) else 'regular'
            style['font'] = {'id': '', 'path': destinations[weight]}
        top_weight = 'bold' if styles[0].get('bold', False) else 'regular'
        material['font_path'] = destinations[top_weight]
        material['font_name'] = 'Microsoft YaHei'
        material['content'] = json.dumps(content, ensure_ascii=False)
        patched.append({'materialId': material['id'], 'text': content.get('text', ''),
                        'topFont': destinations[top_weight], 'styleFontPaths': [s['font']['path'] for s in styles]})
    if not patched:
        raise ValueError('Package has no native text materials to prepare')
    historical_match = None
    text_plan_path = output / 'text_plan.json'
    if text_plan_path.is_file():
        plan = read(text_plan_path)
        expected = plan.get('calibration', {}).get('evidence', {}).get('systemFontSha256', {})
        if expected:
            historical_match = fonts['regular']['sha256'] == expected.get('regular_font') and fonts['bold']['sha256'] == expected.get('bold_font')
    preparation = {'status': 'explicit_local_font_files_prepared_not_native_rendered',
                   'createdAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   'registered': False, 'nativeValidation': 'not_performed',
                   'sourcePackage': str(source), 'sourcePackageHashes': source_hashes,
                   'targetSystemFonts': fonts, 'patchedTextMaterials': len(patched),
                   'fontBytesMatchHistoricalCalibration': historical_match,
                   'redistributionApproved': False,
                   'note': 'Local preparation copy only. Do not redistribute the copied Microsoft system font files. Registration must rebase all relative material/font paths.',
                   'materials': patched}
    manifest['fontDependencies'] = [{'fontName': 'Microsoft YaHei', 'required': True,
                                      'resolvedForLocalPreparation': True,
                                      'regularFont': destinations['regular'], 'boldFont': destinations['bold'],
                                      'fontBytesMatchHistoricalCalibration': historical_match,
                                      'redistributionApproved': False,
                                      'nativeFontRendering': 'not_verified'}]
    manifest['localFontPreparation'] = {k: v for k, v in preparation.items() if k != 'materials'}
    manifest['registered'] = False
    manifest['nativeValidation'] = 'not_performed'
    write(output / 'draft_content.json', draft)
    write(output / 'manifest.json', manifest)
    (output / '仅限本机准备_请勿再分发系统字体.txt').write_text(
        '此副本只用于当前 Windows 机器后续导入。系统字体来自当前机器，未取得再分发授权。\n'
        '请分享原始无字体导出包及准备脚本；不要将这个含字体的暂存副本打包分享。\n'
        '显式字体路径已写入并通过结构校验，不代表已在剪映实际渲染验证。\n', encoding='utf-8')
    result = check(output)
    write(output / 'font_preparation_validation.json', result)
    preparation['packageValidationPassed'] = result['passed']
    preparation['draftSha256'] = sha(output / 'draft_content.json')
    preparation['manifestSha256'] = sha(output / 'manifest.json')
    preparation['sourceUnchanged'] = all(sha(source / name) == value for name, value in source_hashes.items())
    write(output / 'font_preparation_report.json', preparation)
    if not result['passed'] or not preparation['sourceUnchanged']:
        raise RuntimeError('Prepared copy failed checks; inspect its font_preparation_validation.json. The original package was not intentionally changed.')
    return {k: v for k, v in preparation.items() if k != 'materials'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--output', type=Path, help='A new local staging directory; refuses overwrite')
    parser.add_argument('--validator', type=Path, default=Path(__file__).with_name('validate_package.py'))
    parser.add_argument('--check-only', action='store_true', help='Only validate source package and find system fonts; write nothing')
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    source = args.package.resolve()
    check = validator(args.validator)
    result = check(source)
    if not result['passed']:
        raise ValueError('Source package validation failed: ' + '; '.join(result['errors'][:5]))
    fonts = resolve_fonts()
    if args.check_only:
        print(json.dumps({'status': 'preflight_passed_read_only', 'fontRenderingVerified': False,
                          'sourcePackage': str(source), 'targetSystemFonts': fonts,
                          'registered': False, 'packageValidationPassed': True}, ensure_ascii=False, indent=2))
        return
    if args.output is None:
        parser.error('--output is required unless --check-only is used')
    output = output_location(source, args.output)
    print(json.dumps(prepare(source, output, fonts, check), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, KeyError) as exc:
        print(f'{type(exc).__name__}: {exc}', file=sys.stderr)
        raise SystemExit(1)
