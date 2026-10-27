"""Tests for loading pubs onto the Oxford map."""

from unittest.mock import MagicMock, patch

import pytest

from beer_app.pub_data import Pub
from beer_app.pub_loader import LOAD_HELP, load_pubs_onto_map, unload_pubs_from_map


def test_load_help_describes_all_load_options():
    assert "Load help" in LOAD_HELP
    assert "load all" in LOAD_HELP
    assert "load visited" in LOAD_HELP
    assert "load unvisited" in LOAD_HELP


@patch("beer_app.pub_loader.load_pubs")
def test_loads_all_pubs_onto_map(load_pubs, capsys):
    pubs = [object(), object()]
    load_pubs.return_value = pubs
    map_server = MagicMock()

    assert load_pubs_onto_map(map_server) == pubs

    load_pubs.assert_called_once_with()
    map_server.set_pubs.assert_called_once_with(pubs)
    assert "Added 2 all pubs" in capsys.readouterr().out


@patch("beer_app.pub_loader.load_visit_history")
@patch("beer_app.pub_loader.load_pubs")
def test_loads_only_visited_pubs(load_pubs, load_visit_history):
    pubs = [
        Pub(1, "Visited", "One Road", "Oxford", "Independent", "", 51.75, -1.25),
        Pub(2, "Unvisited", "Two Road", "Oxford", "Independent", "", 51.76, -1.26),
    ]
    load_pubs.return_value = pubs
    load_visit_history.return_value = ({1: True, 2: False}, {})
    map_server = MagicMock()

    assert load_pubs_onto_map(map_server, "visited") == [pubs[0]]
    map_server.set_pubs.assert_called_once_with([pubs[0]])


@patch("beer_app.pub_loader.load_visit_history")
@patch("beer_app.pub_loader.load_pubs")
def test_loads_false_and_missing_statuses_as_unvisited(load_pubs, load_visit_history):
    pubs = [
        Pub(1, "Visited", "One Road", "Oxford", "Independent", "", 51.75, -1.25),
        Pub(2, "Explicitly unvisited", "Two Road", "Oxford", "Independent", "", 51.76, -1.26),
        Pub(3, "No history", "Three Road", "Oxford", "Independent", "", 51.77, -1.27),
    ]
    load_pubs.return_value = pubs
    load_visit_history.return_value = ({1: True, 2: False}, {})
    map_server = MagicMock()

    assert load_pubs_onto_map(map_server, "unvisited") == pubs[1:]
    map_server.set_pubs.assert_called_once_with(pubs[1:])


def test_rejects_unknown_load_option():
    with pytest.raises(ValueError, match="Unknown load option"):
        load_pubs_onto_map(MagicMock(), "nearby")


def test_unloads_all_pubs_from_map(capsys):
    map_server = MagicMock()

    unload_pubs_from_map(map_server)

    map_server.clear_pubs.assert_called_once_with()
    assert "Removed all pubs" in capsys.readouterr().out
