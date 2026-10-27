"""Visualizing Script for Pub STATS bby."""

import matplotlib.pyplot as plt
from beer_app.stats import visited_pub_count, visited_pub_path, pub_counts


def p_visits_per_pub(pub_count) -> Figure:
    """Plot the number of Pub'lishes per pub."""
    fig = plt.figure(figsize=(10,6))
    plt.bar(pub_count["name"], pub_count["Count"])
    plt.xlabel("Pub Legal Name")
    plt.ylabel("Number of Pub'lishes")
    plt.title("Pub'lishes per Pub")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    return fig

#Calculate pub visits per visited pub just for expirment
#p_visits_per_pub(pub_counts())
#plt.show()