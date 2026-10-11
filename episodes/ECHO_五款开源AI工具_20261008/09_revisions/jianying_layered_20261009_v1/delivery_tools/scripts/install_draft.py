"""Register a validated portable package as a NEW Jianying draft.

Default is read-only preflight. --install writes only a new draft and appends its
index entry via a compatible locally installed pyJianYingDraft implementation.
No GUI automation, replacement, editor restart, or automatic rollback is used.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import inspect
import json
from pathlib import Path
import shutil
import sys
import uuid

from validate_package import validate_package


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def path_key(value):
    return str(value).replace('\\', '/').rstrip('/').casefold()


def portable_key(value):
    return '/'.join(part for part in value.replace('\\', '/').split('/') if part not in {'', '.'}).casefold()


def checked_target(root, name):
    require(isinstance(name, str) and bool(name.strip()), 'A non-empty draft name is required')
    require(name not in {'.', '..'} and not any(c in name for c in '<>:"/\\|?*'),
            'Draft name must be a single valid directory name')
    require(not name.endswith((' ', '.')) and not any(ord(c) < 32 for c in name),
            'Invalid draft name')
    target = root / name
    require(target.resolve().parent == root.resolve(), 'Draft target escapes draft root')
    require(not target.exists(), f'Draft already exists; choose a new name: {target}')
    return target


def snapshot_existing(roots):
    result = {}
    for root in roots:
        for child in root.iterdir():
            if child.is_dir():
                for filename in ('draft_content.json', 'draft_meta_info.json'):
                    path = child / filename
                    if path.is_file():
                        result[str(path)] = sha(path)
    return result


def unchanged(snapshot):
    return all(Path(path).is_file() and sha(path) == digest for path, digest in snapshot.items())


def relocate(value, paths, field=None):
    if isinstance(value, dict):
        return {key: relocate(item, paths, key) for key, item in value.items()}
    if isinstance(value, list):
        return [relocate(item, paths, field) for item in value]
    if isinstance(value, str):
        is_path = isinstance(field, str) and (field == 'path' or field.endswith('_path'))
        if is_path and portable_key(value) in paths:
            return paths[portable_key(value)]
        if field == 'content' and value.lstrip().startswith(('{', '[')):
            try:
                return json.dumps(relocate(json.loads(value), paths), ensure_ascii=False)
            except (TypeError, ValueError):
                pass
    return value


def load_runtime(installation):
    # Import lazily so --help remains usable without a local editing runtime.
    import pyJianYingDraft as draft_api
    from pyJianYingDraft.draft_codec import JianyingDraftCryptoCodec, load_json_object_with_codec
    from pyJianYingDraft.draft_crypto import DraftCryptoConfig
    parameters = inspect.signature(draft_api.DraftFolder).parameters
    require({'content_codec', 'user_data_path'} <= set(parameters),
            'Local DraftFolder lacks required registration/codec API; use a compatible adapter')
    codec = JianyingDraftCryptoCodec(DraftCryptoConfig(jy_install_dir=str(installation)))
    return draft_api, codec, load_json_object_with_codec


def run(args):
    package = args.package.resolve()
    validation = validate_package(package)
    require(validation['passed'], 'Package validation failed: ' + '; '.join(validation['errors']))
    manifest, payload = read(package / 'manifest.json'), read(package / 'draft_content.json')
    user_data, draft_root, installation = args.user_data.resolve(), args.draft_root.resolve(), args.jy_install.resolve()
    require(draft_root.is_dir(), 'Read the current configuration and provide an existing draft root')
    require(installation.is_dir(), 'Jianying installation directory does not exist')
    index_root = user_data / 'Projects/com.lveditor.draft'
    index_path = index_root / 'root_meta_info.json'
    require(index_path.is_file(), 'Existing Jianying root_meta_info.json is required')
    before_index = read(index_path)
    require(isinstance(before_index.get('all_draft_store'), list), 'Unsupported draft index structure')
    name = args.name or manifest['project']['name']
    target = checked_target(draft_root, name)
    require(not any(path_key(e.get('draft_fold_path', '')) == path_key(target)
                    for e in before_index['all_draft_store']), 'Draft path is already indexed')
    api, codec, decode_json = load_runtime(installation)
    result = {'status': 'preflight_passed_no_writes', 'name': name, 'path': str(target),
              'mediaCount': len(manifest['media']), 'package': str(package),
              'manifestSha256': validation['manifestSha256'], 'draftSha256': validation['draftSha256'],
              'uiOpened': False, 'nativeExportValidation': 'not_performed'}
    if not args.install:
        return result

    stamp = datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + uuid.uuid4().hex[:8]
    audit = args.audit_dir.resolve() if args.audit_dir else package.parent / 'installation_audit' / stamp
    audit.mkdir(parents=True, exist_ok=False)
    result['audit'] = str(audit)
    index_hash = sha(index_path)
    before_index = read(index_path)
    require(sha(index_path) == index_hash, 'Root index changed during snapshot; retry from current state')
    require(not any(path_key(e.get('draft_fold_path', '')) == path_key(target)
                    for e in before_index['all_draft_store']), 'Draft path was indexed during preflight')
    shutil.copy2(index_path, audit / 'root_meta_info_before.json')
    existing = snapshot_existing({index_root, draft_root})
    write(audit / 'existing_draft_hashes.json', existing)
    stage = 'before_new_draft'
    try:
        folder = api.DraftFolder(str(draft_root), content_codec=codec, user_data_path=str(user_data))
        project = manifest['project']
        # Explicit no replacement; only create_draft has the right to create target.
        folder.create_draft(name, project['width'], project['height'], project['fps'],
                            maintrack_adsorb=False, allow_replace=False)
        stage = 'copying_media'
        paths = {}
        for media in manifest['media']:
            destination = target / media['path']
            destination.parent.mkdir(parents=True, exist_ok=True)
            require(not destination.exists(), f'Media collides with draft metadata: {destination}')
            shutil.copy2(package / media['path'], destination)
            require(sha(destination) == media['sha256'].lower(), f'Copied media mismatch: {destination}')
            paths[portable_key(media['path'])] = str(destination)
        cover = package / 'draft_cover.jpg'
        if cover.is_file() and 'draft_cover.jpg' not in paths:
            shutil.copy2(cover, target / 'draft_cover.jpg')
        installed = relocate(payload, paths)
        installed['name'], installed['id'] = name, str(uuid.uuid4()).upper()
        write(target / 'draft_content.json', installed)
        require(sha(package / 'manifest.json') == validation['manifestSha256']
                and sha(package / 'draft_content.json') == validation['draftSha256'],
                'Source package changed during installation')
        stage = 'before_registration'
        require(sha(index_path) == index_hash and unchanged(existing),
                'Editor state changed during copy; new directory is retained unregistered. Read current state before retrying')
        script = folder.load_template(name)
        script.save()
        stage = 'verifying_registration'
        saved, encoded = decode_json(target / 'draft_content.json', content_codec=codec)
        require(saved['id'] == installed['id'] and saved['name'] == name, 'Saved draft identity differs')
        require(saved['duration'] == installed['duration'], 'Saved duration differs')
        require(saved['tracks'] == installed['tracks'], 'Saved track/segment structure differs')
        require(saved['materials'] == installed['materials'], 'Saved media/text materials differ')
        after = read(index_path)
        write(audit / 'root_meta_info_after.json', after)
        matching = [e for e in after['all_draft_store'] if path_key(e.get('draft_fold_path', '')) == path_key(target)]
        require(len(matching) == 1 and matching[0]['draft_id'] == saved['id'], 'Expected exactly one registered draft')
        previous = [e for e in after['all_draft_store'] if path_key(e.get('draft_fold_path', '')) != path_key(target)]
        require(previous == before_index['all_draft_store'], 'Existing index entries changed; inspect audit; do not restore stale index')
        require({k: v for k, v in after.items() if k != 'all_draft_store'} ==
                {k: v for k, v in before_index.items() if k != 'all_draft_store'}, 'Existing root index fields changed')
        require(unchanged(existing), 'Existing draft changed during installation; inspect audit')
        result.update(status='installed_and_structurally_verified', id=saved['id'],
                      tracks=len(saved['tracks']), savedContentEncrypted=bool(encoded),
                      existingDraftFilesUnchanged=len(existing), existingIndexEntriesUnchanged=True)
        write(audit / 'installed_draft.json', result)
        return result
    except Exception as error:
        result.update(status='installation_incomplete', stage=stage, error=str(error),
                      targetDirectoryRetained=target.exists(), automaticRollback=False)
        write(audit / 'installation_incomplete.json', result)
        raise RuntimeError(f'{error}; audit: {audit}; stage: {stage}') from error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', required=True, type=Path)
    parser.add_argument('--user-data', required=True, type=Path)
    parser.add_argument('--draft-root', required=True, type=Path)
    parser.add_argument('--jy-install', required=True, type=Path)
    parser.add_argument('--name')
    parser.add_argument('--install', action='store_true', help='Create and register a new draft; omitted means read-only preflight')
    parser.add_argument('--audit-dir', type=Path, help='New audit directory; must not already exist')
    args = parser.parse_args()
    try:
        print(json.dumps(run(args), ensure_ascii=False, indent=2))
        return 0
    except Exception as error:
        print(json.dumps({'status': 'failed', 'error': str(error)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == '__main__':
    sys.exit(main())
