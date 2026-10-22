"""Card-design gate tests: metadata only, no renderer or standard-lock rewrite."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

PROJECT = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT / "standards/v4.7/production_standard/validate_card_design.py"
spec = importlib.util.spec_from_file_location("v47_card_design_validator", MODULE_PATH)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class CardDesignTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        for relative in ("00_brief", "03_storyboard", "06_project"):
            (self.root / relative).mkdir()
        (self.root / "06_project/cards.js").write_text("function renderCard() {}", encoding="utf-8")
        self.contract = {"clips": [{"id": "clip-a", "layer": "information_card"}]}
        dark = {"background": "#07110C", "accent": "#78EFA2", "paper": "#F0F3EC", "text": "#F0F3EC"}
        paper = {"background": "#F5F2E9", "accent": "#78EFA2", "paper": "#F0F3EC", "text": "#24362B"}
        self.defaults = {"cards": {"default_theme": "dark", "palette": copy.deepcopy(dark),
                                   "palette_presets": {"dark": dark, "paper": paper}}}
        self.locked = copy.deepcopy(self.defaults)
        self.state = {"authoritative_files": {"semantic_design": "03_storyboard/semantic_design.json"},
                      "scoped_overrides": []}
        self.design = {
            "is_template": False,
            "library": {"source_commit": "a" * 40, "catalog_sha256": "b" * 64},
            "cards": [{
                "card_id": "card-a", "clip_ids": ["clip-a"], "relation": "Sources converge on one result",
                "motion_selection": {
                    "queries": ["converge"], "candidates_read": ["research/video-talkcraft/cards/source-converge.md"],
                    "recipe_ids": ["source-converge"], "reason": "Show the stated many-to-one relation",
                    "custom_reason": None,
                    "expected_process": {"initial": "Sources stay visible", "transition": "Copies follow paths",
                                         "result": "The receiver holds the accumulated result"},
                    "narration_anchors": [{"text": "Gather these sources", "start_frame": 0, "end_frame_exclusive": 60}],
                },
                "implementation": {"path": "06_project/cards.js", "symbol": "renderCard"},
                "palette": {"theme": "dark"},
                "output_observations": {"status": "not_performed", "evidence": []},
            }],
        }

    def write(self, relative, data):
        (self.root / relative).write_text(json.dumps(data), encoding="utf-8")

    def check_design(self):
        self.write("03_storyboard/production_contract.json", self.contract)
        self.write("00_brief/episode_state.json", self.state)
        self.write("00_brief/effective_defaults.json", self.defaults)
        self.write("00_brief/locked_defaults.json", self.locked)
        self.write("03_storyboard/semantic_design.json", self.design)
        return validator.validate(self.root, locked_defaults_path=self.root / "00_brief/locked_defaults.json")

    def assert_fails(self, fragment):
        report = self.check_design()
        self.assertFalse(report["passed"], report)
        self.assertIn(fragment, "\n".join(report["errors"]))

    def override(self):
        self.state["scoped_overrides"] = [{"scope": "information_cards", "field": "cards.palette",
                                           "reason": "The episode requires a light diagram surface",
                                           "user_basis": "User explicitly requested this episode in light colors"}]

    def paper_theme(self):
        self.defaults["cards"]["default_theme"] = "paper"
        self.defaults["cards"]["palette"] = copy.deepcopy(self.defaults["cards"]["palette_presets"]["paper"])
        self.design["cards"][0]["palette"]["theme"] = "paper"

    def test_unrendered_observations_are_allowed_and_not_certified(self):
        report = self.check_design()
        self.assertTrue(report["passed"], report)
        self.assertEqual(report["count"], 1)
        self.assertEqual(report["pixel_and_semantic_review"], "not_performed")
        self.assertEqual(report["actual_renderer_parameter_consumption"], "not_proven")

    def test_missing_design_pointer_fails(self):
        self.state["authoritative_files"]["semantic_design"] = None
        self.assert_fails("file path")

    def test_missing_card_fails(self):
        self.design["cards"] = []
        self.assert_fails("covered exactly once; found 0")

    def test_duplicate_card_and_clip_coverage_fail(self):
        self.design["cards"].append(copy.deepcopy(self.design["cards"][0]))
        self.assert_fails("Duplicate card_id")
        self.assert_fails("covered exactly once; found 2")

    def test_uncovered_and_unknown_clips_fail(self):
        self.design["cards"][0]["clip_ids"] = ["wrong-clip"]
        self.assert_fails("covered exactly once; found 0")
        self.assert_fails("unknown clip")

    def test_one_card_may_cover_multiple_contract_fragments_without_quota(self):
        self.contract["clips"].append({"id": "clip-b", "layer": "information_card"})
        self.design["cards"][0]["clip_ids"].append("clip-b")
        self.assertTrue(self.check_design()["passed"])

    def test_missing_query_or_candidate_record_fails(self):
        for field in ("queries", "candidates_read"):
            with self.subTest(field=field):
                saved = self.design["cards"][0]["motion_selection"][field]
                self.design["cards"][0]["motion_selection"][field] = []
                self.assert_fails(field)
                self.design["cards"][0]["motion_selection"][field] = saved

    def test_custom_process_requires_reason(self):
        self.design["cards"][0]["motion_selection"]["recipe_ids"] = []
        self.assert_fails("custom_reason")

    def test_reasoned_custom_static_card_is_allowed(self):
        self.contract["clips"][0].update(motion="none", static_card_purpose="Hold the single conclusion for reading")
        selection = self.design["cards"][0]["motion_selection"]
        selection["recipe_ids"] = []
        selection["custom_reason"] = "A single conclusion has no changing relationship to explain"
        selection["expected_process"] = {"initial": "Conclusion visible", "transition": "Keep the conclusion still for reading",
                                         "result": "The same readable conclusion"}
        self.assertTrue(self.check_design()["passed"])

    def test_missing_process_state_or_anchor_fails(self):
        del self.design["cards"][0]["motion_selection"]["expected_process"]["transition"]
        self.design["cards"][0]["motion_selection"]["narration_anchors"] = [{}]
        self.assert_fails("expected_process.transition")
        self.assert_fails("narration_anchors")

    def test_missing_source_or_symbol_fails(self):
        self.design["cards"][0]["implementation"] = {"path": "06_project/missing.js", "symbol": ""}
        self.assert_fails("source does not exist")
        self.assert_fails("implementation.symbol")

    def test_source_cannot_escape_episode(self):
        self.design["cards"][0]["implementation"]["path"] = "../outside.js"
        self.assert_fails("leaves episode root")

    def test_design_pointer_cannot_escape_episode(self):
        self.state["authoritative_files"]["semantic_design"] = "../outside.json"
        self.assert_fails("leaves episode root")

    def test_palette_drift_without_override_fails(self):
        self.paper_theme()
        self.assert_fails("differs from locked defaults")

    def test_same_theme_color_drift_still_requires_override(self):
        self.defaults["cards"]["palette"]["background"] = "#001100"
        self.defaults["cards"]["palette_presets"]["dark"]["background"] = "#001100"
        self.assert_fails("differs from locked defaults")

    def test_explicit_episode_palette_override_passes_as_declaration_only(self):
        self.paper_theme()
        self.override()
        report = self.check_design()
        self.assertTrue(report["passed"], report)
        self.assertTrue(report["palette_override_declared"])
        self.assertEqual(report["override_authorization"], "declaration_only_not_independently_verified")

    def test_incomplete_override_does_not_authorize_drift(self):
        self.paper_theme()
        self.override()
        self.state["scoped_overrides"][0]["user_basis"] = " "
        self.assert_fails("differs from locked defaults")

    def test_override_does_not_allow_per_card_theme_rotation(self):
        self.override()
        self.design["cards"][0]["palette"]["theme"] = "paper"
        self.assert_fails("must match the episode default_theme")

    def test_override_never_allows_palette_preset_mismatch(self):
        self.override()
        self.defaults["cards"]["palette"]["background"] = "#112233"
        self.assert_fails("must equal cards.palette_presets")

    def test_unfilled_template_is_rejected(self):
        self.design["is_template"] = True
        self.assert_fails("is_template=false")

    def test_missing_library_provenance_fails(self):
        self.design["library"]["catalog_sha256"] = None
        self.assert_fails("catalog_sha256")

    def test_no_information_cards_need_no_design_or_palette_check(self):
        self.write("03_storyboard/production_contract.json", {"clips": [{"id": "illustration-a", "layer": "illustration"}]})
        report = validator.validate(self.root)
        self.assertTrue(report["passed"], report)
        self.assertEqual(report["status"], "not_applicable")
        self.assertEqual(report["count"], 0)


if __name__ == "__main__":
    unittest.main()
