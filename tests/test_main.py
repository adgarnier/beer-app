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
    start_map_server.assert_called_once_with()
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
    start_map_server.assert_called_once_with()
    assert "already running" in capsys.readouterr().out
