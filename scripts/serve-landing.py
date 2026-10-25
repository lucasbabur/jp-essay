"""Serve the landing page and its GitHub star count using local gh authentication."""

import argparse
import json
import subprocess
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


LANDING = Path(__file__).resolve().parents[1] / "landing"
_lock = threading.Lock()
_stars = None
_refresh_at = 0


def github_stars():
    global _stars, _refresh_at
    with _lock:
        if time.monotonic() >= _refresh_at:
            try:
                result = subprocess.run(
                    ["gh", "api", "repos/lucasbabur/jp-essay", "--jq", ".stargazers_count"],
                    capture_output=True, text=True, timeout=6, check=True,
                )
                stars = int(result.stdout.strip())
                if stars < 0:
                    raise ValueError("Invalid star count")
                _stars = stars
                _refresh_at = time.monotonic() + 60
            except (OSError, ValueError, subprocess.SubprocessError):
                _refresh_at = time.monotonic() + 15
        if _stars is None:
            return None
        return {"stargazers_count": _stars}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(LANDING), **kwargs)

    def do_GET(self):
        if urlsplit(self.path).path != "/api/github-stars":
            return super().do_GET()
        payload = github_stars()
        body = json.dumps(payload or {"error": "GitHub temporarily unavailable"}).encode()
        self.send_response(200 if payload is not None else 503)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8774)
    parser.add_argument("--bind", default="0.0.0.0")
    args = parser.parse_args()
    ThreadingHTTPServer((args.bind, args.port), Handler).serve_forever()
