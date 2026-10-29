"""Provide the main menu for the Oxford pub tracking application."""

from beer_app import oxford_map
from beer_app.pub_data import LAUNCH_HELP, load_pubs
from beer_app.pub_loader import LOAD_HELP, UNLOAD_HELP, main as run_load, unload_pubs_from_map
from beer_app.pub_search import (SEARCH_HELP, search_loaded_pubs)
from beer_app.visited_pubs import VISIT_HELP, main as run_visited
from beer_app.visualization import STATS_HELP, main as run_visualization
from beer_app.pub_crawl import CRAWL_HELP, main as run_pub_crawl

WELCOME_MESSAGE = r"""

 _____                                                       _____
( ___ )                                                     ( ___ )
 |   |~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|   |
 |   |   .-,--. ,-.  _   ,-,---.  , .    _,_  .---. ,-_ __,  |   |
 |   |    '|__/   |  |    '|___/ ,' |     |   \___  ' |_|/   |   |
 |   |    .|      |  | .  ,|   \    |     |       \  /| |    |   |
 |   |    `'      `--^-' `-^---'    `--' -'-  `---'  -- --   |   |
 |___|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|___|
(_____)                                                     (_____)
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡀⠀⠀⠀⠀⠀⢀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
               ⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣶⣤⣤⣿⣿⣿⣷⡄⠀⠀⣰⣿⣿⣿⣿⣤⣴⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣶⣶⣶⣿⣿⣿⣿⣿⣿⣿⡿⣿⣇⡀⠀⣿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⠿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣆⢻⣿⣷⡈⣴⣿⣿⣿⣿⣿⣿⣿⡿⠟⠛⠟⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⡶⠲⣤⠀⠰⣶⡄⢲⠶⠬⢍⣙⡻⠿⠿⢿⣿⣿⣾⣿⡿⢃⣿⠿⠿⠿⢛⣋⠩⠥⠖⡂⠃⣰⡶⠄⠀⡶⠛⢷⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡾⠋⠀⠀⠈⠠⢡⣿⣿⣆⢹⣷⣦⣤⣍⣙⠒⣶⡄⣿⣿⣿⠁⣿⡟⣰⠦⢩⣭⣤⣶⣶⣿⣇⣾⣿⣿⡄⡀⠀⠀⠀⠙⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⠁⠀⠀⠀⠀⠄⣘⡛⠛⠿⣿⣿⣿⣿⣿⣯⣤⣌⠳⠈⣿⠃⠺⠟⢠⠀⣴⣶⣼⣿⣿⣿⣿⠟⠛⢛⣭⣅⠀⠀⠀⠀⠀⠈⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡇⠀⠀⠀⠀⠂⣰⣿⣿⠋⠀⣴⣤⣬⠙⠛⠻⣿⡿⢠⠀⠀⠀⠀⠀⠘⠀⢿⣿⠛⠉⢡⣴⣶⡄⠈⢻⣿⣿⣆⠣⠀⠀⠀⠀⢻⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⡸⢠⣿⣿⡏⠀⢸⣿⣿⡇⠀⠐⢰⡟⠀⡌⠀⠀⠀⠀⠀⠀⢆⠀⢻⡆⠀⠀⢿⣿⣿⡆⠀⢿⣿⣿⡄⢆⠀⠀⠀⣸⠇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣷⣄⣀⠀⠁⣾⣿⡿⠀⢠⣿⣿⣿⠁⠀⣠⡿⢀⠀⠁⠀⠀⠀⠀⠀⠀⠈⠈⠈⣿⣆⠀⠘⣿⣿⣧⡀⠈⢿⣿⣷⠘⠀⣀⣴⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠋⣼⠰⣿⣿⡥⢀⣸⣿⣿⠃⠀⣴⣿⠇⠆⠎⠀⠀⠀⠀⠀⠀⠀⠀⢣⠰⢸⣿⣇⠀⠸⣿⣿⣧⠀⢼⣿⡿⠀⣇⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣄⠙⠋⠠⠸⣿⡟⠃⠀⣼⣿⡿⠆⡠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢃⠙⢿⣿⡇⠀⠘⣿⡿⠀⠀⠙⢃⣴⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠛⠿⢷⣦⣬⣅⣀⡀⠙⠛⣡⡼⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢧⣄⡙⢁⣈⣤⣤⣤⡶⠿⠛⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠛⠛⠿⠿⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠛⠛⠛⠛⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

Welcome to PUB'LISH, your Oxford pub companion.

Use the app to explore pubs on an interactive map, search for places that
interest you, keep track of the pubs you have visited, and view statistics
about your visits.

Type "--help" to see all available options or "quit" to leave the app.
"""


HELP_MESSAGE = """PUB'LISH --help

Launch
  Open the interactive Oxford pub map in your browser.
  Use 'launch --help' for more information.

Load
  Add pubs to the map. Choose from all, visited, or unvisited pubs.
  You can also enter 'load all', 'load visited', or 'load unvisited'.
  Use 'load --help' for more information.

Unload
  Remove the currently loaded pubs from the map.
  Use 'unload --help' for more information.

Search
  Search the loaded pubs using names, roads, locations, sponsors, or other keywords.
  Use 'search --help' for more information.

Visit
  Mark pubs as visited and see the pubs you have already visited.
  Use 'visit --help' for more information.

Stats
  Create a graph showing how many times you have visited each pub.
  Use 'stats --help' for more information.

Crawl
  Create your own pub crawl.
  Use 'crawl --help' for more information.

Quit
  Stop the map server and close PUB'LISH.
"""

COMMAND_HELP = {
    "launch": LAUNCH_HELP,
    "load": LOAD_HELP,
    "unload": UNLOAD_HELP,
    "search": SEARCH_HELP,
    "visit": VISIT_HELP,
    "stats": STATS_HELP,
    "crawl": CRAWL_HELP,
}

def main() -> int:
    """Show the welcome menu and run the selected feature."""
    print(WELCOME_MESSAGE)
    map_server = None
    loaded_pubs = []

    try:
        while True:
            try:
                choice = input("Choose an option: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                return 0

            if choice in {"h", "help", "--help"}:
                print(HELP_MESSAGE)
                continue

            help_command = choice.removesuffix(" --help") if choice.endswith(" --help") else None
            if help_command in COMMAND_HELP:
                print(COMMAND_HELP[help_command])
                continue

            if choice in {"1", "launch"}:
                if map_server is None:
                    print("Launching the Oxford map...")
                    map_server = oxford_map.start_map_server(port=0)
                    print("The map is running in the background. You can continue using this menu.")
                else:
                    print(f"The Oxford map is already running at {map_server.url}")
                continue

            if choice in {"2", "load"} or choice.startswith("load "):
                if map_server is None:
                    print("Launch the Oxford map before loading the pub list.")
                else:
                    load_parts = choice.split(maxsplit=1)
                    loaded_selection = run_load(map_server,
                                                load_parts[1] if len(load_parts) == 2 else None)
                    if loaded_selection is not None:
                        loaded_pubs = loaded_selection
                continue

            if choice in {"3", "unload"}:
                if map_server is None:
                    print("Launch the Oxford map before unloading the pub list.")
                else:
                    unload_pubs_from_map(map_server)
                    loaded_pubs = []
                continue

            if choice in {"4", "search"}:
                if map_server is None:
                    print("Launch the Oxford map before searching the pub list.")
                elif not loaded_pubs:
                    print("Load the pub list before searching it.")
                else:
                    search_loaded_pubs(loaded_pubs, map_server.set_pubs)
                continue

            if choice in {"5", "visit"}:
                run_visited(loaded_pubs or load_pubs())
                continue

            if choice in {"6", "stats"}:
                run_visualization()
                continue

            if choice in {"7", "crawl"}:
                if not loaded_pubs:
                    print("Load some pubs before creating a pub crawl.")
                else:
                    run_pub_crawl(loaded_pubs)
                continue

            if choice in {"q", "quit", "bye", "exit", "leave"}:
                print("Goodbye!")
                return 0

            print(
                "Unknown option. Type 'help' to see all \
                available options or 'quit' to leave the app."
            )
    finally:
        if map_server is not None:
            print("Stopping the Oxford map...")
            map_server.stop()

if __name__ == "__main__":
    raise SystemExit(main())
