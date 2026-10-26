"""Writing summary reports to disk."""

import os
from pathlib import Path


def format_report(summaries):
    """
    Format a set of column summaries as plain text.

    Parameters
    ----------
    summaries : dict
        A mapping of column name to summary, as returned by
        :func:`ci_course.summarise_all`.

    Returns
    -------
    str
        The formatted report.
    """
    lines = ["Measurement summary", "==================="]
    for name, summary in summaries.items():
        lines.append(
            f"{name}: n={summary['n']} mean={summary['mean']:.3f} sd={summary['sd']:.3f} "
            f"min={summary['min']:.3f} max={summary['max']:.3f}"
        )
    return "\n".join(lines) + "\n"


def write_report(summaries, path):
    """
    Write a report, replacing any report already at ``path``.

    The report is written to a temporary file and then moved into place, so
    that an interrupted run cannot leave a half written report behind.

    Parameters
    ----------
    summaries : dict
        A mapping of column name to summary.
    path : str or pathlib.Path
        Where to write the report.

    Returns
    -------
    pathlib.Path
        The path the report was written to.
    """
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")

    with open(tmp, "w", encoding="utf-8") as handle:
        handle.write(format_report(summaries))

    os.rename(tmp, path)
    return path
