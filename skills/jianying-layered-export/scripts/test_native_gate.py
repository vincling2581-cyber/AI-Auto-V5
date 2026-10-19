"""Isolated behavior tests. Synthetic fixtures are not native acceptance evidence."""
import argparse
import copy
import json
from pathlib import Path
import struct
import tempfile
import types
import unittest
from unittest.mock import patch
import zlib

import install_draft
from native_evidence import digest, media_manifest_sha256, raster_size
from validate_package import validate_package


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')


def png(path, color):
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
    width, height = 640, 360
    data = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
    data += chunk(b'IDAT', zlib.compress((b'\0' + bytes(color) * width) * height)) + chunk(b'IEND', b'')
    path.write_bytes(data)


class NativeGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='jianying_native_gate_test_')
        self.base = Path(self.tmp.name).resolve()
        self.root = self.base / 'package'
        (self.root / 'media').mkdir(parents=True)
        (self.root / 'evidence').mkdir()
        font = self.root / 'media/font.ttf'
        font.write_bytes(b'fixture-font-not-for-production')
        self.draft = {'name': 'Fixture', 'id': 'DRAFT', 'fps': 30, 'duration': 1000000,
                      'canvas_config': {'width': 640, 'height': 360},
                      'materials': {'texts': [{'id': 'M1', 'font_path': 'media/font.ttf',
                          'content': json.dumps({'text': 'test', 'styles': [{'size': 12, 'font': {'path': 'media/font.ttf'}}]})}]},
                      'tracks': [{'id': 'T1', 'type': 'text', 'segments': [
                          {'id': 'S1', 'material_id': 'M1', 'target_timerange': {'start': 0, 'duration': 1000000}}]}]}
        self.manifest = {'schemaVersion': 1, 'project': {'name': 'Fixture', 'width': 640, 'height': 360,
                        'fps': 30, 'durationUs': 1000000}, 'media': [
                            {'path': 'media/font.ttf', 'bytes': font.stat().st_size, 'sha256': digest(font)}],
                        'panels': [], 'sources': [], 'segments': [
                            {'id': 'S1', 'scene': 'C1', 'owner': 'shared', 'role': 'text', 'textKey': 'test'}]}
        write_json(self.root / 'draft_content.json', self.draft)
        write_json(self.root / 'manifest.json', self.manifest)
        write_json(self.root / 'evidence/calibration.json', self.draft)
        png(self.root / 'evidence/native.png', (250, 250, 250))
        png(self.root / 'evidence/reference.png', (240, 240, 240))
        self.installation = self.base / 'installation'
        self.installation.mkdir()
        (self.installation / 'JianyingPro.exe').write_bytes(b'fixture-executable-not-for-execution')
        def artifact(path):
            return {'path': path, 'sha256': digest(self.root / path)}
        sample = {'timeUs': 100000, 'nativeFrame': artifact('evidence/native.png'),
                  'referenceFrame': artifact('evidence/reference.png'),
                  'capture': {'method': 'jianying_ui', 'draftSha256': digest(self.root / 'draft_content.json'),
                              'recordedAt': '2026-10-13T00:00:00+08:00',
                              'viewport': {'x': 0, 'y': 0, 'width': 640, 'height': 360}},
                  'review': {'status': 'passed', 'font': True, 'textSize': True, 'position': True,
                             'lineBreaks': True, 'clipping': True}}
        calibration_sample = copy.deepcopy(sample)
        calibration_sample.update(fontPaths=['media/font.ttf'], sourceFontSizePx=32, nativeFontSize=12)
        final_sample = copy.deepcopy(sample)
        final_sample['segmentIds'] = ['S1']
        self.evidence = {'schemaVersion': 1, 'binding': {'draftSha256': digest(self.root / 'draft_content.json'),
                         'manifestSha256': digest(self.root / 'manifest.json'),
                         'canvas': {'width': 640, 'height': 360}, 'fps': 30, 'durationUs': 1000000,
                         'mediaManifestSha256': media_manifest_sha256(self.manifest),
                         'fonts': [artifact('media/font.ttf')]},
                         'runtime': {'product': 'JianyingPro', 'version': 'fixture-version',
                                     'executableRelativePath': 'JianyingPro.exe',
                                     'executableSha256': digest(self.installation / 'JianyingPro.exe')},
                         'calibration': {'status': 'passed', 'reviewer': 'SYNTHETIC_TEST_FIXTURE',
                                         'reviewedAt': '2026-10-13', 'method': 'fixture measured mapping',
                                         'parameters': {'sizeLookup': {'32': 12}, 'anchorOffsetPx': [0, 1]},
                                         'draft': artifact('evidence/calibration.json'), 'samples': [calibration_sample]},
                         'finalLayout': {'status': 'passed', 'reviewer': 'SYNTHETIC_TEST_FIXTURE',
                                         'reviewedAt': '2026-10-13', 'samples': [final_sample]}}
        self.save_evidence()

    def tearDown(self):
        self.tmp.cleanup()

    def save_evidence(self):
        write_json(self.root / 'native-evidence.json', self.evidence)

    def assert_rejected(self, name):
        report = validate_package(self.root)
        self.assertFalse(report['deliveryReady'], report)
        self.assertFalse(report['passed'], report)
        self.assertTrue(any(name in error for error in report['errors']), report['errors'])

    def args(self, install=False, test=False):
        user_data, draft_root = self.base / 'user_data', self.base / 'drafts'
        draft_root.mkdir(exist_ok=True)
        write_json(user_data / 'Projects/com.lveditor.draft/root_meta_info.json', {'all_draft_store': []})
        return argparse.Namespace(package=self.root, native_evidence=None, allow_unvalidated_test_draft=test,
                                  user_data=user_data, draft_root=draft_root, jy_install=self.installation,
                                  name='Candidate', install=install, audit_dir=self.base / 'audit')

    def fake_runtime(self, args, auto_scan=False, blank_stub=False):
        class Folder:
            def __init__(self, *unused, **kwargs):
                pass
            def create_draft(inner, name, *unused, **kwargs):
                self.assertFalse(kwargs['allow_replace'])
                path = args.draft_root / name
                path.mkdir()
                write_json(path / 'draft_meta_info.json', {'draft_id': '' if blank_stub else 'OWN-STUB-ID'})
                if auto_scan:
                    index = args.user_data / 'Projects/com.lveditor.draft/root_meta_info.json'
                    write_json(index, {'all_draft_store': [{'draft_fold_path': str(path), 'draft_name': name,
                               'draft_id': 'OWN-STUB-ID' if auto_scan is True else 'UNRELATED-ID'}]})
            def load_template(inner, name):
                def save():
                    path = args.draft_root / name
                    payload = json.loads((path / 'draft_content.json').read_text(encoding='utf-8'))
                    index = args.user_data / 'Projects/com.lveditor.draft/root_meta_info.json'
                    write_json(index, {'all_draft_store': [{'draft_fold_path': str(path), 'draft_id': payload['id']}]})
                return types.SimpleNamespace(save=save)
        def decode(path, **kwargs):
            return json.loads(path.read_text(encoding='utf-8')), False
        return types.SimpleNamespace(DraftFolder=Folder), object(), decode

    def late_scan_copy(self, args, mutate=None, write_user_content=False):
        real_copy = install_draft.shutil.copy2
        def copy_and_scan(source, destination, *positional, **keywords):
            result = real_copy(source, destination, *positional, **keywords)
            if Path(destination).name == 'font.ttf':
                target = Path(destination).parent.parent
                meta = {'draft_id': 'EDITOR-ASSIGNED-STUB', 'draft_name': target.name,
                        'draft_fold_path': str(target), 'draft_root_path': str(target.parent),
                        'tm_duration': 0, 'tm_draft_create': 123000, 'tm_draft_modified': 123000,
                        'draft_timeline_materials_size_': 0, 'draft_materials': []}
                entry = copy.deepcopy(meta)
                if mutate:
                    mutate(meta, entry)
                write_json(target / 'draft_meta_info.json', meta)
                write_json(args.user_data / 'Projects/com.lveditor.draft/root_meta_info.json', {'all_draft_store': [entry]})
                if write_user_content:
                    write_json(target / 'draft_content.json', {'id': 'USER-WORK', 'tracks': ['important edit']})
            return result
        return copy_and_scan

    def test_missing_evidence_blocks_default_delivery(self):
        (self.root / 'native-evidence.json').unlink()
        self.assert_rejected('native.evidence')

    def test_test_flag_never_marks_delivery_ready(self):
        (self.root / 'native-evidence.json').unlink()
        report = validate_package(self.root, allow_unvalidated_test_draft=True)
        self.assertTrue(report['passed'])
        self.assertEqual(report['status'], 'test_only_passed')
        self.assertFalse(report['deliveryReady'])

    def test_complete_record_validates_evidence_without_claiming_playback(self):
        report = validate_package(self.root)
        self.assertTrue(report['deliveryReady'], report['errors'])
        self.assertEqual(report['nativeValidation'], 'evidence_verified')
        self.assertEqual(report['nativeEvidence']['nativePlaybackValidation'], 'not_performed')

    def test_changed_draft_invalidates_evidence(self):
        with (self.root / 'draft_content.json').open('a', encoding='utf-8') as stream:
            stream.write('\n')
        self.assert_rejected('binding.draftSha256')

    def test_changed_manifest_ownership_invalidates_evidence(self):
        self.manifest['segments'][0]['scene'] = 'CHANGED'
        write_json(self.root / 'manifest.json', self.manifest)
        self.assert_rejected('binding.manifestSha256')

    def test_legacy_evidence_without_manifest_binding_is_not_reused(self):
        self.evidence['binding'].pop('manifestSha256')
        self.save_evidence()
        self.assert_rejected('binding.manifestSha256')

    def test_jpeg_dimensions_without_scan_data_are_rejected(self):
        path = self.root / 'evidence/no-scan.jpg'
        payload = bytes([8]) + struct.pack('>HH', 360, 640) + bytes([1, 1, 0x11, 0])
        path.write_bytes(b'\xff\xd8\xff\xc0' + struct.pack('>H', len(payload) + 2) + payload + b'\xff\xd9')
        with self.assertRaises(ValueError):
            raster_size(path)

    def test_png_nonempty_but_incorrect_pixel_length_is_rejected(self):
        def chunk(kind, payload):
            return struct.pack('>I', len(payload)) + kind + payload + struct.pack('>I', zlib.crc32(kind + payload) & 0xffffffff)
        path = self.root / 'evidence/short-pixels.png'
        path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 640, 360, 8, 2, 0, 0, 0))
                         + chunk(b'IDAT', zlib.compress(b'not-enough-pixels')) + chunk(b'IEND', b''))
        with self.assertRaisesRegex(ValueError, 'scanline length'):
            raster_size(path)

    def test_changed_media_invalidates_evidence_after_manifest_refresh(self):
        font = self.root / 'media/font.ttf'
        font.write_bytes(b'changed-font')
        self.manifest['media'][0].update(bytes=font.stat().st_size, sha256=digest(font))
        write_json(self.root / 'manifest.json', self.manifest)
        self.evidence['binding']['manifestSha256'] = digest(self.root / 'manifest.json')
        self.save_evidence()
        self.assert_rejected('binding.mediaManifestSha256')

    def test_font_omission_is_rejected(self):
        self.evidence['binding']['fonts'] = []
        self.save_evidence()
        self.assert_rejected('fonts.coverage')

    def test_each_text_needs_its_own_explicit_font(self):
        self.draft['materials']['texts'].append({'id': 'M2', 'content': json.dumps({'text': 'unbound', 'styles': [{'size': 12}]})})
        self.draft['tracks'].append({'id': 'T2', 'type': 'text', 'segments': [
            {'id': 'S2', 'material_id': 'M2', 'target_timerange': {'start': 0, 'duration': 1000000}}]})
        self.manifest['segments'].append({'id': 'S2', 'scene': 'C1', 'owner': 'shared', 'role': 'text', 'textKey': 'unbound'})
        write_json(self.root / 'draft_content.json', self.draft)
        write_json(self.root / 'manifest.json', self.manifest)
        self.evidence['binding']['draftSha256'] = digest(self.root / 'draft_content.json')
        self.save_evidence()
        self.assert_rejected('fonts.segmentExplicit')

    def test_calibration_must_actually_contain_claimed_font_and_size(self):
        calibration = copy.deepcopy(self.draft)
        calibration['materials'] = {}
        calibration['tracks'] = []
        path = self.root / 'evidence/calibration.json'
        write_json(path, calibration)
        self.evidence['calibration']['draft']['sha256'] = digest(path)
        self.evidence['calibration']['samples'][0]['capture']['draftSha256'] = digest(path)
        self.save_evidence()
        self.assert_rejected('calibrationDraftStyles')

    def test_calibration_claimed_size_must_match_native_material(self):
        self.evidence['calibration']['samples'][0]['nativeFontSize'] = 999
        self.save_evidence()
        self.assert_rejected('calibrationDraftStyles')

    def test_canvas_drift_is_rejected(self):
        self.evidence['binding']['canvas']['width'] = 1280
        self.save_evidence()
        self.assert_rejected('binding.canvas')

    def test_offline_svg_renderer_is_rejected(self):
        self.evidence['finalLayout']['samples'][0]['capture']['method'] = 'svg_reconstruction'
        self.save_evidence()
        self.assert_rejected('nativeOrigin')

    def test_svg_renamed_png_is_rejected(self):
        path = self.root / 'evidence/native.png'
        path.write_text('<svg width="640" height="360"></svg>', encoding='utf-8')
        for stage in ('calibration', 'finalLayout'):
            self.evidence[stage]['samples'][0]['nativeFrame']['sha256'] = digest(path)
        self.save_evidence()
        self.assert_rejected('actual PNG or JPEG')

    def test_source_cannot_be_its_own_native_evidence(self):
        self.evidence['finalLayout']['samples'][0]['nativeFrame'] = copy.deepcopy(self.evidence['finalLayout']['samples'][0]['referenceFrame'])
        self.save_evidence()
        self.assert_rejected('independentFrames')

    def test_unreviewed_text_is_rejected(self):
        self.evidence['finalLayout']['samples'][0]['segmentIds'] = []
        self.save_evidence()
        self.assert_rejected('segmentIds')

    def test_sample_outside_segment_is_rejected(self):
        self.evidence['finalLayout']['samples'][0]['timeUs'] = 1000000
        self.save_evidence()
        self.assert_rejected('timeUs')

    def test_missing_measured_parameters_is_rejected(self):
        self.evidence['calibration']['parameters'] = {}
        self.save_evidence()
        self.assert_rejected('calibration.parameters')

    def test_false_visual_review_is_rejected(self):
        self.evidence['finalLayout']['samples'][0]['review']['position'] = False
        self.save_evidence()
        self.assert_rejected('visualReview')

    def test_missing_evidence_blocks_installer_before_runtime_or_writes(self):
        args = self.args(install=True)
        (self.root / 'native-evidence.json').unlink()
        with patch.object(install_draft, 'load_runtime') as loader:
            with self.assertRaisesRegex(ValueError, 'Package validation failed'):
                install_draft.run(args)
            loader.assert_not_called()
        self.assertEqual(list(args.draft_root.iterdir()), [])
        self.assertFalse(args.audit_dir.exists())

    def test_runtime_drift_blocks_installer_before_writes(self):
        args = self.args(install=True)
        (self.installation / 'JianyingPro.exe').write_bytes(b'upgraded-runtime')
        with patch.object(install_draft, 'load_runtime') as loader:
            with self.assertRaisesRegex(ValueError, 'executable differs'):
                install_draft.run(args)
            loader.assert_not_called()
        self.assertEqual(list(args.draft_root.iterdir()), [])

    def test_test_install_is_visibly_marked_and_not_complete(self):
        args = self.args(install=True, test=True)
        (self.root / 'native-evidence.json').unlink()
        with patch.object(install_draft, 'load_runtime', return_value=self.fake_runtime(args)):
            result = install_draft.run(args)
        self.assertEqual(result['name'], '[TEST] Candidate')
        self.assertEqual(result['status'], 'test_only_installed_not_for_delivery')
        self.assertFalse(result['deliveryReady'])
        self.assertTrue(Path(result['path']).is_dir())
        audit = json.loads((args.audit_dir / 'installed_draft.json').read_text(encoding='utf-8'))
        self.assertFalse(audit['deliveryReady'])

    def test_formal_install_requires_and_records_evidence(self):
        args = self.args(install=True)
        with patch.object(install_draft, 'load_runtime', return_value=self.fake_runtime(args)):
            result = install_draft.run(args)
        self.assertEqual(result['status'], 'installed_with_native_evidence')
        self.assertEqual(result['name'], 'Candidate')
        self.assertTrue(result['deliveryReady'])
        self.assertEqual(result['nativeValidation'], 'evidence_verified')

    def test_saved_canvas_or_fps_drift_cannot_keep_delivery_approval(self):
        for key, changed in [('fps', 24), ('canvas_config', {'width': 1280, 'height': 720})]:
            with self.subTest(field=key):
                args = self.args(install=True)
                args.name = 'Drift_' + key
                args.audit_dir = self.base / ('audit_' + key)
                api, codec, decode = self.fake_runtime(args)
                def changed_decode(path, **kwargs):
                    value, encoded = decode(path, **kwargs)
                    value[key] = changed
                    return value, encoded
                with patch.object(install_draft, 'load_runtime', return_value=(api, codec, changed_decode)):
                    with self.assertRaisesRegex(RuntimeError, 'differs from native evidence'):
                        install_draft.run(args)
                audit = json.loads((args.audit_dir / 'installation_incomplete.json').read_text(encoding='utf-8'))
                self.assertFalse(audit['deliveryReady'])

    def test_editor_scan_of_own_stub_can_finish_registration(self):
        args = self.args(install=True, test=True)
        with patch.object(install_draft, 'load_runtime', return_value=self.fake_runtime(args, auto_scan=True)):
            result = install_draft.run(args)
        self.assertTrue(result['ownTargetAutoIndexed'])
        self.assertEqual(result['status'], 'test_only_installed_not_for_delivery')
        self.assertTrue((args.audit_dir / 'own_target_scan_before_save.json').is_file())

    def test_editor_scan_with_unrelated_identity_is_stopped(self):
        args = self.args(install=True, test=True)
        with patch.object(install_draft, 'load_runtime', return_value=self.fake_runtime(args, auto_scan='wrong')):
            with self.assertRaisesRegex(RuntimeError, 'Scanned target identity'):
                install_draft.run(args)

    def test_editor_can_assign_identity_to_initially_blank_stub(self):
        args = self.args(install=True, test=True)
        with patch.object(install_draft, 'load_runtime', return_value=self.fake_runtime(args, blank_stub=True)), \
             patch.object(install_draft.shutil, 'copy2', side_effect=self.late_scan_copy(args)):
            result = install_draft.run(args)
        self.assertEqual(result['createdStubId'], '')
        self.assertEqual(result['editorAssignedStubId'], 'EDITOR-ASSIGNED-STUB')
        self.assertEqual(result['status'], 'test_only_installed_not_for_delivery')
        self.assertTrue((args.audit_dir / 'created_stub_meta.json').is_file())
        self.assertTrue((args.audit_dir / 'editor_assigned_stub_meta_before_save.json').is_file())

    def test_late_stub_identity_needs_matching_empty_unchanged_sidecar(self):
        scenarios = [
            ('mismatched_id', lambda meta, entry: meta.update(draft_id='UNRELATED'), 'not corroborated'),
            ('wrong_path', lambda meta, entry: meta.update(draft_fold_path='D:/elsewhere'), 'name/path'),
            ('edited_duration', lambda meta, entry: meta.update(tm_duration=100000), 'no longer empty'),
            ('later_modified', lambda meta, entry: meta.update(tm_draft_modified=124000), 'timestamps'),
            ('unknown_setting', lambda meta, entry: meta.update(user_notes='editor work'), 'substantive metadata'),
        ]
        for name, mutate, expected in scenarios:
            with self.subTest(scenario=name):
                args = self.args(install=True, test=True)
                args.name = name
                args.audit_dir = self.base / ('audit_' + name)
                with patch.object(install_draft, 'load_runtime', return_value=self.fake_runtime(args, blank_stub=True)), \
                     patch.object(install_draft.shutil, 'copy2', side_effect=self.late_scan_copy(args, mutate)):
                    with self.assertRaisesRegex(RuntimeError, expected):
                        install_draft.run(args)

    def test_new_target_user_work_is_not_overwritten_during_media_copy(self):
        args = self.args(install=True, test=True)
        with patch.object(install_draft, 'load_runtime', return_value=self.fake_runtime(args, blank_stub=True)), \
             patch.object(install_draft.shutil, 'copy2', side_effect=self.late_scan_copy(args, write_user_content=True)):
            with self.assertRaisesRegex(RuntimeError, 'refusing to overwrite possible editor work'):
                install_draft.run(args)
        payload = json.loads((args.draft_root / '[TEST] Candidate' / 'draft_content.json').read_text(encoding='utf-8'))
        self.assertEqual(payload, {'id': 'USER-WORK', 'tracks': ['important edit']})

    def test_unrelated_index_change_is_still_stopped(self):
        before = {'root_setting': 1, 'all_draft_store': [{'draft_id': 'EXISTING', 'draft_fold_path': 'D:/old'}]}
        current = copy.deepcopy(before)
        current['all_draft_store'][0]['draft_name'] = 'user edit'
        with self.assertRaisesRegex(ValueError, 'existing or unrelated'):
            install_draft.check_index_before_registration(before, current, Path('D:/new'), 'new', {'OWN'})
        current = copy.deepcopy(before)
        current['root_setting'] = 2
        with self.assertRaisesRegex(ValueError, 'root index fields'):
            install_draft.check_index_before_registration(before, current, Path('D:/new'), 'new', {'OWN'})


if __name__ == '__main__':
    unittest.main(verbosity=2)
