"""Tests for the local Oxford map."""

import json
from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from beer_app import oxford_map
from beer_app.oxford_map import (
    BackgroundMapServer,
    MapRequestHandler,
    MapState,
    build_map_page,
    build_static_asset,
    build_template_asset,
    main,
    run_map_server,
    start_map_server,
)
from beer_app.pub_data import Pub

def test_map_page_contains_leaflet_and_oxford_coordinates():
    """Loads the map page with external stylesheet and script references."""
    page = build_map_page()

    assert "leaflet@1.9.4" in page
    assert 'href="oxford_map.css"' in page
    assert 'src="oxford_map.js"' in page
    assert "<style>" not in page
    assert "<script>" not in page

def test_map_javascript_contains_oxford_map_behaviour():
    """Provides the JavaScript needed for pub markers, visit actions, and map refresh."""
    javascript = build_template_asset("oxford_map.js").decode("utf-8")

    assert "51.752" in javascript
    assert "-1.2577" in javascript
    assert "tile.openstreetmap.org" in javascript
    assert "OpenStreetMap contributors" in javascript
    assert 'fetch("/api/pubs")' in javascript
    assert '"Visited today"' in javascript
    assert 'method: "POST"' in javascript
    assert "/visit`" in javascript
    assert "setInterval(updateMap, 1000)" in javascript


def test_static_asset_loads_visit_badge_and_rejects_unknown_files():
    """Loads the packaged marker image and refuses arbitrary static filenames."""
    assert build_static_asset("visitbadge.png").startswith(b"\x89PNG")

    with pytest.raises(FileNotFoundError, match="unknown.png"):
        build_static_asset("unknown.png")


def test_assets_load_from_source_tree_when_module_has_no_package(monkeypatch, tmp_path):
    """Reads HTML, templates, and images beside the module in direct-script mode."""
    module_path = tmp_path / "oxford_map.py"
    templates = tmp_path / "templates"
    images = tmp_path / "images"
    templates.mkdir()
    images.mkdir()
    (templates / "oxford_map.html").write_text("map page", encoding="utf-8")
    (templates / "example.css").write_bytes(b"map css")
    (images / "visitbadge.png").write_bytes(b"badge")
    monkeypatch.setattr(oxford_map, "__package__", "")
    monkeypatch.setattr(oxford_map, "__file__", str(module_path))

    assert build_map_page() == "map page"
    assert build_template_asset("example.css") == b"map css"
    assert build_static_asset("visitbadge.png") == b"badge"

@patch("beer_app.oxford_map.run_map_server")
def test_main_starts_server_without_opening_browser(run_server):
    """Passes host, port, and browser preference to the map server runner."""
    assert main(["--host", "localhost", "--port", "8765", "--no-browser"]) == 0

    run_server.assert_called_once_with(host="localhost", port=8765, open_browser=False)

@patch("beer_app.oxford_map.ThreadingHTTPServer")
def test_starts_map_server_in_background(server_class):
    """Returns a background server controller with its bound URL and empty state."""
    server = server_class.return_value
    server.server_address = ("127.0.0.1", 8765)

    background_server = start_map_server(port=8765, open_browser=False)

    assert isinstance(background_server, BackgroundMapServer)
    assert background_server.url == "http://127.0.0.1:8765"
    assert background_server.state.snapshot() == {"version": 0, "pubs": []}
    server.serve_forever.assert_called_once_with()


@patch("beer_app.oxford_map.threading.Timer")
@patch("beer_app.oxford_map.ThreadingHTTPServer")
def test_start_map_server_schedules_browser_open(server_class, timer_class):
    """Schedules one daemon timer to open the URL when browser launch is enabled."""
    server_class.return_value.server_address = ("127.0.0.1", 4321)

    background_server = start_map_server(host="localhost", port=0)

    timer_class.assert_called_once_with(
        0.25,
        oxford_map.webbrowser.open,
        args=("http://localhost:4321",),
    )
    timer = timer_class.return_value
    assert timer.daemon is True
    timer.start.assert_called_once_with()
    assert background_server.url == "http://localhost:4321"

@patch("beer_app.oxford_map.load_visit_history", return_value=({}, {}))
def test_map_state_is_empty_until_pubs_are_added(_load_visit_history):
    """Increments the map version when pubs are added and marks them unvisited."""
    state = MapState()
    pub = Pub(1, "Example Pub", "Example Road", "Oxford", "Independent", "Notes", 51.75, -1.25)

    assert state.snapshot() == {"version": 0, "pubs": []}

    state.replace_pubs([pub])

    assert state.snapshot() == {
        "version": 1,
        "pubs": [{**pub.as_dict(), "visited": False, "visited_today": False}],
    }

@patch("beer_app.oxford_map.record_visit_today", return_value=True)
@patch("beer_app.oxford_map.load_visit_history", return_value=({}, {}))
def test_map_state_records_visit_for_loaded_pub(_load_visit_history, record_visit_today):
    """Records a visit for a pub shown on the map and updates its status."""
    state = MapState()
    pub = Pub(1, "Example Pub", "Example Road", "Oxford", "Independent", "Notes", 51.75, -1.25)
    state.replace_pubs([pub])

    assert state.record_visit_today(pub.id)

    record_visit_today.assert_called_once_with(pub.id)
    assert state.visited_statuses[pub.id]


@patch("beer_app.oxford_map.load_visit_history")
def test_snapshot_refreshes_changed_visit_status_and_marks_today(load_visit_history):
    """Refreshes externally changed history and marks a pub visited today."""
    today = date.today().isoformat()
    load_visit_history.side_effect = [({}, {}), ({1: True}, {1: [today]})]
    pub = Pub(1, "Example", "Road", "Oxford", "Independent", "", 51.75, -1.25)
    state = MapState(pubs=[pub])

    snapshot = state.snapshot()

    assert snapshot["version"] == 1
    assert snapshot["pubs"][0]["visited"] is True
    assert snapshot["pubs"][0]["visited_today"] is True

@patch("beer_app.oxford_map.load_visit_history", return_value=({}, {}))
def test_map_state_rejects_visit_for_pub_not_on_map(_load_visit_history):
    """Rejects visit recording when the pub is not currently displayed."""
    state = MapState()

    try:
        state.record_visit_today(999)
    except KeyError as error:
        assert error.args == (999,)
    else:
        raise AssertionError("Expected an unloaded pub to be rejected")

def test_background_server_can_clear_pubs():
    """Clears displayed pubs and increments the map state version."""
    state = MapState()
    pub = Pub(1, "Example Pub", "Example Road", "Oxford", "Independent", "Notes", 51.75, -1.25)
    background_server = BackgroundMapServer(
        server=MagicMock(),
        thread=MagicMock(),
        url="http://127.0.0.1:8000",
        state=state,
    )
    background_server.set_pubs([pub])

    background_server.clear_pubs()

    assert state.snapshot() == {"version": 2, "pubs": []}


@pytest.mark.parametrize("thread_alive", [True, False])
def test_background_server_stop_closes_server_and_joins_thread(thread_alive):
    """Closes and joins the server, requesting shutdown only for a live thread."""
    server = MagicMock()
    thread = MagicMock()
    thread.is_alive.return_value = thread_alive
    background_server = BackgroundMapServer(server, thread, "http://map", MapState())

    background_server.stop()

    if thread_alive:
        server.shutdown.assert_called_once_with()
    else:
        server.shutdown.assert_not_called()
    server.server_close.assert_called_once_with()
    thread.join.assert_called_once_with(timeout=2)

class FakeHandler:
    """Minimal request handler streams for exercising routes without sockets."""

    def __init__(self, path, server):
        """Initialize a fake handler for one route."""
        self.path = path
        self.server = server
        self.response_data = {
            "headers": {},
            "status": None,
            "error_message": None,
            "body": b"",
            "headers_complete": False,
        }
        self.wfile = MagicMock()
        self.wfile.write.side_effect = lambda content: self.response_data.update(body=content)

    def send_response(self, status):
        """Record the HTTP status."""
        self.response_data["status"] = status

    def send_header(self, name, value):
        """Record one response header."""
        self.response_data["headers"][name] = value

    def end_headers(self):
        """Complete the response headers."""
        self.response_data["headers_complete"] = True

    def send_error(self, status, message=None):
        """Record an error response and its message."""
        self.response_data["status"] = status
        self.response_data["error_message"] = message

def test_get_health_endpoint_returns_plain_text_ok():
    """Returns the health endpoint status, content type, and response body."""
    handler = FakeHandler("/healthz", MagicMock())

    MapRequestHandler.do_GET(handler)

    assert handler.response_data["status"] == 200
    assert handler.response_data["headers"]["Content-Type"] == "text/plain; charset=utf-8"
    assert handler.response_data["body"] == b"ok\n"


@patch("beer_app.oxford_map.build_map_page", return_value="<html>map</html>")
def test_get_root_returns_map_html(build_page):
    """Serves the generated map page from the root browser route."""
    handler = FakeHandler("/", MagicMock())

    MapRequestHandler.do_GET(handler)

    build_page.assert_called_once_with()
    assert handler.response_data["status"] == 200
    assert handler.response_data["headers"]["Content-Type"] == "text/html; charset=utf-8"
    assert handler.response_data["body"] == b"<html>map</html>"


@pytest.mark.parametrize(
    ("path", "content_type"),
    [
        ("/oxford_map.css", "text/css; charset=utf-8"),
        ("/oxford_map.js", "text/javascript; charset=utf-8"),
    ],
)
@patch("beer_app.oxford_map.build_template_asset", return_value=b"asset")
def test_get_serves_template_assets_with_correct_content_type(
    build_asset, path, content_type
):
    """Serves map CSS and JavaScript with their expected MIME types."""
    handler = FakeHandler(path, MagicMock())

    MapRequestHandler.do_GET(handler)

    build_asset.assert_called_once_with(path.removeprefix("/"))
    assert handler.response_data["status"] == 200
    assert handler.response_data["headers"]["Content-Type"] == content_type
    assert handler.response_data["body"] == b"asset"


@patch("beer_app.oxford_map.build_static_asset", return_value=b"badge")
def test_get_serves_visit_badge_with_cache_headers(build_asset):
    """Serves the visit marker as cached PNG content."""
    handler = FakeHandler("/images/visitbadge.png", MagicMock())

    MapRequestHandler.do_GET(handler)

    build_asset.assert_called_once_with("visitbadge.png")
    assert handler.response_data["status"] == 200
    assert handler.response_data["headers"]["Content-Type"] == "image/png"
    assert handler.response_data["headers"]["Cache-Control"] == "public, max-age=3600"


@patch("beer_app.oxford_map.build_static_asset", side_effect=FileNotFoundError)
def test_get_returns_not_found_when_visit_badge_is_missing(_build_asset):
    """Returns a descriptive 404 when the marker image cannot be loaded."""
    handler = FakeHandler("/images/visitbadge.png", MagicMock())

    MapRequestHandler.do_GET(handler)

    assert handler.response_data["status"] == 404
    assert handler.response_data["error_message"] == "Visited marker image is missing"


@pytest.mark.parametrize(
    ("path", "status"),
    [("/favicon.ico", 204), ("/missing", 404)],
)
def test_get_handles_favicon_and_unknown_routes(path, status):
    """Returns no content for the favicon and not found for unknown routes."""
    handler = FakeHandler(path, MagicMock())

    MapRequestHandler.do_GET(handler)

    assert handler.response_data["status"] == status

def test_pubs_api_returns_current_json_snapshot():
    """Returns the current map version and pub data from the pubs API."""
    pub = Pub(1, "Example", "Road", "Oxford", "Independent", "", 51.75, -1.25)
    state = MapState()
    state.replace_pubs([pub])
    handler = FakeHandler("/api/pubs", MagicMock(map_state=state))

    MapRequestHandler.do_GET(handler)

    payload = json.loads(handler.response_data["body"])
    assert handler.response_data["status"] == 200
    assert handler.response_data["headers"]["Cache-Control"] == "no-store"
    assert payload["pubs"][0]["name"] == "Example"
    assert payload["version"] == 1

def test_visit_endpoint_records_loaded_pub_and_rejects_unknown_pub():
    """Records a visit for a loaded pub and responds with not found for an unloaded pub."""
    pub = Pub(1, "Example", "Road", "Oxford", "Independent", "", 51.75, -1.25)
    state = MapState()
    state.replace_pubs([pub])
    with patch("beer_app.oxford_map.record_visit_today", return_value=True) as record_visit:
        handler = FakeHandler("/api/pubs/1/visit", MagicMock(map_state=state))
        MapRequestHandler.do_POST(handler)
        assert handler.response_data["status"] == 200
        assert json.loads(handler.response_data["body"]) == {
            "recorded": True,
            "visited_today": True,
        }
        record_visit.assert_called_once_with(1)

        missing = FakeHandler("/api/pubs/2/visit", MagicMock(map_state=state))
        MapRequestHandler.do_POST(missing)
        assert missing.response_data["status"] == 404
        assert missing.response_data["error_message"] == "Pub is not currently loaded"


def test_post_rejects_unknown_route():
    """Returns not found for POST requests outside the visit API route."""
    handler = FakeHandler("/api/pubs/1", MagicMock())

    MapRequestHandler.do_POST(handler)

    assert handler.response_data["status"] == 404


@patch("beer_app.oxford_map.start_map_server")
def test_run_map_server_stops_after_keyboard_interrupt(start_server, capsys):
    """Stops the background server when its blocking join is interrupted."""
    background_server = start_server.return_value
    background_server.thread.join.side_effect = KeyboardInterrupt

    run_map_server(host="localhost", port=8765, open_browser=True)

    start_server.assert_called_once_with(host="localhost", port=8765, open_browser=True)
    background_server.stop.assert_called_once_with()
    output = capsys.readouterr().out
    assert "Press Ctrl+C" in output
    assert "open in your browser" in output
    assert "Stopping Oxford Pub Map" in output


@patch("beer_app.oxford_map.run_map_server", side_effect=OSError(48, "Address in use"))
def test_main_explains_how_to_recover_from_server_error(_run_server):
    """Converts server startup errors into a CLI message suggesting another port."""
    with pytest.raises(SystemExit, match="try a different port with --port"):
        main(["--port", "8765"])
