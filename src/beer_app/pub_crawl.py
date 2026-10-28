"""Generates a pub crawl feature, where the user specifies a start and end pub, and the number of pubs they wish to visit""" 

import csv
import random       # Allows Python to select pubs randomly
from importlib.resources import files
from math import cos, hypot, radians    # `cos` and `radians` help convert geographical coordinates into distances in metres. `hypot` calculates the distance between two points.
from pathlib import Path

from beer_app.pub_data import Pub, load_pubs       # Imports existing pub data structure and pub data loader.


CRAWL_HELP = """Crawl help

Create a route between two Oxford pubs with a chosen number of stops.
When used from PUB'LISH, the route only uses the current loaded pub set.
This lets you create a crawl from all, visited, unvisited, or saved crawl pubs.

When prompted, enter:
  starting pub       the name, or a unique part of the name
  ending pub         a different pub name, or a unique part of the name
  total pubs         the total number of pubs in the crawl, including both endpoints

The crawl first looks for intermediate pubs within 100 metres of the route. If
there are not enough, it widens the search to 200, 300, 400, and then 500 metres.
It randomly selects the intermediate pubs and orders them from the starting pub
towards the ending pub. If a name matches more than one pub, enter a more
specific name.

Commands:
  crawl              create a new pub crawl
  crawl --help       show this guidance

The latest crawl is saved and can be displayed on the map with 'load crawl'.
"""

EARTH_RADIUS_M = 6_371_000      # Approximate radius of the earth in metres.
BUFFER_METRES = 100     # Sets the initial corridor width either side of the line.
BUFFER_STEP_METRES = 100
MAX_BUFFER_METRES = 1000
CRAWL_FILE_NAME = "pub_crawl.csv"
CRAWL_COLUMNS = ("Pub", "Road", "Location", "Sponsor", "Notes", "Latitude", "Longitude", "ID")


def crawl_file_path() -> Path:
    """Return the path used to save the latest pub crawl."""
    return Path(files("beer_app").joinpath("data", CRAWL_FILE_NAME))


def save_pub_crawl(crawl: list[Pub], path: str | Path | None = None) -> Path:
    """Save a crawl in route order using the standard pub CSV format."""
    destination = Path(path) if path is not None else crawl_file_path()
    destination.parent.mkdir(parents=True, exist_ok=True)

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


# Function to convert a pub's coordinates into an approximate local coordinate system
def relative_xy(pub: Pub, start: Pub) -> tuple[float, float]:

    # East-West displacement in metres
    x = EARTH_RADIUS_M * radians(
        pub.longitude - start.longitude     # `start` is the reference point. Starting pub will have coordinates (0, 0)
    ) * cos(radians(start.latitude))

    # North-South displacement in metres
    y = EARTH_RADIUS_M * radians(
        pub.latitude - start.latitude       # `start` is the reference point. Starting pub will have coordinates (0, 0)
    )

    return x, y     # Makes converted coordinates available to other functions


# Calculate the distance between a pub and the line
def distance_to_line(pub: Pub, start: Pub, end: Pub) -> float:      # Three pubs: start pub at (0, 0), end pub at (ex, ey) and a candidate pub (px, py)

    px, py = relative_xy(pub, start)        # Candidate pub
    ex, ey = relative_xy(end, start)        # End pub

    length_squared = ex**2 + ey**2      # Calculates squared length of line between start and end pub

    if length_squared == 0:     # Handles where two geographical points have exactly the same coordinates
        return hypot(px, py)

    t = (px * ex + py * ey) / length_squared        # Calculates the point along the line that is nearest to the candidate to the pub.

    t = max(0, min(1, t))       # Makes sure the nearest point stays on the line between the start and end pub.

    closest_x = t * ex      # Calculate x-coordinates of nearest point on the line.
    closest_y = t * ey      # Calculate y-coordinates of nearest point on the line.

    return hypot(px - closest_x, py - closest_y)        # Calculates the distance from the candidate pub to that nearest point on the line, in metres.


# Keep only pubs inside the buffer. Takes four arguments.
def pubs_in_buffer(
    pubs: list[Pub],    # All available pubs from the CSV
    start: Pub,         # The starting pub
    end: Pub,           # The ending pub
    buffer_metres: float = BUFFER_METRES    # The distance allowed from the line
) -> list[Pub]:

    # Quick check to make sure the buffer width is not negative
    if buffer_metres < 0:
        raise ValueError("Buffer width cannot be negative.")

    # Returns a list containing only pubs inside the corridor
    return [
        pub for pub in pubs
        if pub.id not in (start.id, end.id)                         # Excludes the two endpoints from intermediate candidates.
        and distance_to_line(pub, start, end) <= buffer_metres      # Checks whether each pub falls within the specified distance of the line. The distance_to_pub must be less than or equal to the buffer distance.
    ]

# Create the pub crawl function. Takes five arguments.
def create_pub_crawl(
    pubs: list[Pub],        # The list of pubs from pub_data.py (from pub_list_v3.csv). `list[]` gives Python a hint that `pubs` should be a list of `Pub` objects
    start: Pub,             # The starting pub
    end: Pub,               # The ending pub
    total_pubs: int,        # The total number of pubs the user wants to visit. `int` is another type hint (argument should be an integer)
    buffer_metres: float = BUFFER_METRES        # `float` is another type hint, indicating a decimal number.
) -> list[Pub]:     # `->` is a return type hint. In this case, the function is expected to return a list of `Pub` objects.

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

    # Randomly selects the number of pubs required from the candidate list, without selecting the same pub twice
    selected = random.sample(candidates, required)

    # Put the selected pubs in a sensible order to avoid zigzagging around city
    ex, ey = relative_xy(end, start)        # Provides the direction from start to end

    def progress(pub: Pub) -> float:        # Uses a dot product to measure how far along that direction each pub sits
        x, y = relative_xy(pub, start)
        return x * ex + y * ey

    selected.sort(key=progress)     # Puts the selected pubs into an approximate start-to-end order

    return [start, *selected, end]      # Produces the final list with chosen endpoints fixed

def find_pub(pubs: list[Pub], query: str) -> Pub:
    """Find exactly one pub by a case-insensitive name fragment."""
    matches = [pub for pub in pubs if query.casefold() in pub.name.casefold()]
    if not matches:
        raise ValueError(f"No pub found matching {query!r}.")
    if len(matches) > 1:
        names = ", ".join(pub.name for pub in matches)
        raise ValueError(f"More than one pub matches {query!r}: {names}. Please use a more specific name.")
    return matches[0]


def main(pubs: list[Pub] | None = None) -> int:
    """Create a crawl from the supplied pubs, or all pubs when run directly."""
    available_pubs = pubs if pubs is not None else load_pubs()
    print("Pub crawl planner")
    print(f"Using {len(available_pubs)} available pubs.")
    print("Enter pub names (or part of a name) and the total number of pubs.")

    try:
        start_query = input("Starting pub: ").strip()
        end_query = input("Ending pub: ").strip()
        total_pubs = int(input("Total pubs to visit: ").strip())

        start = find_pub(available_pubs, start_query)
        end = find_pub(available_pubs, end_query)
        crawl = create_pub_crawl(available_pubs, start, end, total_pubs)
        saved_path = save_pub_crawl(crawl)
    except (EOFError, KeyboardInterrupt):
        print("\nPub crawl cancelled.")
        return 0
    except ValueError as error:
        print(f"Could not create pub crawl: {error}")
        return 1
    else:
        print("Your pub crawl:")
        for number, pub in enumerate(crawl, start=1):
            print(f"{number}. {pub.name} ({pub.location})")
        print(f"Saved crawl to {saved_path.name}. Use 'load crawl' to show it on the map.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
