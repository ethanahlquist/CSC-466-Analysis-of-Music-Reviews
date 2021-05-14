import pandas as pd
import numpy as np
import time
import sqlite3
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from requests.exceptions import ReadTimeout
import sys
import getopt


from urllib.error import HTTPError
# Spotify Auth Token: BQBbnJKCwwoNfE2ezbZaeLDfYKQQikPOp96FmU2vrbCYe64KZ907Oga0C80

''' YOU NEED TO COPY PASTE THESE TWO COMMENTS INTO YOUR TERMINAL BEFORE RUNNING (without the # of course)'''
# export SPOTIPY_CLIENT_ID='98bd16fb0f01483aace2c3bf79f041a0'
# export SPOTIPY_CLIENT_SECRET='8891a8f08d304b2fb1863d1c1df873c5'

outfile_csv = "../data/ethan_spotify_pitchfork.csv"
outfile_sql = "../data/ethan_spotify_pitchfork.sql"

count = 1
total_albums = 1

spotify = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(), requests_timeout=10, retries=10)

start_time = time.time()

df_features = pd.DataFrame()

desired_features = ['Energy', 'Danceability', 'Happiness', 'Loudness',
                    'Acousticness', 'Instrumentalness', 'Liveness', 'Speechiness', 'Key',
                    'Tempo', 'Duration']


def spotify_call(func, *args, **kwargs):
    calling_func = kwargs['caller']
    while True:
        try:
            if('func_kwargs' in kwargs):
                return func(*args, **kwargs['func_kwargs'])
            else:
                return func(*args)
        except spotipy.exceptions.SpotifyException as e:
            print(e.headers['retry-after'])
            if(calling_func is not None):
                print(calling_func)
            time.sleep(int(e.headers['retry-after']))
            continue
        break


def get_track_features(track):
    their_keys = ['energy', 'danceability', 'valence', 'loudness',
                  'acousticness', 'instrumentalness', 'liveness', 'speechiness', 'key',
                  'tempo', 'duration_ms']

    track_id = track.name

    results = spotify_call(spotify.audio_features, [
                           track_id], caller="get_track_features")[0]

    features = pd.Series(results)
    features = features[their_keys]
    features.index = desired_features

    return features


def get_album_id(album, artist):
    album = album.lower()
    artist = artist.lower()
    lim = 5
    album_info = {}
    try:
        while lim < 100:

            # results = spotify_call(spotify.search, q=album, type='album',

            results = spotify_call(spotify.search,
                                   func_kwargs={"q": album, "type": 'album',
                                                'limit': lim},
                                   caller="get_album_id")

            #results = spotify.search(q=album, type='album', limit=lim)
            items = results['albums']['items']
            for item in items:
                artists = []
                for i in range(len(item['artists'])):
                    artists.append(item['artists'][i]['name'].lower())
                album_info['artists'] = artists
                # print(f"artists: {artists}, album: {item['name'].lower()}, album_id: {item['id']}")
                if artist in artists and album == item['name'].lower():
                    return item['id']
            lim *= 5
    except:
        return None
    return None


def get_album_features(spotify, album_id):
    # Get album tracklist from album id

    tracks = spotify_call(spotify.album_tracks, album_id,
                          caller="get_album_features")

    # Add new features to album features dict
    track_ids = []

    for track in tracks['items']:
        track_ids.append(track['id'])

    album_features = spotify_call(spotify.audio_features,
                                  track_ids, caller="get_track_features")

    their_keys = ['energy', 'danceability', 'valence', 'loudness',
                  'acousticness', 'instrumentalness', 'liveness', 'speechiness', 'key',
                  'tempo', 'duration_ms']

    # get attributes for ablum into a Frame
    album_features = pd.DataFrame(album_features, columns=their_keys)
    album_features.columns = desired_features

    # Get averages of attributes for whole ablum
    return album_features.sum(axis=0) / len(tracks['items'])


def estimate_remaining_time():
    global start_time

    end_time = time.time()
    time_spent = end_time - start_time
    seconds_per_album = time_spent / 100
    albums_left = total_albums - count
    seconds_left = seconds_per_album * albums_left
    hours_left = seconds_left / 3600
    print(f"--------- {hours_left} hours left!! ---------")
    start_time = time.time()


def process_row(row):

    global count

    # Estimate the amount of time remaining
    if count % 5 == 0:
        print(
            f"\n--------- {count}/{total_albums} albums done!! ({round(100*count/total_albums, 2)}%) ---------")
        estimate_remaining_time()
    count += 1

    album_features = pd.Series(index=['reviewid'] + desired_features)

    # Get the album id so we can search for album features
    album_id = get_album_id(row['title'], row['artist'])

    # If the album exists on Spotify
    if album_id is not None:
        album_features.loc[desired_features] = get_album_features(
            spotify, album_id)
        album_features['reviewid'] = row['reviewid']
        return album_features
    else:
        # return empty series of correct size
        return album_features


def main():
    # Read sqlite query results into a pandas DataFrame
    con = sqlite3.connect("../data/ethan_pitchfork.sqlite")
    df_pitchfork = pd.read_sql_query(
        "SELECT reviewid, title, artist from reviews", con)

    # Boot up the spotify client

    global count
    global total_albums
    total_albums = df_pitchfork.shape[0]
    df_features = pd.DataFrame(columns=['reviewid'] + desired_features)

    print(f"\nWe got {total_albums} albums to chug through!")

    # for x in np.split(df_pitchfork, np.arange(5, len(df_pitchfork), 5)):

    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv, 'ci:', longopts=["continue", "index="])

    start_index = 0

    for o, a in opts:
        if o in ("-c", "--continue"):
            past_df = pd.read_csv(outfile_csv)
            start_index = len(past_df)
            count = len(past_df)

        if o in ("-i", "--index"):
            start_index = int(a)
            count = int(a)

    # If we are starting from the top, recreate csv
    if start_index == 0:
        df_features.to_csv(outfile_csv)

    try:
        # Process albums in n chunks, adding to the csv
        n = 5
        for i in range(start_index, df_pitchfork.shape[0], n):
            df = df_pitchfork[i:i+n]
            df.apply(process_row, axis=1).to_csv(
                outfile_csv, header=False, mode='a')
    except:
        print(count)
        print(df.loc[count, "reviewid"])

    # Export dataframe to csv
    #df_features.to_csv(outfile_csv, index=False)

    # Close the database
    con.close()


if __name__ == '__main__':
    main()
