"""Post-save dependency integrity behavior tests; no real editor or draft writes."""
import json
import unittest
from unittest.mock import patch
import test_native_gate as fixtures
import install_draft


class InstalledMediaTests(unittest.TestCase):
    setUp = fixtures.NativeGateTests.setUp
    tearDown = fixtures.NativeGateTests.tearDown
    save_evidence = fixtures.NativeGateTests.save_evidence
    args = fixtures.NativeGateTests.args
    fake_runtime = fixtures.NativeGateTests.fake_runtime

    def install(self, mutation=None, test=False):
        args = self.args(install=True, test=test)
        api, codec, decode = self.fake_runtime(args)
        original_load = api.DraftFolder.load_template
        def load(folder, name):
            script = original_load(folder, name)
            original_save = script.save
            def save():
                original_save()
                if mutation:
                    mutation(args.draft_root / name / 'media/font.ttf')
            script.save = save
            return script
        with patch.object(api.DraftFolder, 'load_template', load), \
             patch.object(install_draft, 'load_runtime', return_value=(api, codec, decode)):
            if mutation:
                with self.assertRaisesRegex(RuntimeError, 'Installed media changed or missing after save'):
                    install_draft.run(args)
                result = json.loads((args.audit_dir / 'installation_incomplete.json').read_text(encoding='utf-8'))
                self.assertFalse(result['deliveryReady'])
                self.assertTrue(args.draft_root.is_dir())
                self.assertEqual(result['exportStatus'], 'exported')
                self.assertTrue(result['registered'])
                self.assertEqual(result['registrationStatus'], 'registered')
            else:
                result = install_draft.run(args)
                self.assertTrue(result['deliveryReady'])
                self.assertEqual(result['installedMediaVerifiedAfterSave'], 1)
        check = json.loads((args.audit_dir / 'installed_media_verification.json').read_text(encoding='utf-8'))
        self.assertEqual(check['passed'], mutation is None)
        return check

    def test_unchanged_saved_media_is_verified(self):
        self.install()

    def test_same_length_font_change_after_save_is_rejected(self):
        self.install(lambda p: p.write_bytes(b'X' * p.stat().st_size))

    def test_truncated_font_after_save_is_rejected(self):
        self.install(lambda p: p.write_bytes(b'X'))

    def test_missing_font_after_save_is_rejected(self):
        self.install(lambda p: p.unlink())

    def test_test_only_mode_still_checks_saved_media(self):
        self.install(lambda p: p.write_bytes(b'changed'), test=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
