"""Isolated regression cases for structural and temporal claims; never native evidence."""
import copy
import json
import unittest

import test_native_gate as fixtures
from native_evidence import digest
from validate_package import validate_package


class MotionContractTests(unittest.TestCase):
    setUp = fixtures.NativeGateTests.setUp
    tearDown = fixtures.NativeGateTests.tearDown
    save_evidence = fixtures.NativeGateTests.save_evidence

    @property
    def segment(self):
        return self.draft['tracks'][0]['segments'][0]

    def frames(self, prop='KFTypeScaleX', points=((0, 1), (500000, 0), (533333, 1))):
        return {'id': 'KL_' + prop, 'property_type': prop, 'keyframe_list': [
            {'id': f'KF_{prop}_{index}', 'time_offset': time, 'values': [value], 'curveType': 'Line'}
            for index, (time, value) in enumerate(points)]}

    def save(self):
        fixtures.write_json(self.root / 'draft_content.json', self.draft)
        fixtures.write_json(self.root / 'manifest.json', self.manifest)

    def report(self):
        self.save()
        return validate_package(self.root, structure_only=True)

    def reject(self, code):
        report = self.report()
        self.assertFalse(report['passed'], report)
        self.assertTrue(any(code in error for error in report['errors']), report['errors'])

    def test_structure_only_does_not_require_native_evidence_or_test_label(self):
        (self.root / 'native-evidence.json').unlink()
        report = self.report()
        self.assertEqual(report['status'], 'structure_passed')
        self.assertEqual(report['nativeValidation'], 'not_performed')
        self.assertFalse(report['deliveryReady'])

    def test_modes_are_mutually_exclusive(self):
        report = validate_package(self.root, structure_only=True, require_native_evidence=True)
        self.assertFalse(report['passed'])

    def test_one_frame_zero_scale_is_detected_with_absolute_time(self):
        self.segment['common_keyframes'] = [self.frames()]
        report = self.report()
        self.assertTrue(report['passed'], report['errors'])
        findings = [item for item in report['warnings'] if item['code'] == 'text.zero_scale_transition']
        self.assertEqual(len(findings), 2)
        self.assertEqual(findings[1]['detail']['startUs'], 500000)
        self.assertTrue(findings[1]['detail']['withinOneFrame'])
        self.assertEqual(report['motionValidation'], 'requires_review')

    def test_declared_alpha_to_scale_workaround_is_rejected(self):
        self.segment['common_keyframes'] = [self.frames()]
        self.manifest['segments'][0]['motionIntent'] = {'visibilityMethod': 'alpha_to_scale'}
        self.reject('text.visibility_zero_scale')

    def test_declared_source_scale_is_information_without_motion_approval(self):
        self.segment['common_keyframes'] = [self.frames()]
        for method in ('segment_ranges', 'native_animation', 'native_alpha'):
            with self.subTest(method=method):
                self.manifest['segments'][0]['motionIntent'] = {'visibilityMethod': method, 'scalePurpose': 'source_animation'}
                report = self.report()
                self.assertTrue(report['passed'], report['errors'])
                self.assertEqual(report['warnings'], [])
                self.assertEqual(report['motionValidation'], 'not_performed')
                self.assertEqual(len(report['motionInfo']), 2)
                self.assertTrue(all(item['verification'] == 'source_intent_declared_only' for item in report['motionInfo']))

    def test_bad_visibility_method_takes_priority_over_source_scale_claim(self):
        self.segment['common_keyframes'] = [self.frames()]
        for method in ('alpha_to_scale', 'zero_scale', 'scale_zero'):
            with self.subTest(method=method):
                self.manifest['segments'][0]['motionIntent'] = {'visibilityMethod': method, 'scalePurpose': 'source_animation'}
                self.reject('text.visibility_zero_scale')

    def test_source_scale_without_safe_visibility_method_remains_warning(self):
        self.segment['common_keyframes'] = [self.frames()]
        self.manifest['segments'][0]['motionIntent'] = {'scalePurpose': 'source_animation'}
        report = self.report()
        self.assertEqual(report['motionValidation'], 'requires_review')
        self.assertEqual(report['motionInfo'], [])

    def test_source_scale_declaration_does_not_clear_text_alpha_warning(self):
        self.segment['common_keyframes'] = [self.frames(), self.frames('KFTypeAlpha', ((0, 0), (1000000, 1)))]
        self.manifest['segments'][0]['motionIntent'] = {'visibilityMethod': 'native_alpha', 'scalePurpose': 'source_animation'}
        report = self.report()
        self.assertTrue(report['passed'], report['errors'])
        self.assertEqual([item['code'] for item in report['warnings']], ['text.alpha_capability_unverified'])
        self.assertEqual(report['motionValidation'], 'requires_review')

    def test_declared_source_scale_alone_does_not_block_static_evidence_gate(self):
        self.segment['common_keyframes'] = [self.frames()]
        self.manifest['segments'][0]['motionIntent'] = {'visibilityMethod': 'segment_ranges', 'scalePurpose': 'source_animation'}
        self.save()
        new_hash = digest(self.root / 'draft_content.json')
        self.evidence['binding'].update(draftSha256=new_hash, manifestSha256=digest(self.root / 'manifest.json'))
        self.evidence['finalLayout']['samples'][0]['capture']['draftSha256'] = new_hash
        self.save_evidence()
        report = validate_package(self.root)
        self.assertTrue(report['deliveryReady'], report['errors'])
        self.assertEqual(report['motionValidation'], 'not_performed')
        self.assertTrue(report['motionInfo'])

    def test_nonzero_scale_animation_remains_valid(self):
        self.segment['common_keyframes'] = [self.frames(points=((0, .8), (1000000, 1.1)))]
        report = self.report()
        self.assertTrue(report['passed'], report['errors'])
        self.assertEqual(report['warnings'], [])

    def test_native_text_alpha_requires_capability_review(self):
        self.segment['common_keyframes'] = [self.frames('KFTypeAlpha', ((0, 0), (1000000, 1)))]
        report = self.report()
        self.assertTrue(report['passed'], report['errors'])
        self.assertEqual(report['warnings'][0]['code'], 'text.alpha_capability_unverified')

    def test_static_layout_evidence_cannot_claim_motion_delivery_ready(self):
        self.segment['common_keyframes'] = [self.frames()]
        self.save()
        self.evidence['binding']['draftSha256'] = digest(self.root / 'draft_content.json')
        self.evidence['finalLayout']['samples'][0]['capture']['draftSha256'] = self.evidence['binding']['draftSha256']
        self.save_evidence()
        report = validate_package(self.root)
        self.assertTrue(report['passed'], report['errors'])
        self.assertFalse(report['deliveryReady'])
        self.assertEqual(report['motionValidation'], 'requires_review')

    def test_bad_keyframe_offsets_and_duplicate_times_fail(self):
        for points, code in [(((0, 1), (1000001, 1)), 'keyframe.time'),
                             (((-1, 1), (1000000, 1)), 'keyframe.time'),
                             (((0, 1), (0, 1)), 'keyframe.time_order'),
                             (((100000, 1), (0, 1)), 'keyframe.time_order'),
                             (((0, 1), (True, 1)), 'keyframe.time'),
                             (((0, 1), (.1, 1)), 'keyframe.time')]:
            with self.subTest(points=points):
                self.segment['common_keyframes'] = [self.frames(points=points)]
                self.reject(code)

    def test_nan_infinity_and_boolean_values_fail(self):
        for value in (float('nan'), float('inf'), True, '1'):
            with self.subTest(value=value):
                self.segment['common_keyframes'] = [self.frames(points=((0, value),))]
                self.reject('keyframe.values')

    def test_global_keyframe_id_collision_fails(self):
        self.segment['common_keyframes'] = [self.frames()]
        self.segment['common_keyframes'][0]['keyframe_list'][0]['id'] = 'M1'
        self.reject('native.id_unique')

    def test_duplicate_keyframe_property_fails(self):
        first = self.frames()
        second = copy.deepcopy(first)
        second['id'] = 'KL_OTHER'
        for frame in second['keyframe_list']:
            frame['id'] += '_OTHER'
        self.segment['common_keyframes'] = [first, second]
        self.reject('keyframes.property_unique')

    def test_uniform_and_separate_scale_conflict_fails(self):
        self.segment['common_keyframes'] = [self.frames('KFTypeScaleY', ((0, 1),))]
        self.segment['uniform_scale'] = {'on': True, 'value': 1}
        self.reject('native_uniform_scale_exclusive')

    def test_api_uniform_alias_cannot_be_serialized_as_native_property(self):
        self.segment['common_keyframes'] = [self.frames('UNIFORM_SCALE', ((0, 1),))]
        self.reject('keyframes.native_property')

    def test_static_zero_scale_is_reported_even_without_a_transition(self):
        self.segment['clip'] = {'scale': {'x': 0, 'y': 0}}
        report = self.report()
        self.assertTrue(report['passed'], report['errors'])
        self.assertEqual(report['warnings'][0]['code'], 'text.static_zero_scale')

    def test_keyframe_hidden_plateau_is_not_a_visible_review_sample(self):
        self.segment['common_keyframes'] = [self.frames(points=((0, 0), (200000, 0), (1000000, 1)))]
        self.save()
        new_hash = digest(self.root / 'draft_content.json')
        self.evidence['binding']['draftSha256'] = new_hash
        self.evidence['finalLayout']['samples'][0]['capture']['draftSha256'] = new_hash
        self.save_evidence()
        report = validate_package(self.root)
        self.assertFalse(report['passed'])
        self.assertTrue(any('segmentNotHidden' in error for error in report['errors']), report['errors'])

    def test_malformed_material_collection_fails(self):
        self.draft['materials']['audios'] = {}
        self.reject('material.collection')

    def test_font_dependency_is_required_in_structure_mode(self):
        content = json.loads(self.draft['materials']['texts'][0]['content'])
        content['styles'][0].pop('font')
        self.draft['materials']['texts'][0]['content'] = json.dumps(content)
        self.reject('fonts.segmentExplicit')

    def system_font(self, family='Microsoft YaHei', dependency=True):
        material = self.draft['materials']['texts'][0]
        material.update(font_name=family, font_path='')
        content = json.loads(material['content'])
        content['styles'][0]['font'] = {'id': '', 'path': ''}
        material['content'] = json.dumps(content)
        if dependency:
            self.manifest['fontDependencies'] = [{'fontName': family, 'required': True, 'redistributed': False,
                                                  'portableFontPaths': 'empty', 'nativeFontResolution': 'not_performed'}]
        return material, content

    def test_declared_system_font_passes_structure_without_motion_warning(self):
        self.system_font()
        report = self.report()
        self.assertTrue(report['passed'], report['errors'])
        self.assertEqual(report['fontValidation'], 'system_dependency_unverified')
        self.assertEqual(report['fontWarnings'][0]['fontName'], 'Microsoft YaHei')
        self.assertEqual(report['warnings'], [])
        self.assertEqual(report['motionValidation'], 'not_performed')

    def test_system_font_without_declaration_is_rejected(self):
        self.system_font(dependency=False)
        self.reject('fonts.segmentExplicit')

    def test_mixed_packaged_and_system_fonts_are_resolved_per_style(self):
        material, content = self.system_font()
        content['styles'].append({'size': 12, 'font': {'path': 'media/font.ttf'}})
        material['content'] = json.dumps(content)
        report = self.report()
        self.assertTrue(report['passed'], report['errors'])
        self.assertEqual(report['fontValidation'], 'system_dependency_unverified')
        self.assertEqual(len(report['fontWarnings']), 1)

    def test_mixed_style_cannot_inherit_wrong_declared_family(self):
        material, content = self.system_font()
        content['styles'].append({'size': 12, 'font': {'path': '', 'family': 'Undeclared Serif'}})
        material['content'] = json.dumps(content)
        self.reject('fonts.segmentExplicit')

    def test_declared_system_font_cannot_excuse_missing_packaged_font(self):
        material, content = self.system_font()
        content['styles'][0]['font']['path'] = 'media/not-packaged.ttf'
        material['content'] = json.dumps(content)
        self.reject('.manifest')

    def test_family_system_source_declaration_is_supported(self):
        self.system_font()
        self.manifest['fontDependencies'] = [{'family': 'Microsoft YaHei', 'source': 'system'}]
        report = self.report()
        self.assertTrue(report['passed'], report['errors'])

    def test_full_native_evidence_does_not_promote_system_font_declaration(self):
        self.system_font()
        self.save()
        new_hash = digest(self.root / 'draft_content.json')
        self.evidence['binding'].update(draftSha256=new_hash, manifestSha256=digest(self.root / 'manifest.json'), fonts=[])
        self.evidence['finalLayout']['samples'][0]['capture']['draftSha256'] = new_hash
        self.save_evidence()
        report = validate_package(self.root)
        self.assertFalse(report['passed'])
        self.assertFalse(report['deliveryReady'])
        self.assertTrue(any('fonts.explicit' in error for error in report['errors']), report['errors'])

    def add_audio(self):
        path = self.root / 'media/audio.wav'
        path.write_bytes(b'synthetic metadata fixture, not real audio')
        self.manifest['media'].append({'path': 'media/audio.wav', 'bytes': path.stat().st_size, 'sha256': digest(path)})
        self.draft['materials']['audios'] = [{'id': 'AUDIO_M', 'type': 'extract_music', 'path': 'media/audio.wav', 'duration': 1000000}]
        self.draft['tracks'].append({'id': 'AUDIO_T', 'type': 'audio', 'segments': [
            {'id': 'AUDIO_S', 'material_id': 'AUDIO_M', 'volume': 1, 'speed': 1,
             'target_timerange': {'start': 0, 'duration': 1000000},
             'source_timerange': {'start': 0, 'duration': 1000000}}]})
        self.manifest['segments'].append({'id': 'AUDIO_S', 'scene': 'C1', 'owner': 'shared', 'role': 'narration', 'expectedVolume': 1})
        return self.draft['tracks'][-1]['segments'][0]

    def test_audio_source_boundary_is_checked_without_decoding_claim(self):
        audio = self.add_audio()
        report = self.report()
        self.assertTrue(report['passed'], report['errors'])
        self.assertEqual(report['audioValidation'], 'metadata_only')
        audio['source_timerange']['start'] = 500000
        self.reject('media.source_within_duration')

    def test_audio_speed_duration_mismatch_fails(self):
        audio = self.add_audio()
        audio['speed'] = 2
        self.reject('media.source_target_duration')

    def test_audio_missing_source_duration_fails(self):
        self.add_audio()
        del self.draft['materials']['audios'][0]['duration']
        self.reject('media.duration')

    def test_video_nonfinite_volume_cannot_bypass_explicit_gain(self):
        audio = self.add_audio()
        audio['volume'] = float('nan')
        self.reject('audio.volume_valid')

    def test_missing_media_path_fails(self):
        self.add_audio()
        self.draft['materials']['audios'][0].pop('path')
        self.reject('material.local_path')

    def test_native_frame_at_hidden_time_is_rejected(self):
        self.segment['clip'] = {'scale': {'x': 0, 'y': 0}}
        self.save()
        new_hash = digest(self.root / 'draft_content.json')
        self.evidence['binding']['draftSha256'] = new_hash
        self.evidence['finalLayout']['samples'][0]['capture']['draftSha256'] = new_hash
        self.save_evidence()
        report = validate_package(self.root)
        self.assertFalse(report['passed'])
        self.assertTrue(any('segmentNotHidden' in error for error in report['errors']), report['errors'])

    def test_duplicate_source_assignment_is_rejected(self):
        self.manifest['sources'] = [{'scene': 'C1', 'objects': [{'id': 'ICON', 'owner': 'shared'}]}]
        self.manifest['segments'][0].update(role='shared_graphics', sourceObjectIds=['ICON', 'ICON'])
        self.reject('segment.sourceObjectIds_unique')

    def test_id_collision_between_track_and_material_fails(self):
        self.draft['tracks'][0]['id'] = 'M1'
        self.reject('native.id_unique')


if __name__ == '__main__':
    unittest.main(verbosity=2)
