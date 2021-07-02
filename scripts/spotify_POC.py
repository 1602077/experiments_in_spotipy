#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import spotify_credentials as cred


def get_artist_data(artist_name, api_credentials):
    """

    """
    
    sp = spotipy.Spotify(client_credentials_manager=api_credentials)

    # Search for artist name, find all their uris (unique reference ids) and
    # the corresponding album names storing: storing both in seperate lists.
    search_result = sp.search(artist_name)
    artist_uri = search_result['tracks']['items'][0]['artists'][0]['uri']
    artist_name_search_result = search_result['tracks']['items'][0]['artists'][0]['name']
    sp_albums = sp.artist_albums(artist_uri, album_type='album')

    album_names = [sp_albums['items'][i]['name'] for i in range(len(sp_albums['items']))]
    album_uris = [sp_albums['items'][i]['uri'] for i in range(len(sp_albums['items']))]

    print(album_names)
    #print(album_uris)

    #################################################################################
    # GET TRACK NAMES & ORDER FOR EACH ARTIST ALBUM
    #################################################################################
    spotify_albums = {}
    album_counter = 0

    for album in album_uris:
        
        # Create key values of empty lists inside nest dict for each album
        track_keys = ['artist_name', 'album', 'track_number', 'id', 'name', 'uri']
        spotify_albums[album] = {key: [] for key in track_keys} 

        tracks = sp.album_tracks(album) #pull data on album tracks

        for n in range(len(tracks['items'])): #for each song track

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
    for album in spotify_albums:
        # Assign audio feature keys empty list values in nested dictionary
        audio_feature_keys = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence', 'popularity']
        for key in audio_feature_keys:
            spotify_albums[album][key] = []
        
        for track in spotify_albums[album]['uri']:
            # Get all audio features for the current track and append values
            # into appropriate key in dictionary

            features = sp.audio_features(track)
            
            spotify_albums[album]['acousticness'].append(features[0]['acousticness'])
            spotify_albums[album]['danceability'].append(features[0]['danceability'])
            spotify_albums[album]['energy'].append(features[0]['energy'])
            spotify_albums[album]['instrumentalness'].append(features[0]['instrumentalness'])
            spotify_albums[album]['liveness'].append(features[0]['liveness'])
            spotify_albums[album]['loudness'].append(features[0]['loudness'])
            spotify_albums[album]['speechiness'].append(features[0]['speechiness'])
            spotify_albums[album]['tempo'].append(features[0]['tempo'])
            spotify_albums[album]['valence'].append(features[0]['valence'])

            #pop = sp.track(track)
            spotify_albums[album]['popularity'].append(sp.track(track)['popularity'])

    #################################################################################
    # REORGANISE DATA INTO AN UNNESTED DICTIONARY TO ALLOW FOR DF CONVERSION
    #################################################################################

    all_albums_data_keys = ['artist_name', 'album', 'track_number', 'id', 'name', 'uri', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence', 'popularity']
    all_albums_data = {key: [] for key in all_albums_data_keys}


    for album in spotify_albums:
        for feature in spotify_albums[album]:
            all_albums_data[feature].extend(spotify_albums[album][feature])

    df = pd.DataFrame.from_dict(all_albums_data)
    df = df.drop_duplicates('name').sort_index()
    print(df.head())
    
    return df

def main():
    
    credentials = SpotifyClientCredentials(client_id=cred.client_id, client_secret=cred.client_secret)
    
    album_master_df = pd.DataFrame()

    artists = ["Tom Misch", "John Mayer", "Loyle Carner"]
    for artist in artists:
        df = get_artist_data(artist, credentials)
        album_master_df = album_master_df.append(df)

    album_master_df.to_csv('master_albums.csv', index=False)
    return


if __name__ == "__main__":
    main()

