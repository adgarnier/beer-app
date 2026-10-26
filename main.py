"""Provide the main menu for the Oxford pub tracking application."""

from __future__ import annotations

from beer_app import oxford_map
from beer_app.pub_data import load_pubs


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
Q. Quit
"""


def main() -> int:
    """Show the welcome menu and run the selected feature."""
    print(WELCOME_MESSAGE)
    map_server = None

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
                    pubs = load_pubs()
                    map_server.set_pubs(pubs)
                    print(f"Added {len(pubs)} pubs to the Oxford map.")
                continue

            if choice == "3":
                if map_server is None:
                    print("Launch the Oxford map before unloading the pub list.")
                else:
                    map_server.clear_pubs()
                    print("Removed all pubs from the Oxford map.")
                continue

            if choice == "q":
                print("Goodbye!")
                return 0

            print("Please enter 1 to launch the map, 2 to load pubs, 3 to unload pubs, or Q to quit.")
    finally:
        if map_server is not None:
            print("Stopping the Oxford map...")
            map_server.stop()


if __name__ == "__main__":
    raise SystemExit(main())
