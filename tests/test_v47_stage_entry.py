"""Exercise the real locked-snapshot preflight and child-process boundary."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PROJECT = Path(__file__).resolve().parents[1]
STANDARD = PROJECT / "standards/v4.7"
RUNNER = STANDARD / "production_standard/run_stage.py"
spec = importlib.util.spec_from_file_location("stage_entry", RUNNER)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class StageEntryTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.brief = self.root / "00_brief"
        shutil.copytree(STANDARD, self.brief / "standard_snapshot", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copyfile(STANDARD / "standard_lock.json", self.brief / "standard_lock.json")
        self.defaults_path = self.brief / "effective_defaults.json"
        self.defaults = json.loads((STANDARD / "production_standard/defaults.json").read_text(encoding="utf-8-sig"))
        self.write_defaults()
        (self.root / "03_storyboard").mkdir()
        (self.root / "06_project").mkdir()
        (self.root / "card.svg").write_text("<svg/>", encoding="utf-8")
        self.contract = {"schema_version": 1, "standard_version": "4.7", "scope": "sample",
                         "fps": 30, "total_frames": 240, "corner_labels": False, "opening": {},
                         "clips": [{"id": "card", "layer": "information_card", "asset_path": "card.svg",
                                    "start_frame": 0, "end_frame_exclusive": 240,
                                    "semantic_gain": "Explain the relation in readable intermediate states",
                                    "narration_anchors": [{"text": "Narration", "start_frame": 0, "end_frame_exclusive": 240}],
                                    "change_dimensions": ["relation"], "motion": "semantic_process",
                                    "transition": "hard_cut"}]}
        self.write_contract()
        self.child = self.root / "06_project/worker.py"
        self.child.write_text(
            "import json,os,sys\nfrom pathlib import Path\n"
            "keys=['V5_EPISODE_ROOT','V5_EFFECTIVE_DEFAULTS','V5_PRODUCTION_CONTRACT','V5_STAGE']\n"
            "Path('child.json').write_text(json.dumps({k:os.environ[k] for k in keys}),encoding='utf-8')\n"
            "raise SystemExit(int(sys.argv[1]) if len(sys.argv)>1 else 0)\n", encoding="utf-8")
        self.state = {"authoritative_files": {"semantic_design": "03_storyboard/semantic_design.json"},
                      "scoped_overrides": []}
        (self.brief / "episode_state.json").write_text(json.dumps(self.state), encoding="utf-8")
        design = {
            "is_template": False,
            "library": {"source_commit": "a" * 40, "catalog_sha256": "b" * 64},
            "cards": [{"card_id": "card", "clip_ids": ["card"], "relation": "A source supplies one result",
                       "motion_selection": {"queries": ["source result"], "candidates_read": ["cards/source-converge.md"],
                                            "recipe_ids": ["source-converge"], "reason": "Show source and result",
                                            "expected_process": {"initial": "Source", "transition": "Copy moves", "result": "Result"},
                                            "narration_anchors": [{"text": "Narration", "start_frame": 0, "end_frame_exclusive": 240}]},
                       "implementation": {"path": "06_project/worker.py", "symbol": "test_worker"},
                       "palette": {"theme": self.defaults["cards"]["default_theme"]},
                       "output_observations": {"status": "not_performed"}}]}
        (self.root / "03_storyboard/semantic_design.json").write_text(json.dumps(design), encoding="utf-8")

    def write_defaults(self):
        self.defaults_path.write_text(json.dumps(self.defaults), encoding="utf-8")

    def write_contract(self):
        (self.root / "03_storyboard/production_contract.json").write_text(json.dumps(self.contract), encoding="utf-8")

    def launch(self, *extra):
        return subprocess.run([sys.executable, "-X", "utf8", str(RUNNER),
                               "--episode-root", str(self.root), "--stage", "render",
                               "--entry", "06_project/worker.py", *extra],
                              capture_output=True, text=True, encoding="utf-8")

    def test_valid_inputs_launch_explicit_child_with_exact_paths(self):
        result = self.launch()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        env = json.loads((self.root / "child.json").read_text(encoding="utf-8"))
        self.assertEqual(env["V5_EFFECTIVE_DEFAULTS"], str(self.defaults_path))
        self.assertEqual(env["V5_PRODUCTION_CONTRACT"], str(self.root / "03_storyboard/production_contract.json"))
        self.assertEqual(env["V5_STAGE"], "render")

    def test_old_unlimited_illustration_default_blocks_before_child(self):
        self.defaults["animation"]["max_static_seconds"] = None
        self.write_defaults()
        result = self.launch()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("animation.max_static_seconds", result.stdout)
        self.assertFalse((self.root / "child.json").exists())

    def test_card_two_second_fallback_blocks_before_child(self):
        self.defaults["cards"]["max_static_seconds"] = 2.0
        self.write_defaults()
        self.assertNotEqual(self.launch().returncode, 0)
        self.assertFalse((self.root / "child.json").exists())

    def test_frame_rate_mismatch_blocks(self):
        self.defaults["video"]["fps"] = 60
        self.write_defaults()
        self.assertIn("video.fps", self.launch().stdout)
        self.assertFalse((self.root / "child.json").exists())

    def test_contract_failure_blocks_child(self):
        self.contract["corner_labels"] = True
        self.write_contract()
        self.assertNotEqual(self.launch().returncode, 0)
        self.assertFalse((self.root / "child.json").exists())

    def test_missing_card_design_blocks_before_child(self):
        (self.root / "03_storyboard/semantic_design.json").unlink()
        result = self.launch()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("card_design", result.stdout)
        self.assertFalse((self.root / "child.json").exists())

    def test_changed_locked_file_blocks_before_importing_child(self):
        target = self.brief / "standard_snapshot/production_standard/defaults.json"
        target.write_text("{}", encoding="utf-8")
        self.assertNotEqual(self.launch().returncode, 0)
        self.assertFalse((self.root / "child.json").exists())

    def test_unlisted_verifier_is_not_executed(self):
        snapshot = self.brief / "standard_snapshot"
        rogue = snapshot / "rogue.py"
        marker = self.root / "unlocked_module_ran"
        rogue.write_text(f"from pathlib import Path\nPath({str(marker)!r}).touch()\n", encoding="utf-8")
        manifest = json.loads((snapshot / "production_standard.json").read_text(encoding="utf-8-sig"))
        manifest["verifier"] = "rogue.py"
        for path in (snapshot / "production_standard.json", snapshot / "standard_lock.json",
                     self.brief / "standard_lock.json"):
            path.write_text(json.dumps(manifest), encoding="utf-8")
        result = self.launch()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("locked dependencies", result.stdout)
        self.assertFalse(marker.exists())
        self.assertFalse((self.root / "child.json").exists())

    def test_preflight_does_not_write_snapshot_cache(self):
        result = self.launch("--check-only")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(list((self.brief / "standard_snapshot").rglob("__pycache__")), [])

    def test_legacy_episode_is_not_silently_migrated(self):
        manifest = self.brief / "standard_snapshot/production_standard.json"
        data = json.loads(manifest.read_text(encoding="utf-8-sig"))
        data["version"] = "4.6"
        manifest.write_text(json.dumps(data), encoding="utf-8")
        self.assertIn("legacy", self.launch().stdout)
        self.assertFalse((self.root / "child.json").exists())

    def test_check_only_never_starts_child(self):
        result = self.launch("--check-only")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((self.root / "child.json").exists())

    def test_child_exit_code_is_not_hidden(self):
        self.assertEqual(self.launch("--", "7").returncode, 7)

    def test_entry_cannot_leave_episode(self):
        report = runner.preflight(self.root, "../outside.py")
        self.assertFalse(report["passed"])
        self.assertIn("leaves", report["errors"][0])

    def test_export_entry_uses_same_preflight_without_native_review(self):
        result = subprocess.run([sys.executable, "-X", "utf8", str(RUNNER),
                                 "--episode-root", str(self.root), "--stage", "export",
                                 "--entry", "06_project/worker.py"],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads((self.root / "child.json").read_text())["V5_STAGE"], "export")


if __name__ == "__main__":
    unittest.main()
