"""Tests for visit statistics derived from CSV history."""

import pandas as pd

from beer_app import stats
from beer_app.pub_data import Pub

def test_visited_pub_count_counts_true_statuses_and_joins_pub_names(monkeypatch, tmp_path):
    """Counts only true visit rows and joins counts to known pub names."""
    history = tmp_path / "visits.csv"
    history.write_text(
        "ID,Visited,VisitDate\n1,true,2025-01-01\n1,TRUE,2025-02-01\n2,false,\n3,yes,2025-03-01\n",
        encoding="utf-8",
    )
    pubs = [
        Pub(1, "One", "Road", "Oxford", "Independent", "", 51.7, -1.2),
        Pub(3, "Three", "Road", "Oxford", "Independent", "", 51.7, -1.2),
    ]
    monkeypatch.setattr(stats, "load_pubs", lambda: pubs)

    result = stats.visited_pub_count(history)

    assert result.to_dict("records") == [{"ID": 1, "Count": 2, "name": "One"}]

def test_visited_pub_times_filters_and_adds_pub_metadata(monkeypatch, tmp_path):
    """Filters out unvisited rows and adds each visited pub name and location."""
    history = tmp_path / "visits.csv"
    history.write_text(
        "ID,Visited,VisitDate\n1,true,2025-01-01\n2,no,2025-02-01\n",
        encoding="utf-8",
    )
    pubs = [
        Pub(1, "One", "Road", "Oxford", "Independent", "", 51.7, -1.2),
        Pub(2, "Two", "Lane", "Jericho", "Independent", "", 51.7, -1.2),
    ]
    monkeypatch.setattr(stats, "visited_pub_path", lambda: history)
    monkeypatch.setattr(stats, "load_pubs", lambda: pubs)

    result = stats.visited_pub_times()

    assert result[["ID", "VisitDate", "name", "location"]].to_dict("records") == [
        {"ID": 1, "VisitDate": "2025-01-01", "name": "One", "location": "Oxford"}
    ]

def test_public_functions_use_the_default_visit_file(monkeypatch, tmp_path):
    """Reads the default history path when computing public visit counts."""
    history = tmp_path / "visits.csv"
    history.write_text(
        "ID,Visited,VisitDate\n1,true,2025-01-01\n", encoding="utf-8"
    )
    monkeypatch.setattr(stats, "visited_pub_path", lambda: history)
    monkeypatch.setattr(
        stats,
        "visited_pub_count",
        lambda path: pd.DataFrame({"path": [str(path)]}),
    )

    assert stats.pub_counts().iloc[0, 0] == str(history)
    assert stats.visited_pub_path() == history
