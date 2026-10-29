"""Tests for recording pub visits."""

from beer_app.visited_pubs import load_visit_history, record_visit_today


def test_records_at_most_one_visit_per_pub_each_day(tmp_path):
    history = tmp_path / "visited_pubs.csv"

    assert record_visit_today(42, history)
    assert not record_visit_today(42, history)

    statuses, dates = load_visit_history(history)
    assert statuses == {42: True}
    assert len(dates[42]) == 1
