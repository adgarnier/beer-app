"""Tests for searching the Oxford pub list."""

from unittest.mock import MagicMock, patch

import pytest

from beer_app.pub_data import Pub
from beer_app.pub_search import (
    SEARCH_HELP,
    format_pub_values,
    is_help_query,
    list_pub_values,
    list_query_field,
    main,
    search_loaded_pubs,
    search_pubs,
)

PUBS = [
    Pub(
        1, "The Gardeners Arms", "Plantation Road", "Jericho", "Independent",
        "Large beer garden", 51.76, -1.26,
    ),
    Pub(
        2, "City Tavern", "High Street", "Town Centre", "Greene King",
        "Historic interior", 51.75, -1.25,
    ),
    Pub(
        3, "Jericho Ale House", "Jericho Road", "Jericho", "Independent",
        "Local ales", 51.77, -1.27,
    ),
]

def test_searches_across_pub_fields_without_case_sensitivity():
    """Matches every query word across pub fields without regard to case."""
    assert [pub.name for pub in search_pubs(PUBS, "GREENE")] == ["City Tavern"]
    assert [pub.name for pub in search_pubs(PUBS, "beer garden")] == ["The Gardeners Arms"]
    assert [pub.name for pub in search_pubs(PUBS, "jericho local")] == ["Jericho Ale House"]

def test_blank_search_returns_all_pubs():
    """Returns the complete loaded pub list for a whitespace-only query."""
    assert search_pubs(PUBS, "   ") == PUBS

def test_search_with_no_matches_returns_empty_list():
    """Returns an empty list when no pub matches the query."""
    assert not search_pubs(PUBS, "not-a-real-pub")

def test_recognises_help_keyword():
    """Recognises the help flag after trimming whitespace and ignoring case."""
    assert is_help_query("--help")
    assert is_help_query(" --HELP ")
    assert not is_help_query("help")

def test_command_line_help_keyword_prints_search_guidance(capsys):
    """Prints search guidance and exits successfully when given the help flag."""
    assert main(["--help"]) == 0

    output = capsys.readouterr().out
    assert output.strip() == SEARCH_HELP.strip()
    assert "pub name" in output
    assert "beer garden" in output

def test_lists_unique_locations_and_splits_combined_values():
    """Splits semicolon-separated locations and returns each unique location once."""
    pubs = [
        Pub(1, "One", "Walton Street", "Jericho", "Independent", "", 51.76, -1.26),
        Pub(2, "Two", "Jericho Street", "Jericho", "Independent", "", 51.75, -1.25),
    ]

    assert list_query_field("--list location") == "location"
    assert list_pub_values(pubs, "location") == ["Jericho"]

def test_list_without_field_shows_available_fields():
    """Lists the supported fields when --list has no field argument."""
    assert list_query_field("--list") == "fields"
    assert list_pub_values(PUBS, "fields") == ["name", "road", "location", "sponsor"]

def test_unknown_list_field_is_rejected():
    """Rejects a --list field that the search interface does not support."""
    try:
        list_query_field("--list price")
    except ValueError as error:
        assert "Unknown list field" in str(error)
    else:
        raise AssertionError("Expected an unknown list field to be rejected")


def test_non_list_query_has_no_list_field():
    """Returns no list field for blank input and ordinary search terms."""
    assert list_query_field("") is None
    assert list_query_field("Jericho") is None


def test_list_command_rejects_more_than_one_field():
    """Rejects list commands containing extra field arguments."""
    with pytest.raises(ValueError, match="one field name"):
        list_query_field("--list location sponsor")


def test_list_pub_values_rejects_non_listable_field():
    """Rejects direct requests for values from unsupported pub fields."""
    with pytest.raises(ValueError, match="cannot be listed"):
        list_pub_values(PUBS, "notes")


def test_format_pub_values_reports_empty_and_populated_results():
    """Formats field headings and explicitly labels empty value collections."""
    assert format_pub_values("fields", ["name"]) == "Available list fields:\n name"
    assert format_pub_values("sponsor", []) == "Available sponsor values:\n  none"

def test_command_line_list_prints_values(capsys):
    """Prints the unique values for a requested field and exits successfully."""
    assert main(["--list", "location"]) == 0

    output = capsys.readouterr().out
    assert "Available location values" in output
    assert "Jericho" in output


def test_interactive_search_handles_help_list_error_then_returns_matches(
    monkeypatch, capsys
):
    """Keeps prompting after help and list commands before publishing search matches."""
    answers = iter(["--help", "--list price", "--list location", "jericho local"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    on_results = MagicMock()

    assert search_loaded_pubs(PUBS, on_results) == 0

    on_results.assert_called_once_with([PUBS[2]])
    output = capsys.readouterr().out
    assert "Search help" in output
    assert "Unknown list field" in output
    assert "Available location values" in output
    assert "Found 1 pubs matching 'jericho local'" in output


def test_interactive_blank_search_restores_all_loaded_pubs(monkeypatch, capsys):
    """Sends every loaded pub to the map when the interactive query is blank."""
    monkeypatch.setattr("builtins.input", lambda _prompt: "   ")
    on_results = MagicMock()

    assert search_loaded_pubs(iter(PUBS), on_results) == 0

    on_results.assert_called_once_with(PUBS)
    assert "Showing all 3 pubs" in capsys.readouterr().out


@pytest.mark.parametrize("interruption", [EOFError, KeyboardInterrupt])
def test_interactive_search_exits_cleanly_when_input_is_interrupted(
    monkeypatch, interruption, capsys
):
    """Leaves search without updating results when input ends or is interrupted."""
    def interrupt(_prompt):
        raise interruption

    monkeypatch.setattr("builtins.input", interrupt)
    on_results = MagicMock()

    assert search_loaded_pubs(PUBS, on_results) == 0

    on_results.assert_not_called()
    assert "Leaving search" in capsys.readouterr().out


@patch("beer_app.pub_search.load_pubs", return_value=PUBS)
def test_command_line_query_prints_each_matching_pub(load_pubs, capsys):
    """Loads packaged pubs and prints names and locations matching CLI query words."""
    assert main(["jericho", "local"]) == 0

    load_pubs.assert_called_once_with()
    output = capsys.readouterr().out
    assert "Found 1 matching pubs" in output
    assert "Jericho Ale House (Jericho)" in output
    assert "City Tavern" not in output
