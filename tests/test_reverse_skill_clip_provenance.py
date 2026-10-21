"""Focused provenance regressions; all generated media lives in temporary episodes."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT / 'episodes/ECHO_逆向工程Skill_20261011/06_project'
sys.path.insert(0, str(SOURCE))
import clip_provenance as provenance


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ClipProvenanceTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='reverse-skill-provenance-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        (self.root / '07_exports').mkdir()
        for filename in ('finish.py', 'clip_provenance.py', 'cards/render_cards.py',
                         'cards/card_scene.html', 'cards/card_kit.js', 'cards/common.js',
                         'cards/scenes_early.js', 'cards/scenes_late.js'):
            dest = self.root / '06_project' / filename
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOURCE / filename, dest)
        self.real_cfg = json.loads((SOURCE.parent / '00_brief/effective_defaults.json').read_text(encoding='utf-8-sig'))
        self.cfg = copy.deepcopy(self.real_cfg)
        for name in ('ffmpeg.exe', 'chrome.exe', 'regular.ttf', 'bold.ttf'):
            self.put('tools/' + name, name.encode())
        self.cfg['tools_local']['ffmpeg'] = str(self.root / 'tools/ffmpeg.exe')
        self.cfg['type']['regular_font'] = str(self.root / 'tools/regular.ttf')
        self.cfg['type']['bold_font'] = str(self.root / 'tools/bold.ttf')
        self.data = {'revision': 'provenance_test', 'fps': 30, 'width': 1920,
                     'height': 1080, 'total_frames': 8, 'cards': []}
        for i, sid in enumerate(('C01', 'C03', 'C08', 'A01')):
            card = {'id': sid, 'type': 'animation' if sid == 'A01' else 'card',
                    'title': sid, 'start_frame': i * 2, 'end_frame_exclusive': i * 2 + 2,
                    'frame_count': 2, 'overview_frames': [0, 1], 'process_events': []}
            if sid == 'A01':
                card['art'] = 'illustrations/A01.png'
            self.data['cards'].append(card)
        self.save_json('00_brief/effective_defaults.json', self.cfg)
        self.save_json('03_storyboard/cards.json', self.data)
        self.put('04_assets/illustrations/A01.png', b'fixture illustration')
        self.put('02_research/official/reverse-skill.png', b'fixture logo')
        self.put('02_research/screenshots/github_repository.png', b'fixture screenshot')
        self.put('00_brief/input/voice_original.mp3', b'fixture voice')
        self.chrome_patch = patch.object(provenance, '_chrome_binary', return_value=self.root / 'tools/chrome.exe')
        self.chrome_patch.start()
        self.addCleanup(self.chrome_patch.stop)

    def put(self, relative, value):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value)
        return path

    def save_json(self, relative, value):
        return self.put(relative, json.dumps(value, ensure_ascii=False).encode('utf-8'))

    def stamp(self, card, suffix='original'):
        self.put('06_project/render/' + card['id'] + '.mp4', (card['id'] + suffix).encode())
        before = provenance.clip_inputs(self.root, card)
        return provenance.record_clip(self.root, card, before)

    def seed(self):
        for card in self.data['cards']:
            self.stamp(card)

    def finish(self):
        return load_module('reverse_finish_test', self.root / '06_project/finish.py')

    def assert_assemble_blocked(self):
        module = self.finish()
        self.put('06_project/render/concat.txt', b'keep concat')
        module.MASTER.parent.mkdir(parents=True, exist_ok=True)
        module.MASTER.write_bytes(b'keep master')
        with patch.object(module, 'call') as ffmpeg:
            with self.assertRaises(provenance.ProvenanceError):
                module.assemble()
            ffmpeg.assert_not_called()
        self.assertEqual(module.MASTER.read_bytes(), b'keep master')
        self.assertEqual((self.root / '06_project/render/concat.txt').read_bytes(), b'keep concat')

    def test_valid_clips_reach_assembler_and_bind_master(self):
        self.seed()
        module = self.finish()
        def encode(_):
            module.MASTER.parent.mkdir(parents=True, exist_ok=True)
            module.MASTER.write_bytes(b'new fixture master')
        with patch.object(module, 'call', side_effect=encode) as ffmpeg:
            module.assemble()
            ffmpeg.assert_called_once()
        receipt = provenance.validate_master(self.root, self.data['cards'], module.MASTER)
        self.assertEqual(len(receipt['inputs']['clips']), 4)
        # Reach the expensive QC only after its provenance gate has passed.
        with patch.object(module, 'dependencies', side_effect=RuntimeError('reached QC')) as check:
            with self.assertRaisesRegex(RuntimeError, 'reached QC'):
                module.qc()
            check.assert_called_once()

    def test_shared_source_change_and_partial_rerender_blocks_others(self):
        self.seed()
        path = self.root / '06_project/cards/common.js'
        path.write_text(path.read_text(encoding='utf-8') + '\n// changed title\n', encoding='utf-8')
        self.stamp(self.data['cards'][1], 'new C03')
        with self.assertRaisesRegex(provenance.ProvenanceError, 'C01'):
            provenance.assembly_inputs(self.root, self.data['cards'])
        self.assert_assemble_blocked()

    def test_single_card_data_change_can_reuse_other_current_clips(self):
        self.seed()
        self.data['cards'][1]['title'] = 'changed C03 only'
        self.save_json('03_storyboard/cards.json', self.data)
        with self.assertRaisesRegex(provenance.ProvenanceError, 'C03'):
            provenance.assembly_inputs(self.root, self.data['cards'])
        self.stamp(self.data['cards'][1], 'changed')
        self.assertEqual(len(provenance.assembly_inputs(self.root, self.data['cards'])['clips']), 4)

    def test_configuration_change_blocks_old_clips(self):
        self.seed()
        self.cfg['video']['crf'] += 1
        self.save_json('00_brief/effective_defaults.json', self.cfg)
        self.assert_assemble_blocked()

    def test_illustration_and_research_assets_are_bound(self):
        for relative, card in [('04_assets/illustrations/A01.png', self.data['cards'][3]),
                               ('02_research/screenshots/github_repository.png', self.data['cards'][2])]:
            with self.subTest(asset=relative):
                self.seed()
                self.put(relative, b'changed asset')
                with self.assertRaises(provenance.ProvenanceError):
                    provenance.validate_clip(self.root, card)

    def test_font_change_and_clip_replacement_are_rejected(self):
        self.seed()
        self.put('tools/bold.ttf', b'new font')
        with self.assertRaises(provenance.ProvenanceError):
            provenance.assembly_inputs(self.root, self.data['cards'])
        self.seed()
        self.put('06_project/render/C03.mp4', b'replaced video')
        self.assert_assemble_blocked()

    def test_missing_corrupt_and_wrong_clip_receipts_are_rejected(self):
        card = self.data['cards'][1]
        for mode in ('missing', 'invalid_json', 'wrong_id', 'forged_fingerprint'):
            with self.subTest(mode=mode):
                self.seed()
                path = provenance.clip_receipt_path(self.root, card)
                if mode == 'missing':
                    path.unlink()
                elif mode == 'invalid_json':
                    path.write_text('{broken', encoding='utf-8')
                else:
                    receipt = provenance.read(path)
                    receipt['card_id' if mode == 'wrong_id' else 'input_fingerprint'] = 'incorrect'
                    provenance.write(path, receipt)
                self.assert_assemble_blocked()

    def test_verify_existing_cannot_bless_missing_receipt(self):
        self.put('06_project/render/C03.mp4', b'legacy unknown video')
        module = load_module('reverse_render_test', self.root / '06_project/cards/render_cards.py')
        with patch.object(module, 'sync_playwright') as browser:
            with self.assertRaisesRegex(provenance.ProvenanceError, '缺少生成记录'):
                module.render(self.data['cards'][1], 'http://unused', False, True)
            browser.assert_not_called()
        self.assertFalse(provenance.clip_receipt_path(self.root, self.data['cards'][1]).exists())

    def assembled_fixture(self):
        self.seed()
        master = self.put('07_exports/master.mp4', b'assembled master')
        before = provenance.assembly_inputs(self.root, self.data['cards'])
        provenance.record_master(self.root, self.data['cards'], master, before)
        return master

    def test_replaced_master_and_rerendered_clip_require_new_assembly(self):
        master = self.assembled_fixture()
        master.write_bytes(b'replaced master')
        with self.assertRaises(provenance.ProvenanceError):
            provenance.validate_master(self.root, self.data['cards'], master)
        master = self.assembled_fixture()
        self.stamp(self.data['cards'][1], 'rerendered after assembly')
        with self.assertRaises(provenance.ProvenanceError):
            provenance.validate_master(self.root, self.data['cards'], master)

    def test_qc_rejects_unbound_master_before_writing_dependencies(self):
        module = self.finish()
        module.MASTER.parent.mkdir(parents=True, exist_ok=True)
        module.MASTER.write_bytes(b'legacy existing master')
        existing = self.put('08_qc/dependencies.json', b'keep old evidence')
        with patch.object(module, 'dependencies') as dependencies:
            with self.assertRaises(provenance.ProvenanceError):
                module.qc()
            dependencies.assert_not_called()
        self.assertEqual(existing.read_bytes(), b'keep old evidence')

    def test_inputs_changing_during_render_or_assembly_cannot_be_stamped(self):
        card = self.data['cards'][1]
        before = provenance.clip_inputs(self.root, card)
        self.put('06_project/render/C03.mp4', b'new output')
        self.put('06_project/cards/scenes_late.js', b'changed while rendering')
        with self.assertRaises(provenance.ProvenanceError):
            provenance.record_clip(self.root, card, before)
        self.assertFalse(provenance.clip_receipt_path(self.root, card).exists())
        self.seed()
        before = provenance.assembly_inputs(self.root, self.data['cards'])
        master = self.put('07_exports/master.mp4', b'new master')
        self.put('00_brief/input/voice_original.mp3', b'changed while assembling')
        with self.assertRaises(provenance.ProvenanceError):
            provenance.record_master(self.root, self.data['cards'], master, before)
        self.assertFalse((self.root / '08_qc/assembly_provenance.json').exists())

    def test_loaded_config_data_and_python_sources_must_still_match_disk(self):
        finish = self.finish()
        renderer = load_module('reverse_renderer_loaded_test', self.root / '06_project/cards/render_cards.py')
        self.cfg['video']['crf'] += 1
        self.save_json('00_brief/effective_defaults.json', self.cfg)
        with patch.object(finish, 'call') as encoder:
            with self.assertRaises(provenance.ProvenanceError):
                finish.assemble()
            encoder.assert_not_called()
        self.save_json('00_brief/effective_defaults.json', renderer.CFG)
        self.data['cards'][1]['title'] = 'changed after import'
        self.save_json('03_storyboard/cards.json', self.data)
        with self.assertRaises(provenance.ProvenanceError):
            renderer.render(renderer.DATA['cards'][1], 'http://unused', False)
        self.save_json('03_storyboard/cards.json', renderer.DATA)
        for module, target in [(finish, 'finish.py'), (renderer, 'cards/render_cards.py')]:
            path = self.root / '06_project' / target
            path.write_text(path.read_text(encoding='utf-8') + '\n# changed after import\n', encoding='utf-8')
            with self.assertRaisesRegex(provenance.ProvenanceError, '运行中的脚本已变更'):
                if module is finish:
                    module.assemble()
                else:
                    module.render(renderer.DATA['cards'][1], 'http://unused', False)
        helper = load_module('provenance_loaded_test', self.root / '06_project/clip_provenance.py')
        path = self.root / '06_project/clip_provenance.py'
        path.write_text(path.read_text(encoding='utf-8') + '\n# changed helper\n', encoding='utf-8')
        with self.assertRaises(helper.ProvenanceError):
            helper.clip_inputs(self.root, renderer.DATA['cards'][1])

    def test_real_renderer_samples_render_partial_and_assembly_in_temporary_episode(self):
        from PIL import Image
        self.chrome_patch.stop()
        self.save_json('00_brief/effective_defaults.json', self.real_cfg)
        self.data['cards'] = [dict(self.data['cards'][3], id='A01a', start_frame=0, end_frame_exclusive=2),
                              dict(self.data['cards'][3], id='A01c', start_frame=2, end_frame_exclusive=4)]
        self.data['total_frames'] = 4
        self.save_json('03_storyboard/cards.json', self.data)
        Image.new('RGB', (1920, 1080), '#75a194').save(self.root / '04_assets/illustrations/A01.png')
        ffmpeg = self.real_cfg['tools_local']['ffmpeg']
        subprocess.run([ffmpeg, '-y', '-v', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
                        '-t', '0.14', str(self.root / '00_brief/input/voice_original.mp3')], check=True)
        def run(entry, *args, success=True):
            command = [sys.executable, '-B', str(self.root / '06_project' / entry), *args]
            result = subprocess.run(command, cwd=self.root, capture_output=True, encoding='utf-8',
                                    errors='replace', timeout=90)
            if success:
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            else:
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            return result
        run('cards/render_cards.py', '--samples', '--workers', '1')
        self.assertFalse(list((self.root / '06_project/render').glob('*.render.json')))
        run('cards/render_cards.py', '--workers', '1')
        run('finish.py', '--assemble')
        master = self.root / '07_exports/AI逆向Skill_1080p_无口播字幕.mp4'
        old_master = master.read_bytes()
        path = self.root / '06_project/cards/common.js'
        path.write_text(path.read_text(encoding='utf-8') + '\n// changed shared source\n', encoding='utf-8')
        run('cards/render_cards.py', '--cards', 'A01a', '--workers', '1')
        rejected = run('finish.py', '--assemble', success=False)
        self.assertIn('A01c', rejected.stderr)
        self.assertEqual(master.read_bytes(), old_master)
        run('cards/render_cards.py', '--cards', 'A01c', '--workers', '1')
        run('finish.py', '--assemble')
        provenance.validate_master(self.root, self.data['cards'], master)


if __name__ == '__main__':
    unittest.main()
