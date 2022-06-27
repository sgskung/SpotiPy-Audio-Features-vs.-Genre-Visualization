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

# spotipy wraps the official spotify api providing simple python functions.
# TODO: Replace these two variables with the client_id and client_secret that you generated
import spotipy

@dataclass
class Artist:
    id: str
    name: str
    genres: List[str]

@dataclass
class AudioFeatures:
    danceability: float
    energy: float
    key: int
    loudness: float
    mode: int
    speechiness: float
    acousticness: float
    instrumentalness: float
    liveness: float
    valence: float
    tempo: float
    duration_ms: int
    time_signature: int
    id: str

@dataclass
class Track:
    id: str
    name: str
    artists: List[Artist]
    audio_features: AudioFeatures

CLIENT_ID = "0197336c154946088d6583393bf8f316"
CLIENT_SECRET = "732274f7c24b44ec863fa84c62574592"

# https://developer.spotify.com/dashboard/applications to get client_id and client_secret
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID,
                                                           client_secret=CLIENT_SECRET))

ide = "37i9dQZF1DX0XUsuxWHRQd"
"""
PART 1: Getting the Top 100 Data!
You must complete Part 1 before moving on down below
"""


playlistdata = sp.playlist(ide)
tracks = playlistdata['tracks']['items']

    # # fetch audio features based on the data stored in the playlist result
track_ids = []
for song in tracks:
    track_ids.append(song['track']['id'])


artist_ids = []
for x in tracks:
    for y in x['track']['artists']:
        artist_ids.append(y['id'])

audio_features = sp.audio_features(track_ids)
audio_info = {}  # Audio features list might not be in the same order as the track list
for af in audio_features:
    audio_info[af['id']] = AudioFeatures(af['danceability'], \
                                             af['energy'], \
                                             af['key'],  \
                                             af['loudness'],  \
                                             af['mode'],  \
                                             af['speechiness'], \
                                             af['acousticness'], \
                                             af['instrumentalness'], \
                                             af['liveness'], \
                                             af['valence'], \
                                             af['tempo'], \
                                             af['duration_ms'], \
                                             af['time_signature'], \
                                             af['id'])


artists = {}
for k in range(1+len(artist_ids)//50): # can only request info on 50 artists at a time!
    artists_response = sp.artists(artist_ids[k*50:min((k+1)*50, len(artist_ids))]) #what is this doing?
    for a in artists_response['artists']:
        artists[a['id']] = Artist(id=a['id'], name=a['name'], genres=a['genres'])
#
trackList = [Track(id=t['track']['id'], \
                            name=t['track']['name'], \
                            artists = [artists[a['id']] for a in t['track']['artists']], \
                            audio_features=audio_info[t['track']['id']]) \
                                        for t in tracks]

print(trackList)

# # #
# def getGenres(t: Track) -> List[str]:
#     '''
#     Takes in a Track and produce a list of unique genres that the artists of this track belong to
#     '''
#     Genres = []
#     Genres.append(t.artists)
#     return Genres
#
# print(getGenres(trackList[0]))
#
# print("my name is justin")
# print(getPlaylist("37i9dQZF1DX0XUsuxWHRQd"))
#     # audio_features = sp.audio_features(track_ids)
#     # audio_info = {}
def getGenres(t: Track) -> List[str]:

    Genres = []
    for artist in t.artists:
        Genres.extend(artist.genres)

    g_set = set(Genres)
    return list(g_set)

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

tracks = trackList
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
print(df)
