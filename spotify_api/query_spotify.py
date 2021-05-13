import pandas as pd
import time
import sqlite3
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from requests.exceptions import ReadTimeout
# Spotify Auth Token: BQBbnJKCwwoNfE2ezbZaeLDfYKQQikPOp96FmU2vrbCYe64KZ907Oga0C80

''' YOU NEED TO COPY PASTE THESE TWO COMMENTS INTO YOUR TERMINAL BEFORE RUNNING (without the # of course)'''
# export SPOTIPY_CLIENT_ID='98bd16fb0f01483aace2c3bf79f041a0'
# export SPOTIPY_CLIENT_SECRET='8891a8f08d304b2fb1863d1c1df873c5'

def get_track_features(spotify, track_id, api_calls):
    desired_features = ['Energy', 'Danceability', 'Valence', 'Loudness', 
    'Acousticness', 'Instrumentalness', 'Liveness', 'Speechiness', 'Key', 
    'Tempo', 'Duration']

    results = spotify.audio_features([track_id])
    api_calls += 1

    track_features = {}
    for feature in desired_features:
        if feature == 'Valence':
            track_features['Happiness'] = results[0][feature.lower()]
        elif feature == 'Duration':
            track_features[feature] = results[0]['duration_ms']
        else:
            track_features[feature] = results[0][feature.lower()]

    return track_features, api_calls

def get_album_id(spotify, album, artist, api_calls):
    album = album.lower()
    artist = artist.lower()
    lim = 5
    album_info = {}
    try:
        while lim < 100:
            results = spotify.search(q=album, type='album', limit=lim)
            api_calls += 1
            items = results['albums']['items']
            for item in items:
                artists = []
                for i in range(len(item['artists'])):
                    artists.append(item['artists'][i]['name'].lower())
                album_info['artists'] = artists
                # print(f"artists: {artists}, album: {item['name'].lower()}, album_id: {item['id']}")
                if artist in artists and album == item['name'].lower():
                    return item['id'], api_calls
            lim *= 5
    except:
        return None, api_calls
    return None, api_calls

def get_album_features(spotify, album_id, api_calls):
    results = spotify.album_tracks(album_id)
    api_calls += 1
    album_features = {}
    is_init = False
    
    # Sum the attributes
    for track in results['items']:
        track_id = track['id']
        track_features, api_calls = get_track_features(spotify, track_id, api_calls)
        for key in track_features:
            if is_init == False:
                album_features[key] = track_features[key]
            else:
                album_features[key] += track_features[key]
    
    # Average the attributes
    for key in album_features:
        album_features[key] = album_features[key] / len(results['items'])

    return album_features, api_calls

def main():
    # Read sqlite query results into a pandas DataFrame
    con = sqlite3.connect("pitchfork.sqlite")
    df = pd.read_sql_query("SELECT * from reviews", con)

    # Boot up the spotify client
    spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(), requests_timeout=10, retries=10)

    # Add new columns to dataframe
    desired_features = ['Energy', 'Danceability', 'Happiness', 'Loudness', 
        'Acousticness', 'Instrumentalness', 'Liveness', 'Speechiness', 'Key', 
        'Tempo', 'Duration']
    df[desired_features] = ''

    # Initialize counters
    album_count = 1 # used to count number of albums we've gone through
    api_calls = 0   # counts the total number of api calls so far
    total_albums = df.shape[0] # total number of rows/albums in pitchfork data

    # Get started with the data querying
    print(f"\nWe got {total_albums} albums to chug through!")
    start_time = time.time()

    # This loop is where all of the api calls stem from
    for index, row in df.iterrows():
        # Estimate the amount of time remaining
        if album_count % 100 == 0:
            end_time = time.time()
            time_spent = end_time - start_time
            seconds_per_album = time_spent / 100
            albums_left = total_albums - album_count
            seconds_left = seconds_per_album * albums_left
            hours_left = seconds_left / 3600
            # Print useful info
            print(f"\n--------- {album_count}/{total_albums} albums done!! ({round(100*album_count/total_albums, 2)}%) ---------")
            print(f"--------- {api_calls} api calls made! ---------")
            print(f"--------- {hours_left} hours left!! ---------")
            start_time = time.time()
            # Save the df to csv every 100 albums just in case a crash happens
            df.to_csv("spotify_and_pitchfork.csv", index=False)

        # Get the album id so we can search for album features
        album_id, api_calls = get_album_id(spotify, row['title'], row['artist'], api_calls) # returns None if album not on Spotify

        # If the album exists on Spotify
        if album_id is not None:
            album_features, api_calls = get_album_features(spotify, album_id, api_calls)
            for feature in desired_features:
                df.at[index, feature] = album_features[feature]

        # Increment row/album counter
        album_count += 1

    # Data gathering finished!!!

    # Now export dataframe to csv
    df.to_csv('pitchfork_spotify.csv', index=False)

    # Close the database
    con.close()

if __name__ == '__main__':
    main()
