#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import spotify_credentials as cred
import os
import glob
import time


def get_artist_data(artist_name, api_credentials):
    """
    Function that calls the Spotify API using Pythons SpotiPy library to search for a 
    specified artist_name within Spotify's dataset. If a match is found that artist /
    bands albums will be appended into a nested dictionary along with each album's 
    subsequent tracks and features as classified by Spotify. More information on the
    meaning of each feature can be found at 
    https://developer.spotify.com/documentation/web-api/reference/#category-tracks.
    
    inputs:
    ---------------------------------------------------------------------------------   
    artist_name:        Artist name of the album and track data to be downloaded. 
    api_crediantials:   Credentials required to call Spotify API. i.e. output of
                        calling SpotifyClientCredentials().

    returns:
    ---------------------------------------------------------------------------------   
    Unique dataframe for each artist_name which contains their whole Spotify catelog,
    with a series of categorisation features as described in the category tracks url
    above.

    """
    
    sp = spotipy.Spotify(client_credentials_manager=api_credentials, retries=15)

    # Search for artist name, find all their uris (unique reference ids) and
    # the corresponding album names storing: storing both in seperate lists.
    search_result = sp.search(artist_name)
    artist_uri = search_result['tracks']['items'][0]['artists'][0]['uri']
    # Top artist name search results
    artist_name_search_result = search_result['tracks']['items'][0]['artists'][0]['name']

    # If this doesn't match the input artist name look through the top 10 results to match
    if artist_name != artist_name_search_result:
        try:
            top_10_search_results = [search_result['tracks']['items'][i]['artists'][0]['name'] for i in range(10)]
            # Get index position of matched artist name in list to use in artist_name_search_result
            index = top_10_search_results.index(artist_name)
            artist_uri = search_result['tracks']['items'][index]['artists'][0]['uri']
            artist_name_search_result = search_result['tracks']['items'][index]['artists'][0]['name']
        except:
            print(f"!! {artist_name} not found in Spotify dataset.")
            return 0

    sp_albums = sp.artist_albums(artist_uri, album_type='album')

    album_names = [sp_albums['items'][i]['name'] for i in range(len(sp_albums['items']))]
    album_uris = [sp_albums['items'][i]['uri'] for i in range(len(sp_albums['items']))]

    print(f">> Currently downloading {artist_name_search_result}'s data.")
    #print(album_names)
    #print(album_uris)

    #################################################################################
    # GET TRACK NAMES & ORDER FOR EACH ARTIST ALBUM
    #################################################################################
    spotify_albums = {}
    album_counter = 0
    track_keys = ['artist_name', 'album', 'track_number', 'id', 'name', 'uri']

    for album in album_uris:
        
        # Assign an empty list to each key value inside a nested dictionary
        spotify_albums[album] = {key: [] for key in track_keys} 

        # Pull track data for each album track and append its info to nest dict
        tracks = sp.album_tracks(album)

        for n in range(len(tracks['items'])):

            spotify_albums[album]['artist_name'].append(artist_name_search_result)
            spotify_albums[album]['album'].append(album_names[album_counter])
            spotify_albums[album]['track_number'].append(tracks['items'][n]['track_number'])
            spotify_albums[album]['id'].append(tracks['items'][n]['id'])
            spotify_albums[album]['name'].append(tracks['items'][n]['name'])
            spotify_albums[album]['uri'].append(tracks['items'][n]['uri'])

        album_counter += 1
    
    #################################################################################
    # GET AUDIO FEATURES FOR EACH ALBUM TRACK
    #################################################################################
    audio_feature_keys = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence', 'release_date', 'popularity']
    for album in spotify_albums:
        # Assign audio feature keys empty list values in nested dictionary
        for key in audio_feature_keys:
            spotify_albums[album][key] = []
        
        for track in spotify_albums[album]['uri']:
            # Get all audio features for the current track and append values
            # into appropriate key in dictionary
            features = sp.audio_features(track)

            # Append data for all keys expect release date popularity which will 
            # need to be obtained using sp.track().
            for key in audio_feature_keys[:-2]:
                spotify_albums[album][key].append(features[0][key])

            track_info = sp.track(track)
            spotify_albums[album]['release_date'].append(track_info['album']['release_date'])
            spotify_albums[album]['popularity'].append(track_info['popularity'])

    #################################################################################
    # REORGANISE DATA INTO AN UNNESTED DICTIONARY TO ALLOW FOR DF CONVERSION
    #################################################################################
    all_albums_data_keys = track_keys + audio_feature_keys
    all_albums_data = {key: [] for key in all_albums_data_keys}

    for album in spotify_albums:
        for feature in spotify_albums[album]:
            all_albums_data[feature].extend(spotify_albums[album][feature])

    df = pd.DataFrame.from_dict(all_albums_data)
    df = df.drop_duplicates('name').sort_index()
    return df


def main():
    
    credentials = SpotifyClientCredentials(client_id=cred.client_id, client_secret=cred.client_secret)

    #################################################################################
    # GET ARISTS IN MY APPLE MUSIC LIBRARY
    #################################################################################
    if not os.path.isfile("../data/artist_list.csv"):
        in_dir = "~/Documents/Computing/SQL/apple_music_replay/input_data/MusicLib.csv"
        artists_df = pd.read_csv(in_dir, usecols=["Album Artist"])
        artists_df.drop_duplicates(inplace=True)
        artists_df.sort_values(by=['Album Artist'], inplace=True, ascending=True)
        artists_df.to_csv("../data/artist_list.csv", index=False)
    else:
        artists_df = pd.read_csv("../data/artist_list.csv")
    artists_list = artists_df.values.tolist()

    #################################################################################
    # CALL get_artist_data() FOR EACH ARTIST IN artists_list
    #################################################################################
    request_counter = 0
    sleep_min, sleep_max = 4, 6
    for artist in artists_list:
        if not os.path.isfile('../data/artists/' + str(*artist) + '.csv'):
            df = get_artist_data(*artist, credentials)
            request_counter += 1
            # Add random delay to avoid being forcibly  disconnected
            if request_counter % 5 == 0:
                time.sleep(np.random.uniform(sleep_min, sleep_max))
            if type(df) != int:
                df.to_csv('../data/artists/' + str(*artist) + '.csv', index=False)
        else:
            print(*artist)

    #################################################################################
    # APPEND ARTISTS DATAFRAMES INTO MASTER DATAFRAME
    #################################################################################
    # Create empty dataframe to append each artists library of music to
    master_df = pd.DataFrame()

    artist_csvs = glob.glob(os.path.join("../data/artists/","*.csv"))
    for f in artist_csvs:
        df = pd.read_csv(f)
        master_df = master_df.append(df, ignore_index=True)

    # Remove duplicate tracks in the case when a collaboration is listed individually each artist
    master_df.drop_duplicates('uri', inplace=True)
    master_df.to_csv('../data/master_data.csv', index=False)
    return 1


if __name__ == "__main__":
    main()

