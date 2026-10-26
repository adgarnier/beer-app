"""Tests for the main application menu."""

from unittest.mock import patch

from beer_app.pub_data import Pub
from beer_app.main import main


@patch("beer_app.main.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["1", "q"])
def test_launches_oxford_map_in_background(input_mock, start_map_server, capsys):
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
    assert main() == 0

    assert input_mock.call_count == 1
    assert "Goodbye!" in capsys.readouterr().out


@patch("beer_app.main.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["1", "1", "q"])
def test_does_not_launch_a_second_map_server(input_mock, start_map_server, capsys):
    start_map_server.return_value.url = "http://127.0.0.1:8000"

    assert main() == 0

    assert input_mock.call_count == 3
    start_map_server.assert_called_once_with(port=0)
    assert "already running" in capsys.readouterr().out


@patch("beer_app.main.load_pubs")
@patch("beer_app.main.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["1", "2", "q"])
def test_loads_pubs_onto_running_map(input_mock, start_map_server, load_pubs, capsys):
    pubs = [object(), object()]
    load_pubs.return_value = pubs
    map_server = start_map_server.return_value

    assert main() == 0

    assert input_mock.call_count == 3
    load_pubs.assert_called_once_with()
    map_server.set_pubs.assert_called_once_with(pubs)
    assert "Added 2 pubs" in capsys.readouterr().out


@patch("beer_app.main.load_pubs")
@patch("builtins.input", side_effect=["2", "q"])
def test_requires_map_before_loading_pubs(input_mock, load_pubs, capsys):
    assert main() == 0

    load_pubs.assert_not_called()
    assert "Launch the Oxford map" in capsys.readouterr().out


@patch("beer_app.main.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["1", "3", "q"])
def test_unloads_pubs_from_running_map(input_mock, start_map_server, capsys):
    map_server = start_map_server.return_value

    assert main() == 0

    assert input_mock.call_count == 3
    map_server.clear_pubs.assert_called_once_with()
    assert "Removed all pubs" in capsys.readouterr().out


@patch("builtins.input", side_effect=["3", "q"])
def test_requires_map_before_unloading_pubs(input_mock, capsys):
    assert main() == 0

    assert "Launch the Oxford map" in capsys.readouterr().out


@patch("beer_app.main.search_pubs")
@patch("beer_app.main.load_pubs")
@patch("beer_app.main.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["1", "2", "4", "jericho", "q"])
def test_searches_loaded_pubs_and_updates_map(input_mock, start_map_server, load_pubs, search_pubs, capsys):
    pubs = [object(), object()]
    matches = [pubs[0]]
    load_pubs.return_value = pubs
    search_pubs.return_value = matches
    map_server = start_map_server.return_value

    assert main() == 0

    assert input_mock.call_count == 5
    search_pubs.assert_called_once_with(pubs, "jericho")
    assert map_server.set_pubs.call_args_list[-1].args == (matches,)
    assert "Found 1 pubs" in capsys.readouterr().out


@patch("beer_app.main.search_pubs")
@patch("beer_app.main.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["1", "4", "q"])
def test_requires_loaded_pubs_before_searching(input_mock, start_map_server, search_pubs, capsys):
    assert main() == 0

    search_pubs.assert_not_called()
    assert "Load the pub list" in capsys.readouterr().out


@patch("beer_app.main.search_pubs")
@patch("beer_app.main.load_pubs")
@patch("beer_app.main.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["1", "2", "4", "--help", "jericho", "q"])
def test_search_help_does_not_change_map(input_mock, start_map_server, load_pubs, search_pubs, capsys):
    pubs = [object()]
    matches = [pubs[0]]
    load_pubs.return_value = pubs
    search_pubs.return_value = matches
    map_server = start_map_server.return_value

    assert main() == 0

    search_pubs.assert_called_once_with(pubs, "jericho")
    assert map_server.set_pubs.call_count == 2
    assert map_server.set_pubs.call_args_list[-1].args == (matches,)
    output = capsys.readouterr().out
    assert "Search help" in output
    assert "pub name" in output


@patch("beer_app.main.search_pubs")
@patch("beer_app.main.load_pubs")
@patch("beer_app.main.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["1", "2", "4", "--list location", "jericho", "q"])
def test_search_list_command_stays_in_search_mode(input_mock, start_map_server, load_pubs, search_pubs, capsys):
    pubs = [
        Pub(1, "Example", "Jericho", "Independent", "", 51.76, -1.26),
    ]
    load_pubs.return_value = pubs
    search_pubs.return_value = pubs

    assert main() == 0

    search_pubs.assert_called_once_with(pubs, "jericho")
    output = capsys.readouterr().out
    assert "Available location values" in output
    assert "Jericho" in output
