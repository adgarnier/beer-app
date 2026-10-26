"""Provide the main menu for the Oxford pub tracking application."""

from __future__ import annotations

from beer_app import oxford_map


WELCOME_MESSAGE = r"""

        OXFORD PUB TRACKING APP

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
                    map_server = oxford_map.start_map_server()
                    print("The map is running in the background. You can continue using this menu.")
                else:
                    print(f"The Oxford map is already running at {map_server.url}")
                continue

            if choice == "q":
                print("Goodbye!")
                return 0

            print("Please enter 1 to launch the map or Q to quit.")
    finally:
        if map_server is not None:
            print("Stopping the Oxford map...")
            map_server.stop()


if __name__ == "__main__":
    raise SystemExit(main())
