"""Package the isolated C04 comparison. All writes stay inside V5/exports.

Run only after the final trial render is complete. Uses existing FFmpeg and
Pillow. PCM source samples are compared directly; AAC is encoded once and reused.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import struct
import subprocess
from datetime import datetime, timedelta, timezone
from fractions import Fraction
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
EXPECTED_ROOT = Path("D:/AI-Auto-V5（Codex+AE）/card_motion_trial_v1").resolve()
OUT = ROOT / "exports"
FPS, START, END = 30, 864, 1142
FRAMES = END - START
DURATION = Fraction(FRAMES, FPS)
REPORT: dict = {"status": "running", "checks": []}


def require(ok: bool, name: str, detail=None):
    REPORT["checks"].append({"name": name, "passed": bool(ok), "detail": detail})
    if not ok:
        raise RuntimeError(f"{name}: {detail}")


def output(name: str) -> Path:
    target = (OUT / name).resolve()
    if ROOT != EXPECTED_ROOT or not target.is_relative_to(ROOT):
        raise RuntimeError(f"Output must stay in the V5 trial: {target}")
    if target.parent != OUT.resolve():
        raise RuntimeError(f"Unexpected output location: {target}")
    return target


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def run(args: list[str | Path]) -> bytes:
    result = subprocess.run(
        [str(arg) for arg in args], cwd=OUT, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace")[-6000:])
    return result.stdout


def probe(path: Path, count_frames=False) -> dict:
    args = [FFPROBE, "-v", "error"]
    if count_frames:
        args += ["-count_frames"]
    args += ["-show_streams", "-show_format", "-of", "json", path]
    return json.loads(run(args))


def packet_signature(path: Path, selector: str) -> dict:
    info = json.loads(run([
        FFPROBE, "-v", "error", "-select_streams", selector,
        "-show_packets", "-show_data_hash", "sha256",
        "-show_entries", "packet=data_hash,size,pts,dts,duration",
        "-of", "json", path,
    ]))
    packets = info.get("packets", [])
    require(bool(packets) and all(p.get("data_hash") for p in packets),
            f"packet_hashes_available:{path.name}:{selector}")
    encoded = json.dumps(packets, sort_keys=True, separators=(",", ":")).encode()
    return {"packet_count": len(packets),
            "payload_and_timing_sha256": hashlib.sha256(encoded).hexdigest()}


def riff_pcm(path: Path) -> dict:
    """Read PCM WAV metadata without decoding, so the sample comparison is independent."""
    with path.open("rb") as handle:
        header = handle.read(12)
        if header[:4] != b"RIFF" or header[8:] != b"WAVE":
            raise RuntimeError(f"Expected an ordinary PCM RIFF/WAVE file: {path}")
        fmt = None
        data = None
        file_size = path.stat().st_size
        while handle.tell() + 8 <= file_size:
            chunk_id, size = struct.unpack("<4sI", handle.read(8))
            offset = handle.tell()
            if offset + size > file_size:
                raise RuntimeError(f"Truncated WAV chunk in {path}")
            if chunk_id == b"fmt ":
                if size < 16 or size > 4096:
                    raise RuntimeError("Unsupported WAV fmt chunk")
                raw = handle.read(size)
                kind, channels, rate, _, align, bits = struct.unpack("<HHIIHH", raw[:16])
                if kind == 0xFFFE:
                    if len(raw) < 40:
                        raise RuntimeError("Invalid extensible WAV header")
                    kind = struct.unpack("<H", raw[24:26])[0]
                if kind not in (1, 3):
                    raise RuntimeError("Sample-exact comparison requires uncompressed PCM")
                fmt = {"format_code": kind, "channels": channels,
                       "sample_rate": rate, "block_align": align, "bits_per_sample": bits}
            elif chunk_id == b"data":
                data = {"data_offset": offset, "data_bytes": size}
            if fmt is not None and data is not None:
                if data["data_bytes"] % fmt["block_align"]:
                    raise RuntimeError("WAV data does not end on a complete sample frame")
                return {**fmt, **data,
                        "sample_frames": data["data_bytes"] // fmt["block_align"]}
            handle.seek(offset + size + (size % 2))
    raise RuntimeError(f"Missing WAV fmt/data chunk: {path}")


def pcm_range_hash(path: Path, fmt: dict, start: int, count: int) -> str:
    digest = hashlib.sha256()
    remaining = count * fmt["block_align"]
    with path.open("rb") as handle:
        handle.seek(fmt["data_offset"] + start * fmt["block_align"])
        while remaining:
            block = handle.read(min(remaining, 1024 * 1024))
            if not block:
                raise RuntimeError(f"Unexpected end of PCM samples: {path}")
            digest.update(block)
            remaining -= len(block)
    return digest.hexdigest()


def mux_audio(video: Path, audio: Path, dest: Path):
    # No -shortest/-t: retain every AAC packet, including its encoder-delay metadata.
    run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", video,
         "-i", audio, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
         "-c:a", "copy", "-map_metadata", "-1", "-movflags", "+faststart", dest])


def inspect_video(path: Path, width: int, height: int, audio_count: int) -> dict:
    info = probe(path, count_frames=True)
    videos = [s for s in info["streams"] if s["codec_type"] == "video"]
    audios = [s for s in info["streams"] if s["codec_type"] == "audio"]
    require(len(videos) == 1 and len(audios) == audio_count,
            f"stream_inventory:{path.name}", {"video": len(videos), "audio": len(audios)})
    video = videos[0]
    require(int(video["nb_read_frames"]) == FRAMES, f"frame_count:{path.name}", video["nb_read_frames"])
    require((video["width"], video["height"]) == (width, height), f"dimensions:{path.name}")
    require(Fraction(video["avg_frame_rate"]) == FPS, f"frame_rate:{path.name}")
    actual = Fraction(int(video["duration_ts"])) * Fraction(video["time_base"])
    require(actual == DURATION, f"video_duration:{path.name}", str(actual))
    if audios:
        audio = audios[0]
        require(audio["codec_name"] == "aac" and int(audio["sample_rate"]) == SAMPLE_RATE,
                f"audio_format:{path.name}")
        require(abs(float(audio.get("start_time", 0))) <= 1 / SAMPLE_RATE,
                f"audio_starts_at_zero:{path.name}")
        # AAC uses blocks and MP4 edit-list timing; the source PCM remains the exact cut.
        require(abs(float(audio["duration"]) - float(DURATION)) <= 0.002,
                f"audio_duration:{path.name}", audio["duration"])
    return {"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size,
            "sha256": sha(path), "streams": info["streams"], "format": info["format"]}


def main():
    global FFMPEG, FFPROBE, SAMPLE_RATE
    require(ROOT == EXPECTED_ROOT, "isolated_v5_root", str(ROOT))
    output("preview_check.json")  # Resolve symlinks before making any output directory.
    OUT.mkdir(parents=True, exist_ok=True)
    cfg = json.loads((ROOT / "baseline/00_brief/effective_defaults.json").read_text(encoding="utf-8"))
    FFMPEG = cfg.get("tools_local", {}).get("ffmpeg") or shutil.which("ffmpeg")
    if not FFMPEG or not Path(FFMPEG).is_file():
        raise RuntimeError("Existing ffmpeg executable not found")
    FFPROBE = str(Path(FFMPEG).with_name("ffprobe.exe"))
    if not Path(FFPROBE).is_file():
        FFPROBE = shutil.which("ffprobe")
    if not FFPROBE:
        raise RuntimeError("Existing ffprobe executable not found")

    source_audio = ROOT / "baseline/01_audio/mixed_audio.wav"
    original = ROOT / "baseline/06_project/render/C04.mp4"
    upgraded = ROOT / "episode/06_project/render/C04.mp4"
    sources = [source_audio, original, upgraded]
    for path in sources:
        require(path.resolve().is_relative_to(ROOT) and path.is_file(), "input_in_v5", str(path))
    before = {str(p.relative_to(ROOT)): sha(p) for p in sources}
    REPORT.update({
        "created_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "global_frame_range": [START, END], "end_exclusive": True,
        "frame_count": FRAMES, "fps": FPS, "duration_fraction": str(DURATION),
        "source_sha256": before,
        "perceptual_review": {"full_speed_viewing": "not_performed", "listening": "not_performed"},
    })
    REPORT["input_video_checks"] = [inspect_video(original, 1920, 1080, 0),
                                    inspect_video(upgraded, 1920, 1080, 0)]
    render_check = ROOT / "episode/08_qc/cards/C04/render_check.json"
    require(render_check.is_file(), "final_render_report_present")
    rendered = json.loads(render_check.read_text(encoding="utf-8"))
    require(rendered.get("sha256") == before[str(upgraded.relative_to(ROOT))],
            "final_render_sha256_matches_report")

    audio_info = probe(source_audio)
    source_stream = next(s for s in audio_info["streams"] if s["codec_type"] == "audio")
    SAMPLE_RATE = int(source_stream["sample_rate"])
    sample_start = Fraction(START * SAMPLE_RATE, FPS)
    sample_end = Fraction(END * SAMPLE_RATE, FPS)
    require(sample_start.denominator == sample_end.denominator == 1,
            "frame_boundaries_are_integer_audio_samples", {"start": str(sample_start), "end": str(sample_end)})
    first, last = int(sample_start), int(sample_end)
    count = last - first
    codec = source_stream["codec_name"]
    require(codec in {"pcm_u8", "pcm_s16le", "pcm_s24le", "pcm_s32le", "pcm_s64le", "pcm_f32le", "pcm_f64le"},
            "supported_native_pcm_codec", codec)
    source_fmt = riff_pcm(source_audio)
    require(source_fmt["sample_rate"] == SAMPLE_RATE and source_fmt["sample_frames"] >= last,
            "source_pcm_covers_requested_range")
    source_samples_hash = pcm_range_hash(source_audio, source_fmt, first, count)
    pcm = output("C04_source_pcm.wav")
    run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", source_audio,
         "-map", "0:a:0", "-af", f"atrim=start_sample={first}:end_sample={last},asetpts=PTS-STARTPTS",
         "-c:a", codec, pcm])
    cut_fmt = riff_pcm(pcm)
    for key in ("sample_rate", "channels", "block_align", "bits_per_sample", "format_code"):
        require(source_fmt[key] == cut_fmt[key], f"pcm_format_preserved:{key}")
    require(cut_fmt["sample_frames"] == count, "pcm_sample_count_exact", count)
    cut_samples_hash = pcm_range_hash(pcm, cut_fmt, 0, count)
    require(cut_samples_hash == source_samples_hash, "pcm_samples_bit_identical_to_source_range")
    REPORT["audio_cut"] = {
        "sample_rate_from_ffprobe": SAMPLE_RATE, "native_codec": codec,
        "start_sample": first, "end_sample_exclusive": last, "sample_frames": count,
        "source_range_pcm_sha256": source_samples_hash, "cut_pcm_sha256": cut_samples_hash,
        "duration_fraction": str(Fraction(count, SAMPLE_RATE)),
        "pcm_is_lossless_source_slice": True, "aac_is_lossy_encoded_once": True,
    }
    print(f"PCM exact cut verified: {SAMPLE_RATE} Hz, samples [{first}, {last})", flush=True)

    aac = output("C04_shared_audio.m4a")
    run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", pcm,
         "-map", "0:a:0", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", aac])
    old_out = output("C04_original_with_audio.mp4")
    new_out = output("C04_upgraded_with_audio.mp4")
    mux_audio(original, aac, old_out)
    mux_audio(upgraded, aac, new_out)
    print("Original and upgraded previews muxed with the same AAC stream.", flush=True)

    labels = output("comparison_labels.png")
    image = Image.new("RGB", (1920, 60), "#E7ECE5")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(cfg["type"]["bold_font"], 29)
    draw.text((480, 30), "原版", fill="#12251A", font=font, anchor="mm")
    draw.text((1440, 30), "动效试样", fill="#12251A", font=font, anchor="mm")
    draw.line((960, 10, 960, 50), fill="#BAC5BB", width=2)
    image.save(labels)
    silent = output("comparison_video_only.mp4")
    filt = (
        "[0:v]scale=960:540:flags=lanczos,setsar=1[left];"
        "[1:v]scale=960:540:flags=lanczos,setsar=1[right];"
        "[left][right]hstack=inputs=2[panels];"
        "[2:v]scale=1920:60:out_color_matrix=bt709:out_range=tv,format=yuv420p[labels];"
        "[labels][panels]vstack=inputs=2,format=yuv420p[v]"
    )
    print("Rendering 1920x600 side-by-side comparison (278 frames).", flush=True)
    run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", original,
         "-i", upgraded, "-loop", "1", "-framerate", str(FPS), "-i", labels,
         "-filter_complex", filt, "-map", "[v]", "-an", "-frames:v", str(FRAMES),
         "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "17",
         "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
         "-colorspace", "bt709", "-color_range", "tv", "-movflags", "+faststart", silent])
    comparison = output("comparison.mp4")
    mux_audio(silent, aac, comparison)

    REPORT["outputs"] = [inspect_video(old_out, 1920, 1080, 1),
                         inspect_video(new_out, 1920, 1080, 1),
                         inspect_video(comparison, 1920, 600, 1)]
    reference_signature = packet_signature(aac, "a:0")
    signatures = {"C04_shared_audio.m4a": reference_signature}
    for dest in (old_out, new_out, comparison):
        signature = packet_signature(dest, "a:0")
        signatures[dest.name] = signature
        require(signature == reference_signature, f"identical_aac_packets_and_timing:{dest.name}")
        run([FFMPEG, "-v", "error", "-i", dest, "-f", "null", "-"])
        require(True, f"complete_av_decode:{dest.name}")
    REPORT["aac_packet_signatures"] = signatures
    for source, dest in ((original, old_out), (upgraded, new_out), (silent, comparison)):
        require(packet_signature(source, "v:0") == packet_signature(dest, "v:0"),
                f"video_stream_copy_preserved:{dest.name}")
    require(before == {str(p.relative_to(ROOT)): sha(p) for p in sources}, "all_inputs_unchanged")
    REPORT["status"] = "passed"
    print("Preview package and stream/sample checks passed.", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        REPORT["status"] = "failed"
        REPORT["error"] = str(exc)
        raise
    finally:
        if ROOT == EXPECTED_ROOT and OUT.is_dir() and OUT.resolve().is_relative_to(ROOT):
            output("preview_check.json").write_text(
                json.dumps(REPORT, ensure_ascii=False, indent=2), encoding="utf-8")
