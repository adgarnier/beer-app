"""Visualizing Script for Pub STATS bby."""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from matplotlib.ticker import MaxNLocator
from matplotlib.figure import Figure
from matplotlib.colors import to_hex
import matplotlib.colors as mcolors
import numpy as np


def p_visits_per_pub(pub_count): #will take pub_counts() from beer_app.stats
    """Plot the number of Pub'lishes per pub."""
    fig = plt.figure(figsize=(10,6))
    plt.bar(pub_count["name"], pub_count["Count"])
    plt.xlabel("Pub Legal Name")
    plt.ylabel("Number of Pub'lishes")
    plt.title("Pub'lishes per Pub")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    return fig

def p_visits_over_time(visited_pub_times: pd.DataFrame) -> Figure:
    """Plot monthly pub visits as a cozy stacked bar chart."""

    # KEEP: Your existing data preparation
    df = visited_pub_times.copy()
    df["VisitDate"] = pd.to_datetime(df["VisitDate"])
    df["Month"] = df["VisitDate"].dt.to_period("M")

    monthly_counts = (
        df.groupby(["ID", "name", "Month"])
        .size()
        .reset_index(name="Count")
    )

    # NEW: Create pub labels including their IDs
    monthly_counts["Pub"] = (
        monthly_counts["name"]
        + " ("
        + monthly_counts["ID"].astype(str)
        + ")"
    )

    # NEW: Reshape data for stacking
    plot_data = monthly_counts.pivot(
        index="Month",
        columns="Pub",
        values="Count"
    ).fillna(0)

    # KEEP: Include months with no visits
    all_months = pd.period_range(
        df["Month"].min(),
        df["Month"].max(),
        freq="M"
    )

    plot_data = plot_data.reindex(
        all_months,
        fill_value=0
    )

    # NEW: Warm pub-inspired colour palette
    pub_colors = [
        "#8B4937",  # Brick red
        "#D09A47",  # Amber
        "#647C5B",  # Sage green
        "#6D536F",  # Plum
        "#B76E50",  # Copper
        "#7B6845",  # Olive brown
        "#477C78",  # Muted teal
        "#C17F85",  # Dusty rose
    ]

    # CHANGED: Create a cream-coloured figure
    fig, ax = plt.subplots(figsize=(12, 6))

    fig.patch.set_facecolor("#F7F0E3")
    ax.set_facecolor("#F7F0E3")

    # NEW: Plot stacked bars instead of steps
    bottom = np.zeros(len(plot_data))

    for i, pub in enumerate(plot_data.columns):

        counts = plot_data[pub].values

        ax.bar(
            range(len(plot_data)),
            counts,
            bottom=bottom,
            width=0.75,
            color=pub_colors[i % len(pub_colors)],
            edgecolor="#F7F0E3",
            linewidth=0.8,
            label=pub
        )

        bottom += counts

    # NEW: Add total visits above each bar
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
                color="#493125"
            )

    # CHANGED: Format chart
    ax.set_xlabel("Month", color="#493125")
    ax.set_ylabel("Number of Pub'lishes", color="#493125")
    ax.set_title(
        "Pub'lishes per Month",
        fontsize=16,
        fontweight="bold",
        color="#493125",
        pad=20
    )

    # CHANGED: Format month labels
    ax.set_xticks(range(len(plot_data)))
    ax.set_xticklabels(
        plot_data.index.strftime("%b %Y"),
        rotation=45,
        ha="right"
    )

    # KEEP: Whole numbers only
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_ylim(bottom=0, top=max(bottom) * 1.15 if len(bottom) else 1)

    # NEW: Subtle horizontal gridlines
    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.25,
        color="#806C59"
    )
    ax.set_axisbelow(True)

    # NEW: Remove unnecessary borders
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#C4B39F")
    ax.spines["bottom"].set_color("#C4B39F")

    ax.tick_params(colors="#604A3A")

    # CHANGED: Legend outside chart
    ax.legend(
        title="Pub",
        loc="upper left",
        bbox_to_anchor=(1.02, 1),
        frameon=False
    )

    fig.tight_layout()

    return fig

#Calculate pub visits per visited pub just for expirment
#will take visited_pub_times() from beer_app.stats
# p_visits_per_pub(pub_counts())
# plt.show()
from beer_app.stats import visited_pub_times
p_visits_over_time(visited_pub_times())
plt.show()
print("Print")