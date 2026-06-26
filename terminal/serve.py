"""Tiny static file server with no-cache headers.

The default `python -m http.server` sends cacheable responses, which
means browsers often hold onto old ES modules even after we edit the
files on disk.  This wrapper always emits Cache-Control: no-store so
every reload is fresh.
"""

from __future__ import annotations
import argparse
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


class NoCacheHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--host", default="127.0.0.1")
    args = p.parse_args()

    httpd = HTTPServer((args.host, args.port), NoCacheHandler)
    print(f"vt-term static server on http://{args.host}:{args.port}/ (no-cache)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[bye]")


if __name__ == "__main__":
    main()
