"""Tests for the local Oxford map."""

from unittest.mock import patch

from beer_app.oxford_map import build_map_page, main


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
