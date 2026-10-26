"""Tests for the main application menu."""

from unittest.mock import patch

from main import main


@patch("main.oxford_map.main", return_value=0)
@patch("builtins.input", return_value="1")
def test_launches_oxford_map(input_mock, map_main, capsys):
    assert main() == 0

    assert input_mock.call_count == 1
    map_main.assert_called_once_with([])
    output = capsys.readouterr().out
    assert "OXFORD PUB TRACKING APP" in output
    assert ".sssssssss." in output


@patch("builtins.input", return_value="q")
def test_can_quit_from_welcome_menu(input_mock, capsys):
    assert main() == 0

    assert input_mock.call_count == 1
    assert "Goodbye!" in capsys.readouterr().out


@patch("main.oxford_map.main", return_value=0)
@patch("builtins.input", side_effect=["invalid", "1"])
def test_reprompts_after_invalid_choice(input_mock, map_main, capsys):
    assert main() == 0

    assert input_mock.call_count == 2
    map_main.assert_called_once_with([])
    assert "Please enter 1" in capsys.readouterr().out
