#!/usr/bin/env python3
"""Render this episode with local Chrome and an MJPEG pipe; no frame cache."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from fractions import Fraction
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import traceback


EPISODE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = "07_exports/HUMAN3_v46_视觉测试_1080p.mp4"
NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0


def inside_episode(value: str | Path) -> Path:
    path = Path(value)
    path = (path if path.is_absolute() else EPISODE_ROOT / path).resolve()
    if not path.is_relative_to(EPISODE_ROOT):
        raise ValueError(f"路径必须位于本测试目录内：{path}")
    return path


def read_json(relative_path: str) -> dict:
    return json.loads(inside_episode(relative_path).read_text(encoding="utf-8-sig"))


@dataclass(frozen=True)
class Config:
    width: int
    height: int
    fps: int
    total_frames: int
    audio: Path
    audio_sha256: str | None
    ffmpeg: Path
    video: dict


def load_config() -> Config:
    episode = read_json("00_brief/episode.json")
    defaults = read_json("00_brief/effective_defaults.json")
    video = defaults["video"]
    fps = int(episode["fps"])
    total_frames = int(episode["total_frames"])
    width, height = int(video["width"]), int(video["height"])
    if fps != video["fps"] or fps <= 0 or total_frames <= 0:
        raise ValueError("episode 与 effective_defaults 的帧率不一致或帧数无效")
    if width <= 0 or height <= 0 or width % 2 or height % 2:
        raise ValueError("视频宽高必须为正偶数")
    voice = episode["inputs"]["voice"]
    return Config(width, height, fps, total_frames,
                  inside_episode(voice["path"]), voice.get("sha256"),
                  Path(defaults["tools_local"]["ffmpeg"]).resolve(), video)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--still-frames", metavar="0,119,525",
                        help="全片绝对帧号；只写 08_qc/frame_XXXX.png，不编码视频")
    parser.add_argument("--output", help="MP4 输出；相对路径以本集目录为根，拒绝覆盖已有视频")
    parser.add_argument("--start-frame", type=int, default=0,
                        help="从全片的指定帧开始（默认 0）")
    parser.add_argument("--frame-count", type=int,
                        help="输出帧数（默认从起点到全片结尾）；局部视频须另设 --output")
    return parser.parse_args()


def choose_frames(args: argparse.Namespace, config: Config) -> list[int] | range:
    if args.still_frames is not None:
        if args.output is not None or args.start_frame != 0 or args.frame_count is not None:
            raise ValueError("--still-frames 不能与 --output/--start-frame/--frame-count 同用")
        fields = args.still_frames.split(",")
        if any(not field.strip() for field in fields):
            raise ValueError("--still-frames 需要逗号分隔的整数，不能含空项")
        frames = list(dict.fromkeys(int(field.strip()) for field in fields))
        if any(frame < 0 or frame >= config.total_frames for frame in frames):
            raise ValueError(f"截图帧号必须在 0..{config.total_frames - 1} 之间")
        return frames
    start = args.start_frame
    count = args.frame_count if args.frame_count is not None else config.total_frames - start
    if start < 0 or start >= config.total_frames or count <= 0 or start + count > config.total_frames:
        raise ValueError("局部渲染范围必须位于本集有效帧范围内，且帧数大于 0")
    if (start != 0 or count != config.total_frames) and args.output is None:
        raise ValueError("局部渲染须指定 --output，避免被误认作完整成片")
    return range(start, start + count)


def make_logger() -> tuple[logging.Logger, Path]:
    qc_root = inside_episode("08_qc")
    qc_root.mkdir(parents=True, exist_ok=True)
    log_path = qc_root / f"render_{datetime.now():%Y%m%d_%H%M%S_%f}_{os.getpid()}.log"
    logger = logging.getLogger("human3.render")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger, log_path


@contextmanager
def local_server(logger: logging.Logger):
    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, fmt, *args):
            # Keep routine HTTP requests out of progress output; preserve failures.
            if len(args) > 1 and str(args[1]).startswith(("4", "5")):
                logger.error("HTTP: " + fmt, *args)

    handler = partial(Handler, directory=str(EPISODE_ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, name="episode-http", daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/06_project/index.html"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


WAIT_READY_JS = """async () => {
  const timeout = new Promise((_, reject) => setTimeout(
    () => reject(new Error('window.ready / fonts / images 超过 60 秒未完成')), 60000));
  await Promise.race([(async () => {
    await window.ready;
    await document.fonts.ready;
    await Promise.all(Array.from(document.images).map(async img => {
      if (img.currentSrc || img.src) {
        await img.decode();
        if (!img.naturalWidth) throw new Error('图片未加载: ' + img.src);
      }
    }));
  })(), timeout]);
}"""

RENDER_FRAME_JS = """async frame => {
  await window.renderFrame(frame);
  await document.fonts.ready;
  await Promise.all(Array.from(document.images).map(async img => {
    if (img.currentSrc || img.src) {
      await img.decode();
      if (!img.naturalWidth) throw new Error('图片未加载: ' + img.src);
    }
  }));
  await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
}"""


def ffmpeg_command(config: Config, frames: range, output: Path) -> list[str]:
    video = config.video
    offset = frames.start / config.fps
    duration = len(frames) / config.fps
    return [
        str(config.ffmpeg), "-hide_banner", "-loglevel", "warning", "-nostats", "-n",
        "-f", "image2pipe", "-vcodec", "mjpeg", "-framerate", str(config.fps), "-i", "pipe:0",
        # Input seeking decodes to the requested time. No gain, speed, or mixing filters.
        "-ss", f"{offset:.12f}", "-t", f"{duration:.12f}", "-i", str(config.audio),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", video["video_codec"], "-crf", str(video["crf"]), "-preset", video["preset"],
        "-pix_fmt", video["pixel_format"], "-frames:v", str(len(frames)),
        "-c:a", video["audio_codec"], "-b:a", video["audio_bitrate"],
        "-movflags", "+faststart", str(output),
    ]


def verify_video(config: Config, partial_path: Path, count: int, logger: logging.Logger):
    ffprobe = config.ffmpeg.with_name("ffprobe.exe" if os.name == "nt" else "ffprobe")
    command = [str(ffprobe), "-v", "error", "-show_entries",
               "stream=codec_type,codec_name,width,height,r_frame_rate,nb_frames",
               "-of", "json", str(partial_path)]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8",
                            errors="replace", creationflags=NO_WINDOW, timeout=60, check=True)
    streams = json.loads(result.stdout)["streams"]
    video = next(stream for stream in streams if stream["codec_type"] == "video")
    if (int(video["nb_frames"]) != count or video["width"] != config.width
            or video["height"] != config.height
            or Fraction(video["r_frame_rate"]) != config.fps):
        raise RuntimeError(f"输出帧数/尺寸/帧率不匹配：{video}")
    if not any(stream["codec_type"] == "audio" for stream in streams):
        raise RuntimeError("输出缺少原配音音轨")
    logger.info("容器检查通过：%s", json.dumps(streams, ensure_ascii=False))


def render(args: argparse.Namespace, config: Config, frames, logger, log_path: Path):
    # Import only for actual rendering; --help and static validation need no browser.
    from playwright.sync_api import sync_playwright

    index = inside_episode("06_project/index.html")
    if not index.is_file():
        raise FileNotFoundError(index)
    output = partial_path = None
    if args.still_frames is None:
        output = inside_episode(args.output or DEFAULT_OUTPUT)
        if output.suffix.lower() != ".mp4" or output.name.lower().endswith(".partial.mp4"):
            raise ValueError("--output 必须是正式 .mp4 文件名，不能以 .partial.mp4 结尾")
        partial_path = output.with_name(output.stem + ".partial.mp4")
        for path in (output, partial_path):
            if path.exists():
                raise FileExistsError(f"拒绝覆盖已有文件；请指定新版本 --output：{path}")
        for required in (config.audio, config.ffmpeg, config.ffmpeg.with_name("ffprobe.exe")):
            if not required.is_file():
                raise FileNotFoundError(required)
        if config.audio_sha256:
            with config.audio.open("rb") as source_audio:
                actual_hash = hashlib.file_digest(source_audio, "sha256").hexdigest()
            if actual_hash != config.audio_sha256:
                raise ValueError("原配音 SHA-256 与 episode.json 不一致")
        output.parent.mkdir(parents=True, exist_ok=True)

    browser_errors: list[str] = []

    def page_error(error):
        browser_errors.append(str(error))
        logger.error("浏览器 JS 异常：%s", error)

    def check_browser():
        if browser_errors:
            raise RuntimeError("浏览器出现 JS 异常：" + " | ".join(browser_errors))

    started = time.monotonic()
    with local_server(logger) as url, sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True, args=[
            "--hide-scrollbars", "--force-color-profile=srgb",
            "--disable-background-timer-throttling", "--disable-renderer-backgrounding",
        ])
        try:
            page = browser.new_page(viewport={"width": config.width, "height": config.height},
                                    device_scale_factor=1)
            page.set_default_timeout(60000)
            page.on("pageerror", page_error)
            page.on("console", lambda message: logger.error("浏览器 console: %s", message.text)
                    if message.type == "error" else None)
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_function("() => typeof window.renderFrame === 'function' && "
                                   "window.ready && typeof window.ready.then === 'function'")
            page.evaluate(WAIT_READY_JS)
            check_browser()

            def capture(frame: int, image_type: str) -> bytes:
                check_browser()
                # Evaluation exceptions deliberately propagate to the run log and caller.
                page.evaluate(RENDER_FRAME_JS, frame)
                check_browser()
                options = {"type": image_type, "full_page": False, "caret": "hide"}
                if image_type == "jpeg":
                    options["quality"] = 94
                data = page.screenshot(**options)
                check_browser()
                return data

            if args.still_frames is not None:
                for frame in frames:
                    path = inside_episode(f"08_qc/frame_{frame:04d}.png")
                    path.write_bytes(capture(frame, "png"))
                    logger.info("截图：%s", path)
                    print(path, flush=True)
                return

            command = ffmpeg_command(config, frames, partial_path)
            logger.info("FFmpeg 参数：%s", json.dumps(command, ensure_ascii=False))
            print(f"开始渲染 {len(frames)} 帧；日志：{log_path}", flush=True)
            with log_path.open("ab", buffering=0) as ffmpeg_log:
                process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                           stderr=ffmpeg_log, creationflags=NO_WINDOW)
                try:
                    for index, frame in enumerate(frames, 1):
                        if process.poll() is not None:
                            raise RuntimeError(f"FFmpeg 提前退出，返回码 {process.returncode}")
                        data = capture(frame, "jpeg")
                        process.stdin.write(data)
                        if index % 300 == 0:
                            message = f"已渲染 {index}/{len(frames)} 帧，用时 {time.monotonic() - started:.1f}s"
                            logger.info(message)
                            print(message, flush=True)
                    process.stdin.close()
                    return_code = process.wait(timeout=180)
                    if return_code:
                        raise RuntimeError(f"FFmpeg 编码失败，返回码 {return_code}")
                except BaseException:
                    if process.poll() is None:
                        process.terminate()
                        try:
                            process.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait(timeout=10)
                    if process.stdin and not process.stdin.closed:
                        try:
                            process.stdin.close()
                        except (BrokenPipeError, OSError):
                            pass
                    raise
            verify_video(config, partial_path, len(frames), logger)
            if output.exists():
                raise FileExistsError(f"目标在渲染期间被创建，拒绝覆盖：{output}")
            # Windows rename is atomic and refuses an existing destination.
            os.rename(partial_path, output)
            logger.info("完成：%s；%s 帧；用时 %.1fs", output, len(frames), time.monotonic() - started)
            print(f"完成：{output}（{len(frames)} 帧）", flush=True)
        finally:
            browser.close()


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    logger = log_path = None
    try:
        config = load_config()
        frames = choose_frames(args, config)
        logger, log_path = make_logger()
        logger.info("本集根目录：%s；参数：%s", EPISODE_ROOT, vars(args))
        render(args, config, frames, logger, log_path)
        return 0
    except BaseException as error:
        if isinstance(error, SystemExit):
            raise
        if logger:
            logger.error("渲染失败，保留 partial 文件供排错：\n%s", traceback.format_exc())
        print(f"失败：{error}" + (f"\n日志：{log_path}" if log_path else ""), file=sys.stderr)
        return 130 if isinstance(error, KeyboardInterrupt) else 1
    finally:
        if logger:
            for handler in list(logger.handlers):
                handler.close()
                logger.removeHandler(handler)


if __name__ == "__main__":
    raise SystemExit(main())
