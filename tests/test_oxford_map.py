"""Tests for the local Oxford map."""

from unittest.mock import MagicMock, patch

from beer_app.oxford_map import (
    BackgroundMapServer,
    MapState,
    build_map_page,
    build_template_asset,
    main,
    start_map_server,
)
from beer_app.pub_data import Pub


def test_map_page_contains_leaflet_and_oxford_coordinates():
    page = build_map_page()

    assert "leaflet@1.9.4" in page
    assert 'href="oxford_map.css"' in page
    assert 'src="oxford_map.js"' in page
    assert "<style>" not in page
    assert "<script>" not in page


def test_map_javascript_contains_oxford_map_behaviour():
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


@patch("beer_app.oxford_map.run_map_server")
def test_main_starts_server_without_opening_browser(run_map_server):
    assert main(["--host", "localhost", "--port", "8765", "--no-browser"]) == 0

    run_map_server.assert_called_once_with(host="localhost", port=8765, open_browser=False)


@patch("beer_app.oxford_map.ThreadingHTTPServer")
def test_starts_map_server_in_background(server_class):
    server = server_class.return_value
    server.server_address = ("127.0.0.1", 8765)

    background_server = start_map_server(port=8765, open_browser=False)

    assert isinstance(background_server, BackgroundMapServer)
    assert background_server.url == "http://127.0.0.1:8765"
    assert background_server.state.snapshot() == {"version": 0, "pubs": []}
    server.serve_forever.assert_called_once_with()


@patch("beer_app.oxford_map.load_visit_history", return_value=({}, {}))
def test_map_state_is_empty_until_pubs_are_added(load_visit_history):
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
def test_map_state_records_visit_for_loaded_pub(load_visit_history, record_visit_today):
    state = MapState()
    pub = Pub(1, "Example Pub", "Example Road", "Oxford", "Independent", "Notes", 51.75, -1.25)
    state.replace_pubs([pub])

    assert state.record_visit_today(pub.id)

    record_visit_today.assert_called_once_with(pub.id)
    assert state.visited_statuses[pub.id]


@patch("beer_app.oxford_map.load_visit_history", return_value=({}, {}))
def test_map_state_rejects_visit_for_pub_not_on_map(load_visit_history):
    state = MapState()

    try:
        state.record_visit_today(999)
    except KeyError as error:
        assert error.args == (999,)
    else:
        raise AssertionError("Expected an unloaded pub to be rejected")


def test_background_server_can_clear_pubs():
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
