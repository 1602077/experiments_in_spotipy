#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd


def get_library_artists(input_file):
    """
    Saves all unique artist names in my apple music library as a list to be 
    fed into get_artist_data to create a sufficiently large dataset for
    analysis.

    inputs:
    ________________________________________________________________________
    input_file: MusicLibrary.csv file accesible through submitting a data &
                privacy request to Apple Music. This  details everything in
                the user's library.'

    returns:
    ________________________________________________________________________
    artist_list: output dataframe saved as a csv file, which contains a 
                 distinct lists of artists in current libary.
    """
    
    artists_df = pd.read_csv(input_file, usecols=["Album Artist"])
    artists_df.drop_duplicates(inplace=True)
    artists_df.sort_values(by=['Album Artist'], inplace=True, ascending=True)
    artists_list = artists_df.values.tolist()
    print(artists_list[0])

    print(f"{len(artists_list)} artists detected in library.")

    artists_df.to_csv("../output_data/artist_list.csv", index=False)
    return artists_list


if __name__ == "__main__":
    get_library_artists("~/Documents/Computing/SQL/apple_music_replay/input_data/MusicLib.csv")
