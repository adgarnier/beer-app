"""Tests for the main application menu."""

from unittest.mock import patch

import pytest

from beer_app.pub_data import Pub
from beer_app.run import main

@patch("beer_app.run.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["1", "q"])
def test_launches_oxford_map_in_background(input_mock, start_map_server, capsys):
    """Starts one background map server and stops it when the menu exits."""
    map_server = start_map_server.return_value
    map_server.url = "http://127.0.0.1:8000"

    assert main() == 0

    assert input_mock.call_count == 2
    start_map_server.assert_called_once_with(port=0)
    map_server.stop.assert_called_once_with()
    output = capsys.readouterr().out
    assert "PUB'LISH" in output
    assert "running in the background" in output

@patch("builtins.input", return_value="q")
def test_can_quit_from_welcome_menu(input_mock, capsys):
    """Exits from the welcome menu when the user chooses quit."""
    assert main() == 0

    assert input_mock.call_count == 1
    assert "Goodbye!" in capsys.readouterr().out


@pytest.mark.parametrize("interruption", [EOFError, KeyboardInterrupt])
def test_input_interruption_exits_and_stops_running_map(monkeypatch, interruption, capsys):
    """Treats EOF and Ctrl+C as a clean exit and stops an active map server."""
    map_server = None
    prompts = iter(["launch"])

    def read_choice(_prompt):
        try:
            return next(prompts)
        except StopIteration as error:
            raise interruption from error

    monkeypatch.setattr("builtins.input", read_choice)
    with patch("beer_app.run.oxford_map.start_map_server") as start_map_server:
        map_server = start_map_server.return_value
        assert main() == 0

    map_server.stop.assert_called_once_with()
    assert "Goodbye!" in capsys.readouterr().out


@patch("builtins.input", side_effect=["help", "quit"])
def test_general_help_lists_all_menu_features(_input, capsys):
    """Prints the complete command guide and then returns to the main prompt."""
    assert main() == 0

    output = capsys.readouterr().out
    assert "PUB'LISH --help" in output
    assert "Launch" in output
    assert "Search" in output
    assert "Crawl" in output

@patch("beer_app.run.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["1", "1", "q"])
def test_does_not_launch_a_second_map_server(input_mock, start_map_server, capsys):
    """Reuses the existing map server when launch is selected a second time."""
    start_map_server.return_value.url = "http://127.0.0.1:8000"

    assert main() == 0

    assert input_mock.call_count == 3
    start_map_server.assert_called_once_with(port=0)
    assert "already running" in capsys.readouterr().out

@patch("beer_app.pub_loader.load_pubs_onto_map")
@patch("beer_app.run.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["1", "2", "all", "q"])
def test_loads_pubs_onto_running_map(input_mock, start_map_server, load_pubs_onto_map):
    """Passes the selected pub set to the loader for display on the map."""
    pubs = [object(), object()]
    load_pubs_onto_map.return_value = pubs
    map_server = start_map_server.return_value

    assert main() == 0

    assert input_mock.call_count == 4
    load_pubs_onto_map.assert_called_once_with(map_server, "all")

@patch("beer_app.pub_loader.load_pubs_onto_map")
@patch("beer_app.run.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["launch", "load visited", "quit"])
def test_loads_visited_pubs_with_direct_command(_input_mock, start_map_server, load_pubs_onto_map):
    """Accepts the direct load visited command and forwards that selection."""
    load_pubs_onto_map.return_value = [object()]
    map_server = start_map_server.return_value

    assert main() == 0

    load_pubs_onto_map.assert_called_once_with(map_server, "visited")

@patch("beer_app.pub_loader.load_pubs_onto_map")
@patch("builtins.input", side_effect=["2", "q"])
def test_requires_map_before_loading_pubs(_input_mock, load_pubs_onto_map, capsys):
    """Refuses to load pubs until the map server has been launched."""
    assert main() == 0

    load_pubs_onto_map.assert_not_called()
    assert "Launch the Oxford map" in capsys.readouterr().out

@patch("beer_app.pub_loader.load_pubs_onto_map")
@patch("builtins.input", side_effect=["load --help", "q"])
def test_load_help_does_not_require_or_change_map(_input_mock, load_pubs_onto_map, capsys):
    """Prints load guidance without requiring or changing map state."""
    assert main() == 0

    load_pubs_onto_map.assert_not_called()
    output = capsys.readouterr().out
    assert "Load help" in output
    assert "load visited" in output

@patch("beer_app.run.unload_pubs_from_map")
@patch("beer_app.run.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["1", "3", "q"])
def test_unloads_pubs_from_running_map(input_mock, start_map_server, unload_pubs_from_map):
    """Clears the loaded pub markers when unload is selected."""
    map_server = start_map_server.return_value

    assert main() == 0

    assert input_mock.call_count == 3
    unload_pubs_from_map.assert_called_once_with(map_server)

@patch("beer_app.pub_loader.unload_pubs_from_map")
@patch("builtins.input", side_effect=["3", "q"])
def test_requires_map_before_unloading_pubs(_input_mock, unload_pubs_from_map, capsys):
    """Refuses to unload pub markers when no map server is running."""
    assert main() == 0

    unload_pubs_from_map.assert_not_called()
    assert "Launch the Oxford map" in capsys.readouterr().out

@patch("beer_app.run.search_loaded_pubs")
@patch("beer_app.pub_loader.load_pubs")
@patch("beer_app.run.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["1", "2", "all", "4", "jericho", "q"])
def test_searches_loaded_pubs_and_updates_map(
    _input_mock, start_map_server, load_pubs, search_pubs
):
    """Sends the loaded pubs and map update callback into the search flow."""
    pubs = [object(), object()]
    load_pubs.return_value = pubs
    map_server = start_map_server.return_value

    assert main() == 0

    search_pubs.assert_called_once_with(pubs, map_server.set_pubs)

@patch("beer_app.run.search_loaded_pubs")
@patch("beer_app.run.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["1", "4", "q"])
def test_requires_loaded_pubs_before_searching(_input_mock, _start_map_server, search_pubs, capsys):
    """Refuses to search when no pubs have been loaded."""
    assert main() == 0

    search_pubs.assert_not_called()
    assert "Load the pub list" in capsys.readouterr().out


@patch("beer_app.run.search_loaded_pubs")
@patch("builtins.input", side_effect=["search", "quit"])
def test_requires_map_before_searching(_input, search_pubs, capsys):
    """Refuses to enter search until the Oxford map has been launched."""
    assert main() == 0

    search_pubs.assert_not_called()
    assert "Launch the Oxford map before searching" in capsys.readouterr().out

@patch("beer_app.run.search_loaded_pubs")
@patch("beer_app.pub_loader.load_pubs")
@patch("beer_app.run.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["1", "2", "all", "4", "q"])
def test_search_dispatches_loaded_pubs_to_search_flow(
    _input_mock, _start_map_server, load_pubs, search_pubs, capsys
):
    """Dispatches loaded pubs to search after loading them onto the map."""
    pubs = [
        Pub(1, "Example", "Jericho Street", "Jericho", "Independent", "", 51.76, -1.26),
    ]
    load_pubs.return_value = pubs

    assert main() == 0

    search_pubs.assert_called_once_with(pubs, _start_map_server.return_value.set_pubs)
    output = capsys.readouterr().out
    assert "Added 1 all pubs" in output

@patch("beer_app.run.run_visualization")
@patch("builtins.input", side_effect=["stats", "quit"])
def test_stats_dispatches_to_visualization_flow(_input_mock, run_visualization):
    """Dispatches the stats command to the visualization menu."""
    assert main() == 0

    run_visualization.assert_called_once_with()


@patch("beer_app.run.run_visited")
@patch("beer_app.run.load_pubs", return_value=["packaged pub"])
@patch("builtins.input", side_effect=["visit", "quit"])
def test_visit_loads_packaged_pubs_when_map_has_no_selection(
    _input, load_pubs, run_visited
):
    """Loads the packaged list for visit management when no map pubs are selected."""
    assert main() == 0

    load_pubs.assert_called_once_with()
    run_visited.assert_called_once_with(["packaged pub"])


@patch("beer_app.run.run_visited")
@patch("beer_app.pub_loader.load_pubs_onto_map", return_value=["loaded pub"])
@patch("beer_app.run.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["launch", "load all", "visit", "quit"])
def test_visit_uses_currently_loaded_map_pubs(
    _input, _start_map_server, _load_pubs, run_visited
):
    """Uses the current map selection for visits instead of reloading all pubs."""
    assert main() == 0

    run_visited.assert_called_once_with(["loaded pub"])


@patch("beer_app.run.run_pub_crawl")
@patch("builtins.input", side_effect=["crawl", "quit"])
def test_crawl_requires_loaded_pubs(_input, run_pub_crawl, capsys):
    """Explains that pubs must be loaded before starting a crawl."""
    assert main() == 0

    run_pub_crawl.assert_not_called()
    assert "Load some pubs before creating a pub crawl" in capsys.readouterr().out


@patch("beer_app.run.run_pub_crawl")
@patch("beer_app.pub_loader.load_pubs_onto_map", return_value=["loaded pub"])
@patch("beer_app.run.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["launch", "load all", "crawl", "quit"])
def test_crawl_uses_currently_loaded_pubs(
    _input, _start_map_server, _load_pubs, run_pub_crawl
):
    """Passes the current map selection to the pub crawl planner."""
    assert main() == 0

    run_pub_crawl.assert_called_once_with(["loaded pub"])


@patch("builtins.input", side_effect=["not-a-command", "quit"])
def test_unknown_command_prints_recovery_guidance(_input, capsys):
    """Prompts the user to view help after an unrecognised menu command."""
    assert main() == 0

    output = capsys.readouterr().out
    assert "Unknown option" in output
    assert "Type 'help'" in output
