#!/usr/bin/env python3
"""healthops local server.

Serves the plan pages in ./public and stores daily-log entries in
./data/days.json (one object keyed by date, YYYY-MM-DD). Standard library
only, so there is nothing to install.

    python3 server.py                 # http://127.0.0.1:8000
    python3 server.py --port 9000
    python3 server.py --host 0.0.0.0  # reachable from your phone on home Wi-Fi
"""
import argparse
import json
import os
import re
import tempfile
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(ROOT, "public")
DATA_FILE = os.path.join(ROOT, "data", "days.json")
DATE_RE = re.compile(r"^/api/days/(\d{4}-\d{2}-\d{2})$")
MAX_BODY = 64 * 1024
LOCK = threading.Lock()


def load_days():
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_days(days):
    # Write to a temp file and rename, so a crash never leaves half a file.
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(DATA_FILE), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(days, f, indent=1, sort_keys=True)
    os.replace(tmp, DATA_FILE)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC, **kwargs)

    def send_json(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/days":
            with LOCK:
                return self.send_json(200, load_days())
        return super().do_GET()

    def do_PUT(self):
        m = DATE_RE.match(self.path)
        if not m:
            return self.send_json(404, {"error": "not found"})
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > MAX_BODY:
            return self.send_json(400, {"error": "bad body size"})
        try:
            entry = json.loads(self.rfile.read(length))
        except ValueError:
            return self.send_json(400, {"error": "invalid JSON"})
        if not isinstance(entry, dict):
            return self.send_json(400, {"error": "expected an object"})
        with LOCK:
            days = load_days()
            days[m.group(1)] = entry
            save_days(days)
        return self.send_json(200, {"ok": True})

    def log_message(self, fmt, *args):
        if "/api/" in (args[0] if args else ""):
            super().log_message(fmt, *args)


def main():
    p = argparse.ArgumentParser(description="healthops local server")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    a = p.parse_args()
    srv = ThreadingHTTPServer((a.host, a.port), Handler)
    print(f"healthops running at http://{'localhost' if a.host == '127.0.0.1' else a.host}:{a.port}")
    print(f"Log data: {DATA_FILE}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
