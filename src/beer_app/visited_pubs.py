"""Load and save the list of pubs marked as visited."""

from __future__ import annotations

import csv
from importlib.resources import files
from pathlib import Path


def _default_visited_path() -> Path:
    """Return the visited-pubs CSV next to the packaged pub lists."""
    return Path(files("beer_app").joinpath("data", "visited_pubs.csv"))


def load_visited(path: str | Path | None = None) -> set[int]:
    """Return the IDs currently marked as visited."""
    source = Path(path) if path is not None else _default_visited_path()
    if not source.exists():
        return set()

    visited = set()
    with source.open(encoding="utf-8-sig", newline="") as csv_file:
        for row in csv.DictReader(csv_file):
            try:
                if row.get("Visited", "").strip().lower() in {"true", "1", "yes"}:
                    visited.add(int(row["ID"]))
            except (KeyError, ValueError):
                continue
    return visited


def save_visited(visited: set[int], path: str | Path | None = None) -> None:
    """Write visited pub IDs to CSV, including a header when the set is empty."""
    destination = Path(path) if path is not None else _default_visited_path()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["ID", "Visited"])
        writer.writerows([pub_id, "true"] for pub_id in sorted(visited))


def manage_visited(pubs) -> None:
    """Show pubs and let the user toggle visited status by ID."""
    visited = load_visited()
    print("\nVisited pubs (enter a pub ID to toggle, or press Enter to return):")
    for pub in pubs:
        marker = "[x]" if pub.id in visited else "[ ]"
        print(f"{marker} {pub.id}: {pub.name}")

    valid_ids = {pub.id for pub in pubs}
    while True:
        try:
            answer = input("Pub ID: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not answer:
            return
        try:
            pub_id = int(answer)
        except ValueError:
            print("Enter a numeric pub ID, or press Enter to return.")
            continue
        if pub_id not in valid_ids:
            print("That ID is not in the pub list.")
            continue
        if pub_id in visited:
            visited.remove(pub_id)
            print(f"Unmarked pub {pub_id} as visited.")
        else:
            visited.add(pub_id)
            print(f"Marked pub {pub_id} as visited.")
        save_visited(visited)
