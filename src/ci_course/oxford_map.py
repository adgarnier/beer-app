"""Run a small local web server that displays an interactive map of Oxford."""

from __future__ import annotations

import argparse
import contextlib
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files


def build_map_page() -> str:
    """Return the HTML page used by the local Oxford map server."""
    template = files("ci_course").joinpath("templates", "oxford_map.html")
    return template.read_text(encoding="utf-8")


class MapRequestHandler(BaseHTTPRequestHandler):
    """Serve the map page and a lightweight health check."""

    def do_GET(self) -> None:  # noqa: N802 - method name is defined by BaseHTTPRequestHandler
        """Handle a browser request."""
        if self.path in {"/", "/index.html"}:
            content = build_map_page().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        if self.path == "/healthz":
            content = b"ok\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        if self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        self.send_error(404)

    def log_message(self, format: str, *args: object) -> None:
        """Suppress routine browser request logs."""


def run_map_server(host: str = "127.0.0.1", port: int = 8000, open_browser: bool = True) -> None:
    """Serve the map until the user stops the process."""
    server = ThreadingHTTPServer((host, port), MapRequestHandler)
    actual_port = server.server_address[1]
    url = f"http://{host}:{actual_port}"

    print(f"Oxford Pub Map is running at {url}")
    print("Press Ctrl+C to stop it.")

    if open_browser:
        threading.Timer(0.25, webbrowser.open, args=(url,)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Oxford Pub Map.")
    finally:
        server.server_close()


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(description="Open an interactive map centred on Oxford.")
    parser.add_argument("--host", default="127.0.0.1", help="local address to serve (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="local port to use (default: 8000)")
    parser.add_argument("--no-browser", action="store_true", help="do not open the map in a browser automatically")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the Oxford map command."""
    args = build_parser().parse_args(argv)

    try:
        run_map_server(host=args.host, port=args.port, open_browser=not args.no_browser)
    except OSError as error:
        with contextlib.suppress(AttributeError):
            if error.errno is not None:
                error.strerror = f"{error.strerror}; try a different port with --port"
        raise SystemExit(f"Could not start the map server: {error}") from error

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
