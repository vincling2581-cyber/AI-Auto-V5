"""Serve this episode's editable-source preview on the local loopback interface."""
from argparse import ArgumentParser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
import sys
import webbrowser


EPISODE_ROOT = Path(__file__).resolve().parent.parent


class PreviewHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Accept-Ranges", "bytes")
        super().end_headers()

    def send_head(self):
        # Browser audio seeks require byte ranges, including when the cache is disabled.
        self._range_remaining = None
        requested = self.headers.get("Range")
        path = Path(self.translate_path(self.path))
        if not requested or not path.is_file():
            return super().send_head()
        match = re.fullmatch(r"bytes=(\d*)-(\d*)", requested.strip())
        size = path.stat().st_size
        if match and size:
            first, last = match.groups()
            if first:
                start = int(first)
                end = min(int(last) if last else size - 1, size - 1)
            elif last and int(last) > 0:
                start, end = max(0, size - int(last)), size - 1
            else:
                start, end = size, -1
        else:
            start, end = size, -1
        if start < 0 or start >= size or end < start:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{size}")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None
        try:
            stream = path.open("rb")
        except OSError:
            self.send_error(404, "File not found")
            return None
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(str(path)))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Last-Modified", self.date_time_string(path.stat().st_mtime))
        self.end_headers()
        stream.seek(start)
        self._range_remaining = end - start + 1
        return stream

    def copyfile(self, source, outputfile):
        if self._range_remaining is None:
            return super().copyfile(source, outputfile)
        remaining = self._range_remaining
        while remaining:
            chunk = source.read(min(65536, remaining))
            if not chunk:
                break
            outputfile.write(chunk)
            remaining -= len(chunk)


def main():
    parser = ArgumentParser(description="启动 ECHO 本地源项目预览；按 Ctrl+C 关闭。")
    parser.add_argument("--port", type=int, default=0, help="监听端口，默认自动选择空闲端口")
    parser.add_argument("--open", action="store_true", help="启动后打开默认浏览器")
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error("端口必须在 0 至 65535 之间")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    entry = EPISODE_ROOT / "06_project" / "cards" / "preview.html"
    if not entry.is_file():
        parser.error(f"预览入口不存在：{entry}")
    handler = partial(PreviewHandler, directory=str(EPISODE_ROOT))
    with ThreadingHTTPServer(("127.0.0.1", args.port), handler) as server:
        url = f"http://127.0.0.1:{server.server_port}/06_project/cards/preview.html"
        print(f"项目目录：{EPISODE_ROOT}", flush=True)
        print(f"预览地址：{url}", flush=True)
        print("按 Ctrl+C 关闭；此入口预览源场景与原始配音。", flush=True)
        if args.open:
            webbrowser.open(url)
        try:
            server.serve_forever(poll_interval=0.25)
        except KeyboardInterrupt:
            print("\n预览服务已关闭。", flush=True)


if __name__ == "__main__":
    main()
