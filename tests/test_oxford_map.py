"""Tests for the local Oxford map."""

from unittest.mock import patch

from beer_app.oxford_map import BackgroundMapServer, build_map_page, main, start_map_server


def test_map_page_contains_leaflet_and_oxford_coordinates():
    page = build_map_page()

    assert "leaflet@1.9.4" in page
    assert "51.752" in page
    assert "-1.2577" in page
    assert "tile.openstreetmap.org" in page
    assert "OpenStreetMap contributors" in page


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
    server.serve_forever.assert_called_once_with()
