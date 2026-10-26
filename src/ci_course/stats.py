"""Summary statistics for columns of measurements."""

import numpy as np


def summarise(values):
    """
    Summarise one column of measurements, ignoring any missing values.

    Parameters
    ----------
    values : array_like
        The measurements to summarise. Missing values should be ``nan``.

    Returns
    -------
    dict
        The number of measurements present, and their mean, standard
        deviation, minimum and maximum.
    """
    values = np.asarray(values, dtype=float)
    present = values[~np.isnan(values)]

    if present.size == 0:
        return {"n": 0, "mean": 0.0, "sd": 0.0, "min": 0.0, "max": 0.0}

    if present.size == 1:
        sd = 0.0
    else:
        sd = float(np.std(present, ddof=1))

    return {
        "n": int(present.size),
        "mean": float(np.mean(present)),
        "sd": sd,
        "min": float(np.min(present)),
        "max": float(np.max(present)),
    }


def count_missing(values):
    values = np.asarray(values, dtype=float)
    return int(np.isnan(values).sum())


def summarise_all(measurements):
    """
    Summarise every column in a table of measurements.

    Parameters
    ----------
    measurements : dict
        A mapping of column name to measurements, as returned by
        :func:`ci_course.load_measurements`.

    Returns
    -------
    dict
        A mapping of column name to the summary of that column.
    """
    return {name: summarise(values) for name, values in measurements.items()}
