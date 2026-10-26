"""Run a small local web server that displays an interactive map of Oxford."""

from __future__ import annotations

import argparse
import contextlib
import threading
import webbrowser
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from pathlib import Path


def build_map_page() -> str:
    """Return the HTML page used by the local Oxford map server."""
    if __package__:
        template = files("beer_app").joinpath("templates", "oxford_map.html")
        return template.read_text(encoding="utf-8")

    template = Path(__file__).with_name("templates") / "oxford_map.html"
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


@dataclass
class BackgroundMapServer:
    """A running map server and its background thread."""

    server: ThreadingHTTPServer
    thread: threading.Thread
    url: str

    def stop(self) -> None:
        """Stop the server and wait briefly for its thread to finish."""
        if self.thread.is_alive():
            self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


def start_map_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    open_browser: bool = True,
) -> BackgroundMapServer:
    """Start the map server in the background and return its controller."""
    server = ThreadingHTTPServer((host, port), MapRequestHandler)
    actual_port = server.server_address[1]
    url = f"http://{host}:{actual_port}"
    thread = threading.Thread(target=server.serve_forever, name="oxford-map-server", daemon=True)
    thread.start()

    if open_browser:
        browser_timer = threading.Timer(0.25, webbrowser.open, args=(url,))
        browser_timer.daemon = True
        browser_timer.start()

    print(f"Oxford Pub Map is running at {url}")
    return BackgroundMapServer(server=server, thread=thread, url=url)


def run_map_server(host: str = "127.0.0.1", port: int = 8000, open_browser: bool = True) -> None:
    """Serve the map until the user stops the process."""
    background_server = start_map_server(host=host, port=port, open_browser=open_browser)
    print("Press Ctrl+C to stop it.")

    if open_browser:
        print("The map should open in your browser shortly.")

    try:
        background_server.thread.join()
    except KeyboardInterrupt:
        print("\nStopping Oxford Pub Map.")
    finally:
        background_server.stop()


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
