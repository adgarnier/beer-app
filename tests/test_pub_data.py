"""Tests for loading the Oxford pub list."""

import pytest

from beer_app.pub_data import load_pubs


def test_loads_packaged_pub_list():
    pubs = load_pubs()

    assert len(pubs) == 101
    assert pubs[0].name == "Duke of Monmouth"
    assert pubs[0].latitude == pytest.approx(51.736673)
    assert pubs[0].longitude == pytest.approx(-1.251886)


def test_rejects_csv_without_required_columns(tmp_path):
    pub_list = tmp_path / "pubs.csv"
    pub_list.write_text("Pub,Latitude,Longitude\nExample,51.75,-1.25\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing required columns"):
        load_pubs(pub_list)


def test_rejects_invalid_coordinates(tmp_path):
    pub_list = tmp_path / "pubs.csv"
    pub_list.write_text(
        "Pub,Road,Location,Sponsor,Notes,Latitude,Longitude,ID\nExample,WaltonRd,Oxford,,,north,-1.25,1\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid ID or coordinates"):
        load_pubs(pub_list)
