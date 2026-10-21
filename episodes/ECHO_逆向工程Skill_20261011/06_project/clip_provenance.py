"""Bind rendered clips and assembled masters to their actual generation inputs."""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re

_LOADED_SOURCE = Path(__file__).resolve()
_LOADED_SHA256 = hashlib.sha256(_LOADED_SOURCE.read_bytes()).hexdigest()

class ProvenanceError(RuntimeError):
    pass


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def file_record(path, cache=None):
    path = Path(path).resolve()
    if not path.is_file():
        raise ProvenanceError(f'依赖或输出文件缺失：{path}')
    if cache is None or path not in cache:
        with path.open('rb') as source:
            value = hashlib.file_digest(source, 'sha256').hexdigest()
        if cache is not None:
            cache[path] = value
    else:
        value = cache[path]
    return {'path': str(path), 'sha256': value}


def require_loaded_source(path, loaded_sha256):
    if file_record(path)['sha256'] != loaded_sha256:
        raise ProvenanceError(f'运行中的脚本已变更，请重新启动命令：{path}')


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f'.{os.getpid()}.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(temporary, path)


def _chrome_binary(channel):
    folders = {'chrome': 'Chrome', 'chrome-beta': 'Chrome Beta',
               'chrome-dev': 'Chrome Dev', 'chrome-canary': 'Chrome SxS'}
    if channel not in folders:
        raise ProvenanceError(f'无法定位浏览器依赖：{channel}')
    for env in ('PROGRAMFILES', 'PROGRAMFILES(X86)', 'LOCALAPPDATA'):
        base = os.environ.get(env)
        if base:
            path = Path(base) / 'Google' / folders[channel] / 'Application/chrome.exe'
            if path.is_file():
                return path
    raise ProvenanceError(f'浏览器依赖缺失：{channel}')


def clip_inputs(episode, card, *, cache=None, expected_config=None, expected_data=None):
    require_loaded_source(_LOADED_SOURCE, _LOADED_SHA256)
    episode = Path(episode).resolve()
    cfg = read(episode / '00_brief/effective_defaults.json')
    data = read(episode / '03_storyboard/cards.json')
    if expected_config is not None and cfg != expected_config:
        raise ProvenanceError('配置已变更，需重新启动渲染或合成命令')
    if expected_data is not None and data != expected_data:
        raise ProvenanceError('分镜已变更，需重新启动渲染或合成命令')
    current = next((c for c in data['cards'] if c['id'] == card['id']), None)
    if current != card:
        raise ProvenanceError(f'{card["id"]}：分镜已变更，需重新渲染')
    project = episode / '06_project'
    page = project / 'cards/card_scene.html'
    sources = [page, project / 'cards/render_cards.py', project / 'clip_provenance.py']
    # Every loaded script may change shared globals; conservatively bind them all.
    for src in re.findall(r'<script\b[^>]*\bsrc=[\"\']([^\"\']+)', page.read_text(encoding='utf-8'), re.I):
        source = (page.parent / src).resolve()
        if not source.is_relative_to(episode):
            raise ProvenanceError(f'渲染源超出本集目录：{src}')
        sources.append(source)
    if card.get('type') == 'animation':
        asset = (episode / '04_assets' / card['art']).resolve()
        if not asset.is_relative_to(episode):
            raise ProvenanceError('插画路径超出本集目录')
        sources.append(asset)
    else:
        # Include episode assets and official screenshots used by card scenes.
        for folder in ('04_assets', '02_research/official', '02_research/screenshots'):
            sources.extend(p for p in (episode / folder).rglob('*')
                           if p.is_file() and '__pycache__' not in p.parts)
    records = []
    for source in sorted(set(sources)):
        item = file_record(source, cache)
        item['path'] = source.relative_to(episode).as_posix()
        records.append(item)
    tool_paths = {'ffmpeg': Path(cfg['tools_local']['ffmpeg']),
                  'chrome': _chrome_binary(cfg['tools_local']['browser_channel']),
                  'regular_font': Path(cfg['type']['regular_font']),
                  'bold_font': Path(cfg['type']['bold_font'])}
    return {'schema_version': 1, 'card': card,
            'video': {k: data[k] for k in ('fps', 'width', 'height')},
            'configuration': cfg, 'files': records,
            'tools': {**{k: file_record(v, cache) for k, v in tool_paths.items()},
                      'python': platform.python_version(),
                      'packages': {k: importlib.metadata.version(k)
                                   for k in ('playwright', 'Pillow')}}}


def clip_receipt_path(episode, card):
    return Path(episode) / '06_project/render' / (card['id'] + '.render.json')


def record_clip(episode, card, before, *, expected_config=None, expected_data=None):
    after = clip_inputs(episode, card, expected_config=expected_config, expected_data=expected_data)
    if after != before:
        raise ProvenanceError(f'{card["id"]}：渲染期间输入发生变化，不签发生成记录')
    clip = Path(episode) / '06_project/render' / (card['id'] + '.mp4')
    receipt = {'schema_version': 1, 'card_id': card['id'], 'inputs': before,
               'input_fingerprint': fingerprint(before), 'output': file_record(clip)}
    write(clip_receipt_path(episode, card), receipt)
    return receipt


def validate_clip(episode, card, *, cache=None, expected_config=None, expected_data=None):
    sid = card['id']
    path = clip_receipt_path(episode, card)
    if not path.is_file():
        raise ProvenanceError(f'{sid}：缺少生成记录，请重新渲染该镜头（不能用 --verify-existing 补发来源）')
    try:
        receipt = read(path)
        expected = clip_inputs(episode, card, cache=cache,
                               expected_config=expected_config, expected_data=expected_data)
        clip = Path(episode) / '06_project/render' / (sid + '.mp4')
        if (receipt['schema_version'] != 1 or receipt['card_id'] != sid
                or receipt['input_fingerprint'] != fingerprint(receipt['inputs'])
                or receipt['input_fingerprint'] != fingerprint(expected)):
            raise ProvenanceError(f'{sid}：源码、配置或素材已变更，请重新渲染该镜头')
        if receipt['output'] != file_record(clip, cache):
            raise ProvenanceError(f'{sid}：片段文件与生成记录不匹配，请重新渲染该镜头')
        return receipt
    except (KeyError, TypeError, ValueError) as error:
        raise ProvenanceError(f'{sid}：生成记录损坏，请重新渲染该镜头') from error


def assembly_inputs(episode, cards, *, expected_config=None, expected_data=None):
    episode = Path(episode)
    cache, clips, errors = {}, [], []
    for card in cards:
        try:
            receipt = validate_clip(episode, card, cache=cache,
                                    expected_config=expected_config, expected_data=expected_data)
            clips.append({'id': card['id'], 'input_fingerprint': receipt['input_fingerprint'],
                          'output': receipt['output']})
        except ProvenanceError as error:
            errors.append(str(error))
    if errors:
        raise ProvenanceError('拒绝合成或检查，以下镜头需要重渲：\n' + '\n'.join(errors))
    cfg = read(episode / '00_brief/effective_defaults.json')
    return {'schema_version': 1, 'clips': clips,
            'voice': file_record(episode / '00_brief/input/voice_original.mp3', cache),
            'audio_encoding': {k: cfg['video'][k] for k in ('audio_codec', 'audio_bitrate')},
            'assembler': file_record(episode / '06_project/finish.py', cache)}


def record_master(episode, cards, master, before, *, expected_config=None, expected_data=None):
    after = assembly_inputs(episode, cards, expected_config=expected_config, expected_data=expected_data)
    if before != after:
        raise ProvenanceError('合成期间输入或片段发生变化，不签发成片生成记录')
    receipt = {'schema_version': 1, 'inputs': before,
               'input_fingerprint': fingerprint(before), 'output': file_record(master)}
    write(Path(episode) / '08_qc/assembly_provenance.json', receipt)
    return receipt


def validate_master(episode, cards, master, *, expected_config=None, expected_data=None):
    path = Path(episode) / '08_qc/assembly_provenance.json'
    if not path.is_file():
        raise ProvenanceError('缺少成片生成记录，请先用已核验片段重新合成；不为已有成片补发当前来源')
    try:
        receipt = read(path)
        current = assembly_inputs(episode, cards, expected_config=expected_config, expected_data=expected_data)
        if (receipt['schema_version'] != 1
                or receipt['input_fingerprint'] != fingerprint(receipt['inputs'])
                or receipt['input_fingerprint'] != fingerprint(current)
                or receipt['output'] != file_record(master)):
            raise ProvenanceError('成片与当前片段或依赖不匹配，请重新合成后再检查')
        return receipt
    except (KeyError, TypeError, ValueError) as error:
        raise ProvenanceError('成片生成记录损坏，请重新合成后再检查') from error
