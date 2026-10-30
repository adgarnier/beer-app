"""Visualizing Script for Pub STATS bby."""

from multiprocessing import Process
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.axes import Axes
from matplotlib.ticker import MaxNLocator
from matplotlib.figure import Figure
from beer_app.stats import pub_counts, visited_pub_times

STATS_HELP = """Stats help

Pick between the two graph options by entering 'stats'
followed by your choice of 'pub' or 'time'.

Commands:
  --help  shows this output
  pub     shows a graph for visits per pub
  time    shows a graph for visits over time
"""

PUB_COLORS = [
    "#8B4937",  # Brick red
    "#D09A47",  # Amber
    "#647C5B",  # Sage green
    "#6D536F",  # Plum
    "#B76E50",  # Copper
    "#7B6845",  # Olive brown
    "#477C78",  # Muted teal
    "#C17F85",  # Dusty rose
]
BACKGROUND_COLOR = "#F7F0E3"
TEXT_COLOR = "#493125"


def format_pub_chart(fig: Figure, ax: Axes, *, title: str, xlabel: str, ylabel: str) -> None:
    """Apply the shared Pub'lish chart style to a figure and axes."""
    fig.patch.set_facecolor(BACKGROUND_COLOR)
    ax.set_facecolor(BACKGROUND_COLOR)

    ax.set_xlabel(xlabel, color=TEXT_COLOR)
    ax.set_ylabel(ylabel, color=TEXT_COLOR)
    ax.set_title(title, fontsize=16, fontweight="bold", color=TEXT_COLOR, pad=20)

    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", linestyle="--", alpha=0.25, color="#806C59")
    ax.set_axisbelow(True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#C4B39F")
    ax.spines["bottom"].set_color("#C4B39F")
    ax.tick_params(colors="#604A3A")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

    fig.tight_layout()


def p_visits_per_pub(pub_count): #will take pub_counts() from beer_app.stats
    """Plot the number of Pub'lishes per pub."""
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = [PUB_COLORS[i % len(PUB_COLORS)] for i in range(len(pub_count))]
    ax.bar(
        pub_count["name"],
        pub_count["Count"],
        color=colors,
        edgecolor=BACKGROUND_COLOR,
        linewidth=0.8,
    )
    format_pub_chart(
        fig,
        ax,
        title="Pub'lishes per Pub",
        xlabel="Pub Legal Name",
        ylabel="Number of Pub'lishes",
    )
    return fig

def p_visits_over_time(visited_pub_times: pd.DataFrame) -> Figure:
    """Plot monthly pub visits as a cozy stacked bar chart."""
    df = visited_pub_times.copy()
    df["VisitDate"] = pd.to_datetime(df["VisitDate"])
    df["Month"] = df["VisitDate"].dt.to_period("M")

    monthly_counts = (
        df.groupby(["ID", "name", "location", "Month"])
        .size()
        .reset_index(name="Count")
    )

    monthly_counts["Pub"] = monthly_counts["name"] + " (" + monthly_counts["location"] + ")"
    plot_data = monthly_counts.pivot(index="Month", columns="Pub", values="Count").fillna(0)
    all_months = pd.period_range(df["Month"].min(), df["Month"].max(), freq="M")
    plot_data = plot_data.reindex(all_months, fill_value=0)
    fig, ax = plt.subplots(figsize=(12, 6))
    bottom = np.zeros(len(plot_data))

    for i, pub in enumerate(plot_data.columns):

        counts = plot_data[pub].values

        ax.bar(
            range(len(plot_data)),
            counts,
            bottom=bottom,
            width=0.75,
            color=PUB_COLORS[i % len(PUB_COLORS)],
            edgecolor=BACKGROUND_COLOR,
            linewidth=0.8,
            label=pub
        )

        bottom += counts

    for i, total in enumerate(bottom):
        if total > 0:
            ax.text(
                i,
                total + 0.1,
                str(int(total)),
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="bold",
                color=TEXT_COLOR
            )

    ax.set_xticks(range(len(plot_data)))
    ax.set_xticklabels(
        plot_data.index.strftime("%b %Y"),
        rotation=45,
        ha="right"
    )

    ax.set_ylim(bottom=0, top=max(bottom) * 1.15 if len(bottom) else 1)
    ax.legend(title="Pub", loc="upper left", bbox_to_anchor=(1.02, 1), frameon=False)
    format_pub_chart(fig, ax, title="Pub'lishes per Month",
                     xlabel="Month", ylabel="Number of Pub'lishes")

    return fig

def show_visits_per_pub():
    """Visit per pub."""
    p_visits_per_pub(pub_counts())
    plt.show()

def show_visits_over_time():
    """Plot pub visits overtime."""
    p_visits_over_time(visited_pub_times())
    plt.show()

def launch_stats_graph(target):
    """Launch the stats graph."""
    process = Process(target=target, daemon=True)
    process.start()
    return process

def main() -> int:
    """Prompt for and display one of the stats graphs."""
    graph_processes = []

    while True:
        # Reap completed graph processes without waiting for open windows.
        graph_processes = [process for process in graph_processes if process.is_alive()]
        try:
            stats_choice = input(
                "Choose 'pub' or 'time'. Type '--help' for more info: "
                ).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nLeaving stats!")
            return 0

        if stats_choice in {"h", "help", "--help"}:
            print(STATS_HELP)
            continue
        if stats_choice in {"visit per pub", "visits per pub", "pub"}:
            graph_processes.append(launch_stats_graph(show_visits_per_pub))
            continue
        if stats_choice in {"visit over time", "visits over time", "time"}:
            graph_processes.append(launch_stats_graph(show_visits_over_time))
            continue
        if stats_choice in {"q", "quit", "exit", "bye", "cya"}:
            print("Leaving stats!")
            return 0

        print("Unknown stats option. Choose 'visits per pub' or "
            "'visits over time'. Exit with 'quit'.")

if __name__ == "__main__":
    raise SystemExit(main())
