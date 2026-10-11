"""Offline checks of FINAL encoded layers and FINAL portable draft placement.

No rendering of source SVG, no Jianying registration/UI, no native text claim.
--plan only prints required source-reference frames and writes nothing.
Missing inputs produce status=pending_inputs, never a successful acceptance.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import io
import json
import math
from pathlib import Path
import runpy
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image

sys.dont_write_bytecode = True
REV = Path(__file__).resolve().parent
SOURCE = REV / "source/episode"
LIMITS = {"mean_abs_lt": .7, "p99_abs_lt": 6, "pixels_gt_16_fraction_lt": .001}
GRAPHICS = {"graphics", "graphics_shared", "shared_graphics"}
BACKGROUND_IDS = {"box_common.js_16_14_0", "raw_heading_rule", "box_common.js_22_9_0"}


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def inside(path, root=REV):
    p, root = Path(path).resolve(), Path(root).resolve()
    if p == root or not p.is_relative_to(root):
        raise ValueError(f"Path escapes allowed directory: {p}")
    return p


def require(condition, detail):
    if not condition:
        raise AssertionError(detail)


def planned_frames(shot):
    n = shot["frame_count"]
    if shot["id"].startswith("A"):
        return sorted({0, n // 2, n - 1})
    return sorted({0, n // 2, n - 1} | set(shot.get("overview_frames", [])) | {
        int(f) for event in shot.get("process_events", [])
        for f in event.get("check_frames", []) if 0 <= int(f) < n})


def reference_path(directory, sid, frame):
    choices = [directory / f"reference_{sid}_{frame}.png",
               directory / f"reference_{sid}_{frame:04d}.png",
               directory / f"reference_{sid}_{frame:06d}.png"]
    return next((p for p in choices if p.is_file()), choices[0])


def find_ffmpeg(explicit, defaults):
    if explicit:
        p = Path(explicit)
        if not p.is_file():
            raise FileNotFoundError(p)
        return str(p)
    values = []
    def walk(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "ffmpeg" and isinstance(item, str):
                    values.append(item)
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)
    walk(defaults)
    values.append(shutil.which("ffmpeg"))
    for value in values:
        if value and Path(value).is_file():
            return str(value)
    raise FileNotFoundError("No configured FFmpeg runtime found")


class Decoder:
    """Decode each file's selected frames in one FFmpeg invocation.

    Cache lossless PNG bytes in memory instead of retaining full RGBA frames.
    The bytes originate from decoding the final media, never the SVG renderer.
    """
    def __init__(self, ffmpeg):
        self.ffmpeg = ffmpeg
        sibling = Path(ffmpeg).with_name("ffprobe.exe" if Path(ffmpeg).suffix.lower() == ".exe" else "ffprobe")
        self.ffprobe = str(sibling) if sibling.is_file() else shutil.which("ffprobe")
        if not self.ffprobe:
            raise FileNotFoundError("ffprobe unavailable")
        self.cache, self.bindings = {}, {}

    def prepare(self, path, frames, width, height, expected_count=None):
        path = Path(path).resolve()
        frames = sorted(set(frames))
        require(frames and frames[0] >= 0, (str(path), "invalid selected frames"))
        key = str(path)
        if path.suffix.lower() == ".png":
            raw = path.read_bytes()
            with Image.open(io.BytesIO(raw)) as im:
                require("A" in im.getbands(), (key, "PNG has no alpha channel"))
                require(im.size == (width, height), (key, "PNG dimensions", im.size))
            self.cache[key, 0] = raw
            self.bindings[key] = {"sha256": sha(path), "bytes": path.stat().st_size,
                                  "type": "PNG", "dimensions": [width, height]}
            return
        probe = json.loads(subprocess.check_output([
            self.ffprobe, "-v", "error", "-show_streams", "-of", "json", str(path)]))
        streams = probe.get("streams", [])
        video = [s for s in streams if s.get("codec_type") == "video"]
        require(len(video) == 1 and len(streams) == 1, (key, "expected one silent video stream"))
        stream = video[0]
        require((stream["width"], stream["height"]) == (width, height), (key, "MOV dimensions"))
        require("a" in stream.get("pix_fmt", ""), (key, "decoded video format has no alpha", stream.get("pix_fmt")))
        count = stream.get("nb_frames")
        if expected_count is not None and count not in (None, "N/A"):
            require(int(count) == expected_count, (key, "encoded frame count", count, expected_count))
        expression = "select=" + "+".join(f"eq(n\\,{f})" for f in frames)
        cmd = [self.ffmpeg, "-hide_banner", "-loglevel", "error", "-threads", "2",
               "-i", str(path), "-vf", expression, "-vsync", "0", "-an",
               "-f", "rawvideo", "-pix_fmt", "rgba", "-threads", "2", "pipe:1"]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        frame_bytes = width * height * 4
        try:
            for frame in frames:
                chunks, remaining = [], frame_bytes
                while remaining:
                    chunk = process.stdout.read(remaining)
                    if not chunk:
                        break
                    chunks.append(chunk)
                    remaining -= len(chunk)
                require(remaining == 0, (key, "missing final encoded frame", frame))
                image = Image.frombytes("RGBA", (width, height), b"".join(chunks))
                out = io.BytesIO()
                image.save(out, format="PNG")
                self.cache[key, frame] = out.getvalue()
            require(not process.stdout.read(1), (key, "unexpected extra selected frame"))
            error = process.stderr.read().decode(errors="replace")
            require(process.wait() == 0, (key, "FFmpeg decode failed", error))
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
            process.stdout.close()
            process.stderr.close()
        self.bindings[key] = {"sha256": sha(path), "bytes": path.stat().st_size,
            "type": "encoded_video", "decoded_frames": frames,
            "dimensions": [width, height], "codec": stream.get("codec_name"),
            "pixel_format": stream.get("pix_fmt"), "declared_frame_count": count}

    def image(self, path, frame):
        path = Path(path).resolve()
        key = (str(path), 0 if path.suffix.lower() == ".png" else frame)
        with Image.open(io.BytesIO(self.cache[key])) as im:
            return im.convert("RGBA")


def compose(items, decoder, size, operation=None):
    canvas = Image.new("RGBA", size)
    for item in sorted(items, key=lambda x: x["order"]):
        selected = (operation and item["owner"] == operation["owner"]
                    and item["role"] in GRAPHICS)
        if selected and operation["kind"] == "hide":
            continue
        image = decoder.image(item["path"], item["frame"])
        x, y = item["x"], item["y"]
        if selected:
            if operation["kind"] == "move":
                x += operation["dx"]
                y += operation.get("dy", 0)
            elif operation["kind"] == "scale":
                factor = operation["scale"]
                target = (max(1, round(image.width * factor)), max(1, round(image.height * factor)))
                x += (image.width - target[0]) / 2
                y += (image.height - target[1]) / 2
                image = image.resize(target, Image.Resampling.LANCZOS)
        canvas.alpha_composite(image, (round(x), round(y)))
    return canvas


def difference(actual, expected):
    a = np.asarray(actual.convert("RGBA")).astype(np.int16)
    b = np.asarray(expected.convert("RGBA")).astype(np.int16)
    require(a.shape == b.shape, ("comparison shape", a.shape, b.shape))
    diff = np.abs(a[:, :, :3] - b[:, :, :3])
    maximum = diff.max(axis=2)
    metrics = {"mean_abs": float(diff.mean()), "p99_abs": float(np.percentile(diff, 99)),
        "max_abs": int(diff.max()), "pixels_gt_16_fraction": float((maximum > 16).mean()),
        "alpha_max_abs": int(np.abs(a[:, :, 3] - b[:, :, 3]).max())}
    passed = (metrics["mean_abs"] < LIMITS["mean_abs_lt"]
        and metrics["p99_abs"] < LIMITS["p99_abs_lt"]
        and metrics["pixels_gt_16_fraction"] < LIMITS["pixels_gt_16_fraction_lt"]
        and metrics["alpha_max_abs"] == 0)
    return {"passed": passed, **metrics}


def region_change(before, after, bounds):
    x, y, w, h = bounds
    height, width = before.shape[:2]
    x0, y0, x1, y1 = max(0, math.floor(x)), max(0, math.floor(y)), min(width, math.ceil(x+w)), min(height, math.ceil(y+h))
    delta = np.abs(before[y0:y1, x0:x1].astype(np.int16) - after[y0:y1, x0:x1].astype(np.int16))
    require(delta.size > 0, ("empty panel ROI", bounds))
    return {"roi": [x0, y0, x1, y1], "changed_pixels": int(np.any(delta != 0, axis=2).sum()),
            "max_abs": int(delta.max())}


def ownership_check(card, package_manifest):
    sid = card["id"]
    declared = {o["id"] if isinstance(o, dict) else o for o in card["source_graphic_ids"]}
    assigned = {}
    for layer in card["layers"]:
        if layer["role"] not in GRAPHICS:
            continue
        require(layer.get("source_ids"), (sid, layer["id"], "empty graphical provenance"))
        for oid in layer["source_ids"]:
            require(oid not in assigned, (sid, oid, "multiple graphic owners"))
            assigned[oid] = (layer["owner"], layer["role"], layer["z"])
    require(set(assigned) == declared, (sid, "source universe mismatch", sorted(declared-set(assigned)), sorted(set(assigned)-declared)))
    sources = [s for s in package_manifest["sources"] if s["scene"] == sid]
    require(len(sources) == 1, (sid, "package source universe count"))
    packaged = {o["id"]: o["owner"] for o in sources[0]["objects"]}
    require(packaged == {oid: value[0] for oid, value in assigned.items()}, (sid, "packaged source ownership changed"))
    catalog_path = REV / "catalog" / f"{sid}.json"
    catalog = load(catalog_path)
    require(catalog.get("full_scan") is True, (sid, "source catalog is not full-frame scanned"))
    catalog_ids = {o["id"] for o in catalog["objects"]}
    require(declared <= catalog_ids, (sid, "export contains unknown source graphics"))
    all_exported = [oid for layer in card["layers"] for oid in layer.get("source_ids", [])]
    counts = Counter(all_exported)
    require(set(counts) == catalog_ids and all(n == 1 for n in counts.values()),
            (sid, "full source object partition mismatch", sorted(catalog_ids-set(counts)),
             sorted(set(counts)-catalog_ids), [k for k, n in counts.items() if n != 1]))
    result = {"card": sid, "graphic_object_count": len(declared), "unique_coverage": True,
              "catalog_sha256": sha(catalog_path), "semantic_crosscheck": "not_independently_classified"}
    if sid in {"C02", "C03"}:
        classifier_path = REV / "adapter/classify_bc.py"
        classifier = runpy.run_path(str(classifier_path))
        expected = {}
        for obj in catalog["objects"]:
            oid = obj["id"]
            if oid in BACKGROUND_IDS:
                continue
            if oid in {"raw_progress_track", "raw_progress_active"}:
                expected[oid] = ("shared", "graphics_shared", 5)
                continue
            info = classifier["classify"](sid, obj)
            if info["role"] in GRAPHICS:
                expected[oid] = (info["owner"], info["role"], info["z"])
        normalize = lambda row: (row[0], "graphics_shared" if row[1] == "shared_graphics" else row[1], row[2])
        require({k: normalize(v) for k, v in assigned.items()} == {k: normalize(v) for k, v in expected.items()},
                (sid, "source-semantics owner/role/z mismatch"))
        result.update(semantic_crosscheck="explicit_source_callsite_and_object_identity", classifier_sha256=sha(classifier_path))
    return result


def verify(args, storyboard):
    layers_path, package = inside(args.layers), inside(args.package)
    data, manifest, draft = load(layers_path), load(package / "manifest.json"), load(package / "draft_content.json")
    width, height, fps = data["width"], data["height"], data["fps"]
    require((width, height, fps) == (storyboard["width"], storyboard["height"], storyboard["fps"]), "Source/contract format mismatch")
    us = lambda f: round(f * 1_000_000 / fps)
    timeline = {c["id"]: c for c in storyboard["cards"]}
    selected = set(args.cards or [c["id"] for c in data["cards"]])
    cards = [c for c in data["cards"] if c["id"] in selected]
    require({c["id"] for c in cards} == selected, "Requested cards missing in contract")
    native = {s["id"]: (track, s) for track in draft["tracks"] for s in track["segments"]}
    materials = {m["id"]: m for m in draft["materials"]["videos"]}
    rows = {(s["scene"], s["sourceLayerId"]): s for s in manifest["segments"] if s.get("sourceLayerId") is not None}
    media = {m["path"]: m for m in manifest["media"]}
    decoder = Decoder(find_ffmpeg(args.ffmpeg, load(SOURCE / "00_brief/effective_defaults.json")))
    comparisons, independent, ownership, bindings = [], [], [], []
    required_panels, covered_panels = set(), set()
    for card in cards:
        sid = card["id"]
        shot = timeline[sid]
        require((card["start_frame"], card["end_frame"]) == (shot["start_frame"], shot["end_frame_exclusive"]), (sid, "timeline changed"))
        frames = planned_frames(shot)
        ownership.append(ownership_check(card, manifest))
        contract_items, native_items = {}, {}
        for layer in card["layers"]:
            original = inside(REV / layer["path"])
            record = rows[sid, layer["id"]]
            track, segment = native[record["id"]]
            material = materials[segment["material_id"]]
            require(track["type"] == "video", (sid, layer["id"], "not a native video track"))
            require(segment["material_id"] == record["materialId"], "Material ID mismatch")
            require(not segment.get("group_id") and not segment.get("common_keyframes"), (sid, layer["id"], "unexpected group or native motion"))
            require(record["owner"] == layer["owner"], (sid, layer["id"], "packaged owner differs"))
            target = inside(package / material["path"], package)
            require(material["path"] == record["path"], "Packaged material path differs")
            actual_hash = sha(target)
            require(actual_hash == layer["sha256"] == media[record["path"]]["sha256"] == sha(original), (sid, layer["id"], "final asset hash mismatch"))
            require(target.stat().st_size == media[record["path"]]["bytes"], "Packaged bytes mismatch")
            a, b = layer["start_frame"], layer["end_frame"]
            require(segment["target_timerange"] == {"start": us(a), "duration": us(b)-us(a)}, (sid, layer["id"], "native target timerange"))
            source_range = segment.get("source_timerange") or {"start": 0}
            require(source_range["start"] == 0, (sid, layer["id"], "unexpected native source offset"))
            clip = segment["clip"]
            require(abs(clip["alpha"]-1) < 1e-9 and abs(clip["rotation"]) < 1e-9, (sid, layer["id"], "unexpected alpha/rotation"))
            require(not any((clip.get("flip") or {}).values()), (sid, layer["id"], "unexpected flip"))
            fit = min(width/layer["width"], height/layer["height"])
            require(abs(clip["scale"]["x"]*fit-1) < 1e-7 and abs(clip["scale"]["y"]*fit-1) < 1e-7, (sid, layer["id"], "native fit compensation"))
            cx, cy = (clip["transform"]["x"]+1)*width/2, (1-clip["transform"]["y"])*height/2
            require(abs(cx-layer["x"]) < 1e-6 and abs(cy-layer["y"]) < 1e-6, (sid, layer["id"], "native placement differs"))
            local_frames = [card["start_frame"]+f-a for f in frames if a <= card["start_frame"]+f < b]
            if local_frames:
                decoder.prepare(target, local_frames, layer["width"], layer["height"], b-a if layer["kind"] == "video" else None)
            bindings.append({"scene": sid, "layer": layer["id"], "owner": layer["owner"],
                "path": target.relative_to(REV).as_posix(), "sha256": actual_hash,
                "segment_id": segment["id"], "material_id": material["id"], "render_index": segment["render_index"],
                "clip": clip, "target_timerange": segment["target_timerange"]})
            for f in frames:
                global_frame = card["start_frame"]+f
                if not a <= global_frame < b:
                    continue
                common = {"owner": layer["owner"], "role": layer["role"], "path": target,
                          "frame": global_frame-a, "layer_id": layer["id"]}
                contract_items.setdefault(f, []).append({**common, "order": layer["z"],
                    "x": layer["x"]-layer["width"]/2, "y": layer["y"]-layer["height"]/2})
                native_items.setdefault(f, []).append({**common, "order": segment["render_index"],
                    "x": cx-layer["width"]/2, "y": cy-layer["height"]/2})
        best = {}
        for f in frames:
            reference_file = reference_path(Path(args.reference_dir), sid, f)
            with Image.open(reference_file) as im:
                reference = im.convert("RGBA")
            require(reference.size == (width, height), (sid, f, "source reference dimensions"))
            actual = compose(contract_items.get(f, []), decoder, (width, height))
            packaged = compose(native_items.get(f, []), decoder, (width, height))
            metrics, draft_metrics = difference(actual, reference), difference(packaged, reference)
            comparison = {"card": sid, "local_frame": f, "global_frame": card["start_frame"]+f,
                "reference": reference_file.relative_to(REV).as_posix(), "reference_sha256": sha(reference_file),
                "encoded_layers_vs_source": metrics, "packaged_native_placement_vs_source": draft_metrics,
                "passed": metrics["passed"] and draft_metrics["passed"]}
            comparisons.append(comparison)
            if not comparison["passed"]:
                out = inside(REV / "qc/encoded_export_failures")
                out.mkdir(parents=True, exist_ok=True)
                actual.save(out / f"{sid}_{f:04d}_encoded.png")
                packaged.save(out / f"{sid}_{f:04d}_draft_placement.png")
            if not card["panels"]:
                continue
            before = np.asarray(packaged)
            for panel in card["panels"]:
                owner = panel["owner"]
                if not any(x["owner"] == owner and x["role"] in GRAPHICS for x in native_items.get(f, [])):
                    continue
                op = {"kind": "hide", "owner": owner}
                after = np.asarray(compose(native_items[f], decoder, (width, height), op))
                own = region_change(before, after, panel["bounds"])
                other = {p["owner"]: region_change(before, after, p["bounds"]) for p in card["panels"] if p["owner"] != owner}
                if own["changed_pixels"] == 0:
                    continue
                ok = all(v["changed_pixels"] == 0 for v in other.values())
                if ok:
                    covered_panels.add((sid, owner))
                independent.append({"card": sid, "local_frame": f, "operation": op,
                    "target_region": own, "neighbor_regions": other, "passed": ok})
                if owner not in best or own["changed_pixels"] > best[owner][0]:
                    best[owner] = (own["changed_pixels"], f, panel)
        required_owners = {l["owner"] for l in card["layers"] if l["role"] in GRAPHICS and l["owner"] != "shared"}
        required_panels.update((sid, owner) for owner in required_owners)
        require(set(best) == required_owners, (sid, "no visible independence test for some owners", sorted(required_owners-set(best))))
        if sid in {"C02", "C03"}:
            for owner, (_, f, panel) in best.items():
                before = np.asarray(compose(native_items[f], decoder, (width, height)))
                center = panel["bounds"][0]+panel["bounds"][2]/2
                others = [p for p in card["panels"] if p["owner"] != owner]
                other_center = sum(p["bounds"][0]+p["bounds"][2]/2 for p in others)/len(others)
                operations = [{"kind": "move", "owner": owner, "dx": -24 if center < other_center else 24},
                              {"kind": "scale", "owner": owner, "scale": .9}]
                for op in operations:
                    after = np.asarray(compose(native_items[f], decoder, (width, height), op))
                    own = region_change(before, after, panel["bounds"])
                    other = {p["owner"]: region_change(before, after, p["bounds"]) for p in others}
                    independent.append({"card": sid, "local_frame": f, "operation": op,
                        "target_region": own, "neighbor_regions": other,
                        "passed": own["changed_pixels"] > 0 and all(v["changed_pixels"] == 0 for v in other.values())})
        print(json.dumps({"card": sid, "encoded_reference_frames": len(frames),
            "failed_comparisons": sum(not x["passed"] for x in comparisons if x["card"] == sid)}, ensure_ascii=False), flush=True)
        decoder.cache.clear()
    require(covered_panels == required_panels, ("Some graphic panels have no passing visible hide check", sorted(required_panels-covered_panels)))
    full = selected == {c["id"] for c in storyboard["cards"]}
    passed = all(x["passed"] for x in comparisons+independent)
    return {"status": ("passed" if full else "partial_passed") if passed else "failed",
        "passed": passed, "all_16_shots": full,
        "all_information_cards": {c["id"] for c in storyboard["cards"] if c["id"].startswith("C")} <= selected,
        "cards": sorted(selected), "hidden_panel_coverage": {"required": len(required_panels), "passed": len(covered_panels), "panels": sorted(covered_panels)},
        "scope": "Final encoded graphic assets and all animation shots; source-reference comparison; actual draft placement/order; hide independence for every graphic panel; extra C02/C03 move/scale",
        "limits": LIMITS, "frame_comparisons": comparisons, "panel_independence": independent,
        "ownership": ownership, "actual_native_bindings": bindings,
        "encoded_media": decoder.bindings,
        "hashes": {"card_layers": sha(layers_path), "draft": sha(package/"draft_content.json"),
                   "package_manifest": sha(package/"manifest.json"), "verifier": sha(Path(__file__))},
        "native_text_rendering": "not_performed", "audio_validation": "not_in_this_report",
        "jianying_native_playback_export": "not_performed", "subjective_full_speed_review": "not_performed",
        "acceptance": "not_asserted; offline graphics evidence only"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--layers", default=str(REV/"card_layers.json"))
    parser.add_argument("--package", default=str(REV/"package"))
    parser.add_argument("--reference-dir", default=str(REV/"qc"))
    parser.add_argument("--report", default=str(REV/"qc/encoded_export_review.json"))
    parser.add_argument("--ffmpeg")
    parser.add_argument("--cards", nargs="+")
    parser.add_argument("--plan", action="store_true")
    args = parser.parse_args()
    storyboard = load(SOURCE/"03_storyboard/cards.json")
    shots = [c for c in storyboard["cards"] if not args.cards or c["id"] in args.cards]
    if args.plan:
        print(json.dumps({"frames_are": "local zero-based source frames", "references": {
            c["id"]: planned_frames(c) for c in shots}, "filename": "qc/reference_{sid}_{frame}.png",
            "image": "1920x1080 source SVG with all native editable text removed; opaque background retained"}, ensure_ascii=False, indent=2))
        return 0
    missing = [str(p) for p in [Path(args.layers), Path(args.package)/"manifest.json", Path(args.package)/"draft_content.json"] if not p.is_file()]
    for shot in shots:
        missing += [str(p) for f in planned_frames(shot) if not (p := reference_path(Path(args.reference_dir), shot["id"], f)).is_file()]
    if missing:
        print(json.dumps({"status": "pending_inputs", "passed": False, "missing": missing,
                          "acceptance": "not_asserted"}, ensure_ascii=False, indent=2))
        return 2
    report_path = inside(args.report)
    try:
        result = verify(args, storyboard)
    except Exception as exc:
        result = {"status": "failed", "passed": False, "error": repr(exc),
                  "verifier_sha256": sha(Path(__file__)), "acceptance": "not_asserted",
                  "jianying_native_playback_export": "not_performed"}
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "passed": result["passed"],
                      "report": str(report_path), "error": result.get("error")}, ensure_ascii=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
