# Personal Oxford Pub Tracking App

This folder contains the reference material for a proposed app that helps users discover Oxford pubs, record the pubs they have visited, and track their progress. The project is intended to apply the software engineering practices covered by the DTC Software Engineering course to a practical, user-focused product.

The first release will be a local Python command-line application. A later release may provide a mobile-friendly website backed by a shared online database.

## Project objectives

The app should allow a user to:

- browse a structured dataset of Oxford pubs;
- search, filter, and sort pubs by attributes such as location, provider, ranking, and price;
- mark pubs as visited and retain that progress between sessions;
- view pubs and their visited status on an interactive map; and
- see statistics that summarise their progress.

## Proposed data sources

The initial pub dataset may be assembled from the following public guides:

- [Ben Gutteridge's Oxford pub list](https://bengutteridge.github.io/pubs/), which includes pub names, areas, rankings, providers, notes, and features;
- [Oxford Pub Guide](https://www.oxfordpubguide.co.uk/allpubs.html), which includes pub names, locations, rankings, and notes; and
- the example spreadsheet in this folder, if suitable for preparing or validating the project's data model.

Before redistributing data from an external source, the project should confirm its licence and terms of use and record the source of each imported field.

## Delivery plan

### Minimum viable product

The minimum viable product will be a locally installed Python application with a command-line interface. It should include:

- a structured Oxford pub dataset;
- search, filtering, and sorting;
- persistent visited status;
- progress statistics;
- an interactive map;
- automated unit tests;
- continuous integration with GitHub Actions; and
- user and developer documentation.

The Python package should be installable with `pip` so that the application can be run consistently on a user's machine.

### Future web version

A later version may replace or supplement the command-line interface with a JavaScript web application:

- **Frontend:** GitHub Pages
- **Backend:** Supabase or Firebase
- **Primary use case:** mobile-friendly access to a centrally stored personal pub list

The local and web versions should share data structures and application logic where practical.

## Engineering approach

Development should follow the working practices taught in the course:

- plan and track work with GitHub issues;
- develop changes on branches and review them through pull requests;
- use modular code and appropriate object-oriented or functional design;
- build automated tests with meaningful coverage;
- run tests, static checks, and documentation builds in continuous integration;
- document installation, usage, architecture, and public interfaces; and
- publish the project under an open-source licence.

## Relationship to the original course brief

This proposal replaces the original pharmacokinetic modelling project with a pub-tracking application while retaining its underlying learning goals.

| Course goal | Pub tracker equivalent |
| --- | --- |
| Distributable Python package | A local version installable with `pip` |
| Transparent development | GitHub issues, branches, and pull requests |
| Reliable implementation | Automated unit tests and test coverage |
| Complete documentation | README, interface documentation, and an open-source licence |
| Continuous integration | GitHub Actions for testing, documentation, and deployment |
| Configurable model inputs | Search and filtering by pub attributes such as location, provider, ranking, and price |
| Modular design | Reusable components shared within the project and, where practical, between local and web versions |
| Quantitative output | User-facing progress statistics and other analytics |
| Visual output | An interactive map that responds to the user's selections and visited status |

## Possible extensions

Once the minimum viable product is complete, possible additions include:

- a **Perfect Pint** recommendation feature that scores pubs against a user's preferred attributes; and
- a **Pub Crawl** planner that suggests routes based on a user's preferences.

These are stretch goals and should not delay delivery of the core tracking experience.

## Reference files

- `project proposal.docx` - the original project proposal
- `example_excel_file.xlsx` - example spreadsheet supplied with the project materials

