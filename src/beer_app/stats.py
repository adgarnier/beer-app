"""Summary statistics for the uploaded pub database."""

import pandas as pd
from importlib.resources import files
from beer_app.pub_data import load_pubs

def pub_counts():
    """Returns a panda dataframe including Pub ID, Name, and number of total visits"""
    pub_count = visited_pub_count(visited_pub_path())
    return pub_count

def visited_pub_path():
    """Defines file path for recorded pub visits"""
    visited_pub_path = files("beer_app").joinpath("data","visited_pubs.csv")
    return visited_pub_path

def visited_pub_count(visited_pubs_path):
    """Cound visited trips to each pub as a panda df"""
    
    #Load in visit data
    df = pd.read_csv(visited_pubs_path)
    
    #Load in pub data
    pubs = load_pubs()
    
    #Convert list of Pub objects into a DataFrame
    pubs_df = pd.DataFrame([pub.as_dict() for pub in pubs])

    #Filter for pubs visited are only 'true'
    filt_df = df[
        df["Visited"].astype(str).str.lower() == "true"
    ]
    #Talley all visits
    pub_counts = (
    filt_df["ID"]
    .value_counts()
    .rename_axis("ID")
    .reset_index(name="Count")
    )

    #Merge visit counts with pub names
    pub_counts = pd.merge(
        pub_counts,
        pubs_df[["id", "name"]],
        left_on="ID",
        right_on="id",
        how="left"
    )
    #Remove duplicate ID column
    pub_counts = pub_counts.drop(columns=["id"])

    return pub_counts