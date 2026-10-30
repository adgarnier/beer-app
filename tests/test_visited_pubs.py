"""Tests for recording and managing pub visits."""

import pytest

from beer_app.pub_data import Pub
from beer_app.visited_pubs import (
    load_visit_history,
    manage_visited,
    record_visit_today,
    save_visit_history,
)

def test_records_at_most_one_visit_per_pub_each_day(tmp_path):
    """Records a pub once per day and preserves its visited status and date."""
    history = tmp_path / "visited_pubs.csv"

    assert record_visit_today(42, history)
    assert not record_visit_today(42, history)

    statuses, dates = load_visit_history(history)
    assert statuses == {42: True}
    assert len(dates[42]) == 1

def test_load_visit_history_accepts_common_boolean_values_and_skips_invalid_ids(tmp_path):
    """Parses common true and false values while skipping rows with invalid IDs."""
    history = tmp_path / "visits.csv"
    history.write_text(
        "ID,Visited,VisitDate\n1,YES,2025-01-01\n2,0,2025-01-02\n"
        "3,unknown,2025-01-03\nbad,true,2025-01-04\n",
        encoding="utf-8",
    )

    assert load_visit_history(history) == (
        {1: True, 2: False},
        {1: ["2025-01-01"], 2: ["2025-01-02"], 3: ["2025-01-03"]},
    )

def test_missing_history_is_empty_and_save_is_sorted_and_round_trips(tmp_path):
    """Returns empty history for a missing file and round-trips saved rows in sorted order."""
    history = tmp_path / "nested" / "visits.csv"
    assert load_visit_history(history) == ({}, {})

    save_visit_history({2: False, 1: True}, {2: ["2025-01-03", "2025-01-04"]}, history)

    assert load_visit_history(history) == (
        {1: True, 2: False},
        {2: ["2025-01-03", "2025-01-04"]},
    )

def test_manage_visited_records_visit_and_can_unvisit_without_deleting_dates(
    monkeypatch, tmp_path, capsys
):
    """Accepts valid visit and unvisit commands while retaining past visit dates."""
    history = tmp_path / "visits.csv"
    pub = Pub(42, "Example", "Road", "Oxford", "Independent", "", 51.75, -1.25)
    monkeypatch.setattr("beer_app.visited_pubs._default_visited_path", lambda: history)
    answers = iter(["nope", "not-an-id", "999", "42 extra", "42", "unvisit 42", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    manage_visited([pub])

    statuses, dates = load_visit_history(history)
    assert 42 not in statuses
    assert 42 not in dates
    output = capsys.readouterr().out
    assert "numeric pub ID" in output
    assert "not in the pub list" in output
    assert "Removed pub" in output

@pytest.mark.parametrize("exception", [EOFError, KeyboardInterrupt])
def test_manage_visited_returns_cleanly_when_input_is_interrupted(monkeypatch, exception, capsys):
    """Returns to the caller when input ends or is interrupted."""
    monkeypatch.setattr("builtins.input", lambda _prompt: (_ for _ in ()).throw(exception()))

    manage_visited([])

    assert capsys.readouterr().out.endswith("\n")
