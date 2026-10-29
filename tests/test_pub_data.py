"""Tests for loading the Oxford pub list."""

import pytest

from beer_app import pub_data
from beer_app.pub_data import Pub, load_pubs


CSV_HEADER = "Pub,Road,Location,Sponsor,Notes,Latitude,Longitude,ID\n"


def test_loads_packaged_pub_list():
    """Loads the packaged pub list with the expected first pub and coordinates."""
    pubs = load_pubs()

    assert len(pubs) == 101
    assert pubs[0].name == "Duke of Monmouth"
    assert pubs[0].latitude == pytest.approx(51.736673)
    assert pubs[0].longitude == pytest.approx(-1.251886)


def test_loads_custom_csv_trims_text_and_exposes_json_ready_dict(tmp_path):
    """Trims CSV text fields and represents the resulting pub as plain values."""
    PUB_LIST = tmp_path / "pubs.csv"
    PUB_LIST.write_text(
        CSV_HEADER
        + "  Example Pub  ,  Walton Road  , Oxford , Independent ,  Notes  ,51.75,-1.25,7\n",
        encoding="utf-8",
    )

    assert load_pubs(PUB_LIST) == [
        Pub(7, "Example Pub", "Walton Road", "Oxford", "Independent", "Notes", 51.75, -1.25)
    ]
    assert load_pubs(PUB_LIST)[0].as_dict() == {
        "id": 7,
        "name": "Example Pub",
        "road": "Walton Road",
        "location": "Oxford",
        "sponsor": "Independent",
        "notes": "Notes",
        "latitude": 51.75,
        "longitude": -1.25,
    }

def test_rejects_csv_without_required_columns(tmp_path):
    """Rejects a CSV file that omits required pub columns."""
    PUB_LIST = tmp_path / "pubs.csv"
    PUB_LIST.write_text("Pub,Latitude,Longitude\nExample,51.75,-1.25\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing required columns"):
        load_pubs(PUB_LIST)

def test_rejects_invalid_coordinates(tmp_path):
    """Rejects non-numeric or out-of-range coordinates in a pub row."""
    PUB_LIST = tmp_path / "pubs.csv"
    PUB_LIST.write_text(
        "Pub,Road,Location,Sponsor,Notes,Latitude,Longitude,ID\n"
        "Example,WaltonRd,Oxford,,,north,-1.25,1\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid ID or coordinates"):
        load_pubs(PUB_LIST)


def test_rejects_blank_pub_name_with_csv_row_number(tmp_path):
    """Rejects whitespace-only pub names and identifies their CSV row."""
    PUB_LIST = tmp_path / "pubs.csv"
    PUB_LIST.write_text(
        CSV_HEADER + "   ,Walton Road,Oxford,Independent,,51.75,-1.25,1\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Missing pub name on CSV row 2"):
        load_pubs(PUB_LIST)


@pytest.mark.parametrize(
    ("latitude", "longitude"),
    [
        ("90.01", "-1.25"),
        ("-90.01", "-1.25"),
        ("51.75", "180.01"),
        ("51.75", "-180.01"),
    ],
)
def test_rejects_coordinates_outside_world_bounds(tmp_path, latitude, longitude):
    """Rejects latitude and longitude values outside their geographic ranges."""
    PUB_LIST = tmp_path / "pubs.csv"
    PUB_LIST.write_text(
        CSV_HEADER
        + f"Example,Walton Road,Oxford,Independent,,{latitude},{longitude},1\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Coordinates out of range on CSV row 2"):
        load_pubs(PUB_LIST)


def test_default_pub_list_uses_adjacent_data_in_direct_script_mode(
    monkeypatch, tmp_path
):
    """Loads the data file beside the module when no package context exists."""
    module_path = tmp_path / "pub_data.py"
    data_directory = tmp_path / "data"
    data_directory.mkdir()
    PUB_LIST = data_directory / "direct.csv"
    PUB_LIST.write_text(
        CSV_HEADER + "Direct Pub,Road,Oxford,Independent,,51.75,-1.25,3\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(pub_data, "__package__", "")
    monkeypatch.setattr(pub_data, "__file__", str(module_path))
    monkeypatch.setattr(pub_data, "PUB_LIST", "direct.csv")

    pubs = load_pubs()

    assert [pub.name for pub in pubs] == ["Direct Pub"]
