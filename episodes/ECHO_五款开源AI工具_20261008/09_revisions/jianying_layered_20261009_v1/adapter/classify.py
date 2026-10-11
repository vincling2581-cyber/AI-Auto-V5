"""Explicit semantic ownership for this export's audited, instrumented source.

No source or catalog files are modified.  Coordinates are panel metadata, not
classification heuristics.  Every object is matched by an audited source call
site/loop slot; unknown scene, ID, kind or site fails closed.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import re
import sys

try:
    from . import classify_bc
except ImportError:
    import classify_bc

_ART_SCENES = {f"A{i:02d}" for i in range(1, 10)}
_CARD_SCENES = {f"C{i:02d}" for i in range(7)}
_SCENES = _ART_SCENES | _CARD_SCENES
_COMMON_TAIL = "__common.js_18_55"


def _panel(owner, label, slot, bounds, source_id):
    return {"owner": owner, "owner_label": label, "slot": slot,
            "bounds": bounds, "source_id": source_id}


_PANELS = {
    "C00": [
        _panel(f"tool{i + 1}", label, i, [110 + i * 348, 360, 320, 350],
               f"box_scenes_a.js_4_96__common.js_18_55_{i}")
        for i, label in enumerate(("声音制作·VoiceStudio", "任务协作·Paperclip",
                                   "长期记忆·MemOS", "本地模型·Ollama + WebUI",
                                   "界面设计·Impeccable"))
    ],
    "C01": [
        _panel("left", "左框·参考录音与配音制作", 0, [90, 282, 740, 640],
               "box_scenes_a.js_7_66__common.js_18_55_0"),
        _panel("right", "右框·音色档案与许可核对", 1, [870, 282, 960, 640],
               "box_scenes_a.js_7_86__common.js_18_55_0"),
    ],
    "C04": [
        _panel("left", "左框·本地模型协作与断网流程", 0, [90, 280, 1060, 630],
               "box_scenes_de.js_7_55__scenes_de.js_31_13__common.js_18_55_0"),
        _panel("right", "右框·官方界面与平台条件", 1, [1190, 280, 640, 630],
               "box_scenes_de.js_7_55__scenes_de.js_32_8__common.js_18_55_0"),
    ],
    "C05": [
        _panel("left", "左框·界面结构重排", 0, [90, 280, 1040, 630],
               "box_scenes_de.js_7_55__scenes_de.js_114_13__common.js_18_55_0"),
        _panel("right", "右框·设计检查与官方案例", 1, [1165, 280, 665, 630],
               "box_scenes_de.js_7_55__scenes_de.js_115_8__common.js_18_55_0"),
    ],
    "C06": [
        _panel("main", "主框·系列结束语", 0, [90, 290, 1740, 628],
               "box_scenes_a.js_20_73__common.js_18_55_0"),
    ],
}


def panels(sid):
    """Independent main boxes, using classify_bc's metadata contract."""
    if sid in {"C02", "C03"}:
        return classify_bc.panels(sid)
    if sid in _ART_SCENES:
        return []
    if sid in _PANELS:
        return deepcopy(_PANELS[sid])
    raise ValueError(f"Unknown scene: {sid!r}")


def _result(obj, owner, layer, z, is_text=False, role=None):
    if is_text:
        return {"owner": owner, "role": "text",
                "layer_key": f"{owner}_text__{obj['id']}", "z": z}
    return {"owner": owner,
            "role": role or ("graphics_shared" if owner == "shared" else "graphics"),
            "layer_key": layer, "z": z}


# Explicit primitive IDs (without a text-content hash).  Kind is part of each
# ID; an unexpected primitive at an otherwise known call site is not accepted.
_GRAPHICS = {}
_TEXT = {}


def _register(table, sid, kind, site, owner, layer, z, indices=(0,), role=None):
    for index in indices:
        key = (sid, f"{kind}_{site}_{index}")
        if key in table:
            raise RuntimeError(f"Duplicate classifier rule: {key}")
        table[key] = (owner, layer, z, role)


def _graphic(sid, kind, site, owner, z=30, indices=(0,), layer=None):
    _register(_GRAPHICS, sid, kind, site, owner, layer or f"{owner}_graphics", z, indices)


def _text(sid, site, owner, indices=(0,)):
    _register(_TEXT, sid, "text", site, owner, f"{owner}_text", 200, indices)


def _a(line, col):
    return f"scenes_a.js_{line}_{col}" + _COMMON_TAIL


def _de(helper, line, col, tail=_COMMON_TAIL):
    return f"scenes_de.js_{helper}__scenes_de.js_{line}_{col}" + tail


# C00: five loop slots are five owners, never one combined row of cards.
for _i in range(5):
    _graphic("C00", "icon", _a(4, 215), f"tool{_i + 1}", indices=(_i,))
    for _column in (158, 307, 384):
        _text("C00", _a(4, _column), f"tool{_i + 1}", (_i,))
_text("C00", _a(5, 10), "shared")

# C01: retained audio is left; extraction path/packet is shared; the receiving
# archive is above those shared objects so entry occlusion remains intact.
for _kind, _site, _indices in [
    ("box", "common.js_12_36__scenes_a.js_8_16" + _COMMON_TAIL, (0,)),
    ("waveform", "scenes_a.js_6_54__scenes_a.js_8_115" + _COMMON_TAIL, (0,)),
    ("box", "common.js_12_36__scenes_a.js_13_74" + _COMMON_TAIL, (0, 1, 2)),
    ("box", _a(15, 93), (0, 1, 2)),
    ("waveform", "scenes_a.js_6_54__scenes_a.js_15_187" + _COMMON_TAIL, (0, 1, 2)),
    ("img", _a(17, 77), (0,)),
]:
    _graphic("C01", _kind, _site, "left", 30, _indices)
for _kind, _site in [
    ("box", _a(10, 47)), ("icon", _a(10, 90)),
    ("waveform", "scenes_a.js_6_54__scenes_a.js_11_11" + _COMMON_TAIL),
    ("img", _a(16, 59)),
    ("path", "common.js_9_45__scenes_a.js_18_127" + _COMMON_TAIL),
    ("box", _a(18, 297)),
]:
    _graphic("C01", _kind, _site, "right", 50, layer="right_foreground")
for _kind, _site in [
    ("path", "common.js_9_45__scenes_a.js_9_50" + _COMMON_TAIL),
    ("packet", "common.js_10_39__scenes_a.js_9_87" + _COMMON_TAIL),
]:
    _graphic("C01", _kind, _site, "shared", 40, layer="shared_extraction")
for _line, _col in ((8, 40), (8, 79), (14, 21), (17, 34), (17, 124)):
    _text("C01", _a(_line, _col), "left")
_text("C01", "common.js_12_88__scenes_a.js_8_16" + _COMMON_TAIL, "left")
_text("C01", "common.js_12_88__scenes_a.js_13_74" + _COMMON_TAIL, "left", (0, 1, 2))
_text("C01", _a(15, 140), "left", (0, 1, 2))
for _line, _col in ((10, 5), (11, 50), (12, 5), (16, 4), (16, 108),
                   (18, 10), (18, 50), (18, 84), (18, 161),
                   (18, 204), (18, 255), (18, 337)):
    _text("C01", _a(_line, _col), "right")

# C04: all model/runtime/browser links are internal to the left MAIN panel.
# They are not shared merely because they cross its smaller diagram blocks.
for _line, _col in ((35, 8), (36, 8), (37, 8), (51, 8), (52, 8), (53, 8),
                   (66, 12), (73, 8), (74, 8), (75, 8), (78, 13)):
    _graphic("C04", "box", _de("7_55", _line, _col), "left")
for _line, _col in ((39, 8), (40, 8), (54, 8), (58, 13), (59, 13),
                   (71, 22), (72, 8)):
    _graphic("C04", "raw_path", _de("11_52", _line, _col), "left")
for _line, _col in ((41, 10), (56, 12), (57, 10), (62, 12)):
    _graphic("C04", "path", f"common.js_9_45__scenes_de.js_{_line}_{_col}" + _COMMON_TAIL, "left")
for _line, _col in ((60, 34), (61, 35), (64, 14)):
    _graphic("C04", "packet", f"common.js_10_39__scenes_de.js_{_line}_{_col}" + _COMMON_TAIL, "left")
for _line in (46, 47):
    _graphic("C04", "raw_circle", _de("12_58", _line, 8), "left")
for _model_line in (42, 43):
    _graphic("C04", "box", f"scenes_de.js_7_55__scenes_de.js_15_17__scenes_de.js_{_model_line}_8", "left")
    _graphic("C04", "raw_path", f"scenes_de.js_11_52__scenes_de.js_16_8__scenes_de.js_{_model_line}_8", "left")
    _text("C04", f"scenes_de.js_8_76__scenes_de.js_17_8__scenes_de.js_{_model_line}_8", "left")
for _line, _col in ((84, 8), (88, 15), (90, 8), (92, 8)):
    _graphic("C04", "box", _de("7_55", _line, _col), "right")
_graphic("C04", "img", "scenes_de.js_85_10" + _COMMON_TAIL, "right")
for _line, _col in ((33, 8), (34, 8), (38, 10), (44, 8), (45, 10),
                   (48, 8), (49, 8), (50, 10), (55, 8), (76, 8), (79, 8), (80, 8)):
    _text("C04", _de("8_76", _line, _col), "left")
for _line, _col in ((82, 10), (83, 8), (86, 8), (87, 8), (89, 8), (91, 8), (93, 8)):
    _text("C04", _de("8_76", _line, _col), "right")

# C05: persistent metric objects keep their source-call identities while moving.
for _line, _col in ((118, 8), (125, 15), (136, 10)):
    _graphic("C05", "box", _de("7_55", _line, _col), "left")
_graphic("C05", "raw_path", _de("11_52", 120, 51), "left", indices=range(4))
_graphic("C05", "raw_path", _de("11_52", 121, 46), "left", indices=range(3))
for _metric_line in (128, 131, 134):
    _graphic("C05", "box", f"scenes_de.js_7_55__scenes_de.js_98_12__scenes_de.js_{_metric_line}_10", "left")
    for _inner in (99, 100):
        _text("C05", f"scenes_de.js_8_76__scenes_de.js_{_inner}_8__scenes_de.js_{_metric_line}_10", "left")
_graphic("C05", "box", "scenes_de.js_7_55__scenes_de.js_146_14__scenes_de.js_144_12", "right", indices=range(3))
_graphic("C05", "raw_path", "scenes_de.js_11_52__scenes_de.js_148_17__scenes_de.js_144_12", "right", indices=range(3))
for _line in (152, 159):
    _graphic("C05", "box", _de("7_55", _line, 10), "right")
_graphic("C05", "img", "scenes_de.js_161_54" + _COMMON_TAIL, "right")
for _line, _col in ((116, 8), (117, 8), (123, 10), (124, 8), (126, 8),
                   (137, 8), (138, 13), (139, 10)):
    _text("C05", _de("8_76", _line, _col), "left")
for _line, _col in ((140, 10), (142, 12), (151, 12), (153, 10),
                   (154, 10), (155, 10), (158, 12), (162, 10), (163, 10)):
    _text("C05", _de("8_76", _line, _col), "right")
_text("C05", "scenes_de.js_8_76__scenes_de.js_147_12__scenes_de.js_144_12", "right", range(3))

# C06: the call-to-action inset belongs to the single main panel.
_graphic("C06", "box", _a(20, 252), "main")
for _column in (120, 177, 292):
    _text("C06", _a(20, _column), "main")


def classify(sid, obj, is_text=False):
    """Return exactly owner, role, layer_key and z for one catalog object."""
    if sid not in _SCENES:
        raise ValueError(f"Unknown scene: {sid!r}")
    oid = str(obj["id"])
    if is_text:
        # Dynamic wording changes the terminal content hash, not ownership.
        key_id = re.sub(r"_t[0-9a-f]+$", "", oid)
        shared_text_ids = {"text_common.js_17_10_0", "text_common.js_17_46_0",
                           "text_common.js_19_10_0", "text_common.js_22_65_0"}
        if key_id in shared_text_ids:
            if sid in _ART_SCENES and key_id != "text_common.js_22_65_0":
                raise ValueError(f"Unexpected card typography in art scene: {sid} {oid}")
            return _result(obj, "shared", "shared_text", 200, True)
        if sid in _ART_SCENES:
            if key_id == "text_common.js_15_135_0":
                return _result(obj, "shared", "shared_text", 200, True)
            raise ValueError(f"Unknown art text: {sid} {oid}")
        if sid in {"C02", "C03"}:
            return classify_bc.classify(sid, obj, True)
        rule = _TEXT.get((sid, key_id))
    else:
        key_id = oid
        if oid == "box_common.js_22_9_0":
            return _result(obj, "shared", "background", 0,
                           role="animation" if sid in _ART_SCENES else "background")
        if sid in _ART_SCENES:
            if oid in {"img_common.js_14_16_0", "raw_art_label_plate"}:
                return _result(obj, "shared", "background", 0, role="animation")
            raise ValueError(f"Unknown art graphic: {sid} {oid}")
        if oid in {"box_common.js_16_14_0", "raw_heading_rule"}:
            return _result(obj, "shared", "background", 0, role="background")
        if oid in {"raw_progress_track", "raw_progress_active"}:
            return _result(obj, "shared", "shared_progress", 5, role="graphics_shared")
        if sid in {"C02", "C03"}:
            return classify_bc.classify(sid, obj, False)
        for panel in _PANELS[sid]:
            if oid == panel["source_id"]:
                return _result(obj, panel["owner"], panel["owner"] + "_box", 10, role="box")
        rule = _GRAPHICS.get((sid, key_id))
    if rule is None:
        raise ValueError(f"Unassigned {sid} {'text' if is_text else 'graphic'}: {oid}")
    owner, layer, z, role = rule
    return _result(obj, owner, layer, z, is_text, role)


def validate_catalog(directory):
    """Read every complete scene catalog and return coverage statistics only."""
    directory = Path(directory)
    totals, scenes = Counter(), []
    seen_scenes = set()
    for path in sorted(directory.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        sid = data["id"]
        if sid in seen_scenes:
            raise ValueError(f"Duplicate scene catalog: {sid}")
        seen_scenes.add(sid)
        if not data.get("full_scan"):
            raise ValueError(f"Catalog is not a full-frame scan: {sid}")
        main_panels = panels(sid)
        allowed_owners = {"shared"} | {panel["owner"] for panel in main_panels}
        owners, roles, layers, object_ids, panel_hits = Counter(), Counter(), {}, set(), Counter()
        for is_text, rows in ((False, data["objects"]), (True, data["texts"])):
            for obj in rows:
                oid = obj["id"]
                if oid in object_ids:
                    raise ValueError(f"Duplicate object/text ID in {sid}: {oid}")
                object_ids.add(oid)
                result = classify(sid, obj, is_text)
                if set(result) != {"owner", "role", "layer_key", "z"}:
                    raise ValueError(f"Classifier contract mismatch: {sid} {oid}")
                if result["owner"] not in allowed_owners:
                    raise ValueError(f"Owner is not a main panel/shared: {sid} {oid}")
                if is_text != (result["role"] == "text"):
                    raise ValueError(f"Native-text role mismatch: {sid} {oid}")
                layer = result["layer_key"]
                signature = (result["owner"], result["role"], result["z"])
                if layer in layers and layers[layer] != signature:
                    raise ValueError(f"Layer groups incompatible owners/roles/z: {sid} {layer}")
                layers[layer] = signature
                owners[result["owner"]] += 1
                roles[result["role"]] += 1
                if result["role"] == "box":
                    panel_hits[oid] += 1
        expected_panels = {panel["source_id"] for panel in main_panels}
        if set(panel_hits) != expected_panels or any(v != 1 for v in panel_hits.values()):
            raise ValueError(f"Missing or repeated independent main panel: {sid}")
        totals.update(objects=len(data["objects"]), texts=len(data["texts"]),
                      panels=len(main_panels), layers=len(layers))
        scenes.append({"scene": sid, "objects": len(data["objects"]), "texts": len(data["texts"]),
                       "panels": len(main_panels), "layers": len(layers),
                       "owners": dict(owners), "roles": dict(roles)})
    if seen_scenes != _SCENES:
        raise ValueError(f"Catalog scenes differ: missing={sorted(_SCENES - seen_scenes)}, unknown={sorted(seen_scenes - _SCENES)}")
    return {"passed": True, "catalog": str(directory), "scene_count": len(scenes),
            "unknown_objects": 0, "totals": dict(totals), "scenes": scenes,
            "limits": "Semantic ownership and catalog coverage only; does not certify encoded alpha, recomposition fidelity, editable-text rendering or native Jianying behavior."}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=Path(__file__).resolve().parents[1] / "catalog")
    args = parser.parse_args()
    print(json.dumps(validate_catalog(args.catalog), ensure_ascii=False, indent=2))
