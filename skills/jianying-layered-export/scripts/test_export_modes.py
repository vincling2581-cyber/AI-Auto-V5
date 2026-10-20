"""Exercise ordinary export helpers without native review; isolated fixtures only."""
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import install_draft
import test_native_gate as fixtures
import validate_package as package_validator


class ExportModeTests(unittest.TestCase):
    setUp = fixtures.NativeGateTests.setUp
    tearDown = fixtures.NativeGateTests.tearDown
    save_evidence = fixtures.NativeGateTests.save_evidence
    args = fixtures.NativeGateTests.args
    fake_runtime = fixtures.NativeGateTests.fake_runtime

    def test_default_validation_does_not_read_native_evidence(self):
        (self.root / 'native-evidence.json').unlink()
        with patch.object(package_validator, 'validate_native_evidence') as native:
            report = package_validator.validate_package(self.root)
        native.assert_not_called()
        self.assertTrue(report['passed'], report['errors'])
        self.assertEqual(report['validationMode'], 'structure_only')
        self.assertEqual(report['nativeValidation'], 'not_performed')
        self.assertFalse(report['deliveryReady'])

    def test_evidence_path_alone_does_not_opt_into_native_review(self):
        with patch.object(package_validator, 'validate_native_evidence') as native:
            report = package_validator.validate_package(self.root, Path('missing-evidence.json'))
        native.assert_not_called()
        self.assertTrue(report['passed'], report['errors'])
        self.assertEqual(report['nativeValidation'], 'not_performed')

    def test_default_installer_registers_without_review_or_test_label(self):
        args = self.args(install=True)
        (self.root / 'native-evidence.json').unlink()
        with patch.object(install_draft, 'load_runtime', return_value=self.fake_runtime(args)), \
             patch.object(package_validator, 'validate_native_evidence') as native:
            result = install_draft.run(args)
        native.assert_not_called()
        self.assertEqual(result['name'], 'Candidate')
        self.assertEqual(result['status'], 'registered_native_review_not_performed')
        self.assertTrue(result['registered'])
        self.assertEqual(result['nativeReviewStatus'], 'not_performed')
        self.assertFalse(result['deliveryReady'])

    def test_validator_cli_requires_explicit_native_mode(self):
        (self.root / 'native-evidence.json').unlink()
        command = [sys.executable, str(Path(package_validator.__file__)), '--package', str(self.root)]
        ordinary = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(ordinary.returncode, 0, ordinary.stderr)
        self.assertEqual(json.loads(ordinary.stdout)['nativeValidation'], 'not_performed')
        reviewed = subprocess.run(command + ['--require-native-evidence'],
                                  capture_output=True, text=True, check=False)
        self.assertEqual(reviewed.returncode, 1, reviewed.stderr)
        self.assertTrue(any('native.evidence' in error for error in json.loads(reviewed.stdout)['errors']))


if __name__ == '__main__':
    unittest.main()
