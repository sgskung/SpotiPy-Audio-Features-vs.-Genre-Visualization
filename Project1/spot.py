import pandas as pd
from dataclasses import dataclass, field, asdict
from typing import List, Tuple
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import billboard
from collections import defaultdict, Counter
from models import *

"""
NOTE: When submitting to PrairieLearn, please ensure that the function call to main() at the bottom of the file is commented out,
as well as any other places you have called the getPlaylist() or getHot100() functions. A simple CTRL/CMD + F to search will 
suffice. PrairieLearn will fail to grade your submission if the main() function is still commented in OR if a call to 
getPlaylist() or getHot100() is sill present in your code.  
"""

"""
SETUP: Must do first!
"""
#spotipy wraps the official spotify api providing simple python functions.
# TODO: Replace these two variables with the client_id and client_secret that you generated
CLIENT_ID = "0197336c154946088d6583393bf8f316"
CLIENT_SECRET = "732274f7c24b44ec863fa84c62574592"

#https://developer.spotify.com/dashboard/applications to get client_id and client_secret
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID,
                                                           client_secret=CLIENT_SECRET))

"""
PART 1: Getting the Top 100 Data!
You must complete Part 1 before moving on down below
"""
def getPlaylist(id: str) -> List[Track]:
    '''
    Given a playlist ID, returns a list of Track objects corresponding to the songs on the playlist. See
    models.py for the definition of dataclasses Track, Artist, and AudioFeatures.
    We need the audio features of each track to populate the audiofeatures list.
    We need the genre(s) of each artist in order to populate the artists in the artist list.

    We've written parts of this function, but it's up to you to complete it!
    '''
    
    # fetch tracks data from spotify given a playlist id
    playlistdata = sp.playlist(id)
    tracks = playlistdata['tracks']['items']

    # fetch audio features based on the data stored in the playlist result
    track_ids = []
    for song in tracks:
        track_ids.append(song['track']['id'])

    audio_features = sp.audio_features(track_ids)
    audio_info = {}  # Audio features list might not be in the same order as the track list
    for af in audio_features:
        audio_info[af['id']] = AudioFeatures(af['danceability'], \
                                             af['energy'], \
                                             af['key'], \
                                             af['loudness'], \
                                             af['mode'], \
                                             af['speechiness'], \
                                             af['acousticness'], \
                                             af['instrumentalness'], \
                                             af['liveness'], \
                                             af['valence'], \
                                             af['tempo'], \
                                             af['duration_ms'], \
                                             af['time_signature'], \
                                             af['id'])

#
    # prepare artist dictionary
    artist_ids = []
    for x in tracks:
        for y in x['track']['artists']:
            artist_ids.append(y['id'])

    artists = {}
    for k in range(1+len(artist_ids)//50): # can only request info on 50 artists at a time!
        artists_response = sp.artists(artist_ids[k*50:min((k+1)*50,len(artist_ids))]) # what is this doing?
        for a in artists_response['artists']:
            artists[a['id']] = Artist(id=a['id'], name=a['name'], genres=a['genres'])


    # populate track dataclass
    trackList = [Track(id=t['track']['id'], \
                            name=t['track']['name'], \
                            artists = [artists[a['id']] for a in t['track']['artists']], \
                            audio_features=audio_info[t['track']['id']]) \
                                        for t in tracks]

    return trackList
#
# ''' this function is just a way of naming the list we're using. You can write
# additional functions like "top Canadian hits!" if you want.'''
def getHot100() -> List[Track]:
    # Billboard hot 100 Playlist ID URI
    hot_100_id = "6UeSakyzhiEt4NB3UAd6NQ"
    return getPlaylist(hot_100_id)

# print(getHot100())
# # ---------------------------------------------------------------------
#
# """
# Part 2: The Helper Functions
# Now that we have the billboard's top 100 tracks, let's design some helper functions that will make our lives easier when creating our dataframe.
# """
#

def getGenres(t: Track) -> List[str]:

    Genres = []
    for artist in t.artists:
        Genres.extend(artist.genres)

    g_set = set(Genres)
    return list(g_set)

# print(getGenres(getHot100()[0]))
#
def doesGenreContains(t: Track, genre: str) -> bool:
    '''
    TODO
    Checks if the genres of a track contains the key string specified
    For example, if a Track's unique genres are ['pop', 'country pop', 'dance pop']
    doesGenreContains(t, 'dance') == True
    doesGenreContains(t, 'pop') == True
    doesGenreContains(t, 'hip hop') == False
    '''

    for x in t.artists:
        if genre in x.genres:
            return True
        elif genre not in x.genres:
            return False

print(doesGenreContains(getHot100()[0], "8"))

def getTrackDataFrame(tracks: List[Track]) -> pd.DataFrame:
    '''
    This function is given.
    Prepare dataframe for a list of tracks
    audio-features: 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
                    'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
                    'duration_ms', 'time_signature', 'id',
    track & artist: 'track_name', 'artist_ids', 'artist_names', 'genres',
                    'is_pop', 'is_rap', 'is_dance', 'is_country'
    '''
    # populate records
    records = []
    for t in tracks:
        to_add = asdict(t.audio_features) #converts the audio_features object to a dict
        to_add["track_name"] = t.name
        to_add["artist_ids"] = list(map(lambda a: a.id, t.artists)) # we will discuss this in class
        to_add["artist_names"] = list(map(lambda a: a.name, t.artists))
        to_add["genres"] = getGenres(t)
        to_add["is_pop"] = doesGenreContains(t, "pop")
        to_add["is_rap"] = doesGenreContains(t, "rap")
        to_add["is_dance"] = doesGenreContains(t, "dance")
        to_add["is_country"] = doesGenreContains(t, "country")

        records.append(to_add)

    # create dataframe from records
    df = pd.DataFrame.from_records(records)
    return df

# top100Tracks = getHot100()
# df = getTrackDataFrame(top100Tracks)
# # ---------------------------------------------------------------------
# # The most popular artist of the week
#
def artist_with_most_tracks(tracks: List[Track]) -> (Artist, int):
    '''
    TODO
    List of tracks -> (artist, number of tracks the artist has)
    This function finds the artist with most number of tracks on the list
    If there is a tie, you may return any of the artists
    '''
    # tally = Counter() # these structures will be useful!
    # arts = {}
    arts = []
    for q in tracks:
        for art in q.artists:
            arts.append(art.id)

    arts2 = {}
    for x in tracks:
        for y in x.artists:
            arts2[y.id] = y

    print(arts)
    print(arts2)

    tally = Counter(arts)

    print(tally)
    maxartist= max(tally, key=tally.get)

    return (arts2[maxartist]), max(tally.values())

    # return Artist(), 0

# print(artist_with_most_tracks(getHot100()))
#
# """
# Part 3: Visualizing the Data
# """
#
# # 3.1 scatter plot of dancability-speechiness with markers colored by genre: is_rap
#
def danceability_plot(tracks:List[Track]):
    # TODO assemble a scatter plot using the audio characteristics of the songs
    leest = getTrackDataFrame(tracks)
    conditional = [leest['is_rap'] == True]

    plt.scatter(leest['danceability'], leest['speechiness'], c = conditional)

    plt.show()
#
# danceability_plot(getHot100())

# # 3.2 scatter plot of duration and tempo with markers for: is_pop -> to determine if most pop songs have the same tempo and duration.

def popisfastandloud_plot(tracks:List[Track]):
    # TODO assemble a scatter plot using the audio characteristics of the songs
    leest2 = getTrackDataFrame(tracks)
    conditional = [leest2['is_pop'] == True]

    plt.scatter(leest2['duration_ms'], leest2['tempo'], c = conditional)

    plt.show()

# #
# popisfastandloud_plot(getHot100())

# def main():
#     top100Tracks = getHot100()
#     df = getTrackDataFrame(top100Tracks)
#     print(df.head())
#     artist, num_track = artist_with_most_tracks(top100Tracks)
#     print("%s has the most number of tracks on this week's Hot 100 at a whopping %d tracks!" % (artist.name, num_track))
#     danceability_plot(top100Tracks)
#
# main()
