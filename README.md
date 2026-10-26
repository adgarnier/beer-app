# OxRSE Continuous Integration course

This repository contains a small Python package for summarising experimental measurements.
Over the course you will use free cloud services to automate:

- unit testing on multiple Python versions
- unit testing on multiple operating systems
- static analysis
- coverage testing
- checking that public functions are documented
- documentation generation and deployment

## The package

```text
src/ci_course/
    io.py       read measurements from a CSV file
    stats.py    summarise a column of measurements
    report.py   write a summary report
    cli.py      the ci-course command
tests/
```

## Setting up

You will need Python 3.12 or later.
From the repository directory, create and activate a virtual environment using the commands for your shell.

| Platform and shell | Create | Activate |
| :- | :- | :- |
| Linux / macOS, bash or zsh | `python3 -m venv venv` | `source venv/bin/activate` |
| Windows, Command Prompt | `python -m venv venv` | `venv\Scripts\activate.bat` |
| Windows, PowerShell | `python -m venv venv` | `.\venv\Scripts\Activate.ps1` |

Install this project:

```bash
python -m pip install -e ".[dev,docs]"
```

The `-e` matters: it installs the project in editable mode, so that the package you import is the source tree you are editing.

## Running the package and checks

Try the command line tool and run the checks:

```bash
ci-course                     # summarise the bundled sample data
pytest                        # run the tests
ruff check .                  # run the linter
ruff check --select D src/    # check the docstrings
```

This repository is the starting point for the practical, so some checks may report problems.
Follow the practical instructions to investigate the results and improve the project.

## Oxford map prototype

The first pub-tracker prototype is an interactive Leaflet map centred on Oxford. After installing the project, start it with:

```bash
oxford-pub-map
```

The command starts a local server at <http://127.0.0.1:8000> and opens the map in your browser. Press Ctrl+C in the terminal to stop it. If port 8000 is already in use, choose another one with `oxford-pub-map --port 8001`.

The map uses hosted Leaflet files and OpenStreetMap tiles, so it needs an internet connection while it is open.
