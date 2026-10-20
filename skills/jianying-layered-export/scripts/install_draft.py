"""Register a portable package as a NEW Jianying draft.

Default is read-only preflight. --install writes only a new draft and appends its
index entry via a compatible locally installed pyJianYingDraft implementation.
No GUI automation, replacement, editor restart, or automatic rollback is used.
Native evidence is checked only with --require-native-evidence.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import inspect
import json
import ntpath
import os
from pathlib import Path, PureWindowsPath
import shutil
import sys
import tempfile
import uuid

from validate_package import validate_package
from native_evidence import digest, digest as sha


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    """Publish this helper's JSON as a complete file, retaining old bytes on failure."""
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         prefix='.' + path.name + '.', suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def read_snapshot(path):
    data = Path(path).read_bytes()
    return json.loads(data.decode('utf-8-sig')), hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def path_key(value):
    return ntpath.normpath(str(value).replace('/', '\\')).casefold()


def portable_key(value):
    return '/'.join(part for part in value.replace('\\', '/').split('/') if part not in {'', '.'}).casefold()


def checked_target(root, name):
    require(isinstance(name, str) and bool(name.strip()), 'A non-empty draft name is required')
    require(name not in {'.', '..'} and not any(c in name for c in '<>:"/\\|?*'),
            'Draft name must be a single valid directory name')
    require(not name.endswith((' ', '.')) and not any(ord(c) < 32 for c in name),
            'Invalid draft name')
    require(not PureWindowsPath(name).is_reserved(), 'Windows reserved draft name')
    target = root / name
    require(target.resolve().parent == root.resolve(), 'Draft target escapes draft root')
    require(not target.exists() and not target.is_symlink(), f'Draft already exists; choose a new name: {target}')
    return target


def contained_path(root, raw):
    """Treat portable paths identically on Windows and POSIX before any copy."""
    require(isinstance(raw, str) and bool(raw), 'Media path must be a nonempty string')
    relative = raw.replace('\\', '/')
    parts = relative.split('/')
    win = PureWindowsPath(raw)
    require(not win.drive and not win.root and ':' not in raw and '..' not in parts,
            f'Media path escapes root: {raw}')
    require(all(not any(ord(c) < 32 or c in '<>"|?*' for c in part)
                and not part.endswith((' ', '.')) and not PureWindowsPath(part).is_reserved()
                for part in parts if part not in ('', '.')), f'Invalid portable media path: {raw}')
    candidate = root / relative
    require(candidate.resolve().is_relative_to(root.resolve()) and candidate.resolve() != root.resolve(),
            f'Media path escapes root through a link: {raw}')
    return candidate


def checked_audit(path, package, draft_root, index_root):
    for root in (package, draft_root, index_root):
        require(not path.is_relative_to(root.resolve()),
                'Audit directory must be outside the package and draft/index roots')
    require(not path.exists() and not path.is_symlink(), 'Audit directory must be new')
    return path


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


def verify_installed_media(target, media_items, audit):
    """Recheck actual target bytes after save, before declaring installation complete."""
    records = []
    for item in media_items:
        record = {'path': item['path'], 'expectedBytes': item['bytes'],
                  'expectedSha256': item['sha256'].lower(), 'passed': False}
        try:
            path = contained_path(target, item['path']).resolve()
            require(path.is_relative_to(target.resolve()), 'Installed media escapes target')
            require(path.is_file(), 'Installed media is missing')
            record.update(actualBytes=path.stat().st_size, actualSha256=sha(path))
            record['passed'] = (record['actualBytes'] == record['expectedBytes']
                                and record['actualSha256'] == record['expectedSha256'])
        except (OSError, ValueError) as error:
            record['error'] = str(error)
        records.append(record)
    report = {'stage': 'after_save', 'passed': all(r['passed'] for r in records), 'media': records}
    write(audit / 'installed_media_verification.json', report)
    require(report['passed'], 'Installed media changed or missing after save: ' +
            ', '.join(r['path'] for r in records if not r['passed']))
    return len(records)


def check_index_before_registration(before, current, target, name, owned_ids):
    """Allow only the editor's scan of the new directory created by this run."""
    require(isinstance(current, dict) and isinstance(current.get('all_draft_store'), list),
            'Unsupported or concurrently changed draft index structure')
    require({k: v for k, v in current.items() if k != 'all_draft_store'} ==
            {k: v for k, v in before.items() if k != 'all_draft_store'},
            'Editor changed root index fields during copy')
    target_entries = [e for e in current['all_draft_store'] if path_key(e.get('draft_fold_path', '')) == path_key(target)]
    previous_entries = [e for e in current['all_draft_store'] if path_key(e.get('draft_fold_path', '')) != path_key(target)]
    require(previous_entries == before['all_draft_store'], 'Editor changed existing or unrelated index entries during copy')
    require(len(target_entries) <= 1, 'Editor indexed this target more than once')
    if target_entries:
        entry = target_entries[0]
        require(entry.get('draft_id') in owned_ids and
                ('draft_name' not in entry or entry['draft_name'] == name),
                'Scanned target identity does not match the stub or payload created by this run')
    return bool(target_entries)


def collect_owned_stub_ids(initial_meta, current_meta, before, current, target, name, installed_id):
    """Recognize the editor assigning an ID to this run's initially empty stub.

    Never learn an ID from the root index alone. A newly assigned ID must also
    match a still-empty sidecar at this exact newly created target.
    """
    owned_ids = {installed_id}
    initial_id = initial_meta.get('draft_id')
    if isinstance(initial_id, str) and initial_id:
        owned_ids.add(initial_id)
        return owned_ids, None
    require(initial_id in ('', None), 'Unsupported initial stub identity')
    target_entries = [entry for entry in current.get('all_draft_store', [])
                      if path_key(entry.get('draft_fold_path', '')) == path_key(target)]
    if len(target_entries) != 1 or target_entries[0].get('draft_id') in owned_ids:
        return owned_ids, None
    scanned = target_entries[0]
    late_id = scanned.get('draft_id')
    require(isinstance(late_id, str) and bool(late_id) and current_meta.get('draft_id') == late_id,
            'Late stub identity is not corroborated by this target sidecar')
    require(current_meta.get('draft_name') == name and scanned.get('draft_name') == name
            and path_key(current_meta.get('draft_fold_path', '')) == path_key(target),
            'Late stub sidecar name/path does not match this newly created target')
    if current_meta.get('draft_root_path'):
        require(path_key(current_meta['draft_root_path']) == path_key(target.parent),
                'Late stub sidecar has a different draft root')
    require(current_meta.get('tm_duration') == 0 and scanned.get('tm_duration') == 0,
            'Late stub is no longer empty; inspect possible editor changes instead of adopting its identity')
    created_at = current_meta.get('tm_draft_create')
    require(isinstance(created_at, int) and not isinstance(created_at, bool) and created_at > 0
            and all(record.get('tm_draft_create') == created_at and record.get('tm_draft_modified') == created_at
                    and record.get('tm_draft_removed', 0) == 0 for record in (current_meta, scanned)),
            'Late stub timestamps or removed state suggest changes beyond initial scanning')
    for record in (current_meta, scanned):
        for field in ('draft_timeline_materials_size', 'draft_timeline_materials_size_'):
            require(record.get(field, 0) == 0, 'Late stub contains timeline media; stop before registration')
    materials = current_meta.get('draft_materials', [])
    require(isinstance(materials, list) and all(isinstance(item, dict) and not item.get('value') for item in materials)
            and not current_meta.get('draft_segment_extra_info'),
            'Late stub sidecar contains edits; stop before registration')
    require(not any(entry.get('draft_id') == late_id for entry in before['all_draft_store']),
            'Late stub identity was already used by an existing draft')
    identity_fields = {'draft_id', 'draft_name', 'draft_fold_path', 'draft_root_path',
                       'draft_cover', 'draft_removable_storage_device', 'tm_draft_create', 'tm_draft_modified'}
    cloud_sentinels = {'tm_draft_cloud_entry_id', 'tm_draft_cloud_parent_entry_id',
                       'tm_draft_cloud_space_id', 'tm_draft_cloud_user_id'}
    def neutral(value):
        if isinstance(value, dict):
            return all(neutral(item) for item in value.values())
        if isinstance(value, list):
            return all(neutral(item) for item in value)
        return value in ('', None, False, 0)
    for key in set(initial_meta) | set(current_meta):
        old, new = initial_meta.get(key), current_meta.get(key)
        if key in identity_fields or old == new or (neutral(old) and neutral(new)):
            continue
        if key in cloud_sentinels and neutral(old) and new == -1:
            continue
        require(False, f'Late stub has a substantive metadata change: {key}')
    cover = current_meta.get('draft_cover', '')
    require(not cover or cover == 'draft_cover.jpg' or path_key(cover) == path_key(target / 'draft_cover.jpg'),
            'Late stub cover refers outside its own directory')
    device = current_meta.get('draft_removable_storage_device', '')
    require(not device or path_key(device) == path_key(target.drive), 'Late stub device does not match its own target')
    owned_ids.add(late_id)
    return owned_ids, late_id


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
    try:
        import pyJianYingDraft as draft_api
        from pyJianYingDraft.draft_codec import JianyingDraftCryptoCodec, load_json_object_with_codec
        from pyJianYingDraft.draft_crypto import DraftCryptoConfig
        parameters = inspect.signature(draft_api.DraftFolder).parameters
    except (ImportError, AttributeError, TypeError, ValueError) as error:
        raise ValueError('Compatible local pyJianYingDraft runtime is unavailable in this Python: '
                         f'{sys.executable}. This helper requires the codec and DraftFolder registration APIs; '
                         'use the project\'s existing compatible environment/adapter. '
                         'The exported package remains available; no automatic dependency installation. '
                         f'Original error: {error}') from error
    require({'content_codec', 'user_data_path'} <= set(parameters),
            'Local DraftFolder lacks required registration/codec API; use a compatible adapter')
    codec = JianyingDraftCryptoCodec(DraftCryptoConfig(jy_install_dir=str(installation)))
    return draft_api, codec, load_json_object_with_codec


def run(args):
    package = args.package.resolve()
    test_only = args.allow_unvalidated_test_draft
    native_required = getattr(args, 'require_native_evidence', False)
    require(sum(bool(mode) for mode in (native_required, test_only, getattr(args, 'allow_unreviewed', False))) <= 1,
            'Choose one registration mode: normal unreviewed, native evidence, or test draft')
    unreviewed = not (native_required or test_only)
    validation = validate_package(package, args.native_evidence,
                                  allow_unvalidated_test_draft=test_only,
                                  structure_only=unreviewed,
                                  require_native_evidence=native_required)
    require(validation['passed'], 'Package validation failed: ' + '; '.join(validation['errors']))
    if native_required:
        require(validation['deliveryReady'],
                'Native evidence does not cover all required checks; registration in native-reviewed mode is blocked')
    manifest, manifest_hash = read_snapshot(package / 'manifest.json')
    payload, payload_hash = read_snapshot(package / 'draft_content.json')
    require(manifest_hash == validation['manifestSha256'] and payload_hash == validation['draftSha256'],
            'Source package changed after validation; retry from the current package')
    user_data, draft_root, installation = args.user_data.resolve(), args.draft_root.resolve(), args.jy_install.resolve()
    require(draft_root.is_dir(), 'Read the current configuration and provide an existing draft root')
    require(installation.is_dir(), 'Jianying installation directory does not exist')
    if native_required:
        runtime = validation['nativeEvidence']['runtime']
        executable = contained_path(installation, runtime['executableRelativePath']).resolve()
        require(executable.is_relative_to(installation) and executable.is_file(),
                'Evidence runtime executable is absent from --jy-install')
        require(digest(executable) == runtime['executableSha256'],
                'Jianying executable differs from native calibration/layout evidence; recalibrate and recheck')
    index_root = user_data / 'Projects/com.lveditor.draft'
    index_path = index_root / 'root_meta_info.json'
    require(index_path.is_file(), 'Existing Jianying root_meta_info.json is required')
    before_index = read(index_path)
    require(isinstance(before_index.get('all_draft_store'), list), 'Unsupported draft index structure')
    name = args.name or manifest['project']['name']
    if test_only and not name.startswith(('[TEST]', '[CALIBRATION]')):
        name = '[TEST] ' + name
    target = checked_target(draft_root, name)
    for media in manifest['media']:
        contained_path(package, media['path'])
        contained_path(target, media['path'])
    cover = package / 'draft_cover.jpg'
    if cover.exists() or cover.is_symlink():
        require(contained_path(package, 'draft_cover.jpg').is_file(), 'Package cover must be a contained file')
    require(not any(path_key(e.get('draft_fold_path', '')) == path_key(target)
                    for e in before_index['all_draft_store']), 'Draft path is already indexed')
    api, codec, decode_json = load_runtime(installation)
    result = {'status': 'test_only_preflight_passed_no_writes' if test_only else 'preflight_passed_no_writes',
              'name': name, 'path': str(target), 'deliveryReady': validation['deliveryReady'],
              'validationMode': validation['validationMode'], 'nativeValidation': validation['nativeValidation'],
              'mediaCount': len(manifest['media']), 'package': str(package),
              'manifestSha256': validation['manifestSha256'], 'draftSha256': validation['draftSha256'],
              'exportStatus': 'exported', 'registered': False, 'registrationStatus': 'not_performed',
              'nativeReviewStatus': 'evidence_verified' if native_required else 'not_performed',
              'uiOpened': False, 'nativeExportValidation': 'not_performed'}
    # Keep structural diagnostics visible in preflight and both audit outcomes.
    # Unreviewed registration does not resolve system fonts or native text motion.
    for key in ('warnings', 'motionFindings', 'motionInfo', 'motionValidation', 'fontWarnings', 'fontValidation'):
        if key in validation:
            result[key] = validation[key]
    if native_required:
        result['nativeEvidence'] = validation['nativeEvidence']
    if not args.install:
        return result

    stamp = datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + uuid.uuid4().hex[:8]
    audit = checked_audit(args.audit_dir.resolve() if args.audit_dir else package.parent / 'installation_audit' / stamp,
                          package, draft_root, index_root)
    audit.mkdir(parents=True, exist_ok=False)
    result['audit'] = str(audit)
    before_index, index_hash = read_snapshot(index_path)
    require(sha(index_path) == index_hash, 'Root index changed during snapshot; retry from current state')
    require(not any(path_key(e.get('draft_fold_path', '')) == path_key(target)
                    for e in before_index['all_draft_store']), 'Draft path was indexed during preflight')
    write(audit / 'root_meta_info_before.json', before_index)
    existing = snapshot_existing({index_root, draft_root})
    write(audit / 'existing_draft_hashes.json', existing)
    write(audit / 'package_validation.json', validation)
    stage = 'before_new_draft'
    try:
        folder = api.DraftFolder(str(draft_root), content_codec=codec, user_data_path=str(user_data))
        project = manifest['project']
        # Explicit no replacement; only create_draft has the right to create target.
        folder.create_draft(name, project['width'], project['height'], project['fps'],
                            maintrack_adsorb=False, allow_replace=False)
        require(target.is_dir() and target.resolve() == target and not target.is_symlink(),
                'Runtime created a target redirected through a link; refusing to use another draft')
        stub_meta_path = contained_path(target, 'draft_meta_info.json')
        initial_stub_meta = read(stub_meta_path) if stub_meta_path.is_file() else {}
        stub_content_path = contained_path(target, 'draft_content.json')
        initial_content_hash = sha(stub_content_path) if stub_content_path.is_file() else None
        stub_id = initial_stub_meta.get('draft_id')
        result['createdStubId'] = stub_id
        write(audit / 'created_stub_meta.json', initial_stub_meta)
        stage = 'copying_media'
        paths = {}
        for media in manifest['media']:
            source = contained_path(package, media['path'])
            destination = contained_path(target, media['path'])
            destination.parent.mkdir(parents=True, exist_ok=True)
            require(not destination.exists() and not destination.is_symlink(),
                    f'Media collides with draft metadata: {destination}')
            shutil.copy2(source, destination)
            require(sha(destination) == media['sha256'].lower(), f'Copied media mismatch: {destination}')
            paths[portable_key(media['path'])] = str(destination)
        if cover.is_file() and 'draft_cover.jpg' not in paths:
            cover_target = contained_path(target, 'draft_cover.jpg')
            require(not cover_target.exists() and not cover_target.is_symlink(),
                    'Package cover collides with existing runtime/editor cover')
            shutil.copy2(contained_path(package, 'draft_cover.jpg'), cover_target)
        installed = relocate(payload, paths)
        installed['name'], installed['id'] = name, str(uuid.uuid4()).upper()
        require((not stub_content_path.exists() if initial_content_hash is None else
                 stub_content_path.is_file() and sha(stub_content_path) == initial_content_hash),
                'New target content appeared or changed during media copy; refusing to overwrite possible editor work')
        write(target / 'draft_content.json', installed)
        installed_content_hash = sha(target / 'draft_content.json')
        require(sha(package / 'manifest.json') == validation['manifestSha256']
                and sha(package / 'draft_content.json') == validation['draftSha256'],
                'Source package changed during installation')
        stage = 'before_registration'
        if native_required:
            final_validation = validate_package(package, args.native_evidence, require_native_evidence=True)
            require(final_validation['deliveryReady'] and
                    final_validation['nativeEvidence'].get('evidenceSha256') == validation['nativeEvidence']['evidenceSha256']
                    and digest(executable) == runtime['executableSha256'],
                    'Native evidence or runtime changed during installation; keep this directory unregistered')
        require(unchanged(existing),
                'Existing draft changed during copy; retain new directory and read current state before retrying')
        current_index_hash = sha(index_path)
        current_index = read(index_path)
        current_meta_hash = sha(stub_meta_path) if stub_meta_path.is_file() else None
        current_stub_meta = read(stub_meta_path) if current_meta_hash else {}
        require(sha(index_path) == current_index_hash and
                (current_meta_hash is None or sha(stub_meta_path) == current_meta_hash),
                'Root index or target sidecar changed while checking registration state')
        require(sha(target / 'draft_content.json') == installed_content_hash,
                'New target content changed during installation; stop before saving editor changes')
        owned_ids, late_stub_id = collect_owned_stub_ids(initial_stub_meta, current_stub_meta,
            before_index, current_index, target, name, installed['id'])
        result['ownTargetAutoIndexed'] = check_index_before_registration(
            before_index, current_index, target, name, owned_ids)
        if late_stub_id:
            result['editorAssignedStubId'] = late_stub_id
            write(audit / 'editor_assigned_stub_meta_before_save.json', current_stub_meta)
        if result['ownTargetAutoIndexed']:
            write(audit / 'own_target_scan_before_save.json', current_index)
        script = folder.load_template(name)
        # Loading can be slow or run adapter hooks. Recheck immediately before
        # handing control to save(); the backend's internal write is not a CAS.
        require(sha(index_path) == current_index_hash, 'Root index changed during template load; stop before save')
        require((not stub_meta_path.exists() if current_meta_hash is None else
                 stub_meta_path.is_file() and sha(stub_meta_path) == current_meta_hash),
                'Target sidecar changed during template load; stop before save')
        require(sha(target / 'draft_content.json') == installed_content_hash and unchanged(existing),
                'Draft content changed during template load; stop before save')
        script.save()
        stage = 'verifying_registration'
        saved, encoded = decode_json(target / 'draft_content.json', content_codec=codec)
        require(saved['id'] == installed['id'] and saved['name'] == name, 'Saved draft identity differs')
        require(saved['duration'] == installed['duration'], 'Saved duration differs')
        require(saved.get('fps') == installed.get('fps'), 'Saved FPS differs from native evidence')
        require(saved.get('canvas_config') == installed.get('canvas_config'), 'Saved canvas differs from native evidence')
        require(saved['tracks'] == installed['tracks'], 'Saved track/segment structure differs')
        require(saved['materials'] == installed['materials'], 'Saved media/text materials differ')
        after = read(index_path)
        write(audit / 'root_meta_info_after.json', after)
        matching = [e for e in after['all_draft_store'] if path_key(e.get('draft_fold_path', '')) == path_key(target)]
        require(len(matching) == 1 and matching[0]['draft_id'] == saved['id'], 'Expected exactly one registered draft')
        result.update(registered=True, registrationStatus='registered')
        previous = [e for e in after['all_draft_store'] if path_key(e.get('draft_fold_path', '')) != path_key(target)]
        require(previous == before_index['all_draft_store'], 'Existing index entries changed; inspect audit; do not restore stale index')
        require({k: v for k, v in after.items() if k != 'all_draft_store'} ==
                {k: v for k, v in before_index.items() if k != 'all_draft_store'}, 'Existing root index fields changed')
        require(unchanged(existing), 'Existing draft changed during installation; inspect audit')
        verified_media = verify_installed_media(target, manifest['media'], audit)
        result.update(status=('test_only_installed_not_for_delivery' if test_only else
                              'registered_native_review_not_performed' if unreviewed else 'installed_with_native_evidence'), id=saved['id'],
                      tracks=len(saved['tracks']), savedContentEncrypted=bool(encoded),
                      installedMediaVerifiedAfterSave=verified_media,
                      existingDraftFilesUnchanged=len(existing), existingIndexEntriesUnchanged=True)
        write(audit / 'installed_draft.json', result)
        return result
    except Exception as error:
        # A backend can fail after indexing. Report only what can be observed,
        # preserve all files, and never restore a stale root index.
        try:
            failed_index = read(index_path)
            entries = [e for e in failed_index.get('all_draft_store', [])
                       if isinstance(e, dict) and path_key(e.get('draft_fold_path', '')) == path_key(target)]
            result['registered'] = len(entries) == 1 and entries[0].get('draft_id') == locals().get('installed', {}).get('id')
            result['registrationStatus'] = ('registered' if result['registered'] else
                                            'target_indexed_registration_incomplete' if entries else 'not_registered')
        except (OSError, ValueError, TypeError):
            result.update(registered=False, registrationStatus='unknown')
        result.update(status='installation_incomplete', deliveryReady=False, stage=stage, error=str(error),
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
    parser.add_argument('--native-evidence', type=Path, help='Evidence JSON inside package; default native-evidence.json')
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--require-native-evidence', action='store_true',
                       help='Check existing native evidence before registration; use only when review is explicitly requested')
    modes.add_argument('--allow-unreviewed', action='store_true',
                       help='Compatibility alias for the default registration without native evidence')
    modes.add_argument('--allow-unvalidated-test-draft', action='store_true',
                        help='Register only a visibly marked [TEST]/[CALIBRATION] draft; never delivery ready')
    args = parser.parse_args()
    try:
        print(json.dumps(run(args), ensure_ascii=False, indent=2))
        return 0
    except Exception as error:
        print(json.dumps({'status': 'failed', 'deliveryReady': False, 'error': str(error)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == '__main__':
    sys.exit(main())
