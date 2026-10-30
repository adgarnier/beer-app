"""Load and save the list of pubs marked as visited."""

import csv
import threading
from datetime import date
from importlib.resources import files
from pathlib import Path
from beer_app.pub_data import Pub, load_pubs

VISIT_HELP = """VISIT help

View the pubs from the currently loaded list.
Mark off which pubs you have visited by typing the corresponding ID.

Commands:
  visit --help
"""

_HISTORY_LOCK = threading.Lock()

def _default_visited_path() -> Path:
    """Return the visited-pubs CSV next to the packaged pub lists."""
    return Path(files("beer_app").joinpath("data", "visited_pubs.csv"))

def load_visit_history(path: str | Path | None = None
                       ) -> tuple[dict[int, bool], dict[int, list[str]]]:
    """Return current visited statuses and visit dates from the CSV."""
    source = Path(path) if path is not None else _default_visited_path()
    if not source.exists():
        return {}, {}

    statuses: dict[int, bool] = {}
    dates: dict[int, list[str]] = {}
    with source.open(encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            try:
                pub_id = int(row["ID"])
            except (KeyError, ValueError):
                continue
            # Removed True vs False from visited_pubs.csv so this may be removed
            status_text = (row.get("Visited") or "").strip().lower()
            if status_text in {"true", "1", "yes"}:
                statuses[pub_id] = True
            elif status_text in {"false", "0", "no"}:
                statuses[pub_id] = False
            visit_date = (row.get("VisitDate") or "").strip()
            if visit_date:
                dates.setdefault(pub_id, []).append(visit_date)
    return statuses, dates

def save_visit_history(
        statuses: dict[int, bool],
        dates: dict[int, list[str]],
        path: str | Path | None = None
        ) -> None:
    """Write current status and visit dates for each pub to CSV."""
    destination = Path(path) if path is not None else _default_visited_path()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["ID", "Visited", "VisitDate"])
        for pub_id in sorted(statuses.keys() | dates.keys()):
            visit_dates = dates.get(pub_id) or [""]
            for visit_date in visit_dates:
                writer.writerow([pub_id, str(statuses.get(pub_id, False)).lower(), visit_date])

def record_visit_today(pub_id: int, path: str | Path | None = None) -> bool:
    """Record one visit for today, returning whether a new visit was added."""
    today = date.today().isoformat()
    with _HISTORY_LOCK:
        statuses, dates = load_visit_history(path)
        pub_dates = dates.setdefault(pub_id, [])
        if today in pub_dates:
            return False
        statuses[pub_id] = True
        pub_dates.append(today)
        save_visit_history(statuses, dates, path)
    return True

def manage_visited(pubs: list[Pub]) -> None:
    """Show pub visit status and record each visit entered by the user."""
    statuses, dates = load_visit_history()
    print("\nEnter a pub ID to record a visit, "
        "'unvisit ID' to clear its status, or Enter to return:")
    for pub in pubs:
        marker = "[x]" if statuses.get(pub.id, False) else "[ ]"
        visit_dates = ", ".join(dates.get(pub.id, []))
        suffix = f" — visits: {visit_dates}" if visit_dates else ""
        print(f"{marker} {pub.id}: {pub.name}{suffix}")
    valid_ids = {pub.id for pub in pubs}

    # CLI input handling
    while True:
        try:
            answer = input("Pub ID or command: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not answer or answer in {"q", "quit", "exit", "bye"}:
            return
        parts = answer.split()
        unvisit = len(parts) == 2 and parts[0].lower() == "unvisit"
        if len(parts) > 1 and not unvisit:
            print("Enter a pub ID, 'unvisit ID', or press Enter to return.")
            continue
        try:
            pub_id = int(parts[-1])
        except ValueError:
            print("Enter a numeric pub ID, 'unvisit ID', or press Enter to return.")
            continue
        if pub_id not in valid_ids:
            print("That ID is not in the pub list.")
            continue
        if unvisit:
            statuses.pop(pub_id, None)
            dates.pop(pub_id, None)
            save_visit_history(statuses, dates)
            print(f"Removed pub {pub_id} from the visit history.")
        else:
            visit_date = date.today().isoformat()
            statuses[pub_id] = True
            dates.setdefault(pub_id, []).append(visit_date)
            save_visit_history(statuses, dates)
            print(f"Recorded a visit to pub {pub_id} on {visit_date}.")

def main(pubs: list[Pub] | None = None) -> int:
    """Run the interactive visit manager for the supplied or packaged pub list."""
    manage_visited(pubs if pubs is not None else load_pubs())
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
