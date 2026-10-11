"""Export-only ownership for the locked C02/C03 source.

Rules use semantic data-object-id prefixes and audited source call sites, never
screen-side clipping or a moving object's instantaneous coordinates.  Multiple
graphics layers of one owner preserve the source's text/receiver occlusion.
Common frame graphics are deliberately left to the caller's global classifier.
Unrecognized objects fail closed so a changed source cannot silently lose art.
"""

from copy import deepcopy
import re


_PANELS = {
    "C02": [
        {"owner": "left", "owner_label": "左框·目标派发与 Agent 执行", "slot": 0,
         "bounds": [90, 270, 1000, 620],
         "source_id": "box_scenes_bc.js_47_17__common.js_18_55_0"},
        {"owner": "right", "owner_label": "右框·结果进度与官方界面", "slot": 1,
         "bounds": [1130, 270, 700, 620],
         "source_id": "box_scenes_bc.js_47_53__common.js_18_55_0"},
    ],
    "C03": [
        {"owner": "left", "owner_label": "左框·来源上下文与持久记忆库", "slot": 0,
         "bounds": [90, 270, 750, 620],
         "source_id": "box_scenes_bc.js_126_17__common.js_18_55_0"},
        {"owner": "right", "owner_label": "右框·检索复用与应用接入", "slot": 1,
         "bounds": [880, 270, 950, 620],
         "source_id": "box_scenes_bc.js_126_52__common.js_18_55_0"},
    ],
}


def panels(sid):
    """Return the two independently editable main panels for this scene."""
    if sid not in _PANELS:
        raise ValueError(f"classify_bc does not own scene {sid!r}")
    return deepcopy(_PANELS[sid])


def _result(obj, owner, layer, z, is_text=False, role=None):
    if is_text:
        # Dynamic wording variants already have distinct catalog IDs.  Keep
        # every logical wording separate; do not merge equal text across nodes.
        return {"owner": owner, "role": "text",
                "layer_key": f"{owner}_text__{obj['id']}", "z": z}
    return {"owner": owner,
            "role": role or ("graphics_shared" if owner == "shared" else "graphics"),
            "layer_key": layer, "z": z}


def _source_lines(obj):
    # Include the outer caller: checked() and transfer() have shared helpers.
    value = str(obj.get("site", "")) + "__" + str(obj["id"])
    return {int(n) for n in re.findall(r"scenes_bc\.js_(\d+)_\d+", value)}


def classify(sid, obj, is_text=False):
    """Map one instrumented source object to owner, role, layer_key and z.

    z applies to both raster layers and native text tracks.  In particular,
    moving labels must remain below their destination's opaque foreground.
    """
    if sid not in _PANELS:
        raise ValueError(f"classify_bc does not own scene {sid!r}")
    oid = str(obj["id"])
    lines = _source_lines(obj)
    for panel in _PANELS[sid]:
        if oid == panel["source_id"]:
            if is_text:
                raise ValueError(f"Panel source cannot be text: {sid} {oid}")
            return _result(obj, panel["owner"], panel["owner"] + "_box", 10, role="box")

    # Root-level typography may be handled earlier by the caller.  These exact
    # common.js sites are title/kicker, footer and series branding, not panels.
    if is_text and not lines and re.search(r"text_common\.js_(17|19|22)_", oid):
        return _result(obj, "shared", "shared_text", 200, True)

    if sid == "C02":
        if re.match(r"paperclip-task-[123]-dispatch__", oid):
            return _result(obj, "left", "left_graphics_base", 40 if is_text else 30, is_text)
        if re.match(r"paperclip-task-[123]-return__", oid):
            return _result(obj, "shared", "shared_returns", 40 if is_text else 30, is_text)
        if oid.startswith("paperclip-goal__"):
            return _result(obj, "left", "left_graphics_base", 200 if is_text else 30, is_text)
        if re.match(r"paperclip-agent-[123]__", oid):
            return _result(obj, "left", "left_foreground", 200 if is_text else 50, is_text)
        if re.match(r"paperclip-result-[123]__", oid) or oid.startswith("paperclip-official-ui__"):
            return _result(obj, "right", "right_foreground", 200 if is_text else 50, is_text)
        if is_text:
            if lines & {77, 86, 87}:
                return _result(obj, "right", "right_text", 200, True)
            if lines & {93, 95, 96}:
                return _result(obj, "left", "left_text", 200, True)
        else:
            if 55 in lines:  # Goal fan-out: wholly inside the left main panel.
                return _result(obj, "left", "left_graphics_base", 30)
            if 64 in lines:  # Genuine return route traverses both main panels.
                return _result(obj, "shared", "shared_returns", 30)
            if lines & {88, 89}:
                return _result(obj, "right", "right_foreground", 50)
            if lines & {92, 94}:
                return _result(obj, "left", "left_foreground", 50)

    if sid == "C03":
        # Classify transfer prefixes before the similarly named retained chips.
        if re.match(r"memory-store-M[123]__", oid):
            return _result(obj, "left", "left_context_store", 40 if is_text else 30, is_text)
        if re.match(r"memory-query-[01]__", oid):
            return _result(obj, "right", "right_query", 40 if is_text else 30, is_text)
        if re.match(r"memory-candidate-transfer-M[123]__", oid):
            return _result(obj, "right", "right_candidate_transfer", 70 if is_text else 60, is_text)
        if re.match(r"memory-retrieve-M[12]__", oid):
            return _result(obj, "right", "right_retrieve", 100 if is_text else 90, is_text)
        if oid.startswith("memory-integration-copy-M1__"):
            return _result(obj, "shared", "shared_integration", 125 if is_text else 120, is_text)
        if re.match(r"memory-source-M[123]__", oid):
            return _result(obj, "left", "left_context_store", 200 if is_text else 30, is_text)
        if re.match(r"memory-library-M[123]__", oid):
            return _result(obj, "left", "left_library_foreground", 200 if is_text else 50, is_text)
        if re.match(r"memory-candidate-M[123]__", oid):
            return _result(obj, "right", "right_candidates_foreground", 200 if is_text else 80, is_text)
        if oid.startswith("memory-received-context__") and is_text:
            return _result(obj, "right", "right_text", 200, True)
        if is_text:
            if lines & {128, 138, 142}:
                return _result(obj, "left", "left_text", 200, True)
            if lines & {144, 146, 153, 178, 184, 185, 189, 190, 192, 193, 197, 198}:
                return _result(obj, "right", "right_text", 200, True)
        else:
            rules = [
                ({129, 134}, "left", "left_context_store", 30),
                ({137}, "left", "left_library_foreground", 50),
                ({145, 150}, "right", "right_query", 30),
                ({152}, "right", "right_lanes_foreground", 50),
                ({159}, "right", "right_candidate_transfer", 60),
                ({164, 165}, "right", "right_candidates_foreground", 80),
                ({171}, "right", "right_retrieve", 90),
                ({174}, "right", "right_receiver_foreground", 110),
                # The API-to-app line is painted before the travelling copy.
                # Keep it below the copy body, not baked with its front panels.
                ({187}, "right", "right_integration_link", 119),
                ({186}, "shared", "shared_integration", 120),
                # API-to-application link is inside the right panel; only the
                # library-to-API route and travelling copy are shared assets.
                ({188, 191, 196}, "right", "right_integration_foreground", 130),
            ]
            for callers, owner, layer, z in rules:
                if lines & callers:
                    return _result(obj, owner, layer, z)

    raise ValueError(f"Unassigned {sid} {'text' if is_text else 'graphic'}: {oid}")
