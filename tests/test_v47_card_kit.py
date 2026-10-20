"""Run the v4.7 SVG helpers; these checks do not imply visual or video acceptance."""
import copy
import json
from pathlib import Path
import subprocess
import unittest
import xml.etree.ElementTree as ET


PROJECT = Path(__file__).resolve().parents[1]
STANDARD = PROJECT / "standards/v4.7/production_standard"
KIT = STANDARD / "method_assets/reference_cards_v1/card_kit.js"
FLUBBER = KIT.parent / "vendor/flubber.min.js"
DEFAULTS = json.loads((STANDARD / "defaults.json").read_text(encoding="utf-8"))


class CardKitTest(unittest.TestCase):
    def setUp(self):
        self.effective = copy.deepcopy(DEFAULTS)

    def render(self, expression):
        script = """
const fs = require('node:fs');
const vm = require('node:vm');
const {effective, expression, kitPath, flubberPath} = JSON.parse(fs.readFileSync(0, 'utf8'));
const context = vm.createContext({effective});
vm.runInContext(fs.readFileSync(flubberPath, 'utf8'), context);
vm.runInContext(fs.readFileSync(kitPath, 'utf8'), context);
vm.runInContext('globalThis.K = createReferenceCardKit(effective)', context);
process.stdout.write(JSON.stringify(vm.runInContext(expression, context)));
"""
        result = subprocess.run(
            ["node", "-e", script],
            input=json.dumps({
                "effective": self.effective,
                "expression": expression,
                "kitPath": str(KIT),
                "flubberPath": str(FLUBBER),
            }),
            capture_output=True, text=True, encoding="utf-8", check=True,
        )
        return json.loads(result.stdout)

    @staticmethod
    def svg(fragment):
        return ET.fromstring("<svg>" + fragment + "</svg>")

    def test_panel_variants_follow_the_scene_palette(self):
        palette = self.effective["cards"]["palette"]
        palette.update({
            "dark": "#123456", "edge": "#ABCDEF",
            "soft": "#456789", "line": "#FEDCBA",
        })
        fragments = self.render(
            "['dark','soft','paper','accent','outline'].map(tone=>K.panel(0,0,300,200,tone))"
        )
        roles = [("dark", "edge"), ("soft", "edge"), ("paper", None),
                 ("accent", "accent"), ("soft", "line")]
        for fragment, (fill, stroke) in zip(fragments, roles):
            rect = self.svg(fragment)[0]
            self.assertEqual(rect.get("fill"), palette[fill])
            self.assertEqual(rect.get("stroke"), palette[stroke] if stroke else "none")

    def test_geometry_reaches_panels_connections_and_both_icon_helpers(self):
        self.effective["cards"]["geometry"].update({
            "panel_border_px": 7, "panel_radius_px": 13,
            "connection_stroke_px": 5, "icon_stroke_local_px": 9,
        })
        fragments = self.render("""({
panel:K.panel(0,0,300,200),
square:K.box(0,0,300,200,'paper','line',0),
connection:K.path('M0 0L100 100'),
icon:K.icon('folder',0,0,200),
folder:K.folder(0,0,200,.5)
})""")
        panel = self.svg(fragments["panel"])[0]
        self.assertEqual(panel.get("stroke-width"), "7")
        self.assertEqual(panel.get("rx"), "13")
        self.assertEqual(self.svg(fragments["square"])[0].get("rx"), "0")
        self.assertEqual(self.svg(fragments["connection"])[1].get("stroke-width"), "5")
        self.assertEqual(self.svg(fragments["icon"])[0].get("stroke-width"), "9")
        self.assertEqual(self.svg(fragments["icon"])[0].get("transform"),
                         "translate(0,0) scale(2)")
        for path in self.svg(fragments["folder"])[0]:
            self.assertEqual(path.get("stroke-width"), "9")

    def test_font_family_quotes_and_text_survive_svg_serialization(self):
        self.effective["type"]["family"] = '"Example & Serif", sans-serif'
        fragment = self.render("""K.text('A < B & "quoted"',12,34)""")
        text = self.svg(fragment)[0]
        self.assertEqual(text.get("font-family"), self.effective["type"]["family"])
        self.assertEqual(text.text, 'A < B & "quoted"')

    def test_node_default_and_explicit_typography_sizes(self):
        self.effective["cards"]["typography"].update({
            "node_px": 41, "title_px": 65, "support_px": 29,
        })
        fragments = self.render("""[
K.text('Node',0,0),
K.text('Title',0,0,effective.cards.typography.title_px),
K.text('Support',0,0,effective.cards.typography.support_px)
]""")
        self.assertEqual(
            [self.svg(fragment)[0].get("font-size") for fragment in fragments],
            ["41", "65", "29"],
        )

    def test_morph_intermediate_frames_use_the_scene_ink(self):
        self.effective["cards"]["palette"]["ink"] = "#123456"
        fragments = self.render("""[.2,.5,.8].map(t=>K.morph(
'doc','folder',t,0,1,[0,0,100,100],[300,200,120,120]))""")
        outlines = []
        for fragment in fragments:
            group = self.svg(fragment)[0]
            self.assertEqual(group[1].get("stroke"), "#123456")
            self.assertNotIn("NaN", fragment)
            outlines.append(group[0].get("d"))
        self.assertEqual(len(set(outlines)), 3)
        dark = self.render("""K.morph('doc','folder',.5,0,1,
[0,0,100,100],[300,200,120,120],'dark','dark','accent',65,true,'paper')""")
        self.assertEqual(self.svg(dark)[0][1].get("stroke"),
                         self.effective["cards"]["palette"]["paper"])

    def test_local_motion_duration_and_easing_are_consumed(self):
        self.effective["cards"]["process_initial_seconds"] = 2
        self.effective["cards"]["frame_time_easing"]["object_default"] = "linear"
        actual = self.render("[K.m(1,0),K.m(1,0,2,'quadratic_out'),K.m(1,0,2,'cubic_out')]")
        self.assertEqual(actual, [.5, .75, .875])

    def test_connection_mask_uses_the_effective_canvas(self):
        self.effective["video"].update({"width": 1280, "height": 720})
        fragment = self.render("K.path('M0 0L100 100',.5)")
        mask = self.svg(fragment).find("./defs/mask")
        self.assertEqual((mask.get("width"), mask.get("height")), ("1280", "720"))


if __name__ == "__main__":
    unittest.main()
