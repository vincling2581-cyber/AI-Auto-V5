"""Calibration coverage behavior tests; synthetic fixtures are never native evidence."""
import copy
import json
import unittest

import test_native_gate as fixtures
from native_evidence import digest
from validate_package import validate_package


class StyleCoverageTests(unittest.TestCase):
    setUp = fixtures.NativeGateTests.setUp
    tearDown = fixtures.NativeGateTests.tearDown
    save_evidence = fixtures.NativeGateTests.save_evidence
    assert_rejected = fixtures.NativeGateTests.assert_rejected

    @staticmethod
    def style(size=12, **flags):
        return {'size': size, 'font': {'path': 'media/font.ttf'}, **flags}

    def set_final(self, styles):
        self.draft['materials']['texts'][0]['content'] = json.dumps({'text': 'test', 'styles': styles})
        fixtures.write_json(self.root / 'draft_content.json', self.draft)
        current_hash = digest(self.root / 'draft_content.json')
        self.evidence['binding']['draftSha256'] = current_hash
        for sample in self.evidence['finalLayout']['samples']:
            sample['capture']['draftSha256'] = current_hash
        self.save_evidence()

    def set_calibration(self, styles, declarations):
        calibration = copy.deepcopy(self.draft)
        calibration['materials']['texts'][0]['content'] = json.dumps({'text': 'test', 'styles': styles})
        path = self.root / 'evidence/calibration.json'
        fixtures.write_json(path, calibration)
        current_hash = digest(path)
        self.evidence['calibration']['draft']['sha256'] = current_hash
        template = self.evidence['calibration']['samples'][0]
        samples = []
        for declaration in declarations:
            sample = copy.deepcopy(template)
            sample.pop('nativeStyle', None)
            sample.update(declaration)
            sample['capture']['draftSha256'] = current_hash
            samples.append(sample)
        self.evidence['calibration']['samples'] = samples
        self.save_evidence()

    def assert_ready(self):
        report = validate_package(self.root, require_native_evidence=True)
        self.assertTrue(report['deliveryReady'], report['errors'])
        self.assertTrue(report['passed'], report['errors'])
        return report

    def test_legacy_regular_sample_still_passes(self):
        self.assert_ready()

    def test_unmeasured_final_size_is_rejected(self):
        self.set_final([self.style(72)])
        self.assert_rejected('calibration.sizeCoverage')

    def test_regular_cannot_cover_bold_italic_or_underline(self):
        for flag in ('bold', 'italic', 'underline'):
            with self.subTest(flag=flag):
                self.set_final([self.style(**{flag: True})])
                self.assert_rejected('calibration.styleCoverage')

    def test_explicit_matching_flags_pass(self):
        for flags in ({'bold': True}, {'italic': True}, {'underline': True},
                      {'bold': True, 'italic': True, 'underline': True}):
            with self.subTest(flags=flags):
                self.set_final([self.style(**flags)])
                self.set_calibration([self.style(**flags)], [{'nativeStyle': flags}])
                self.assert_ready()

    def test_claimed_bold_must_exist_in_active_calibration(self):
        self.set_final([self.style(bold=True)])
        self.set_calibration([self.style()], [{'nativeStyle': {'bold': True}}])
        self.assert_rejected('calibrationDraftStyles')

    def test_implicit_regular_does_not_collect_other_styles_in_frame(self):
        self.set_final([self.style(bold=True)])
        self.set_calibration([self.style(), self.style(bold=True)], [{}])
        self.assert_rejected('calibration.styleCoverage')

    def test_explicit_regular_does_not_collect_other_styles_in_frame(self):
        self.set_final([self.style(bold=True)])
        self.set_calibration([self.style(), self.style(bold=True)], [{'nativeStyle': {'bold': False}}])
        self.assert_rejected('calibration.styleCoverage')

    def test_explicit_bold_does_not_collect_regular_in_frame(self):
        self.set_final([self.style()])
        self.set_calibration([self.style(), self.style(bold=True)], [{'nativeStyle': {'bold': True}}])
        self.assert_rejected('calibration.styleCoverage')

    def test_range_covers_endpoints_and_intermediate_sizes(self):
        self.set_calibration([self.style(12), self.style(72)],
                             [{'nativeFontSize': 12}, {'nativeFontSize': 72}])
        for size in (12, 40, 72, 12 - 0.5e-6, 72 + 0.5e-6):
            with self.subTest(size=size):
                self.set_final([self.style(size)])
                self.assert_ready()

    def test_size_outside_measured_range_is_rejected(self):
        self.set_calibration([self.style(12), self.style(72)],
                             [{'nativeFontSize': 12}, {'nativeFontSize': 72}])
        for size in (10, 80, 12 - 2e-6, 72 + 2e-6):
            with self.subTest(size=size):
                self.set_final([self.style(size)])
                self.assert_rejected('calibration.sizeCoverage')

    def test_only_declared_sizes_extend_the_range(self):
        self.set_final([self.style(72)])
        self.set_calibration([self.style(12), self.style(72)], [{'nativeFontSize': 12}])
        self.assert_rejected('calibration.sizeCoverage')

    def test_size_range_is_separate_for_each_weight(self):
        self.set_final([self.style(72, bold=True)])
        self.set_calibration([self.style(12), self.style(72), self.style(12, bold=True)],
                             [{'nativeFontSize': 12}, {'nativeFontSize': 72},
                              {'nativeFontSize': 12, 'nativeStyle': {'bold': True}}])
        self.assert_rejected('calibration.sizeCoverage')

    def test_every_final_mixed_style_must_be_covered(self):
        self.set_final([self.style(), self.style(72, bold=True)])
        self.set_calibration([self.style(), self.style(72, bold=True)],
                             [{'nativeFontSize': 12}, {'nativeFontSize': 72, 'nativeStyle': {'bold': True}}])
        self.assert_ready()

    def test_typo_in_style_declaration_does_not_silently_mean_regular(self):
        self.set_calibration([self.style()], [{'nativeStyle': {'b0ld': True}}])
        self.assert_rejected('nativeStyle.fields')

    def test_hidden_calibration_text_does_not_count_as_font_coverage(self):
        path = self.root / 'evidence/calibration.json'
        calibration = json.loads(path.read_text(encoding='utf-8'))
        calibration['tracks'][0]['segments'][0]['clip'] = {'scale': {'x': 0, 'y': 0}}
        fixtures.write_json(path, calibration)
        new_hash = digest(path)
        self.evidence['calibration']['draft']['sha256'] = new_hash
        self.evidence['calibration']['samples'][0]['capture']['draftSha256'] = new_hash
        self.save_evidence()
        self.assert_rejected('calibrationDraftStyles')


if __name__ == '__main__':
    unittest.main(verbosity=2)
