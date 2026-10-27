"""Search Oxford pubs by their text fields."""

from __future__ import annotations

import argparse
from collections.abc import Iterable

from .pub_data import Pub, load_pubs


SEARCH_HELP = """Search help

You can search the loaded pubs by:
  pub name, for example: lamb and flag
  location, for example: jericho
  road, for example: cowley road
  sponsor or owner, for example: greene king
  words in the notes, for example: beer garden

Searches ignore capital letters. When you enter several words, a pub must match
all of them. Submit a blank search to show every loaded pub again.

Search commands:
  --help              show this guidance
  --list              show the fields that can be listed
  --list name         show every pub name
  --list location     show available locations
  --list road         show available roads
  --list sponsor      show available sponsors or owners
"""

LISTABLE_FIELDS = ("name", "location", "road", "sponsor")


def is_help_query(query: str) -> bool:
    """Return whether a query requests search guidance."""
    return query.strip().casefold() == "--help"


def list_query_field(query: str) -> str | None:
    """Return the requested field for a ``--list`` command, if present."""
    parts = query.strip().casefold().split()
    if not parts or parts[0] != "--list":
        return None
    if len(parts) == 1:
        return "fields"
    if len(parts) != 2:
        raise ValueError("Use --list by itself or with one field name.")
    if parts[1] not in LISTABLE_FIELDS:
        fields = ", ".join(LISTABLE_FIELDS)
        raise ValueError(f"Unknown list field {parts[1]!r}. Choose from: {fields}.")
    return parts[1]


def list_pub_values(pubs: Iterable[Pub], field: str) -> list[str]:
    """Return sorted unique values for a listable pub field."""
    if field == "fields":
        return list(LISTABLE_FIELDS)
    if field not in LISTABLE_FIELDS:
        raise ValueError(f"Field {field!r} cannot be listed.")

    values = set()
    for pub in pubs:
        value = getattr(pub, field)
        parts = value.split(";") if field == "location" else [value]
        values.update(part.strip() for part in parts if part.strip())
    return sorted(values, key=str.casefold)


def format_pub_values(field: str, values: Iterable[str]) -> str:
    """Format list-command results for terminal display."""
    value_list = list(values)
    heading = "Available list fields" if field == "fields" else f"Available {field} values"
    if not value_list:
        return f"{heading}:\n- none"
    return f"{heading}:\n" + "\n".join(f" {value}" for value in value_list)


def search_pubs(pubs: Iterable[Pub], query: str) -> list[Pub]:
    """Return pubs matching every word in a case-insensitive query."""
    terms = query.casefold().split()
    pub_list = list(pubs)
    if not terms:
        return pub_list

    matches = []
    for pub in pub_list:
        searchable_text = " ".join((pub.name, pub.road, pub.location, pub.sponsor, pub.notes)).casefold()
        if all(term in searchable_text for term in terms):
            matches.append(pub)
    return matches


def main(argv: list[str] | None = None) -> int:
    """Search the packaged pub list from the command line."""
    parser = argparse.ArgumentParser(description="Search the Oxford pub list.", add_help=False)
    parser.add_argument("--help", action="store_true", help="show search guidance")
    parser.add_argument("--list", nargs="?", const="fields", choices=("fields", *LISTABLE_FIELDS))
    parser.add_argument("query", nargs="*", help="words to find in pub names, roads, locations, sponsors, or notes")
    args = parser.parse_args(argv)

    if args.help:
        print(SEARCH_HELP)
        return 0

    pubs = load_pubs()
    if args.list is not None:
        print(format_pub_values(args.list, list_pub_values(pubs, args.list)))
        return 0

    query = " ".join(args.query)
    matches = search_pubs(pubs, query)
    print(f"Found {len(matches)} matching pubs:")
    for pub in matches:
        print(f"- {pub.name} ({pub.location})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
