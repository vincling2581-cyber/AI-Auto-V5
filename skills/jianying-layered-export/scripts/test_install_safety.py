"""Installer safety behavior tests using isolated synthetic files only."""
import json
import os
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

import install_draft
import test_native_gate as fixtures


class InstallSafetyTests(unittest.TestCase):
    setUp = fixtures.NativeGateTests.setUp
    tearDown = fixtures.NativeGateTests.tearDown
    save_evidence = fixtures.NativeGateTests.save_evidence
    args = fixtures.NativeGateTests.args
    fake_runtime = fixtures.NativeGateTests.fake_runtime

    @staticmethod
    def directory_link(link, target):
        if os.name == 'nt':
            subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(target)],
                           check=True, capture_output=True)
        else:
            link.symlink_to(target, target_is_directory=True)

    def test_reserved_windows_draft_names_are_rejected(self):
        for name in ('CON', 'nul.txt', 'COM1', 'LPT9', 'AUX.txt'):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'reserved'):
                install_draft.checked_target(self.base, name)

    def test_runtime_media_symlink_cannot_escape_new_target(self):
        args = self.args(install=True, test=True)
        outside = self.base / 'outside'
        outside.mkdir()
        api, codec, decode = self.fake_runtime(args)
        create = api.DraftFolder.create_draft
        def create_link(folder, name, *values, **options):
            create(folder, name, *values, **options)
            link = args.draft_root / name / 'media'
            self.directory_link(link, outside)
        with patch.object(api.DraftFolder, 'create_draft', create_link), \
             patch.object(install_draft, 'load_runtime', return_value=(api, codec, decode)):
            with self.assertRaisesRegex(RuntimeError, 'escapes|link'):
                install_draft.run(args)
        self.assertEqual(list(outside.iterdir()), [])

    def test_runtime_target_junction_cannot_redirect_into_existing_draft(self):
        args = self.args(install=True, test=True)
        old = args.draft_root / 'old'
        old.mkdir()
        content = old / 'draft_content.json'
        content.write_bytes(b'{"user":"important edit"}')
        api, codec, decode = self.fake_runtime(args)
        def create_link(folder, name, *values, **options):
            self.directory_link(args.draft_root / name, old)
        with patch.object(api.DraftFolder, 'create_draft', create_link), \
             patch.object(install_draft, 'load_runtime', return_value=(api, codec, decode)):
            with self.assertRaisesRegex(RuntimeError, 'redirected through a link'):
                install_draft.run(args)
        self.assertEqual(content.read_bytes(), b'{"user":"important edit"}')
        self.assertEqual([p.name for p in old.iterdir()], ['draft_content.json'])

    def test_runtime_cover_is_not_overwritten(self):
        args = self.args(install=True, test=True)
        (self.root / 'draft_cover.jpg').write_bytes(b'package cover')
        api, codec, decode = self.fake_runtime(args)
        create = api.DraftFolder.create_draft
        def create_cover(folder, name, *values, **options):
            create(folder, name, *values, **options)
            (args.draft_root / name / 'draft_cover.jpg').write_bytes(b'editor cover')
        with patch.object(api.DraftFolder, 'create_draft', create_cover), \
             patch.object(install_draft, 'load_runtime', return_value=(api, codec, decode)):
            with self.assertRaisesRegex(RuntimeError, 'cover|collides'):
                install_draft.run(args)
        self.assertEqual((args.draft_root / '[TEST] Candidate' / 'draft_cover.jpg').read_bytes(), b'editor cover')

    def test_index_change_during_template_load_is_preserved(self):
        args = self.args(install=True, test=True)
        index = args.user_data / 'Projects/com.lveditor.draft/root_meta_info.json'
        api, codec, decode = self.fake_runtime(args)
        load = api.DraftFolder.load_template
        editor_index = {'all_draft_store': [{'draft_id': 'USER-NEW', 'draft_fold_path': str(self.base / 'user-new')}]}
        def load_and_edit(folder, name):
            script = load(folder, name)
            fixtures.write_json(index, editor_index)
            return script
        with patch.object(api.DraftFolder, 'load_template', load_and_edit), \
             patch.object(install_draft, 'load_runtime', return_value=(api, codec, decode)):
            with self.assertRaisesRegex(RuntimeError, 'changed.*save|changed.*template'):
                install_draft.run(args)
        self.assertEqual(json.loads(index.read_text()), editor_index)

    def test_audit_directory_cannot_be_inside_existing_draft(self):
        args = self.args(install=True, test=True)
        old = args.draft_root / 'old'
        old.mkdir()
        fixtures.write_json(old / 'draft_content.json', {'user': 'work'})
        args.audit_dir = old / 'audit'
        with patch.object(install_draft, 'load_runtime', return_value=self.fake_runtime(args)):
            with self.assertRaisesRegex(ValueError, 'audit|Audit'):
                install_draft.run(args)
        self.assertFalse(args.audit_dir.exists())

    def test_nested_json_font_paths_are_relocated_without_changing_visible_text(self):
        source = {'font_path': 'media/font.ttf', 'content': json.dumps({
            'text': 'media/font.ttf', 'styles': [{'font': {'path': r'media\font.ttf'}}]})}
        relocated = install_draft.relocate(source, {'media/font.ttf': 'C:/new/media/font.ttf'})
        nested = json.loads(relocated['content'])
        self.assertEqual(nested['styles'][0]['font']['path'], 'C:/new/media/font.ttf')
        self.assertEqual(nested['text'], 'media/font.ttf')
        self.assertEqual(relocated['font_path'], 'C:/new/media/font.ttf')
        self.assertEqual(source['font_path'], 'media/font.ttf')

    def test_cross_platform_path_traversal_and_reserved_parts_are_rejected(self):
        for raw in ('../outside', r'media\..\outside', '/outside', r'\outside',
                    'C:/outside', 'C:outside', r'\\server\share\outside',
                    'media/file:stream', 'media/nul.ttf', 'media/space /font.ttf'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                install_draft.contained_path(self.root, raw)
        self.assertEqual(install_draft.contained_path(self.root, r'media\font.ttf'), self.root / 'media/font.ttf')

    def test_normal_unreviewed_registration_needs_no_evidence_or_test_label(self):
        args = self.args(install=True)
        args.allow_unreviewed = True
        (self.root / 'native-evidence.json').unlink()
        with patch.object(install_draft, 'load_runtime', return_value=self.fake_runtime(args)):
            result = install_draft.run(args)
        self.assertEqual(result['name'], 'Candidate')
        self.assertEqual(result['status'], 'registered_native_review_not_performed')
        self.assertEqual(result['exportStatus'], 'exported')
        self.assertTrue(result['registered'])
        self.assertEqual(result['nativeValidation'], 'not_performed')
        self.assertFalse(result['deliveryReady'])
        self.assertFalse(result['uiOpened'])
        saved = json.loads((Path(result['path']) / 'draft_content.json').read_text(encoding='utf-8'))
        nested = json.loads(saved['materials']['texts'][0]['content'])
        self.assertEqual(Path(nested['styles'][0]['font']['path']), Path(result['path']) / 'media/font.ttf')

    def test_unreviewed_preflight_writes_nothing(self):
        args = self.args()
        args.allow_unreviewed = True
        (self.root / 'native-evidence.json').unlink()
        with patch.object(install_draft, 'load_runtime', return_value=self.fake_runtime(args)):
            result = install_draft.run(args)
        self.assertFalse(result['registered'])
        self.assertEqual(result['registrationStatus'], 'not_performed')
        self.assertEqual(list(args.draft_root.iterdir()), [])
        self.assertFalse(args.audit_dir.exists())

    def test_package_change_after_validation_is_stopped_before_copy(self):
        args = self.args(install=True, test=True)
        validate = install_draft.validate_package
        def mutate_package(*values, **options):
            report = validate(*values, **options)
            self.manifest['media'][0]['path'] = '../outside'
            fixtures.write_json(self.root / 'manifest.json', self.manifest)
            return report
        with patch.object(install_draft, 'validate_package', side_effect=mutate_package), \
             patch.object(install_draft, 'load_runtime') as loader:
            with self.assertRaisesRegex(ValueError, 'changed after validation'):
                install_draft.run(args)
        loader.assert_not_called()
        self.assertEqual(list(args.draft_root.iterdir()), [])
        self.assertFalse(args.audit_dir.exists())

    def test_atomic_json_publish_failure_preserves_old_bytes_and_removes_temp(self):
        path = self.base / 'owned.json'
        path.write_bytes(b'{"user":"old"}')
        with patch.object(install_draft.os, 'replace', side_effect=OSError('simulated publish failure')):
            with self.assertRaisesRegex(OSError, 'simulated'):
                install_draft.write(path, {'user': 'new'})
        self.assertEqual(path.read_bytes(), b'{"user":"old"}')
        self.assertEqual(list(self.base.glob('.owned.json.*.tmp')), [])

    def test_missing_compatible_runtime_has_actionable_error(self):
        import builtins
        original_import = builtins.__import__
        def without_runtime(name, *values, **options):
            if name == 'pyJianYingDraft':
                raise ModuleNotFoundError('synthetic runtime missing')
            return original_import(name, *values, **options)
        with patch('builtins.__import__', side_effect=without_runtime):
            with self.assertRaisesRegex(ValueError, 'existing compatible environment/adapter'):
                install_draft.load_runtime(self.installation)

    def test_failed_install_retains_new_target_and_retry_does_not_overwrite_it(self):
        args = self.args(install=True, test=True)
        api, codec, decode = self.fake_runtime(args)
        def fail_to_load(folder, name):
            raise OSError('simulated adapter failure')
        with patch.object(api.DraftFolder, 'load_template', fail_to_load), \
             patch.object(install_draft, 'load_runtime', return_value=(api, codec, decode)):
            with self.assertRaisesRegex(RuntimeError, 'simulated adapter failure'):
                install_draft.run(args)
        target = args.draft_root / '[TEST] Candidate'
        before = (target / 'draft_content.json').read_bytes()
        report = json.loads((args.audit_dir / 'installation_incomplete.json').read_text(encoding='utf-8'))
        self.assertEqual(report['exportStatus'], 'exported')
        self.assertEqual(report['registrationStatus'], 'not_registered')
        self.assertTrue(report['targetDirectoryRetained'])
        self.assertFalse(report['automaticRollback'])
        with self.assertRaisesRegex(ValueError, 'already exists'):
            install_draft.run(args)
        self.assertEqual((target / 'draft_content.json').read_bytes(), before)

    def system_font_and_text_alpha_package(self):
        material = self.draft['materials']['texts'][0]
        material.update(font_name='Microsoft YaHei', font_path='')
        content = json.loads(material['content'])
        content['styles'][0]['font'] = {'id': '', 'path': ''}
        material['content'] = json.dumps(content)
        self.manifest['fontDependencies'] = [{'fontName': 'Microsoft YaHei', 'redistributed': False}]
        self.draft['tracks'][0]['segments'][0]['common_keyframes'] = [{
            'id': 'ALPHA_SEQUENCE', 'property_type': 'KFTypeAlpha', 'keyframe_list': [
                {'id': 'ALPHA_START', 'time_offset': 0, 'values': [0], 'curveType': 'Line'},
                {'id': 'ALPHA_END', 'time_offset': 1000000, 'values': [1], 'curveType': 'Line'}]}]
        fixtures.write_json(self.root / 'draft_content.json', self.draft)
        fixtures.write_json(self.root / 'manifest.json', self.manifest)
        (self.root / 'native-evidence.json').unlink()
        validation = install_draft.validate_package(self.root, structure_only=True)
        self.assertTrue(validation['passed'], validation['errors'])
        self.assertEqual(validation['warnings'][0]['code'], 'text.alpha_capability_unverified')
        self.assertEqual(validation['fontWarnings'][0]['fontName'], 'Microsoft YaHei')
        return validation

    def assert_risk_diagnostics(self, result, validation):
        self.assertEqual(result['motionValidation'], 'requires_review')
        self.assertEqual(result['fontValidation'], 'system_dependency_unverified')
        self.assertEqual(result['warnings'], validation['warnings'])
        self.assertEqual(result['motionInfo'], validation['motionInfo'])
        self.assertEqual(result['fontWarnings'], validation['fontWarnings'])
        self.assertEqual(result['nativeValidation'], 'not_performed')
        self.assertFalse(result['deliveryReady'])

    def test_unreviewed_preflight_preserves_font_and_motion_diagnostics(self):
        validation = self.system_font_and_text_alpha_package()
        args = self.args()
        args.allow_unreviewed = True
        with patch.object(install_draft, 'load_runtime', return_value=self.fake_runtime(args)):
            result = install_draft.run(args)
        self.assert_risk_diagnostics(result, validation)
        self.assertFalse(result['registered'])
        self.assertFalse(args.audit_dir.exists())

    def test_unreviewed_success_and_audit_preserve_font_and_motion_diagnostics(self):
        validation = self.system_font_and_text_alpha_package()
        args = self.args(install=True)
        args.allow_unreviewed = True
        with patch.object(install_draft, 'load_runtime', return_value=self.fake_runtime(args)):
            result = install_draft.run(args)
        self.assertTrue(result['registered'])
        self.assert_risk_diagnostics(result, validation)
        audit = json.loads((args.audit_dir / 'installed_draft.json').read_text(encoding='utf-8'))
        self.assert_risk_diagnostics(audit, validation)

    def test_unreviewed_failure_audit_preserves_font_and_motion_diagnostics(self):
        validation = self.system_font_and_text_alpha_package()
        args = self.args(install=True)
        args.allow_unreviewed = True
        api, codec, decode = self.fake_runtime(args)
        with patch.object(api.DraftFolder, 'load_template', side_effect=OSError('simulated save boundary failure')), \
             patch.object(install_draft, 'load_runtime', return_value=(api, codec, decode)):
            with self.assertRaisesRegex(RuntimeError, 'simulated save boundary failure'):
                install_draft.run(args)
        audit = json.loads((args.audit_dir / 'installation_incomplete.json').read_text(encoding='utf-8'))
        self.assert_risk_diagnostics(audit, validation)
        self.assertEqual(audit['exportStatus'], 'exported')
        self.assertEqual(audit['registrationStatus'], 'not_registered')


if __name__ == '__main__':
    unittest.main(verbosity=2)
