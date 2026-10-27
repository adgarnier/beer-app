"""Tests for the local Oxford map."""

from unittest.mock import MagicMock, patch

from beer_app.oxford_map import BackgroundMapServer, MapState, build_map_page, main, start_map_server
from beer_app.pub_data import Pub


def test_map_page_contains_leaflet_and_oxford_coordinates():
    page = build_map_page()

    assert "leaflet@1.9.4" in page
    assert "51.752" in page
    assert "-1.2577" in page
    assert "tile.openstreetmap.org" in page
    assert "OpenStreetMap contributors" in page
    assert 'fetch("/api/pubs")' in page
    assert "setInterval(updateMap, 1000)" in page


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


def test_map_state_is_empty_until_pubs_are_added():
    state = MapState()
    pub = Pub(1, "Example Pub", "Oxford", "Independent", "Notes", 51.75, -1.25)

    assert state.snapshot() == {"version": 0, "pubs": []}

    state.replace_pubs([pub])

    assert state.snapshot() == {
        "version": 1,
        "pubs": [pub.as_dict()],
    }


def test_background_server_can_clear_pubs():
    state = MapState()
    pub = Pub(1, "Example Pub", "Oxford", "Independent", "Notes", 51.75, -1.25)
    background_server = BackgroundMapServer(
        server=MagicMock(),
        thread=MagicMock(),
        url="http://127.0.0.1:8000",
        state=state,
    )
    background_server.set_pubs([pub])

    background_server.clear_pubs()

    assert state.snapshot() == {"version": 2, "pubs": []}
