"""Tests for loading pubs onto the Oxford map."""

from unittest.mock import MagicMock, patch

import pytest

from beer_app.pub_data import Pub
from beer_app.pub_loader import (
    LOAD_HELP,
    load_pubs_onto_map,
    main,
    unload_pubs_from_map,
)

def test_load_help_describes_all_load_options():
    """Documents the supported map load and unload commands."""
    assert "Load help" in LOAD_HELP
    assert "load all" in LOAD_HELP
    assert "load visited" in LOAD_HELP
    assert "load unvisited" in LOAD_HELP

@patch("beer_app.pub_loader.load_pubs")
def test_loads_all_pubs_onto_map(load_pubs, capsys):
    """Loads every pub, updates the map, and reports the number loaded."""
    pubs = [object(), object()]
    load_pubs.return_value = pubs
    map_server = MagicMock()

    assert load_pubs_onto_map(map_server) == pubs

    load_pubs.assert_called_once_with()
    map_server.set_pubs.assert_called_once_with(pubs)
    assert "Added 2 all pubs" in capsys.readouterr().out


@patch("beer_app.pub_loader.crawl_file_path")
@patch("beer_app.pub_loader.load_pubs")
def test_loads_saved_crawl_in_file_order(load_pubs, crawl_file_path, tmp_path):
    """Loads the saved crawl CSV and sends its ordered pubs to the map."""
    crawl_path = tmp_path / "pub_crawl.csv"
    crawl_path.touch()
    pubs = [object(), object()]
    crawl_file_path.return_value = crawl_path
    load_pubs.return_value = pubs
    map_server = MagicMock()

    assert load_pubs_onto_map(map_server, " CRAWL ") == pubs

    load_pubs.assert_called_once_with(crawl_path)
    map_server.set_pubs.assert_called_once_with(pubs)


@patch("beer_app.pub_loader.crawl_file_path")
def test_rejects_crawl_selection_when_no_saved_route_exists(crawl_file_path, tmp_path):
    """Explains how to create a crawl when its saved CSV does not exist."""
    crawl_file_path.return_value = tmp_path / "missing.csv"

    with pytest.raises(ValueError, match="Create one with 'crawl' first"):
        load_pubs_onto_map(MagicMock(), "crawl")


@patch("beer_app.pub_loader.load_visit_history")
@patch("beer_app.pub_loader.load_pubs")
def test_loads_only_visited_pubs(load_pubs, load_visit_history):
    """Includes only pubs whose visit status is true."""
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
    """Treats false and absent visit statuses as unvisited."""
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
    """Raises a clear error when the requested load option is unsupported."""
    with pytest.raises(ValueError, match="Unknown load option"):
        load_pubs_onto_map(MagicMock(), "nearby")


def test_unloads_all_pubs_from_map(capsys):
    """Clears the map and confirms that all pubs were removed."""
    map_server = MagicMock()

    unload_pubs_from_map(map_server)

    map_server.clear_pubs.assert_called_once_with()
    assert "Removed all pubs" in capsys.readouterr().out


@patch("beer_app.pub_loader.start_map_server")
@patch("builtins.input", return_value="no")
def test_main_does_not_start_map_when_user_declines(_input, start_map_server):
    """Returns without launching a server when standalone startup is declined."""
    assert main() is None

    start_map_server.assert_not_called()


@patch("beer_app.pub_loader.load_pubs_onto_map")
@patch("builtins.input", return_value="visited")
def test_main_prompts_for_selection_with_existing_map(_input, load_pubs, capsys):
    """Prompts for a selection and loads it without stopping a caller-owned map."""
    map_server = MagicMock()
    pubs = [object()]
    load_pubs.return_value = pubs

    assert main(map_server) == pubs

    load_pubs.assert_called_once_with(map_server, "visited")
    map_server.stop.assert_not_called()
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("interruption", [EOFError, KeyboardInterrupt])
@patch("beer_app.pub_loader.start_map_server")
def test_main_stops_owned_map_when_selection_is_interrupted(
    start_map_server, monkeypatch, interruption, capsys
):
    """Cancels selection cleanly and stops a map launched by this command."""
    map_server = start_map_server.return_value
    answers = iter(["yes"])

    def prompt(_message):
        try:
            return next(answers)
        except StopIteration as error:
            raise interruption from error

    monkeypatch.setattr("builtins.input", prompt)

    assert main() is None

    map_server.stop.assert_called_once_with()
    assert "Load cancelled" in capsys.readouterr().out


@patch("beer_app.pub_loader.load_pubs_onto_map", side_effect=ValueError("bad selection"))
def test_main_reports_load_error_without_stopping_caller_owned_map(load_pubs, capsys):
    """Reports selection errors while leaving a caller-owned map running."""
    map_server = MagicMock()

    assert main(map_server, "invalid") is None

    load_pubs.assert_called_once_with(map_server, "invalid")
    map_server.stop.assert_not_called()
    assert "bad selection" in capsys.readouterr().out


@patch("beer_app.pub_loader.load_pubs_onto_map", side_effect=ValueError("bad selection"))
@patch("beer_app.pub_loader.start_map_server")
@patch("builtins.input", return_value="yes")
def test_main_stops_owned_map_when_loading_fails(
    _input, start_map_server, load_pubs, capsys
):
    """Stops a standalone map server when its requested pub load fails."""
    map_server = start_map_server.return_value

    assert main(selection="invalid") is None

    load_pubs.assert_called_once_with(map_server, "invalid")
    map_server.stop.assert_called_once_with()
    assert "bad selection" in capsys.readouterr().out


@patch("beer_app.pub_loader.load_pubs_onto_map", return_value=[object()])
@patch("beer_app.pub_loader.start_map_server")
@patch("builtins.input", return_value="yes")
def test_main_runs_owned_map_until_interrupted(
    _input, start_map_server, load_pubs, capsys
):
    """Joins and then stops a standalone map server after Ctrl+C."""
    map_server = start_map_server.return_value
    map_server.thread.join.side_effect = KeyboardInterrupt

    loaded = main(selection="all")

    assert loaded == load_pubs.return_value
    load_pubs.assert_called_once_with(map_server, "all")
    map_server.thread.join.assert_called_once_with()
    map_server.stop.assert_called_once_with()
    output = capsys.readouterr().out
    assert "map is running" in output
    assert "Stopping the Oxford map" in output
