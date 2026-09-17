#!/usr/bin/env python3
"""Local demo server for the Northwind Widgets fixture site.

It is Python's standard-library ``http.server`` with four extra routes that let
you exercise the crawler's awkward-case handling without needing a real
broken website:

    /redirect    302 -> /about.html            (redirect handling)
    /broken      500 with an HTML error body   (page that fails to load)
    /download.pdf  200 application/pdf         (non-HTML response)
    /slow        sleeps 20s before answering   (navigation timeout)
    /empty       200 text/html with no content (empty page)

Usage
-----
    python3 examples/serve_demo.py --port 8765 --root examples/demo-site

Do not use this in production. It binds to 127.0.0.1 only.
"""
from __future__ import annotations

import argparse
import functools
import http.server
import os
import socketserver
import sys
import time


class DemoHandler(http.server.SimpleHTTPRequestHandler):
    server_version = "NorthwindDemo/1.0"

    def _send_text(self, code: int, body: str, content_type: str = "text/html; charset=utf-8") -> None:
        payload = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(payload)

    def _dispatch_extra(self, method: str) -> bool:
        """Answer the fixture's special routes for GET and HEAD. True if handled."""
        path = self.path.split("?", 1)[0]

        if path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/about.html")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return True

        if path == "/broken":
            self._send_text(
                500,
                "<!DOCTYPE html><html lang='en'><head><title>Portal error</title></head>"
                "<body><h1>Customer portal is unavailable</h1></body></html>",
            )
            return True

        if path == "/download.pdf":
            self._send_text(
                200,
                "%PDF-1.4\n% fixture stub, not a real PDF\n%%EOF\n",
                content_type="application/pdf",
            )
            return True

        if path == "/slow":
            # Only the real request waits: a HEAD must not stall the crawler's
            # header probe for 20 seconds.
            if method == "GET":
                time.sleep(20)
            self._send_text(200, "<!DOCTYPE html><html lang='en'><body><h1>Slow</h1></body></html>")
            return True

        if path == "/empty":
            self._send_text(200, "")
            return True

        return False

    def do_GET(self) -> None:  # noqa: N802 (stdlib naming)
        if self._dispatch_extra("GET"):
            return
        super().do_GET()

    def do_HEAD(self) -> None:  # noqa: N802 (stdlib naming)
        if self._dispatch_extra("HEAD"):
            return
        super().do_HEAD()

    def log_message(self, fmt: str, *args) -> None:  # keep the default access log, prefixed
        sys.stderr.write("[demo-server] %s - %s\n" % (self.address_string(), fmt % args))


class ThreadedServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Serve the demo fixture site with awkward-case routes.")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument(
        "--root",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo-site"),
    )
    args = parser.parse_args(argv)

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"error: --root {root} is not a directory", file=sys.stderr)
        return 2

    handler = functools.partial(DemoHandler, directory=root)
    with ThreadedServer((args.host, args.port), handler) as httpd:
        print(f"demo site serving {root} on http://{args.host}:{args.port}/", flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("demo server stopped", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
