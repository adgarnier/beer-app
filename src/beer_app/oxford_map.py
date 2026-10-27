"""Run a small local web server that displays an interactive map of Oxford."""

from __future__ import annotations

import argparse
import contextlib
import json
import mimetypes
import re
import threading
import webbrowser
from datetime import date
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from pathlib import Path

if __package__:
    from .pub_data import Pub
    from .visited_pubs import load_visit_history, record_visit_today


def build_map_page() -> str:
    """Return the HTML page used by the local Oxford map server."""
    if __package__:
        template = files("beer_app").joinpath("templates", "oxford_map.html")
        return template.read_text(encoding="utf-8")

    template = Path(__file__).with_name("templates") / "oxford_map.html"
    return template.read_text(encoding="utf-8")


def build_template_asset(filename: str) -> bytes:
    """Return a template asset used by the local Oxford map server."""
    if __package__:
        asset = files("beer_app").joinpath("templates", filename)
        return asset.read_bytes()

    asset = Path(__file__).with_name("templates") / filename
    return asset.read_bytes()


def build_static_asset(filename: str) -> bytes:
    """Return a static image asset used by the map."""
    if filename != "visitbadge.png":
        raise FileNotFoundError(filename)

    if __package__:
        asset = files("beer_app").joinpath("images", filename)
        return asset.read_bytes()

    asset = Path(__file__).with_name("images") / filename
    return asset.read_bytes()


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

        if self.path == "/api/pubs":
            map_state = self.server.map_state  # type: ignore[attr-defined]
            content = json.dumps(map_state.snapshot()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        template_assets = {
            "/oxford_map.css": ("oxford_map.css", "text/css; charset=utf-8"),
            "/oxford_map.js": ("oxford_map.js", "text/javascript; charset=utf-8"),
        }
        if self.path in template_assets:
            filename, content_type = template_assets[self.path]
            content = build_template_asset(filename)
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        if self.path == "/images/visitbadge.png":
            try:
                content = build_static_asset("visitbadge.png")
            except FileNotFoundError:
                self.send_error(404, "Visited marker image is missing")
                return
            self.send_response(200)
            self.send_header("Content-Type", mimetypes.guess_type("visitbadge.png")[0] or "image/png")
            self.send_header("Cache-Control", "public, max-age=3600")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        if self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        self.send_error(404)

    def do_POST(self) -> None:  # noqa: N802 - method name is defined by BaseHTTPRequestHandler
        """Record a visit submitted by a map popup."""
        match = re.fullmatch(r"/api/pubs/(\d+)/visit", self.path)
        if match is None:
            self.send_error(404)
            return

        pub_id = int(match.group(1))
        map_state = self.server.map_state  # type: ignore[attr-defined]
        try:
            recorded = map_state.record_visit_today(pub_id)
        except KeyError:
            self.send_error(404, "Pub is not currently loaded")
            return

        content = json.dumps({"recorded": recorded, "visited_today": True}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format: str, *args: object) -> None:
        """Suppress routine browser request logs."""


@dataclass
class MapState:
    """Thread-safe pub data shared by the terminal and browser map."""

    pubs: list[Pub] = field(default_factory=list)
    version: int = 0
    visited_statuses: dict[int, bool] = field(default_factory=lambda: load_visit_history()[0])
    lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def replace_pubs(self, pubs: list[Pub]) -> None:
        """Replace the pubs displayed by the map."""
        with self.lock:
            self.pubs = list(pubs)
            self.version += 1

    def record_visit_today(self, pub_id: int) -> bool:
        """Record today's visit for a pub currently displayed on the map."""
        with self.lock:
            if not any(pub.id == pub_id for pub in self.pubs):
                raise KeyError(pub_id)
        recorded = record_visit_today(pub_id)
        with self.lock:
            self.visited_statuses[pub_id] = True
            self.version += 1
        return recorded

    def snapshot(self) -> dict[str, int | list[dict[str, int | float | str | bool]]]:
        """Return a consistent JSON-ready snapshot of the map state."""
        visited_statuses, visit_dates = load_visit_history()
        today = date.today().isoformat()
        with self.lock:
            if visited_statuses != self.visited_statuses:
                self.visited_statuses = visited_statuses
                self.version += 1
            return {
                "version": self.version,
                "pubs": [
                    {
                        **pub.as_dict(),
                        "visited": self.visited_statuses.get(pub.id, False),
                        "visited_today": today in visit_dates.get(pub.id, []),
                    }
                    for pub in self.pubs
                ],
            }


@dataclass
class BackgroundMapServer:
    """A running map server and its background thread."""

    server: ThreadingHTTPServer
    thread: threading.Thread
    url: str
    state: MapState

    def set_pubs(self, pubs: list[Pub]) -> None:
        """Replace the pub markers exposed to the browser map."""
        self.state.replace_pubs(pubs)

    def clear_pubs(self) -> None:
        """Remove all pub markers exposed to the browser map."""
        self.state.replace_pubs([])

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
    state = MapState()
    server.map_state = state  # type: ignore[attr-defined]
    actual_port = server.server_address[1]
    url = f"http://{host}:{actual_port}"
    thread = threading.Thread(target=server.serve_forever, name="oxford-map-server", daemon=True)
    thread.start()

    if open_browser:
        browser_timer = threading.Timer(0.25, webbrowser.open, args=(url,))
        browser_timer.daemon = True
        browser_timer.start()

    print(f"Oxford Pub Map is running at {url}")
    return BackgroundMapServer(server=server, thread=thread, url=url, state=state)


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
