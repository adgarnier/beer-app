"""Tests for creating and saving pub crawls."""

import csv

import pytest

from beer_app import pub_crawl
from beer_app.pub_data import Pub, load_pubs

def make_pub(pub_id, name, latitude=51.75, longitude=-1.25):
    """Create a pub fixture with convenient default coordinates."""
    return Pub(pub_id, name, "Road", "Oxford", "Independent", "", latitude, longitude)

def test_distance_to_line_handles_perpendicular_and_outside_segment_points():
    """Measures perpendicular distance and clamps projections to the route endpoints."""
    start = make_pub(1, "Start")
    end = make_pub(2, "End", longitude=-1.24)
    on_route = make_pub(3, "On route", latitude=51.75, longitude=-1.245)
    north_of_route = make_pub(4, "Near route", latitude=51.7505, longitude=-1.245)
    beyond_end = make_pub(5, "Beyond", latitude=51.75, longitude=-1.23)

    assert pub_crawl.distance_to_line(on_route, start, end) == pytest.approx(0)
    assert pub_crawl.distance_to_line(north_of_route, start, end) == pytest.approx(55.6, abs=1)
    assert pub_crawl.distance_to_line(beyond_end, start, end) == pytest.approx(688, abs=2)

def test_pubs_in_buffer_excludes_endpoints_and_pubs_outside_corridor():
    """Keeps only intermediate pubs inside the corridor and rejects negative widths."""
    start = make_pub(1, "Start")
    end = make_pub(2, "End", longitude=-1.24)
    near = make_pub(3, "Near", latitude=51.7505, longitude=-1.245)
    far = make_pub(4, "Far", latitude=51.753, longitude=-1.245)

    assert pub_crawl.pubs_in_buffer([start, end, near, far], start, end, 100) == [near]
    with pytest.raises(ValueError, match="cannot be negative"):
        pub_crawl.pubs_in_buffer([], start, end, -1)

def test_create_crawl_selects_unique_pubs_in_start_to_end_order(monkeypatch):
    """Returns the requested unique stops between fixed endpoints in route order."""
    start = make_pub(1, "Start")
    end = make_pub(2, "End", longitude=-1.24)
    first = make_pub(3, "First", longitude=-1.248)
    second = make_pub(4, "Second", longitude=-1.242)
    monkeypatch.setattr(pub_crawl.random, "sample", lambda candidates, count: [second, first])

    crawl = pub_crawl.create_pub_crawl([start, end, first, second], start, end, 4)

    assert crawl == [start, first, second, end]
    assert len({pub.id for pub in crawl}) == 4

def test_create_crawl_widens_corridor_and_reports_insufficient_pubs(monkeypatch):
    """Widens the route corridor until enough stops are found, or reports shortage."""
    start = make_pub(1, "Start")
    end = make_pub(2, "End", longitude=-1.24)
    candidate = make_pub(3, "Candidate", latitude=51.751, longitude=-1.245)
    buffers = []
    real_pubs_in_buffer = pub_crawl.pubs_in_buffer

    def track_buffer(pubs, start_pub, end_pub, width):
        buffers.append(width)
        return real_pubs_in_buffer(pubs, start_pub, end_pub, width)

    monkeypatch.setattr(pub_crawl, "pubs_in_buffer", track_buffer)
    monkeypatch.setattr(pub_crawl.random, "sample", lambda candidates, count: candidates[:count])
    assert pub_crawl.create_pub_crawl(
        [start, end, candidate], start, end, 3
    ) == [start, candidate, end]
    assert buffers == [100, 200]

    with pytest.raises(ValueError, match="Only 1 intermediate pubs"):
        pub_crawl.create_pub_crawl([start, end, candidate], start, end, 4)
    with pytest.raises(ValueError, match="at least two"):
        pub_crawl.create_pub_crawl([start, end], start, end, 1)
    with pytest.raises(ValueError, match="different pubs"):
        pub_crawl.create_pub_crawl([start, end], start, start, 2)

def test_find_pub_is_case_insensitive_and_rejects_missing_or_ambiguous_queries():
    """Finds a single case-insensitive name fragment and rejects missing or ambiguous matches."""
    pubs = [make_pub(1, "The Crown"), make_pub(2, "Crown and Anchor")]
    assert pub_crawl.find_pub(pubs, "the crown") == pubs[0]
    with pytest.raises(ValueError, match="No pub found"):
        pub_crawl.find_pub(pubs, "missing")
    with pytest.raises(ValueError, match="More than one pub"):
        pub_crawl.find_pub(pubs, "crown")

def test_save_crawl_round_trips_in_route_order(tmp_path):
    """Writes a standard pub CSV that can be reloaded in the original route order."""
    crawl = [make_pub(2, "End"), make_pub(1, "Start")]
    path = tmp_path / "nested" / "crawl.csv"

    assert pub_crawl.save_pub_crawl(crawl, path) == path
    assert [pub.id for pub in load_pubs(path)] == [2, 1]
    with path.open(encoding="utf-8", newline="") as csv_file:
        assert next(csv.reader(csv_file)) == list(pub_crawl.CRAWL_COLUMNS)

def test_main_saves_and_displays_a_valid_crawl(monkeypatch, tmp_path, capsys):
    """Creates, saves, and displays a crawl from valid interactive input."""
    pubs = [make_pub(1, "Start"), make_pub(2, "End", longitude=-1.24)]
    destination = tmp_path / "crawl.csv"
    answers = iter(["Start", "End", "2"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    monkeypatch.setattr(pub_crawl, "save_pub_crawl", lambda crawl: destination)

    assert pub_crawl.main(pubs) == 0
    assert "1. Start" in capsys.readouterr().out

def test_main_reports_invalid_input_and_cancellation(monkeypatch, capsys):
    """Reports invalid pub input and exits cleanly when the prompt is interrupted."""
    answers = iter(["missing", "End", "2"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    assert pub_crawl.main([make_pub(1, "Start"), make_pub(2, "End")]) == 1
    assert "No pub found" in capsys.readouterr().out

    def cancel(_prompt):
        raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", cancel)
    assert pub_crawl.main([]) == 0
    assert "cancelled" in capsys.readouterr().out
