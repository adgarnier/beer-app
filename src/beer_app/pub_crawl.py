"""Generates a pub crawl feature, where the user specifies a start and end pub, and the number of pubs they wish to visit""" 

import random       # Allows Python to select pubs randomly
from math import cos, hypot, radians    # `cos` and `radians` help convert geographical coordinates into distances in metres. `hypot` calculates the distance between two points.

from .pub_data import Pub       # Imports existing pub data structure from code.


EARTH_RADIUS_M = 6_371_000      # Approximate radius of the earth in metres.
BUFFER_METRES = 400     # Sets the corridor width either side of the straight line between the start and end pub.


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

    # `candidates` contains all the intermediate pubs that lie inside the buffer
    candidates = pubs_in_buffer(
        pubs, start, end, buffer_metres
    )

    # Calculates how many intermediate pubs we need to randomly select
    required = total_pubs - 2

    # Check whether there are enough pubs in the corridor. If a user requests 10 pubs but only 5 intermediate candidates are available, the user will be notified to decrease pubs or increase buffer.
    if len(candidates) < required:
        raise ValueError(
            f"Only {len(candidates)} intermediate pubs are within "
            f"{buffer_metres:g} metres of the line; need{required}."
            "Try fewer pubs or a larger buffer."
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