"""Behavior tests for opacity planning; these are not native-editor evidence."""
import copy
import unittest

from text_motion import frame_us, plan_text_visibility


def source(start, alphas, scales=None):
    return [{"frame": start+i, "x": 200+i, "y": 150, "alpha": alpha,
             "scaleX": scales[i] if scales else 1, "scaleY": scales[i] if scales else 1}
            for i, alpha in enumerate(alphas)]


class TextVisibilityTests(unittest.TestCase):
    def test_opening_fade_does_not_become_zero_scale_pop(self):
        rows = source(126, [0, 0, 0, .0681575, .272882, .445185, 1])
        before = copy.deepcopy(rows)
        plan = plan_text_visibility(rows, fps=30, text_key="credit")
        self.assertEqual(plan["opacityActiveSpans"], [[129, 133]])
        seg = plan["segments"][0]
        self.assertEqual(seg["startUs"], 4_300_000)
        self.assertTrue(all(s["scaleX"] == s["scaleY"] == 1 for s in seg["transformSamples"]))
        self.assertNotIn("nativeAlphaSamples", seg)
        self.assertEqual(plan["status"], "needs_mapping")
        self.assertEqual(rows, before)

    def test_fade_out_keeps_geometry_and_trims_only_invisible_tail(self):
        p = plan_text_visibility(source(122, [.00385975, .000203542, 0, 0]), fps=30, text_key="hook")
        self.assertEqual(p["opacityActiveSpans"], [[122, 124]])
        self.assertEqual(p["segments"][0]["transformSamples"][-1]["scaleX"], 1)

    def test_reappearance_uses_ranges_and_records_edit_mapping(self):
        p = plan_text_visibility(source(60, [1, 1, 0, 0, 1, 1]), fps=30, text_key="again")
        self.assertEqual(p["opacityActiveSpans"], [[60, 62], [64, 66]])
        self.assertEqual(len(p["segments"]), 2)
        self.assertEqual({s["textKey"] for s in p["segments"]}, {"again"})
        self.assertEqual([s["transformSamples"][0]["offsetUs"] for s in p["segments"]], [0, 0])
        self.assertEqual(p["requirements"][0]["code"], "reappearance_edit_mapping_required")

    def test_verified_alpha_can_keep_one_continuous_segment_without_scale_hiding(self):
        p = plan_text_visibility(source(0, [0, .3, 1, 0, 1, 0]), fps=30, text_key="verified", alpha_keyframes_verified=True)
        self.assertEqual(len(p["segments"]), 1)
        s = p["segments"][0]
        self.assertEqual((s["startFrame"], s["endFrameExclusive"]), (1, 5))
        self.assertEqual([x["value"] for x in s["nativeAlphaSamples"]], [.3, 1, 0, 1])
        self.assertTrue(all(x["scaleX"] == 1 for x in s["transformSamples"]))

    def test_source_scale_animation_is_preserved(self):
        p = plan_text_visibility(source(0, [1, 1, 1], [0, .5, 1]), fps=30, text_key="intentional")
        self.assertEqual([x["scaleX"] for x in p["segments"][0]["transformSamples"]], [0, .5, 1])
        self.assertEqual(p["status"], "ready")

    def test_round_absolute_frame_boundaries(self):
        p = plan_text_visibility(source(129, [1]*5), fps=30, text_key="time")
        s = p["segments"][0]
        self.assertEqual(s["durationUs"], frame_us(134, 30)-frame_us(129, 30))
        self.assertEqual(s["transformSamples"][-1]["offsetUs"], frame_us(133, 30)-frame_us(129, 30))

    def test_all_hidden_has_no_native_segment(self):
        p = plan_text_visibility(source(0, [0, 0]), fps=30, text_key="hidden")
        self.assertEqual(p["status"], "not_visible")
        self.assertEqual(p["segments"], [])

    def test_invalid_samples_are_not_silently_treated_as_hidden(self):
        cases = [source(0, [1, float("nan")]), source(0, [1, 1.01]),
                 [source(0, [1])[0], source(2, [1])[0]],
                 [source(0, [1])[0], source(0, [1])[0]],
                 [{"frame": 0, "x": float("inf"), "y": 1}]]
        for rows in cases:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                plan_text_visibility(rows, fps=30, text_key="bad")


if __name__ == "__main__":
    unittest.main()
