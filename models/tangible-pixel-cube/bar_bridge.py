"""バー画面（demo/bar.html）を配り、ブラウザからの角度指令をシリアルへ流す。Web Serial が使えないブラウザ用。

  py -3.11 models/tangible-pixel-cube/bar_bridge.py --port COM18 [--http 8124]

角度は 90 度の組み立て角から ±LIMIT 度に制限する（既定 30）。http://localhost:8124/bar.html を開く。
"""
import argparse
import re
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import serial

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
args = argparse.ArgumentParser()
args.add_argument("--port", required=True)
args.add_argument("--http", type=int, default=8124)
args.add_argument("--limit", type=float, default=30.0)
opt = args.parse_args()

link = serial.Serial(opt.port, 115200, timeout=0.05)
time.sleep(2.3)      # 接続で Arduino が再起動する
lock = threading.Lock()
SAFE = re.compile(r"^(a-?\d+(\.\d+)?\n|[+\-zw])$")


def clamp(text):
    """a<角度> を ±limit に収める。許す文字は a 指令と位相の +/-/z/w だけ"""
    if not SAFE.match(text):
        return None
    if text.startswith("a"):
        deg = max(90 - opt.limit, min(90 + opt.limit, float(text[1:])))
        return f"a{deg:.1f}\n"
    return text


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def reply(self, code, body=b"", kind="text/plain"):
        self.send_response(code)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/ping":
            self.reply(200, f"{opt.limit:g}".encode())
        elif self.path in ("/", "/bar.html"):
            self.reply(200, (HERE / "demo" / "bar.html").read_bytes(), "text/html; charset=utf-8")
        else:
            self.reply(404)

    def do_POST(self):
        text = self.rfile.read(int(self.headers.get("Content-Length", 0))).decode("ascii", "ignore")
        out = clamp(text)
        if out is None:
            self.reply(400)
            return
        with lock:
            link.write(out.encode())
        self.reply(204)


print(f"http://localhost:{opt.http}/bar.html  serial {opt.port}  limit 90±{opt.limit:g}", flush=True)
ThreadingHTTPServer(("127.0.0.1", opt.http), Handler).serve_forever()
