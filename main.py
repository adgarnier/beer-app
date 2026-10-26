"""Provide the main menu for the Oxford pub tracking application."""

from __future__ import annotations

from beer_app import oxford_map
from beer_app.pub_data import load_pubs
from beer_app.pub_search import (
    SEARCH_HELP,
    format_pub_values,
    is_help_query,
    list_pub_values,
    list_query_field,
    search_pubs,
)


WELCOME_MESSAGE = r"""

              PUB'LISH

              ::::
            :+=======-::::
         :==*-    :::-+===+-
        :#-:          :   -%:
        -#          :*====+#:
        -% -=-=+=-:-*=    -#----:
        :*=*=--:----:     -#----*-
          :               -*    =+
          ::              -*    =+
          =*              -*    =+
          =+              -*    =+
          =+              -#----*-
          =+              -#----:
          =+              -*
          -*==============++
           ::::::::::::::::

1. Launch the interactive Oxford map
2. Load the pub list onto the map
3. Unload the pub list from the map
4. Search the loaded pubs
Q. Quit
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

            if choice == "1":
                if map_server is None:
                    print("Launching the Oxford map...")
                    map_server = oxford_map.start_map_server(port=0)
                    print("The map is running in the background. You can continue using this menu.")
                else:
                    print(f"The Oxford map is already running at {map_server.url}")
                continue

            if choice == "2":
                if map_server is None:
                    print("Launch the Oxford map before loading the pub list.")
                else:
                    loaded_pubs = load_pubs()
                    map_server.set_pubs(loaded_pubs)
                    print(f"Added {len(loaded_pubs)} pubs to the Oxford map.")
                continue

            if choice == "3":
                if map_server is None:
                    print("Launch the Oxford map before unloading the pub list.")
                else:
                    map_server.clear_pubs()
                    loaded_pubs = []
                    print("Removed all pubs from the Oxford map.")
                continue

            if choice == "4":
                if map_server is None:
                    print("Launch the Oxford map before searching the pub list.")
                elif not loaded_pubs:
                    print("Load the pub list before searching it.")
                else:
                    while True:
                        try:
                            prompt = 'Search by name, location, sponsor, or notes. Type "--help" for more info: '
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

            if choice == "q":
                print("Goodbye!")
                return 0

            print("Please enter 1 to launch, 2 to load, 3 to unload, 4 to search, or Q to quit.")
    finally:
        if map_server is not None:
            print("Stopping the Oxford map...")
            map_server.stop()


if __name__ == "__main__":
    raise SystemExit(main())
