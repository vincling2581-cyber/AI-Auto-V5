"""Render only this isolated, static five-image demo. Run: python render_demo.py.

No files outside this directory are changed. --prepare prepares captions/assets
without requiring the two generated illustrations. --check checks an existing MP4.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
EPISODE = ROOT.parent.parent
FFMPEG = Path(r"D:\ffmpeg\bin\ffmpeg.exe")
FFPROBE = Path(r"D:\ffmpeg\bin\ffprobe.exe")
SOURCE_AUDIO = EPISODE / "00_brief/input/10月18日.mp3"
SOURCE_SRT = EPISODE / "00_brief/input/10月18日.srt"
PLAN = json.loads((ROOT / "demo_plan.json").read_text(encoding="utf-8-sig"))
FPS = int(PLAN["fps"])
START_FRAME, END_FRAME = PLAN["source_interval_frames"]
TOTAL_FRAMES = END_FRAME - START_FRAME
START = Fraction(START_FRAME, FPS)
END = Fraction(END_FRAME, FPS)
DURATION = END - START
SHOTS = PLAN["shots"]
OUTPUT = ROOT / "exports/demo.mp4"
COMMANDS: list[dict] = json.loads((ROOT / "qa/commands.json").read_text(encoding="utf-8")) if (ROOT / "qa/commands.json").is_file() else []


def dump(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(name: str, args: list[str | Path], binary: bool = False) -> bytes | str:
    args = [str(arg) for arg in args]
    result = subprocess.run(args, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    log = result.stderr.decode("utf-8", errors="replace")
    (ROOT / "qa" / f"{name}.log").write_text(log, encoding="utf-8")
    COMMANDS.append({"name": name, "argv": args, "returncode": result.returncode})
    dump(ROOT / "qa/commands.json", COMMANDS)
    if result.returncode:
        raise RuntimeError(f"{name} failed; see qa/{name}.log")
    return result.stdout if binary else result.stdout.decode("utf-8", errors="replace")


def ceil_fraction(value: Fraction) -> int:
    return -(-value.numerator // value.denominator)


def parse_srt_time(text: str) -> Fraction:
    hh, mm, ss, ms = map(int, re.split(r"[:,]", text))
    return Fraction(((hh * 60 + mm) * 60 + ss) * 1000 + ms, 1000)


def srt_time(seconds: Fraction) -> str:
    millis = round(seconds * 1000)
    seconds_int, ms = divmod(millis, 1000)
    minutes, sec = divmod(seconds_int, 60)
    hours, minute = divmod(minutes, 60)
    return f"{hours:02}:{minute:02}:{sec:02},{ms:03}"


def ass_frame_time(frame: int) -> str:
    # ASS uses centiseconds. Flooring a frame boundary keeps the exact same
    # set of presented 30-fps frames because 1/100 is shorter than 1/30.
    centis = frame * 100 // FPS
    seconds, cs = divmod(centis, 100)
    minutes, sec = divmod(seconds, 60)
    hours, minute = divmod(minutes, 60)
    return f"{hours}:{minute:02}:{sec:02}.{cs:02}"


def prepare() -> dict:
    for folder in ("assets", "exports", "qa"):
        (ROOT / folder).mkdir(exist_ok=True)
    previous_assets = ROOT.parent / "identity_semantic_full_20261018_v2/assets"
    copied = []
    for name in ("talk_followup", "talk_blocker", "talk_answer"):
        src = previous_assets / f"{name}.png"
        dst = ROOT / "assets" / src.name
        shutil.copy2(src, dst)
        copied.append({"source": str(src), "copy": str(dst), "sha256": sha256(dst)})

    cues = []
    discarded_no_frame = []
    text = SOURCE_SRT.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = block.splitlines()
        match = re.fullmatch(r"(\d\d:\d\d:\d\d,\d{3}) --> (\d\d:\d\d:\d\d,\d{3})", lines[1])
        if match is None:
            raise ValueError(f"Unrecognized SRT timing: {lines[1]}")
        absolute_start, absolute_end = map(parse_srt_time, match.groups())
        relative_start = max(absolute_start, START) - START
        relative_end = min(absolute_end, END) - START
        if relative_end <= relative_start:
            continue
        first_frame = max(0, ceil_fraction(relative_start * FPS))
        stop_frame = min(TOTAL_FRAMES, ceil_fraction(relative_end * FPS))
        if first_frame >= stop_frame:
            discarded_no_frame.append({"source_cue": int(lines[0]), "text": "\n".join(lines[2:])})
            continue
        cues.append({
            "source_cue": int(lines[0]),
            "text": "\n".join(lines[2:]),
            "relative_start": float(relative_start),
            "relative_end": float(relative_end),
            "first_frame": first_frame,
            "stop_frame_exclusive": stop_frame,
            "srt_start": srt_time(relative_start),
            "srt_end": srt_time(relative_end),
        })

    srt = "\n\n".join(
        f"{index}\n{cue['srt_start']} --> {cue['srt_end']}\n{cue['text']}"
        for index, cue in enumerate(cues, 1)
    ) + "\n"
    (ROOT / "subtitles.srt").write_text(srt, encoding="utf-8-sig")
    ass = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Microsoft YaHei,44,&H00FFFFFF,&H00FFFFFF,&H00151515,&H80000000,-1,0,0,0,100,100,0,0,1,2.5,0,2,80,80,46,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    for cue in cues:
        escaped = cue["text"].replace("\\", "\\\\").replace("{", r"\{").replace("}", r"\}").replace("\n", r"\N")
        ass += f"Dialogue: 0,{ass_frame_time(cue['first_frame'])},{ass_frame_time(cue['stop_frame_exclusive'])},Default,,0,0,0,,{escaped}\n"
    (ROOT / "subtitles.ass").write_text(ass, encoding="utf-8-sig")

    manifest = {
        "source_audio": str(SOURCE_AUDIO), "source_audio_sha256": sha256(SOURCE_AUDIO),
        "source_srt": str(SOURCE_SRT), "source_srt_sha256": sha256(SOURCE_SRT),
        "source_interval_frames": [START_FRAME, END_FRAME],
        "source_interval_seconds": [float(START), float(END)],
        "duration_seconds": float(DURATION), "fps": FPS, "total_frames": TOTAL_FRAMES,
        "copied_assets": copied, "captions": cues,
        "intersecting_cues_with_no_presented_frame": discarded_no_frame,
        "caption_note": "Original wording retained. Cue 23 has only a 0.333 ms intersection after the last presented video frame and is omitted. ASS endpoints are quantized to preserve original visible 30-fps frames.",
        "audio_processing": "Decoded original MP3, exact integer sample trim, timestamp reset only. No atempo, resampling, volume, loudness, BGM or SFX. One AAC encode in the final MP4.",
        "subjective_normal_speed_av_review": "not_performed",
    }
    dump(ROOT / "qa/preparation.json", manifest)
    return manifest


def render() -> dict:
    missing = [shot["id"] for shot in SHOTS if not (ROOT / "assets" / f"{shot['id']}.png").is_file()]
    if missing:
        raise FileNotFoundError("Missing real illustrations: " + ", ".join(missing))
    probe = json.loads(run("source_audio_probe", [FFPROBE, "-v", "error", "-show_streams", "-of", "json", SOURCE_AUDIO]))
    source_audio_stream = next(s for s in probe["streams"] if s["codec_type"] == "audio")
    sample_rate = int(source_audio_stream["sample_rate"])
    start_sample, end_sample = START * sample_rate, END * sample_rate
    assert start_sample.denominator == end_sample.denominator == 1
    args: list[str | Path] = [FFMPEG, "-hide_banner", "-y", "-loglevel", "info"]
    filters = []
    assets = []
    expected_start = 0
    for index, shot in enumerate(SHOTS):
        assert shot["start_frame"] == expected_start
        length = shot["end_frame_exclusive"] - shot["start_frame"]
        assert 0 < length <= 60
        expected_start = shot["end_frame_exclusive"]
        path = ROOT / "assets" / f"{shot['id']}.png"
        with Image.open(path) as pic:
            size = list(pic.size)
        assets.append({"id": shot["id"], "path": str(path), "sha256": sha256(path), "source_size": size, "frames": length})
        args.extend(["-loop", "1", "-framerate", str(FPS), "-i", path])
        filters.append(f"[{index}:v]scale=1920:1080:flags=lanczos,setsar=1,format=yuv420p,trim=end_frame={length},setpts=N/({FPS}*TB)[v{index}]")
    assert expected_start == TOTAL_FRAMES == PLAN["total_frames"]
    args.extend(["-i", SOURCE_AUDIO])
    video_inputs = "".join(f"[v{i}]" for i in range(len(SHOTS)))
    filters.append(f"{video_inputs}concat=n={len(SHOTS)}:v=1:a=0,ass=filename=subtitles.ass[v]")
    filters.append(f"[{len(SHOTS)}:a]atrim=start_sample={int(start_sample)}:end_sample={int(end_sample)},asetpts=PTS-STARTPTS[a]")
    graph = ";\n".join(filters)
    (ROOT / "render_filter.txt").write_text(graph + "\n", encoding="utf-8")
    args.extend([
        "-filter_complex_script", ROOT / "render_filter.txt", "-map", "[v]", "-map", "[a]",
        "-frames:v", str(TOTAL_FRAMES), "-r", str(FPS), "-fps_mode", "cfr",
        "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-tune", "stillimage",
        "-x264-params", "keyint=300:min-keyint=300:scenecut=0", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "320k", "-ar", str(sample_rate),
        "-movie_timescale", str(sample_rate), "-movflags", "+faststart", OUTPUT,
    ])
    render_manifest = {
        "assets": assets,
        "source_audio_sample_rate": sample_rate,
        "source_audio_channels": int(source_audio_stream["channels"]),
        "audio_source_sample_interval": [int(start_sample), int(end_sample)],
        "audio_source_sample_count": int(end_sample - start_sample),
        "video_graph": graph,
        "video_policy": "Five static full-frame images; a single time-invariant spatial scale per image; concat hard cuts; fixed subtitles only.",
        "aac_encodes": 1,
    }
    dump(ROOT / "qa/render_manifest.json", render_manifest)
    run("render", args)
    return render_manifest


def audio_window_lag(reference: np.ndarray, decoded: np.ndarray, center: int) -> dict:
    first = center - 2048
    last = center + 2048
    ref = reference[first:last]
    best = (-2.0, 0)
    for lag in range(-128, 129):
        got = decoded[first + lag:last + lag]
        score = float(np.dot(ref, got) / np.sqrt(np.dot(ref, ref) * np.dot(got, got)))
        if score > best[0]:
            best = (score, lag)
    return {"reference_center_sample": center, "best_lag_samples": best[1], "correlation": best[0]}


def check() -> dict:
    manifest = json.loads((ROOT / "qa/render_manifest.json").read_text(encoding="utf-8"))
    probe = json.loads(run("output_probe", [FFPROBE, "-v", "error", "-count_frames", "-show_streams", "-show_format", "-of", "json", OUTPUT]))
    dump(ROOT / "qa/output_probe.json", probe)
    video = next(s for s in probe["streams"] if s["codec_type"] == "video")
    audio = next(s for s in probe["streams"] if s["codec_type"] == "audio")
    structure_ok = (
        int(video["nb_read_frames"]) == TOTAL_FRAMES
        and (int(video["width"]), int(video["height"])) == (1920, 1080)
        and Fraction(video["avg_frame_rate"]) == FPS
        and abs(float(video["duration"]) - float(DURATION)) < 0.00001
        and int(audio["sample_rate"]) == manifest["source_audio_sample_rate"]
        and int(audio["channels"]) == manifest["source_audio_channels"]
        and abs(float(audio["duration"]) - float(DURATION)) < 1 / manifest["source_audio_sample_rate"]
    )

    # Decodes all video frames; upper 864 pixels exclude the fixed bottom caption.
    raw = run("decode_subject_region", [FFMPEG, "-v", "error", "-i", OUTPUT, "-map", "0:v:0", "-an", "-vf", "crop=1920:864:0:0,scale=480:216:flags=area,format=gray", "-fps_mode", "passthrough", "-f", "rawvideo", "-"], binary=True)
    subjects = np.frombuffer(raw, dtype=np.uint8).reshape((-1, 216, 480))
    subject_checks = []
    boundary_changes = []
    for shot in SHOTS:
        first, stop = shot["start_frame"], shot["end_frame_exclusive"]
        frames = subjects[first:stop]
        difference = np.abs(frames.astype(np.int16) - frames[0].astype(np.int16))
        frame_mae = difference.mean(axis=(1, 2))
        result = {"id": shot["id"], "start_frame": first, "end_frame_exclusive": stop,
                  "frames": stop - first, "seconds": (stop - first) / FPS,
                  "decoded_subject_unique_hashes": len({hashlib.sha256(frame.tobytes()).hexdigest() for frame in frames}),
                  "max_subject_mae_luma_0_255": float(frame_mae.max()),
                  "max_subject_p99_difference_luma": float(np.percentile(difference, 99)),
                  "passed": bool(stop - first <= 60 and frame_mae.max() <= 0.8 and np.percentile(difference, 99) <= 3)}
        subject_checks.append(result)
        if first:
            mae = float(np.abs(subjects[first].astype(np.int16) - subjects[first - 1].astype(np.int16)).mean())
            boundary_changes.append({"frame": first, "subject_mae_luma": mae, "passed": mae > 3})
    subject_ok = len(subjects) == TOTAL_FRAMES and all(s["passed"] for s in subject_checks) and all(b["passed"] for b in boundary_changes)

    sample_rate = manifest["source_audio_sample_rate"]
    channels = manifest["source_audio_channels"]
    start_sample, end_sample = manifest["audio_source_sample_interval"]
    sample_count = end_sample - start_sample
    ref_bytes = run("decode_audio_reference", [FFMPEG, "-v", "error", "-i", SOURCE_AUDIO, "-af", f"atrim=start_sample={start_sample}:end_sample={end_sample},asetpts=PTS-STARTPTS", "-f", "f32le", "-acodec", "pcm_f32le", "-"], binary=True)
    got_bytes = run("decode_audio_output", [FFMPEG, "-v", "error", "-i", OUTPUT, "-vn", "-af", f"atrim=end_sample={sample_count}", "-f", "f32le", "-acodec", "pcm_f32le", "-"], binary=True)
    reference = np.frombuffer(ref_bytes, dtype="<f4").reshape((-1, channels)).astype(np.float64)
    decoded = np.frombuffer(got_bytes, dtype="<f4").reshape((-1, channels)).astype(np.float64)
    sample_counts_ok = len(reference) == len(decoded) == sample_count
    rms_reference = float(np.sqrt(np.mean(reference ** 2)))
    rms_decoded = float(np.sqrt(np.mean(decoded ** 2)))
    gain_db = float(20 * np.log10(rms_decoded / rms_reference))
    overall_correlation = float(np.corrcoef(reference.ravel(), decoded.ravel())[0, 1])
    mono_reference, mono_decoded = reference.mean(axis=1), decoded.mean(axis=1)
    windows = [audio_window_lag(mono_reference, mono_decoded, int(sample_count * position)) for position in (0.1, 0.5, 0.9)]
    lags = [window["best_lag_samples"] for window in windows]
    audio_ok = (sample_counts_ok and overall_correlation > 0.98 and abs(gain_db) < 0.1
                and max(lags) - min(lags) <= 1 and max(map(abs, lags)) <= 1
                and all(window["correlation"] > 0.98 for window in windows))
    audio_check = {
        "source_sample_interval": [start_sample, end_sample], "expected_sample_count": sample_count,
        "reference_samples_per_channel": len(reference), "output_compared_samples_per_channel": len(decoded),
        "sample_rate": sample_rate, "channels": channels,
        "source_trim_duration_seconds": sample_count / sample_rate,
        "output_audio_stream_duration_seconds": float(audio["duration"]),
        "overall_correlation": overall_correlation, "aac_rms_gain_difference_db": gain_db,
        "alignment_windows": windows, "lag_drift_samples": max(lags) - min(lags),
        "processing_filters": "atrim,asetpts only; one final AAC encode",
        "passed": bool(audio_ok),
    }
    result = {
        "passed": bool(structure_ok and subject_ok and audio_ok),
        "structure_passed": bool(structure_ok), "full_video_and_audio_decode_passed": True,
        "output": str(OUTPUT), "output_sha256": sha256(OUTPUT), "output_bytes": OUTPUT.stat().st_size,
        "width": int(video["width"]), "height": int(video["height"]),
        "fps": video["avg_frame_rate"], "decoded_video_frames": len(subjects),
        "duration_seconds": float(video["duration"]), "shot_count": len(SHOTS),
        "static_subject_region": {"crop": [0, 0, 1920, 864], "analysis_size": [480, 216],
                                  "note": "Lossy H.264 may create small pixel differences. Source graph is time-invariant; thresholds test compression-scale changes in the subject region.",
                                  "passed": bool(subject_ok), "shots": subject_checks, "hard_cut_boundaries": boundary_changes},
        "audio": audio_check,
        "normal_speed_subjective_av_review": "not_performed",
        "native_editor_open_or_export": "not_performed",
    }
    dump(ROOT / "qa/check_results.json", result)
    if not result["passed"]:
        raise RuntimeError("Demo QA failed; see qa/check_results.json")
    return result


def render_baseline() -> dict:
    """Same source three-image composition, captions, and verified AAC packets."""
    output = ROOT / "exports/baseline.mp4"
    shots = [
        {"id": "talk_followup", "start_frame": 0, "end_frame_exclusive": 70},
        {"id": "talk_blocker", "start_frame": 70, "end_frame_exclusive": 155},
        {"id": "talk_answer", "start_frame": 155, "end_frame_exclusive": 251},
    ]
    filters = []
    args: list[str | Path] = [FFMPEG, "-hide_banner", "-y", "-loglevel", "info"]
    for index, shot in enumerate(shots):
        args.extend(["-loop", "1", "-framerate", str(FPS), "-i", ROOT / "assets" / f"{shot['id']}.png"])
        length = shot["end_frame_exclusive"] - shot["start_frame"]
        filters.append(f"[{index}:v]scale=1920:1080:flags=lanczos,setsar=1,format=yuv420p,trim=end_frame={length},setpts=N/({FPS}*TB)[v{index}]")
    filters.append("[v0][v1][v2]concat=n=3:v=1:a=0,ass=filename=subtitles.ass[v]")
    graph_path = ROOT / "baseline_filter.txt"
    graph_path.write_text(";\n".join(filters) + "\n", encoding="utf-8")
    args.extend([
        "-i", OUTPUT, "-filter_complex_script", graph_path, "-map", "[v]", "-map", "3:a:0",
        "-frames:v", str(TOTAL_FRAMES), "-r", str(FPS), "-fps_mode", "cfr",
        "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-tune", "stillimage",
        "-x264-params", "keyint=300:min-keyint=300:scenecut=0", "-pix_fmt", "yuv420p",
        "-c:a", "copy", "-movie_timescale", "44100", "-movflags", "+faststart", output,
    ])
    run("render_baseline", args)
    probe = json.loads(run("baseline_probe", [FFPROBE, "-v", "error", "-count_frames", "-show_streams", "-of", "json", output]))
    dump(ROOT / "qa/baseline_probe.json", probe)
    video = next(s for s in probe["streams"] if s["codec_type"] == "video")
    run("baseline_full_decode", [FFMPEG, "-v", "error", "-i", output, "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "-"])
    packets = []
    for tag, path in (("demo", OUTPUT), ("baseline", output)):
        data = run(f"{tag}_aac_packets", [FFMPEG, "-v", "error", "-i", path, "-map", "0:a:0", "-c:a", "copy", "-f", "adts", "-"], binary=True)
        packets.append(hashlib.sha256(data).hexdigest())
    result = {
        "passed": int(video["nb_read_frames"]) == TOTAL_FRAMES and Fraction(video["avg_frame_rate"]) == FPS
                  and (int(video["width"]), int(video["height"])) == (1920, 1080)
                  and abs(float(video["duration"]) - float(DURATION)) < 0.00001 and packets[0] == packets[1],
        "output": str(output), "sha256": sha256(output), "output_bytes": output.stat().st_size,
        "frames": int(video["nb_read_frames"]), "duration_seconds": float(video["duration"]), "shots": shots,
        "audio": "AAC packets copied from verified demo.mp4; no additional AAC encode",
        "demo_aac_packets_sha256": packets[0], "baseline_aac_packets_sha256": packets[1],
        "full_video_and_audio_decode_passed": True,
        "normal_speed_subjective_av_review": "not_performed",
    }
    dump(ROOT / "qa/baseline_check_results.json", result)
    if not result["passed"]:
        raise RuntimeError("Baseline QA failed; see qa/baseline_check_results.json")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--baseline", action="store_true", help="Also render the original three-image comparison")
    parser.add_argument("--baseline-only", action="store_true", help="Render only the three-image comparison using existing demo audio")
    args = parser.parse_args()
    if args.baseline_only:
        result = render_baseline()
        print(json.dumps({key: result[key] for key in ("passed", "output", "frames", "duration_seconds")}, ensure_ascii=False))
        return
    if args.check:
        result = check()
    else:
        prepare()
        if args.prepare:
            missing = [shot["id"] for shot in SHOTS if not (ROOT / "assets" / f"{shot['id']}.png").is_file()]
            print(json.dumps({"prepared": True, "missing_real_illustrations": missing}, ensure_ascii=False))
            return
        render()
        result = check()
    if args.baseline:
        render_baseline()
    print(json.dumps({key: result[key] for key in ("passed", "output", "decoded_video_frames", "duration_seconds", "shot_count", "normal_speed_subjective_av_review")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
