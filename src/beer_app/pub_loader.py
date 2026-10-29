"""Load Oxford pub data onto the interactive map."""

from beer_app.oxford_map import BackgroundMapServer, start_map_server
from beer_app.pub_crawl import crawl_file_path
from beer_app.pub_data import Pub, load_pubs
from beer_app.visited_pubs import load_visit_history

LOAD_OPTIONS = ("all", "visited", "unvisited", "crawl")

LOAD_HELP = """Load help

Choose which pubs to display on the Oxford map:
  all        load every pub
  visited    load pubs marked as visited
  unvisited  load pubs not yet marked as visited
  crawl      load the most recently generated pub crawl

Commands:
  load all
  load visited
  load unvisited
  load crawl
  load --help

You must launch the map before loading pubs.
"""

UNLOAD_HELP = """Unload help

Cleans the map from the preivously loaded pubs.

Commands:
  unload
  unload --help

You must launch the map before unloading pubs.
"""

def load_pubs_onto_map(map_server: BackgroundMapServer, selection: str = "all") -> list[Pub]:
    """Load the selected pubs, display them on the map, and return them."""
    selection = selection.strip().lower()
    if selection not in LOAD_OPTIONS:
        options = ", ".join(LOAD_OPTIONS)
        raise ValueError(f"Unknown load option {selection!r}. Choose from: {options}.")

    if selection == "crawl":
        crawl_path = crawl_file_path()
        if not crawl_path.exists():
            raise ValueError("No saved pub crawl was found. Create one with 'crawl' first.")
        pubs = load_pubs(crawl_path)
    else:
        pubs = load_pubs()

    if selection in {"visited", "unvisited"}:
        statuses, _ = load_visit_history()
        if selection == "visited":
            pubs = [pub for pub in pubs if statuses.get(pub.id, False)]
        else:
            pubs = [pub for pub in pubs if not statuses.get(pub.id, False)]

    map_server.set_pubs(pubs)
    print(f"Added {len(pubs)} {selection} pubs to the Oxford map.")
    return pubs

def unload_pubs_from_map(map_server: BackgroundMapServer) -> None:
    """Remove all currently displayed pubs from the map."""
    map_server.clear_pubs()
    print("Removed all pubs from the Oxford map.")

def main(
    map_server: BackgroundMapServer | None = None,
    selection: str | None = None,
) -> list[Pub] | None:
    """Load pubs onto the supplied map, or launch a map when run as a script."""
    owns_map_server = map_server is None
    if map_server is None:
        choice = input("Need to start server to load pubs, would you like to continue? [y/n] ").strip().lower()
        if choice in {"y", "yes"}:
            map_server = start_map_server()
        else:
            return

    if selection is None:
        try:
            selection = input("Load all, visited, unvisited, or crawl pubs: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nLoad cancelled.")
            if owns_map_server:
                map_server.stop()
            return None

    try:
        loaded_pubs = load_pubs_onto_map(map_server, selection)
    except ValueError as error:
        print(error)
        if owns_map_server:
            map_server.stop()
        return None
    if owns_map_server:
        print("The map is running. Press Ctrl+C to stop it.")
        try:
            map_server.thread.join()
        except KeyboardInterrupt:
            print("\nStopping the Oxford map.")
        finally:
            map_server.stop()
    return loaded_pubs

if __name__ == "__main__":
    raise SystemExit(main())
