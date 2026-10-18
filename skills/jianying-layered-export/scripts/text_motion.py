"""Plan native-text visibility without turning opacity into scale.

Pure planning utilities for project adapters. No editor, filesystem mutation,
Jianying dependency, or native-validation claim. A plan is not an animation
implementation: unresolved opacity requirements must be handled by the adapter.
"""
from __future__ import annotations

import math
from collections.abc import Mapping, Sequence


def _number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    return value


def frame_us(frame: int, fps: float) -> int:
    """Round absolute frame boundaries, never accumulate rounded frame lengths."""
    if isinstance(frame, bool) or not isinstance(frame, int) or frame < 0:
        raise ValueError("frame must be a nonnegative integer")
    if _number(fps, "fps") <= 0:
        raise ValueError("fps must be positive")
    return round(frame * 1_000_000 / fps)


def plan_text_visibility(samples: Sequence[Mapping], *, fps: float,
                         text_key: str, alpha_keyframes_verified: bool = False) -> dict:
    """Preserve source transforms and expose the opacity mapping still required.

    Samples are consecutive, full source frames with frame/x/y and alpha in
    [0,1]; scaleX/scaleY default to 1, rotation to 0. Missing frames are an
    error, not implicit hiding. For sparse source animations, evaluate them at
    source fps before calling this function.

    An unverified alpha channel is NEVER emitted as native keyframes. Outer
    invisible spans are trimmed. Internal invisible spans become separate
    suggested segments carrying the same logical text key; an adapter must
    expose their linked-edit relationship rather than promise one-click edits.
    Fractional opacity always remains an explicit mapping requirement unless
    native text alpha has relevant runtime evidence. True source scale=0 is
    preserved; this function never invents scale=0 from alpha=0.
    """
    frame_us(0, fps)
    if not isinstance(text_key, str) or not text_key.strip():
        raise ValueError("text_key is required")
    if not isinstance(alpha_keyframes_verified, bool):
        raise ValueError("alpha_keyframes_verified must be bool")
    rows = []
    for i, sample in enumerate(samples):
        if not isinstance(sample, Mapping):
            raise ValueError("each sample must be a mapping")
        row = dict(sample)
        frame_us(row.get("frame"), fps)
        if rows and row["frame"] != rows[-1]["frame"] + 1:
            raise ValueError("source frames must be consecutive, ordered and unique")
        for name, default in (("alpha", 1), ("scaleX", 1), ("scaleY", 1), ("rotation", 0)):
            row[name] = _number(row.get(name, default), f"sample[{i}].{name}")
        for name in ("x", "y"):
            row[name] = _number(row.get(name), f"sample[{i}].{name}")
        if not 0 <= row["alpha"] <= 1:
            raise ValueError("alpha must be in [0,1]")
        rows.append(row)

    spans = []
    for row in rows:
        if row["alpha"] > 0:
            f = row["frame"]
            if spans and spans[-1][1] == f:
                spans[-1][1] = f + 1
            else:
                spans.append([f, f + 1])
    result = {"textKey": text_key, "fps": fps, "opacityActiveSpans": spans,
              "visibilityMethod": "segment_ranges", "nativeAlphaEnabled": alpha_keyframes_verified,
              "segments": [], "requirements": [], "status": "ready"}
    if not spans:
        result["status"] = "not_visible"
        return result
    ranges = [[spans[0][0], spans[-1][1]]] if alpha_keyframes_verified else spans
    by_frame = {row["frame"]: row for row in rows}
    for number, (a, b) in enumerate(ranges, 1):
        selected = [by_frame[f] for f in range(a, b)]
        transforms = [{"offsetUs": frame_us(row["frame"], fps) - frame_us(a, fps),
                       **{key: row[key] for key in ("x", "y", "scaleX", "scaleY", "rotation")}}
                      for row in selected]
        item = {"textKey": text_key, "segmentKey": f"{text_key}#appearance-{number}", "occurrence": number, "startFrame": a,
                "endFrameExclusive": b, "startUs": frame_us(a, fps),
                "durationUs": frame_us(b, fps) - frame_us(a, fps),
                "transformSamples": transforms,
                "sourceOpacitySamples": [{"offsetUs": frame_us(row["frame"], fps) - frame_us(a, fps),
                                           "value": row["alpha"]} for row in selected]}
        if alpha_keyframes_verified:
            item["nativeAlphaSamples"] = list(item["sourceOpacitySamples"])
        elif any(row["alpha"] != 1 for row in selected):
            result["requirements"].append({"code": "text_opacity_mapping_required", "occurrence": number,
                "message": "Use a supported native text animation with matching timing, or explicitly resolve the editability/fidelity tradeoff. Do not replace this fade with zero scale or silently drop it."})
        result["segments"].append(item)
    if len(ranges) > 1:
        result["requirements"].append({"code": "reappearance_edit_mapping_required",
            "message": "Separate source appearances share one logical key; expose their relationship in the edit index. Do not split per frame or share mutable native materials implicitly."})
    if result["requirements"]:
        result["status"] = "needs_mapping"
    return result
