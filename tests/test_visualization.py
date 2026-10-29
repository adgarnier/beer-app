"""Tests for visit chart data and presentation."""

from unittest.mock import MagicMock, patch

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

from beer_app import visualization

matplotlib.use("Agg")

def test_pub_chart_has_labels_bars_and_cycles_palette():
    """Labels the per-pub chart and repeats its color palette after eight pubs."""
    data = pd.DataFrame(
        {"name": [f"Pub {index}" for index in range(10)], "Count": range(1, 11)}
    )

    fig = visualization.p_visits_per_pub(data)

    ax = fig.axes[0]
    assert ax.get_title() == "Pub'lishes per Pub"
    assert ax.get_xlabel() == "Pub Legal Name"
    assert ax.get_ylabel() == "Number of Pub'lishes"
    assert len(ax.patches) == 10
    assert ax.patches[0].get_facecolor() == ax.patches[8].get_facecolor()
    plt.close(fig)

def test_time_chart_aggregates_months_and_keeps_months_without_visits():
    """Aggregates visits by month and includes a zero-height bar for empty months."""
    data = pd.DataFrame(
        {
            "ID": [1, 1, 2],
            "name": ["A", "A", "B"],
            "location": ["Oxford", "Oxford", "Jericho"],
            "VisitDate": ["2025-01-02", "2025-01-20", "2025-03-04"],
        }
    )

    fig = visualization.p_visits_over_time(data)

    ax = fig.axes[0]
    month_labels = [label.get_text() for label in ax.get_xticklabels()]
    assert month_labels == ["Jan 2025", "Feb 2025", "Mar 2025"]
    assert sorted(patch.get_height() for patch in ax.patches) == [0, 0, 0, 0, 1, 2]
    assert ax.get_title() == "Pub'lishes per Month"
    plt.close(fig)

def test_stats_menu_help_launches_graph_and_quits(monkeypatch, capsys):
    """Shows help, launches the pub chart, and exits on the quit command."""
    choices = iter(["--help", "pub", "q"])
    launched = []

    process = type("FinishedProcess", (), {"is_alive": lambda _self: False})()

    def launch(target):
        launched.append(target)
        return process

    monkeypatch.setattr("builtins.input", lambda _prompt: next(choices))
    monkeypatch.setattr(visualization, "launch_stats_graph", launch)

    assert visualization.main() == 0
    assert launched == [visualization.show_visits_per_pub]
    assert "Stats help" in capsys.readouterr().out

def test_stats_menu_handles_eof(monkeypatch, capsys):
    """Returns cleanly when the stats prompt reaches end of input."""
    monkeypatch.setattr("builtins.input", lambda _prompt: (_ for _ in ()).throw(EOFError()))

    assert visualization.main() == 0
    assert "Leaving stats" in capsys.readouterr().out


@patch("beer_app.visualization.plt.show")
@patch("beer_app.visualization.p_visits_per_pub")
@patch("beer_app.visualization.pub_counts", return_value="visit counts")
def test_show_visits_per_pub_builds_and_displays_chart(
    pub_counts, plot_visits, show
):
    """Fetches pub counts, builds their chart, and displays it once."""
    visualization.show_visits_per_pub()

    pub_counts.assert_called_once_with()
    plot_visits.assert_called_once_with("visit counts")
    show.assert_called_once_with()


@patch("beer_app.visualization.plt.show")
@patch("beer_app.visualization.p_visits_over_time")
@patch("beer_app.visualization.visited_pub_times", return_value="visit history")
def test_show_visits_over_time_builds_and_displays_chart(
    visited_pub_times, plot_visits, show
):
    """Fetches visit history, builds its time chart, and displays it once."""
    visualization.show_visits_over_time()

    visited_pub_times.assert_called_once_with()
    plot_visits.assert_called_once_with("visit history")
    show.assert_called_once_with()


@patch("beer_app.visualization.Process")
def test_launch_stats_graph_starts_daemon_process(process_class):
    """Starts and returns a daemon process for the requested chart function."""
    target = MagicMock()

    process = visualization.launch_stats_graph(target)

    process_class.assert_called_once_with(target=target, daemon=True)
    process_class.return_value.start.assert_called_once_with()
    assert process is process_class.return_value


def test_stats_menu_launches_time_chart_and_reports_unknown_choice(
    monkeypatch, capsys
):
    """Reports invalid input, launches the time chart, then accepts a quit alias."""
    choices = iter(["not-a-chart", "visits over time", "bye"])
    process = MagicMock()
    process.is_alive.return_value = True
    launch = MagicMock(return_value=process)
    monkeypatch.setattr("builtins.input", lambda _prompt: next(choices))
    monkeypatch.setattr(visualization, "launch_stats_graph", launch)

    assert visualization.main() == 0

    launch.assert_called_once_with(visualization.show_visits_over_time)
    assert process.is_alive.call_count == 1
    output = capsys.readouterr().out
    assert "Unknown stats option" in output
    assert "Leaving stats" in output
