"""Boundary tests for metadata/hash checks, not raster or subjective video QA."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

PROJECT = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT / 'standards/v4.7/production_standard/validate_episode.py'
spec = importlib.util.spec_from_file_location('v47_contract_validator', MODULE_PATH)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class ProductionContractTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / '03_storyboard').mkdir()
        (self.root / 'assets').mkdir()
        # Deliberately simple bytes: this tool checks identity, not image decoding.
        for name, payload in [('a.png', b'asset-a'), ('b.png', b'asset-b'), ('c.png', b'asset-c'), ('alias.png', b'asset-a'), ('card.svg', b'<svg/>')]:
            (self.root / 'assets' / name).write_bytes(payload)

    def clip(self, cid='a', start=0, end=60, asset='a.png', layer='illustration'):
        return {'id': cid, 'layer': layer, 'asset_path': 'assets/' + asset,
                'start_frame': start, 'end_frame_exclusive': end,
                'semantic_gain': 'Establish a question, then show a relevant response.',
                'narration_anchors': [{'text': 'Locked narration', 'start_frame': start, 'end_frame_exclusive': end}],
                'change_dimensions': ['establishing'],
                'scene_id': 'interview', 'scene_progress': 'Question is followed by a concrete response.',
                'motion': 'none' if layer == 'illustration' else 'semantic_process',
                'transition': 'hard_cut'}

    def contract(self, clips=None, scope='sample', fps=30):
        clips = clips if clips is not None else [self.clip()]
        return {'schema_version': 1, 'standard_version': '4.7', 'scope': scope,
                'fps': fps, 'total_frames': clips[-1]['end_frame_exclusive'],
                'corner_labels': False, 'opening': {}, 'clips': clips}

    def run_check(self, data):
        path = self.root / '03_storyboard/production_contract.json'
        path.write_text(json.dumps(data), encoding='utf-8')
        return validator.validate(self.root)

    def test_exactly_two_seconds_passes(self):
        self.assertTrue(self.run_check(self.contract())['passed'])

    def test_one_frame_over_two_seconds_fails(self):
        self.assertFalse(self.run_check(self.contract([self.clip(end=61)]))['passed'])

    def test_shorter_unequal_holds_pass(self):
        self.assertTrue(self.run_check(self.contract([
            self.clip(end=43), self.clip('b', 43, 98, 'b.png')]))['passed'])

    def test_information_card_not_capped_at_two_seconds(self):
        self.assertTrue(self.run_check(self.contract([
            self.clip(end=240, asset='card.svg', layer='information_card')]))['passed'])

    def test_card_entry_cannot_animate_over_previous_illustration(self):
        card = self.clip('card', 60, 240, 'card.svg', 'information_card')
        card['transition'] = 'card_entry'
        self.assertFalse(self.run_check(self.contract([self.clip(), card]))['passed'])

    def test_card_to_card_transition_can_use_semantic_entry(self):
        first = self.clip('card1', 0, 120, 'card.svg', 'information_card')
        second = self.clip('card2', 120, 240, 'card.svg', 'information_card')
        second['transition'] = 'semantic_transition'
        self.assertTrue(self.run_check(self.contract([first, second]))['passed'])

    def test_same_asset_split_does_not_reset_cap(self):
        self.assertFalse(self.run_check(self.contract([
            self.clip(end=45), self.clip('a2', 45, 90)]))['passed'])

    def test_renamed_identical_asset_does_not_reset_cap(self):
        self.assertFalse(self.run_check(self.contract([
            self.clip(end=45), self.clip('a2', 45, 90, 'alias.png')]))['passed'])

    def test_returning_to_same_narrative_image_fails(self):
        self.assertFalse(self.run_check(self.contract([
            self.clip(end=30), self.clip('b', 30, 60, 'b.png'), self.clip('a2', 60, 90)]))['passed'])

    def test_global_corner_label_fails(self):
        data = self.contract(); data['corner_labels'] = True
        self.assertFalse(self.run_check(data)['passed'])

    def test_clip_corner_label_fails(self):
        data = self.contract(); data['clips'][0]['corner_labels'] = True
        self.assertFalse(self.run_check(data)['passed'])

    def test_zoom_motion_fails(self):
        data = self.contract(); data['clips'][0]['motion'] = 'zoom'
        self.assertFalse(self.run_check(data)['passed'])

    def test_illustration_fade_fails(self):
        data = self.contract(); data['clips'][0]['transition'] = 'fade'
        self.assertFalse(self.run_check(data)['passed'])

    def test_asset_path_escape_fails(self):
        data = self.contract(); data['clips'][0]['asset_path'] = '../../other_episode/a.png'
        self.assertFalse(self.run_check(data)['passed'])

    def test_missing_semantic_plan_fails(self):
        data = self.contract(); data['clips'][0]['semantic_gain'] = ''
        self.assertFalse(self.run_check(data)['passed'])

    def test_opening_required_for_full_episode(self):
        data = self.contract(scope='episode')
        self.assertFalse(self.run_check(data)['passed'])
        data['opening'] = {'viewer_question': 'Which direction?', 'visual_payoff': 'A relevant choice.',
                           'narration_anchor': 'Original sentence.', 'entry_clip_id': 'a'}
        self.assertTrue(self.run_check(data)['passed'])

    def test_gap_fails(self):
        self.assertFalse(self.run_check(self.contract([
            self.clip(end=30), self.clip('b', 31, 60, 'b.png')]))['passed'])

    def test_fractional_fps_obeys_actual_two_second_boundary(self):
        self.assertFalse(self.run_check(self.contract(fps='30000/1001'))['passed'])

    def test_horizontal_caption_motion_fails(self):
        data = self.contract()
        data['subtitles'] = dict(validator.read_json(validator.SPEC_PATH)['subtitles'], enabled=True)
        data['subtitles']['motion'] = 'slide_right'
        self.assertFalse(self.run_check(data)['passed'])

    def test_template_does_not_pass_as_completed_contract(self):
        data = self.contract(); data['is_template'] = True
        self.assertFalse(self.run_check(data)['passed'])

    def test_invalid_layer_type_returns_errors(self):
        data = self.contract(); data['clips'][0]['layer'] = []
        self.assertFalse(self.run_check(data)['passed'])

    def test_missing_scene_progress_fails(self):
        data = self.contract(); del data['clips'][0]['scene_progress']
        self.assertFalse(self.run_check(data)['passed'])

    def test_scene_change_requires_reason_even_across_card(self):
        second = self.clip('b', 120, 180, 'b.png'); second['scene_id'] = 'real_task'
        data = self.contract([self.clip(), self.clip('card', 60, 120, 'card.svg', 'information_card'), second])
        self.assertFalse(self.run_check(data)['passed'])
        second['scene_change_reason'] = 'Show the real consequence of the answer.'
        self.assertTrue(self.run_check(data)['passed'])

    def test_same_scene_can_progress_without_group_duration_quota(self):
        data = self.contract([self.clip(), self.clip('b', 60, 120, 'b.png'), self.clip('c', 120, 180, 'c.png')])
        report = self.run_check(data)
        self.assertTrue(report['passed'])
        self.assertEqual(report['contiguous_illustration_scene_groups'][0]['duration_seconds'], 6.0)
        self.assertEqual(len(report['contiguous_illustration_scene_groups']), 1)

    def test_returning_scene_allowed_with_new_image_and_reason(self):
        second = self.clip('b', 60, 120, 'b.png')
        second.update(scene_id='real_task', scene_change_reason='Show a concrete blocked task.')
        third = self.clip('c', 120, 180, 'c.png')
        third['scene_change_reason'] = 'Return to the interview with concrete notes.'
        report = self.run_check(self.contract([self.clip(), second, third]))
        self.assertTrue(report['passed'])
        self.assertEqual([g['scene_id'] for g in report['contiguous_illustration_scene_groups']],
                         ['interview', 'real_task', 'interview'])


if __name__ == '__main__':
    unittest.main()
