"""
Generate a pub crawl feature, where the user specifies
starting pud, ending pub, and the number of pubs they wish to visit.
"""

import csv
import random
from importlib.resources import files
from math import cos, hypot, radians
from pathlib import Path
from beer_app.pub_data import Pub, load_pubs

CRAWL_HELP = """Crawl help

Create a route between two Oxford pubs with a chosen number of pub stops.
When used from PUB'LISH, the route only uses the current loaded pub set.
This lets you create a crawl from all, visited, unvisited, or saved crawl pubs.

When prompted, enter:
  starting pub       the name, or a unique part of the name
  ending pub         a different pub name, or a unique part of the name
  total pubs         the total number of pubs in the crawl, including both endpoints

It randomly selects the intermediate pubs and orders them from the starting pub
towards the ending pub. If a name matches more than one pub, enter a more
specific name.

Commands:
  crawl              create a new pub crawl
  crawl --help       show this guidance

The latest crawl is saved and can be displayed on the map with 'load crawl'.
"""

# Default variables used for the following functions
EARTH_RADIUS_M = 6_371_000      # Approximate radius of the earth in metres
BUFFER_METRES = 100     # Sets the initial corridor width either side of the line
BUFFER_STEP_METRES = 100
MAX_BUFFER_METRES = 1000    # The maximum buffer width either side of the line
CRAWL_FILE_NAME = "pub_crawl.csv"   # Stores the filename for the most recently generated pub crawl
CRAWL_COLUMNS = ("Pub", "Road", "Location", "Sponsor", "Notes", "Latitude", "Longitude", "ID")

# Function to convert a pub's coordinates into an approximate local coordinate system
def relative_xy(pub: Pub, start: Pub) -> tuple[float, float]:
    """Set East-West and North-south displacement in metres."""
    x = EARTH_RADIUS_M * radians(pub.longitude - start.longitude) * cos(radians(start.latitude))
    y = EARTH_RADIUS_M * radians(pub.latitude - start.latitude)
    return x, y

def distance_to_line(pub: Pub, start: Pub, end: Pub) -> float:
    """Calculate the distance between a pub and the line between start and end pub."""
    px, py = relative_xy(pub, start)        # Candidate pub
    ex, ey = relative_xy(end, start)        # End pub

    # Squared length of line between start and end pub
    length_squared = ex**2 + ey**2

    # Handles if two points have exactly the same coordinates
    if length_squared == 0:
        return hypot(px, py)
    # Calculates point along line (between start and end) that is nearest to candidate pub
    t = (px * ex + py * ey) / length_squared
    t = max(0, min(1, t))
    closest_x = t * ex
    closest_y = t * ey

    # Calculates the distance from the candidate pub to that nearest point on the line, in metres
    return hypot(px - closest_x, py - closest_y)

def pubs_in_buffer(
    pubs: list[Pub],
    start: Pub,
    end: Pub,
    buffer_metres:
    float = BUFFER_METRES
) -> list[Pub]:
    """
    Create a list of pubs that fall within the corridor created above.

    Parameters
    ----------
    pubs : list
        A list of pubs generated using pub_data.py
    start : `Pub` object
        The starting pub, specified by the user
    end : `Pub` object
        The ending pub, specified by the user
    buffer_metres : float
        The buffer distance to create the corridor between start and end

    """
    if buffer_metres < 0:   # Quick check to make sure the buffer width is not negative
        raise ValueError("Buffer width cannot be negative.")

    # Returns a list containing only pubs inside the corridor
    return [
        pub for pub in pubs
        if pub.id not in (start.id, end.id)
        and distance_to_line(pub, start, end) <= buffer_metres
    ]

def create_pub_crawl(
    pubs: list[Pub],
    start: Pub,
    end: Pub,
    total_pubs: int,
    buffer_metres: float = BUFFER_METRES
) -> list[Pub]:
    """
    Randomly selects a set number of pubs (set by the user) that 
    fall in the corridor between the start and end pub.
    
    Parameters
    ----------
    pubs : list
        A list of pubs that sit in the corridor, created by pubs_in_buffer() above
    start : 'Pub' object
        The starting pub, specified by the user
    end : 'Pub' object
        The ending pub, specified by the user
    total_pubs : integer
        The total number of pubs on the pub crawl, specified by the user
    buffer_metres : float
        The buffer distance to create the corridor between start and end
    """
    
    if total_pubs < 2:
        raise ValueError("A crawl must include at least two pubs.")

    if start.id == end.id:
        raise ValueError("Start and end must be different pubs.")

    # Calculates how many intermediate pubs we need to randomly select
    required = total_pubs - 2

    # Start with the narrowest corridor and widen it until enough pubs are found.
    current_buffer = buffer_metres
    candidates = pubs_in_buffer(pubs, start, end, current_buffer)
    while len(candidates) < required and current_buffer < MAX_BUFFER_METRES:
        current_buffer = min(current_buffer + BUFFER_STEP_METRES, MAX_BUFFER_METRES)
        candidates = pubs_in_buffer(pubs, start, end, current_buffer)

    # Check whether there are enough pubs at the maximum search radius.
    if len(candidates) < required:
        raise ValueError(
            f"Only {len(candidates)} intermediate pubs are within "
            f"{current_buffer:g} metres of the route; need {required}. "
            "Try requesting fewer pubs."
        )

    # Randomly selects the number of pubs required from the candidate list, without replacement
    selected = random.sample(candidates, required)

    # Put the selected pubs in a sensible order to avoid zigzagging around city
    ex, ey = relative_xy(end, start)    # Provides the direction from start to end

    def progress(pub: Pub) -> float:
        """Use a dot product to measure how far along that direction each pub sits."""
        x, y = relative_xy(pub, start)
        return x * ex + y * ey

    # Puts the selected pubs into an approximate start-to-end order
    selected.sort(key=progress)

    # Produces the final list with chosen endpoints fixed
    return [start, *selected, end]

def find_pub(pubs: list[Pub], query: str) -> Pub:
    """Find exactly one pub by a case-insensitive name fragment."""
    if not query.strip():
        raise ValueError("Please enter a pub name.")
    # Examine each pub and check whether the entered text appears anywhere in its name
    matches = [pub for pub in pubs if query.casefold() in pub.name.casefold()]
    # Raises a ValueError if no pubs match the search terms
    if not matches:
        raise ValueError(f"No pub found matching {query!r}.")
    if len(matches) > 1:
        names = ", ".join(pub.name for pub in matches)
        raise ValueError(f"More than one pub matches {query!r}: {names}. \
                         Please use a more specific name.")

    # Reaches this line if the function has found exactly one match
    return matches[0]

def crawl_file_path() -> Path:
    """Return the path used to save the latest pub crawl."""
    return Path(files("beer_app").joinpath("data", CRAWL_FILE_NAME))

def save_pub_crawl(crawl: list[Pub], path: str | Path | None = None) -> Path:
    """Save a crawl in route order using the standard pub CSV format."""
    destination = Path(path) if path is not None else crawl_file_path()
    # Creates the directory (beer_app/data) if necessary.
    destination.parent.mkdir(parents=True, exist_ok=True)

    # Creating the csv writer
    # with ensures the file is closed after the block finishes
    # "w" opens the file and overwrites existing contents
    with destination.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CRAWL_COLUMNS)
        writer.writeheader()
        for pub in crawl:
            writer.writerow(
                {
                    "Pub": pub.name,
                    "Road": pub.road,
                    "Location": pub.location,
                    "Sponsor": pub.sponsor,
                    "Notes": pub.notes,
                    "Latitude": pub.latitude,
                    "Longitude": pub.longitude,
                    "ID": pub.id,
                }
            )

    return destination

def main(pubs: list[Pub] | None = None) -> int:
    """Create a crawl from the supplied pubs, or all pubs when run directly."""
    available_pubs = pubs if pubs is not None else load_pubs()
    print("Pub crawl planner")
    print(f"Using {len(available_pubs)} available pubs.")
    print("Enter pub names (or part of a name) and the total number of pubs.")

    # If execution fails in try block, jump to except block
    # input() waits for user to enter text following prompt
    # .strip() removes leading and trailing whitespace
    try:
        start_query = input("Starting pub: ").strip()
        end_query = input("Ending pub: ").strip()
        total_pubs = int(input("Total pubs to visit: ").strip())

        # Calls the find_pub function above to find start and end pubs, as `Pub` objects
        # Creates the pub crawl
        # Saves the pubs in the crawl as csv
        start = find_pub(available_pubs, start_query)
        end = find_pub(available_pubs, end_query)
        crawl = create_pub_crawl(available_pubs, start, end, total_pubs)
        saved_path = save_pub_crawl(crawl)
    # Below handles exceptions
    except (EOFError, KeyboardInterrupt):
        print("\nPub crawl cancelled.")
        return 0
    except ValueError as error:
        print(f"Could not create pub crawl: {error}")
        return 1
    # Runs if `try` block runs without exception, printing pub crawl in order
    print("Your pub crawl:")
    for number, pub in enumerate(crawl, start=1):
        print(f"{number}. {pub.name} ({pub.location})")
    print(f"Saved crawl to {saved_path.name}. Use 'load crawl' to show it on the map.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
