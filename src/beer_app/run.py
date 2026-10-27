"""Provide the main menu for the Oxford pub tracking application."""

from __future__ import annotations

from beer_app import oxford_map
from beer_app.pub_data import LAUNCH_HELP, load_pubs
from beer_app.pub_loader import LOAD_HELP, UNLOAD_HELP, load_pubs_onto_map, unload_pubs_from_map
from beer_app.pub_search import (
    SEARCH_HELP,
    format_pub_values,
    is_help_query,
    list_pub_values,
    list_query_field,
    search_pubs,
)
from beer_app.visited_pubs import VISIT_HELP, manage_visited
from beer_app.stats import pub_counts
from beer_app.visualization import p_visits_per_pub
import matplotlib.pyplot as plt


WELCOME_MESSAGE = r"""

 _____                                                       _____ 
( ___ )                                                     ( ___ )
 |   |~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|   | 
 |   |   .-,--. ,-.  .   ,-,---.    .    ,-_/ .---. ,-_/,.   |   | 
 |   |    '|__/   |  |    '|___/ ,' |    '  | \___  ' |_|/   |   | 
 |   |    .|      |  | .  ,|   \    |    .- |     \  /| |    |   | 
 |   |    `'      `--^-' `-^---'    `--' `--' `---'  `' `'   |   | 
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
  Use "launch --help" for more information.

Load
  Add pubs to the map. Choose from all, visited, or unvisited pubs.
  You can also enter "load all", "load visited", or "load unvisited".
  Use "load --help" for more information.

Unload
  Remove the currently loaded pubs from the map.
  Use "unload --help" for more information.

Search
  Search the loaded pubs using names, roads, locations, sponsors, or other keywords.
  Use "search --help" for more information.

Visit
  Mark pubs as visited and see the pubs you have already visited.
  Use "visit --help" for more information.

Stats
  Create a graph showing how many times you have visited each pub.

Quit
  Stop the map server and close PUB'LISH.
"""


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

            if choice == "launch --help":
                print(LAUNCH_HELP)
                continue

            if choice == "load --help":
                print(LOAD_HELP)
                continue

            if choice == "search --help":
                print(SEARCH_HELP)
                continue

            if choice == "visit --help":
                print(VISIT_HELP)
                continue

            if choice == "stats --help":
                print("Need to implement help in visualization.py")
                continue

            if choice == "1" or choice == "launch":
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
                    if len(load_parts) == 2:
                        load_selection = load_parts[1]
                    else:
                        try:
                            load_selection = input("Load all, visited, or unvisited pubs: ").strip().lower()
                        except (EOFError, KeyboardInterrupt):
                            print("\nGoodbye!")
                            return 0
                    try:
                        loaded_pubs = load_pubs_onto_map(map_server, load_selection)
                    except ValueError as error:
                        print(error)
                continue

            if choice == "3" or choice == "unload":
                if map_server is None:
                    print("Launch the Oxford map before unloading the pub list.")
                else:
                    unload_pubs_from_map(map_server)
                    loaded_pubs = []
                continue

            if choice == "4" or choice == "search":
                if map_server is None:
                    print("Launch the Oxford map before searching the pub list.")
                elif not loaded_pubs:
                    print("Load the pub list before searching it.")
                else:
                    while True:
                        try:
                            prompt = 'Search by name, road, location, sponsor, or notes. Type "--help" for more info: '
                            query = input(prompt).strip()
                        except (EOFError, KeyboardInterrupt):
                            print("\nGoodbye!")
                            return 0
                        if is_help_query(query):
                            print(SEARCH_HELP)
                            continue
                        try:
                            list_field = list_query_field(query)
                        except ValueError as error:
                            print(error)
                            continue
                        if list_field is not None:
                            values = list_pub_values(loaded_pubs, list_field)
                            print(format_pub_values(list_field, values))
                            continue
                        break
                    matches = search_pubs(loaded_pubs, query)
                    map_server.set_pubs(matches)
                    if query:
                        print(f"Found {len(matches)} pubs matching {query!r}.")
                    else:
                        print(f"Showing all {len(matches)} pubs.")
                continue

            if choice == "5" or choice == "visit":
                manage_visited(loaded_pubs or load_pubs())
                continue

            if choice == "6" or choice =="stats":
                print("Working on adding this feature, please check back later.")
                p_visits_per_pub(pub_counts())
                # this plt should be moved to visualization
                plt.show()
                continue

            if choice == "q" or choice == "quit":
                print("Goodbye!")
                return 0

            print(
                "Unknown option. Type 'help' to see all available options or 'quit' to leave the app."
            )
    finally:
        if map_server is not None:
            print("Stopping the Oxford map...")
            map_server.stop()


if __name__ == "__main__":
    raise SystemExit(main())
