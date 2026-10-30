"""Provide the main menu for the Oxford pub tracking application."""

from dataclasses import dataclass, field

from beer_app import oxford_map
from beer_app.oxford_map import BackgroundMapServer
from beer_app.pub_crawl import CRAWL_HELP, main as run_pub_crawl
from beer_app.pub_data import LAUNCH_HELP, Pub, load_pubs
from beer_app.pub_loader import LOAD_HELP, UNLOAD_HELP, main as run_load, unload_pubs_from_map
from beer_app.pub_search import SEARCH_HELP, search_loaded_pubs
from beer_app.visited_pubs import VISIT_HELP, main as run_visited
from beer_app.visualization import STATS_HELP, main as run_visualization

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

Use the app to explore pubs on an interactive map, search for pubs,
keep track of the pubs you have visited, view statistics about
your visits, and make pub crawls.

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

@dataclass
class MenuState:
    """Keep track of resources shared by the menu choices."""

    map_server: BackgroundMapServer | None = None
    loaded_pubs: list[Pub] = field(default_factory=list)

def show_help(choice: str) -> bool:
    """Print help when ``choice`` is a general or command help request."""
    if choice in {"h", "help", "--help"}:
        print(HELP_MESSAGE)
        return True

    help_command = choice.removesuffix(" --help") if choice.endswith(" --help") else None
    if help_command in COMMAND_HELP:
        print(COMMAND_HELP[help_command])
        return True

    return False

def launch_map(state: MenuState) -> None:
    """Launch the Oxford map unless it is already running."""
    if state.map_server is None:
        print("Launching the Oxford map...")
        state.map_server = oxford_map.start_map_server(port=0)
        print("The map is running in the background. You can continue using this menu.")
    else:
        print(f"The Oxford map is already running at {state.map_server.url}")

def load_map_pubs(state: MenuState, choice: str) -> None:
    """Load the selected pubs onto the running map."""
    if state.map_server is None:
        print("Launch the Oxford map before loading the pub list.")
        return

    load_parts = choice.split(maxsplit=1)
    selection = load_parts[1] if len(load_parts) == 2 else None
    loaded_selection = run_load(state.map_server, selection)
    if loaded_selection is not None:
        state.loaded_pubs = loaded_selection

def unload_map_pubs(state: MenuState) -> None:
    """Remove all pubs from the running map."""
    if state.map_server is None:
        print("Launch the Oxford map before unloading the pub list.")
        return

    unload_pubs_from_map(state.map_server)
    state.loaded_pubs = []

def search_map_pubs(state: MenuState) -> None:
    """Search the pubs currently loaded on the map."""
    if state.map_server is None:
        print("Launch the Oxford map before searching the pub list.")
    elif not state.loaded_pubs:
        print("Load the pub list before searching it.")
    else:
        search_loaded_pubs(state.loaded_pubs, state.map_server.set_pubs)

def visit_pubs(state: MenuState) -> None:
    """Open the visit tracker with the current or packaged pub list."""
    run_visited(state.loaded_pubs or load_pubs())

def show_stats() -> None:
    """Open the visit statistics flow."""
    run_visualization()

def create_pub_crawl(state: MenuState) -> None:
    """Create a crawl from the pubs currently loaded on the map."""
    if not state.loaded_pubs:
        print("Load some pubs before creating a pub crawl.")
    else:
        run_pub_crawl(state.loaded_pubs)

def handle_choice(choice: str, state: MenuState) -> bool:
    """Run one menu choice and return whether the menu should stay open."""
    if show_help(choice):
        return True
    if choice in {"1", "launch"}:
        launch_map(state)
    elif choice in {"2", "load"} or choice.startswith("load "):
        load_map_pubs(state, choice)
    elif choice in {"3", "unload"}:
        unload_map_pubs(state)
    elif choice in {"4", "search"}:
        search_map_pubs(state)
    elif choice in {"5", "visit"}:
        visit_pubs(state)
    elif choice in {"6", "stats"}:
        show_stats()
    elif choice in {"7", "crawl"}:
        create_pub_crawl(state)
    elif choice in {"q", "quit", "bye", "exit", "leave"}:
        print("Goodbye!")
        return False
    else:
        print(
            "Unknown option. Type 'help' to see all "
            "available options or 'quit' to leave the app."
        )
    return True

def main() -> int:
    """Show the welcome menu and run the selected feature."""
    print(WELCOME_MESSAGE)
    state = MenuState()

    try:
        while True:
            try:
                choice = input("Choose an option: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                return 0

            if not handle_choice(choice, state):
                return 0
    finally:
        if state.map_server is not None:
            print("Stopping the Oxford map...")
            state.map_server.stop()

if __name__ == "__main__":
    raise SystemExit(main())
