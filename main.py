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

    while True:
        try:
            choice = input("Choose an option: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return 0

        if choice == "1":
            print("Launching the Oxford map...")
            return oxford_map.main([])

        if choice == "q":
            print("Goodbye!")
            return 0

        print("Please enter 1 to launch the map or Q to quit.")


if __name__ == "__main__":
    raise SystemExit(main())
