#!/usr/bin/env python3
"""Render this locked episode through run_stage.py, local Chrome and an MJPEG pipe."""

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
from urllib.parse import urlsplit


EPISODE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = "07_exports/HUMAN3_v47_TalkCraft_完整重制_1080p.mp4"
NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
REQUIRED_VIDEO_FIELDS = (
    "width", "height", "fps", "video_codec", "crf", "preset", "pixel_format",
    "audio_codec", "audio_bitrate",
)


def inside_episode(value: str | Path) -> Path:
    path = Path(value)
    path = (path if path.is_absolute() else EPISODE_ROOT / path).resolve()
    if not path.is_relative_to(EPISODE_ROOT):
        raise ValueError(f"路径必须位于本集目录内：{path}")
    return path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def positive_integer(value, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} 必须为正整数")
    return value


@dataclass(frozen=True)
class Config:
    width: int
    height: int
    fps: int
    total_frames: int
    audio: Path
    audio_sha256: str
    ffmpeg: Path
    browser_channel: str
    video: dict
    defaults_path: Path
    contract_path: Path
    defaults_sha256: str
    contract_sha256: str


def load_config() -> Config:
    # No direct-render fallback: these paths must be supplied by this episode's
    # locked run_stage.py after its dependency/contract preflight has passed.
    required_env = ("V5_EPISODE_ROOT", "V5_EFFECTIVE_DEFAULTS", "V5_PRODUCTION_CONTRACT", "V5_STAGE")
    missing = [name for name in required_env if not os.environ.get(name)]
    if missing:
        raise ValueError("必须通过本集锁定 run_stage.py 启动；缺少：" + ", ".join(missing))
    if Path(os.environ["V5_EPISODE_ROOT"]).resolve() != EPISODE_ROOT:
        raise ValueError("V5_EPISODE_ROOT 与渲染器所在集不一致")
    if os.environ["V5_STAGE"] != "render":
        raise ValueError("本适配器仅接受 V5_STAGE=render")
    defaults_path = inside_episode(os.environ["V5_EFFECTIVE_DEFAULTS"])
    contract_path = inside_episode(os.environ["V5_PRODUCTION_CONTRACT"])
    if defaults_path != inside_episode("00_brief/effective_defaults.json"):
        raise ValueError("V5_EFFECTIVE_DEFAULTS 必须指向本集有效配置")
    if contract_path != inside_episode("03_storyboard/production_contract.json"):
        raise ValueError("V5_PRODUCTION_CONTRACT 必须指向本集分层合同")
    episode = read_json(inside_episode("00_brief/episode.json"))
    defaults, contract = read_json(defaults_path), read_json(contract_path)
    video = defaults["video"]
    for field in REQUIRED_VIDEO_FIELDS:
        if field not in video:
            raise ValueError("缺少视频配置字段：video." + field)
    fps = positive_integer(episode["fps"], "episode.fps")
    total_frames = positive_integer(episode["total_frames"], "episode.total_frames")
    width = positive_integer(video["width"], "video.width")
    height = positive_integer(video["height"], "video.height")
    if (width, height, fps, total_frames) != (1920, 1080, 30, 1678):
        raise ValueError("本集必须为 1920×1080、30fps、1678帧；不接受静默重解释")
    if (isinstance(video["fps"], bool) or Fraction(str(video["fps"])) != fps
            or isinstance(contract["fps"], bool) or Fraction(str(contract["fps"])) != fps
            or positive_integer(contract["total_frames"], "contract.total_frames") != total_frames):
        raise ValueError("episode / effective_defaults / production_contract 帧率或总帧数不一致")
    if episode["id"] != EPISODE_ROOT.name:
        raise ValueError("episode.id 与本集目录不一致")
    if contract.get("episode_id", episode["id"]) != episode["id"]:
        raise ValueError("合同 episode_id 与本集不一致")
    if width % 2 or height % 2:
        raise ValueError("视频尺寸必须为正偶数")
    if not defaults["audio"]["preserve_provided_voice"]:
        raise ValueError("本集仅允许保留原配音")
    voice = episode["inputs"]["voice"]
    audio = inside_episode(voice["path"])
    if not audio.is_file() or digest(audio) != voice["sha256"]:
        raise ValueError("原配音文件缺失或 SHA-256 与 episode.json 不一致")
    ffmpeg = Path(defaults["tools_local"]["ffmpeg"]).resolve()
    for executable in (ffmpeg, ffmpeg.with_name("ffprobe.exe" if os.name == "nt" else "ffprobe")):
        if not executable.is_file():
            raise FileNotFoundError(executable)
    for font_field in ("regular_font", "bold_font"):
        if not Path(defaults["type"][font_field]).is_file():
            raise FileNotFoundError("字体不存在：" + defaults["type"][font_field])
    return Config(width, height, fps, total_frames, audio, voice["sha256"], ffmpeg,
                  defaults["tools_local"]["browser_channel"], video,
                  defaults_path, contract_path, digest(defaults_path), digest(contract_path))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--still-frames", metavar="0,119,525",
                        help="全片绝对帧号；只写 08_qc/frame_XXXX.png，不编码视频")
    parser.add_argument("--output", help="本集内部的 MP4 路径；拒绝覆盖已有视频")
    parser.add_argument("--start-frame", type=int, default=0)
    parser.add_argument("--frame-count", type=int,
                        help="默认从起点到全片结尾；局部视频必须另设 --output")
    parser.add_argument("--validate-config", action="store_true",
                        help="只验证 stage 环境和配置，不启动网页、Chrome或编码")
    return parser.parse_args()


def choose_frames(args: argparse.Namespace, config: Config) -> list[int] | range:
    if args.still_frames is not None:
        if args.output is not None or args.start_frame != 0 or args.frame_count is not None:
            raise ValueError("--still-frames 不能与局部视频参数或 --output 同用")
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
        raise ValueError("渲染范围必须位于本集帧区间内，且帧数大于0")
    if (start != 0 or count != config.total_frames) and args.output is None:
        raise ValueError("局部视频必须指定 --output")
    return range(start, start + count)


def make_logger() -> tuple[logging.Logger, Path]:
    qc_root = inside_episode("08_qc")
    qc_root.mkdir(parents=True, exist_ok=True)
    log_path = qc_root / f"render_{datetime.now():%Y%m%d_%H%M%S_%f}_{os.getpid()}.log"
    logger = logging.getLogger("human3.v47.render")
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
            if len(args) > 1 and str(args[1]).startswith(("4", "5")):
                logger.error("HTTP: " + fmt, *args)

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(EPISODE_ROOT)))
    thread = threading.Thread(target=server.serve_forever, name="episode-http", daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/06_project/index.html"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


WAIT_READY_JS = """async () => {
  if (!window.ready || typeof window.ready.then !== 'function')
    throw new Error('window.ready must be a Promise');
  const timeout = new Promise((_, reject) => setTimeout(
    () => reject(new Error('window.ready/fonts/images exceeded 60 seconds')), 60000));
  await Promise.race([(async () => {
    await window.ready;
    await document.fonts.ready;
    for (const font of document.fonts)
      if (font.status === 'error') throw new Error('Font load failed: ' + font.family);
    await Promise.all(Array.from(document.images).map(async img => {
      if (img.currentSrc || img.src) {
        await img.decode();
        if (!img.naturalWidth) throw new Error('Image load failed: ' + img.src);
      }
    }));
  })(), timeout]);
}"""

RENDER_FRAME_JS = """async frame => {
  await window.renderFrame(frame);
  await document.fonts.ready;
  for (const font of document.fonts)
    if (font.status === 'error') throw new Error('Font load failed: ' + font.family);
  await Promise.all(Array.from(document.images).map(async img => {
    if (img.currentSrc || img.src) {
      await img.decode();
      if (!img.naturalWidth) throw new Error('Image load failed: ' + img.src);
    }
  }));
  await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
}"""


def ffmpeg_command(config: Config, frames: range, output: Path) -> list[str]:
    video = config.video
    offset, duration = frames.start / config.fps, len(frames) / config.fps
    return [
        str(config.ffmpeg), "-hide_banner", "-loglevel", "warning", "-nostats", "-n",
        "-f", "image2pipe", "-vcodec", "mjpeg", "-framerate", str(config.fps), "-i", "pipe:0",
        # Decode the original voice from this absolute timeline offset. No
        # volume, tempo, delay, resampling or mixing filters are introduced.
        "-ss", f"{offset:.12f}", "-t", f"{duration:.12f}", "-i", str(config.audio),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", video["video_codec"], "-crf", str(video["crf"]), "-preset", video["preset"],
        "-pix_fmt", video["pixel_format"], "-frames:v", str(len(frames)),
        "-c:a", video["audio_codec"], "-b:a", video["audio_bitrate"],
        # No -shortest: the 1678th video frame must survive the slightly shorter voice.
        "-movflags", "+faststart", str(output),
    ]


def verify_video(config: Config, partial_path: Path, count: int, logger: logging.Logger) -> dict:
    ffprobe = config.ffmpeg.with_name("ffprobe.exe" if os.name == "nt" else "ffprobe")
    command = [str(ffprobe), "-v", "error", "-show_entries",
               "stream=codec_type,codec_name,width,height,pix_fmt,r_frame_rate,nb_frames,duration,start_time:format=duration",
               "-of", "json", str(partial_path)]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8",
                            errors="replace", creationflags=NO_WINDOW, timeout=60, check=True)
    probe = json.loads(result.stdout)
    streams = probe["streams"]
    video = next(stream for stream in streams if stream["codec_type"] == "video")
    if (int(video["nb_frames"]) != count or video["width"] != config.width
            or video["height"] != config.height or video["pix_fmt"] != config.video["pixel_format"]
            or Fraction(video["r_frame_rate"]) != config.fps
            or abs(float(video["duration"]) - count / config.fps) > 0.5 / config.fps):
        raise RuntimeError(f"视频帧数/尺寸/帧率/像素格式/时长不匹配：{video}")
    audio = next((stream for stream in streams if stream["codec_type"] == "audio"), None)
    if audio is None or float(audio.get("duration", 0)) <= 0:
        raise RuntimeError("输出缺少有效原配音音轨")
    expected_codec = {"libx264": "h264", "libx265": "hevc"}.get(config.video["video_codec"])
    if expected_codec and video["codec_name"] != expected_codec:
        raise RuntimeError("编码器与输出视频编码不一致")
    if config.video["audio_codec"] == "aac" and audio["codec_name"] != "aac":
        raise RuntimeError("音频编码与配置不一致")
    if abs(float(video.get("start_time", 0))) > 1 / config.fps or abs(float(audio.get("start_time", 0))) > 1 / config.fps:
        raise RuntimeError("视频或配音未在局部输出时间轴0点起始")
    logger.info("容器基本检查通过：%s", json.dumps(probe, ensure_ascii=False))
    return probe


def render(args: argparse.Namespace, config: Config, frames, logger, log_path: Path):
    from playwright.sync_api import sync_playwright

    for relative in ("06_project/index.html", "06_project/app.js"):
        if not inside_episode(relative).is_file():
            raise FileNotFoundError("页面源未完成，不启动渲染：" + relative)
    output = partial_path = None
    if args.still_frames is None:
        output = inside_episode(args.output or DEFAULT_OUTPUT)
        if output.suffix.lower() != ".mp4" or output.name.lower().endswith(".partial.mp4"):
            raise ValueError("--output 必须为正式 .mp4 文件名")
        partial_path = output.with_name(output.stem + ".partial.mp4")
        for path in (output, partial_path):
            if path.exists():
                raise FileExistsError(f"拒绝覆盖已有视频，请指定新版本 --output：{path}")
        output.parent.mkdir(parents=True, exist_ok=True)

    browser_errors: list[str] = []

    def browser_error(message):
        browser_errors.append(str(message))
        logger.error("浏览器资源或脚本错误：%s", message)

    def check_browser():
        if browser_errors:
            raise RuntimeError("浏览器资源或脚本错误：" + " | ".join(browser_errors))

    started = time.monotonic()
    with local_server(logger) as url, sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=config.browser_channel, headless=True, args=[
            "--hide-scrollbars", "--force-color-profile=srgb",
            "--disable-background-timer-throttling", "--disable-renderer-backgrounding",
        ])
        try:
            context = browser.new_context(viewport={"width": config.width, "height": config.height},
                                          device_scale_factor=1, service_workers="block")
            origin = urlsplit(url).netloc

            def local_only(route):
                parsed = urlsplit(route.request.url)
                if parsed.scheme in ("data", "blob") or (parsed.scheme == "http" and parsed.netloc == origin):
                    route.continue_()
                else:
                    browser_error("禁止外网或非本地源：" + route.request.url)
                    route.abort()

            context.route("**/*", local_only)
            page = context.new_page()
            page.set_default_timeout(60000)
            page.on("pageerror", browser_error)
            page.on("console", lambda message: browser_error("console: " + message.text)
                    if message.type == "error" else None)
            page.on("requestfailed", lambda request: browser_error(
                f"资源请求失败：{request.url} ({request.failure})"))
            page.on("response", lambda response: browser_error(
                f"HTTP {response.status}: {response.url}") if response.status >= 400 else None)
            page.goto(url, wait_until="networkidle")
            page.wait_for_function("() => typeof window.renderFrame === 'function' && "
                                   "window.ready && typeof window.ready.then === 'function'")
            page.evaluate(WAIT_READY_JS)
            check_browser()

            def capture(frame: int, image_type: str) -> bytes:
                check_browser()
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
                        process.stdin.write(capture(frame, "jpeg"))
                        if index % 300 == 0 or index == len(frames):
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
            probe = verify_video(config, partial_path, len(frames), logger)
            # Bind the report to exactly the configuration and original voice used.
            if digest(config.defaults_path) != config.defaults_sha256 or digest(config.contract_path) != config.contract_sha256:
                raise RuntimeError("渲染期间配置或合同发生变化，保留 partial 拒绝转正")
            if digest(config.audio) != config.audio_sha256:
                raise RuntimeError("渲染期间原配音发生变化，保留 partial 拒绝转正")
            if output.exists():
                raise FileExistsError(f"目标在渲染期间被创建，拒绝覆盖：{output}")
            os.rename(partial_path, output)
            report_path = inside_episode("08_qc") / (log_path.stem + ".json")
            report_path.write_text(json.dumps({
                "status": "rendered_and_container_verified",
                "scope": "machine_checks_only_subjective_av_not_performed",
                "output": str(output), "output_sha256": digest(output),
                "episode_root": str(EPISODE_ROOT), "stage": os.environ["V5_STAGE"],
                "effective_defaults": str(config.defaults_path), "effective_defaults_sha256": config.defaults_sha256,
                "production_contract": str(config.contract_path), "production_contract_sha256": config.contract_sha256,
                "audio": str(config.audio), "audio_sha256": config.audio_sha256,
                "video_parameters_consumed": {key: config.video[key] for key in REQUIRED_VIDEO_FIELDS},
                "start_frame": frames.start, "frame_count": len(frames),
                "ffmpeg_command": command, "ffprobe": probe,
                "elapsed_seconds": round(time.monotonic() - started, 3),
            }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            logger.info("完成：%s；%s帧；%.1fs；报告：%s", output, len(frames), time.monotonic() - started, report_path)
            print(f"完成：{output}（{len(frames)}帧）", flush=True)
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
        if args.validate_config:
            print(json.dumps({"configuration": "valid", "episode_root": str(EPISODE_ROOT),
                              "width": config.width, "height": config.height, "fps": config.fps,
                              "total_frames": config.total_frames,
                              "effective_defaults_sha256": config.defaults_sha256,
                              "production_contract_sha256": config.contract_sha256},
                             ensure_ascii=False, indent=2))
            return 0
        logger, log_path = make_logger()
        logger.info("本集根目录：%s；参数：%s；有效配置sha256：%s；合同sha256：%s", EPISODE_ROOT,
                    vars(args), config.defaults_sha256, config.contract_sha256)
        render(args, config, frames, logger, log_path)
        return 0
    except BaseException as error:
        if isinstance(error, SystemExit):
            raise
        if logger:
            logger.error("渲染失败；保留partial供排错：\n%s", traceback.format_exc())
        print(f"失败：{error}" + (f"\n日志：{log_path}" if log_path else ""), file=sys.stderr)
        return 130 if isinstance(error, KeyboardInterrupt) else 1
    finally:
        if logger:
            for handler in list(logger.handlers):
                handler.close()
                logger.removeHandler(handler)


if __name__ == "__main__":
    raise SystemExit(main())
