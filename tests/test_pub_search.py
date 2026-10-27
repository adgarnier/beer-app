"""Tests for searching the Oxford pub list."""

from beer_app.pub_data import Pub
from beer_app.pub_search import (
    SEARCH_HELP,
    format_pub_values,
    is_help_query,
    list_pub_values,
    list_query_field,
    main,
    search_pubs,
)


PUBS = [
    Pub(1, "The Gardeners Arms", "Plantation Road", "Jericho", "Independent", "Large beer garden", 51.76, -1.26),
    Pub(2, "City Tavern", "High Street", "Town Centre", "Greene King", "Historic interior", 51.75, -1.25),
    Pub(3, "Jericho Ale House", "Jericho Road", "Jericho", "Independent", "Local ales", 51.77, -1.27),
]


def test_searches_across_pub_fields_without_case_sensitivity():
    assert [pub.name for pub in search_pubs(PUBS, "GREENE")] == ["City Tavern"]
    assert [pub.name for pub in search_pubs(PUBS, "beer garden")] == ["The Gardeners Arms"]
    assert [pub.name for pub in search_pubs(PUBS, "jericho local")] == ["Jericho Ale House"]


def test_blank_search_returns_all_pubs():
    assert search_pubs(PUBS, "   ") == PUBS


def test_search_with_no_matches_returns_empty_list():
    assert search_pubs(PUBS, "not-a-real-pub") == []


def test_recognises_help_keyword():
    assert is_help_query("--help")
    assert is_help_query(" --HELP ")
    assert not is_help_query("help")


def test_command_line_help_keyword_prints_search_guidance(capsys):
    assert main(["--help"]) == 0

    output = capsys.readouterr().out
    assert output.strip() == SEARCH_HELP.strip()
    assert "pub name" in output
    assert "beer garden" in output


def test_lists_unique_locations_and_splits_combined_values():
    pubs = [
        Pub(1, "One", "Walton Street", "Jericho", "Independent", "", 51.76, -1.26),
        Pub(2, "Two", "Jericho Street", "Jericho", "Independent", "", 51.75, -1.25),
    ]

    assert list_query_field("--list location") == "location"
    assert list_pub_values(pubs, "location") == ["Walton Street", "Jericho"]


def test_list_without_field_shows_available_fields():
    assert list_query_field("--list") == "fields"
    assert list_pub_values(PUBS, "fields") == ["name", "road", "location", "sponsor"]


def test_unknown_list_field_is_rejected():
    try:
        list_query_field("--list price")
    except ValueError as error:
        assert "Unknown list field" in str(error)
    else:
        raise AssertionError("Expected an unknown list field to be rejected")


def test_formats_list_values_for_terminal():
    output = format_pub_values("location", ["Town Centre", "Jericho"])

    assert output == "Available location values:\n  Town Centre\n  Jericho"


def test_command_line_list_prints_values(capsys):
    assert main(["--list", "location"]) == 0

    output = capsys.readouterr().out
    assert "Available location values" in output
    assert "Jericho" in output
