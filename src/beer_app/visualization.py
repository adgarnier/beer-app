"""Visualizing Script for Pub STATS bby."""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from matplotlib.ticker import MaxNLocator


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

def p_visits_over_time(visited_pub_times): #will take visited_pub_times() from beer_app.stats
    """Plot the visits of a pub over time."""
    #Update df to group by ID, name, and month
    df = visited_pub_times.copy()
    df["VisitDate"] = pd.to_datetime(df["VisitDate"])
    df["Month"] = df["VisitDate"].dt.to_period("M")

    monthly_counts = (
        df.groupby(["ID", "name", "Month"])
        .size()
        .reset_index(name="Count")
    )

    #create figure
    fig, ax = plt.subplots(figsize=(12, 6))

    #Gather the months in the dataset to size
    all_months = pd.period_range(
        df["Month"].min(),
        df["Month"].max(),
        freq="M"
    )

    #Plot each pub
    for (pub_id, pub_name), group in monthly_counts.groupby(["ID", "name"]):

        #Include the months with no visits
        counts = (
            group.set_index("Month")["Count"]
            .reindex(all_months, fill_value=0)
        )
        #Convert the months to a timestamp
        dates = all_months.to_timestamp()
        #Now plot monthly visits
        ax.step(
            dates,
            counts,
            where="post",
            linewidth=2.5,
            alpha=0.85,
            label=f"{pub_name} ({pub_id})"
        )

    #Format the plot
    ax.set_xlabel("Month")
    ax.set_ylabel("Number of Pub'lishes")
    ax.set_title("Pub'lishes per Month")
    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1)) #add yr to mo; change interval to change month frequency
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y")) #adds year to the month labels
    ax.yaxis.set_major_locator(MaxNLocator(integer=True)) #Ensures only whole numbers are displayed for visits
    ax.set_ylim(bottom=0) #No negative pub visits
    #Add a legend to display pub names
    ax.legend(title="Pub", loc="best")
    return fig

#Calculate pub visits per visited pub just for expirment
#p_visits_per_pub(pub_counts())
#print(pub_counts())
#print(visited_pub_times())
#from beer_app.stats import visited_pub_times
#p_visits_over_time(visited_pub_times())
#plt.show()
