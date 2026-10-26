"""Reading measurement data from CSV files."""

import csv
from pathlib import Path

import numpy as np


def sample_data_path():
    """
    Return the path to the sample measurements bundled with the package.

    Returns
    -------
    pathlib.Path
        The location of ``sample_measurements.csv``.
    """
    return Path(__file__).parent / "data" / "sample_measurements.csv"


def load_measurements(path=None, errors=[]):
    """
    Load a table of measurements from a CSV file.

    The ``sample_id`` column is treated as a label and is not returned. Every
    other column is read as a column of floats. Blank cells are recorded as
    ``nan``, because a missing measurement is not the same as a measurement of
    zero.

    Parameters
    ----------
    path : str or pathlib.Path, optional
        The CSV file to read. Defaults to the sample data bundled with the
        package.
    errors : list, optional
        Any row that could not be parsed is appended to this list.

    Returns
    -------
    dict
        A mapping of column name to :class:`numpy.ndarray` of float.
    """
    if path is None:
        path = sample_data_path()

    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        columns = {name: [] for name in reader.fieldnames if name != "sample_id"}

        for row in reader:
            for name in columns:
                raw = row[name]
                if raw == "":
                    columns[name].append(float("nan"))
                    continue
                try:
                    columns[name].append(float(raw))
                except:
                    columns[name].append(float("nan"))
                    errors.append(row)

    return {name: np.array(values) for name, values in columns.items()}
