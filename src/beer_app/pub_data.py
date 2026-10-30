"""Load and validate Oxford pub data from CSV files."""

import csv
from dataclasses import asdict, dataclass
from importlib.resources import files
from pathlib import Path

LAUNCH_HELP = """Launch help

Just type launch mate.

Commands:
  launch
  launch --help
"""

REQUIRED_COLUMNS = {"ID", "Pub", "Road", "Location", "Sponsor", "Notes", "Latitude", "Longitude"}
PUB_LIST = "pub_list_v3.csv"

# Define the Pub class, this is used through much of the codebase
@dataclass(frozen=True)
class Pub:
    """A pub that can be displayed on the Oxford map."""

    id: int
    name: str
    road: str
    location: str
    sponsor: str
    notes: str
    latitude: float
    longitude: float

    def as_dict(self) -> dict[str, int | float | str]:
        """Return a JSON-ready representation of the pub."""
        return asdict(self)

def _default_pub_list():
    """Return the packaged pub-list resource."""
    if __package__:
        return files("beer_app").joinpath("data", PUB_LIST)
    return Path(__file__).with_name("data") / PUB_LIST

def load_pubs(path: str | Path | None = None) -> list[Pub]:
    """Load pubs from a CSV file, using the packaged list by default."""
    source = Path(path) if path is not None else _default_pub_list()

    with source.open(encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        columns = set(reader.fieldnames or [])
        missing_columns = REQUIRED_COLUMNS - columns
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Pub CSV is missing required columns: {missing}")

        pubs = [_pub_from_row(row, row_number) for row_number, row in enumerate(reader, start=2)]

    return pubs

def _pub_from_row(row: dict[str, str], row_number: int) -> Pub:
    """Validate and convert one CSV row."""
    try:
        pub_id = int(row["ID"])
        latitude = float(row["Latitude"])
        longitude = float(row["Longitude"])
    except (TypeError, ValueError) as error:
        raise ValueError(f"Invalid ID or coordinates on CSV row {row_number}") from error

    name = row["Pub"].strip()
    if not name:
        raise ValueError(f"Missing pub name on CSV row {row_number}")
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise ValueError(f"Coordinates out of range on CSV row {row_number}")

    return Pub(
        id=pub_id,
        name=name,
        road=row["Road"].strip(),
        location=row["Location"].strip(),
        sponsor=row["Sponsor"].strip(),
        notes=row["Notes"].strip(),
        latitude=latitude,
        longitude=longitude,
    )

if __name__ == "__main__":
    loaded_pubs = load_pubs()
    print(f"Loaded {len(loaded_pubs)} pubs from {PUB_LIST}")
