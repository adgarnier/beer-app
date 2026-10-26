"""Command line interface for the package."""

import argparse
import sys

from .io import load_measurements
from .report import format_report, write_report
from .stats import summarise_all


def main(argv=None):
    """
    Summarise a CSV file of measurements.

    Parameters
    ----------
    argv : list of str, optional
        Command line arguments. Defaults to those given on the command line.

    Returns
    -------
    int
        Zero if the summary was produced successfully.
    """
    parser = argparse.ArgumentParser(prog="ci-course", description="Summarise a CSV file of measurements.")
    parser.add_argument("csv", nargs="?", default=None, help="the CSV file to summarise")
    parser.add_argument("-o", "--output", default=None, help="write the report to this file")
    args = parser.parse_args(argv)

    summaries = summarise_all(load_measurements(args.csv))

    if args.output is None:
        print(format_report(summaries), end="")
    else:
        write_report(summaries, args.output)

    return 0
