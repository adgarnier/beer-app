"""Tests for the main application menu."""

from unittest.mock import patch

from main import main


@patch("main.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["1", "q"])
def test_launches_oxford_map_in_background(input_mock, start_map_server, capsys):
    map_server = start_map_server.return_value
    map_server.url = "http://127.0.0.1:8000"

    assert main() == 0

    assert input_mock.call_count == 2
    start_map_server.assert_called_once_with(port=0)
    map_server.stop.assert_called_once_with()
    output = capsys.readouterr().out
    assert "OXFORD PUB TRACKING APP" in output
    assert "running in the background" in output


@patch("builtins.input", return_value="q")
def test_can_quit_from_welcome_menu(input_mock, capsys):
    assert main() == 0

    assert input_mock.call_count == 1
    assert "Goodbye!" in capsys.readouterr().out


@patch("main.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["1", "1", "q"])
def test_does_not_launch_a_second_map_server(input_mock, start_map_server, capsys):
    start_map_server.return_value.url = "http://127.0.0.1:8000"

    assert main() == 0

    assert input_mock.call_count == 3
    start_map_server.assert_called_once_with(port=0)
    assert "already running" in capsys.readouterr().out


@patch("main.load_pubs")
@patch("main.oxford_map.start_map_server")
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


@patch("main.load_pubs")
@patch("builtins.input", side_effect=["2", "q"])
def test_requires_map_before_loading_pubs(input_mock, load_pubs, capsys):
    assert main() == 0

    load_pubs.assert_not_called()
    assert "Launch the Oxford map" in capsys.readouterr().out


@patch("main.oxford_map.start_map_server")
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
