"""Tests for the main application menu."""

from unittest.mock import patch

from beer_app.pub_data import Pub
from beer_app.run import main


@patch("beer_app.run.oxford_map.start_map_server")
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


@patch("beer_app.run.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["1", "1", "q"])
def test_does_not_launch_a_second_map_server(input_mock, start_map_server, capsys):
    start_map_server.return_value.url = "http://127.0.0.1:8000"

    assert main() == 0

    assert input_mock.call_count == 3
    start_map_server.assert_called_once_with(port=0)
    assert "already running" in capsys.readouterr().out


@patch("beer_app.run.load_pubs_onto_map")
@patch("beer_app.run.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["1", "2", "all", "q"])
def test_loads_pubs_onto_running_map(input_mock, start_map_server, load_pubs_onto_map, capsys):
    pubs = [object(), object()]
    load_pubs_onto_map.return_value = pubs
    map_server = start_map_server.return_value

    assert main() == 0

    assert input_mock.call_count == 4
    load_pubs_onto_map.assert_called_once_with(map_server, "all")


@patch("beer_app.run.load_pubs_onto_map")
@patch("beer_app.run.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["launch", "load visited", "quit"])
def test_loads_visited_pubs_with_direct_command(input_mock, start_map_server, load_pubs_onto_map):
    load_pubs_onto_map.return_value = [object()]
    map_server = start_map_server.return_value

    assert main() == 0

    load_pubs_onto_map.assert_called_once_with(map_server, "visited")


@patch("beer_app.run.load_pubs_onto_map")
@patch("builtins.input", side_effect=["2", "q"])
def test_requires_map_before_loading_pubs(input_mock, load_pubs_onto_map, capsys):
    assert main() == 0

    load_pubs_onto_map.assert_not_called()
    assert "Launch the Oxford map" in capsys.readouterr().out


@patch("beer_app.run.load_pubs_onto_map")
@patch("builtins.input", side_effect=["load --help", "q"])
def test_load_help_does_not_require_or_change_map(input_mock, load_pubs_onto_map, capsys):
    assert main() == 0

    load_pubs_onto_map.assert_not_called()
    output = capsys.readouterr().out
    assert "Load help" in output
    assert "load visited" in output


@patch("beer_app.run.unload_pubs_from_map")
@patch("beer_app.run.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["1", "3", "q"])
def test_unloads_pubs_from_running_map(input_mock, start_map_server, unload_pubs_from_map, capsys):
    map_server = start_map_server.return_value

    assert main() == 0

    assert input_mock.call_count == 3
    unload_pubs_from_map.assert_called_once_with(map_server)


@patch("beer_app.run.unload_pubs_from_map")
@patch("builtins.input", side_effect=["3", "q"])
def test_requires_map_before_unloading_pubs(input_mock, unload_pubs_from_map, capsys):
    assert main() == 0

    unload_pubs_from_map.assert_not_called()
    assert "Launch the Oxford map" in capsys.readouterr().out


@patch("beer_app.run.search_pubs")
@patch("beer_app.pub_loader.load_pubs")
@patch("beer_app.run.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["1", "2", "all", "4", "jericho", "q"])
def test_searches_loaded_pubs_and_updates_map(input_mock, start_map_server, load_pubs, search_pubs, capsys):
    pubs = [object(), object()]
    matches = [pubs[0]]
    load_pubs.return_value = pubs
    search_pubs.return_value = matches
    map_server = start_map_server.return_value

    assert main() == 0

    assert input_mock.call_count == 6
    search_pubs.assert_called_once_with(pubs, "jericho")
    assert map_server.set_pubs.call_args_list[-1].args == (matches,)
    assert "Found 1 pubs" in capsys.readouterr().out


@patch("beer_app.run.search_pubs")
@patch("beer_app.run.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["1", "4", "q"])
def test_requires_loaded_pubs_before_searching(input_mock, start_map_server, search_pubs, capsys):
    assert main() == 0

    search_pubs.assert_not_called()
    assert "Load the pub list" in capsys.readouterr().out


@patch("beer_app.run.search_pubs")
@patch("beer_app.pub_loader.load_pubs")
@patch("beer_app.run.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["1", "2", "all", "4", "--help", "jericho", "q"])
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


@patch("beer_app.run.search_pubs")
@patch("beer_app.pub_loader.load_pubs")
@patch("beer_app.run.oxford_map.start_map_server")
@patch("builtins.input", side_effect=["1", "2", "all", "4", "--list location", "jericho", "q"])
def test_search_list_command_stays_in_search_mode(input_mock, start_map_server, load_pubs, search_pubs, capsys):
    pubs = [
        Pub(1, "Example", "Jericho Street", "Jericho", "Independent", "", 51.76, -1.26),
    ]
    load_pubs.return_value = pubs
    search_pubs.return_value = pubs

    assert main() == 0

    search_pubs.assert_called_once_with(pubs, "jericho")
    output = capsys.readouterr().out
    assert "Available location values" in output
    assert "Jericho" in output


@patch("beer_app.run.plt.show")
@patch("beer_app.run.p_visits_per_pub")
@patch("beer_app.run.pub_counts", return_value="pub counts")
@patch("builtins.input", side_effect=["stats", "visits per pub", "quit"])
def test_stats_can_show_visits_per_pub(input_mock, pub_counts, p_visits_per_pub, show):
    assert main() == 0

    p_visits_per_pub.assert_called_once_with("pub counts")
    show.assert_called_once_with()


@patch("beer_app.run.plt.show")
@patch("beer_app.run.p_visits_over_time")
@patch("beer_app.run.visited_pub_times", return_value="visit times")
@patch("builtins.input", side_effect=["stats", "visits over time", "quit"])
def test_stats_can_show_visits_over_time(input_mock, visited_pub_times, p_visits_over_time, show):
    assert main() == 0

    p_visits_over_time.assert_called_once_with("visit times")
    show.assert_called_once_with()


@patch("beer_app.run.plt.show")
@patch("beer_app.run.p_visits_per_pub")
@patch("beer_app.run.pub_counts", return_value="pub counts")
@patch("builtins.input", side_effect=["stats", "--help", "pub", "quit"])
def test_stats_help_stays_in_stats_menu(input_mock, pub_counts, p_visits_per_pub, show, capsys):
    assert main() == 0

    assert "Stats help" in capsys.readouterr().out
    p_visits_per_pub.assert_called_once_with("pub counts")
    show.assert_called_once_with()
