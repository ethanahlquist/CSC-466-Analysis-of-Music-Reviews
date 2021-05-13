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
    # Get album tracklist from album id
    results = spotify.album_tracks(album_id)
    api_calls += 1

    # Add new features to album features dict
    album_features = {}
    desired_features = ['Energy', 'Danceability', 'Happiness', 'Loudness', 
        'Acousticness', 'Instrumentalness', 'Liveness', 'Speechiness', 'Key', 
        'Tempo', 'Duration']
    for feature in desired_features:
        album_features[feature] = 0

    # Sum the attributes of each song together in album_features dict
    for track in results['items']:
        track_id = track['id']
        track_features, api_calls = get_track_features(spotify, track_id, api_calls)
        for key in track_features:
            album_features[key] += track_features[key]
    
    # Average the attributes in album_features dict
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

    count = 1
    api_calls = 0
    total_albums = df.shape[0]
    print(f"\nWe got {total_albums} albums to chug through!")
    start_time = time.time()
    for index, row in df.iterrows():

        if count == 6:
            break

        # Estimate the amount of time remaining
        if count % 100 == 0:
            end_time = time.time()
            time_spent = end_time - start_time
            seconds_per_album = time_spent / 100
            albums_left = total_albums - count
            seconds_left = seconds_per_album * albums_left
            hours_left = seconds_left / 3600
            print(f"\n--------- {count}/{total_albums} albums done!! ({round(100*count/total_albums, 2)}%) ---------")
            print(f"--------- {api_calls} api calls made! ---------")
            print(f"--------- {hours_left} hours left!! ---------")
            start_time = time.time()
            df.to_csv("spotify_and_pitchfork.csv", index=False)

        # Get the album id so we can search for album features
        album_id, api_calls = get_album_id(spotify, row['title'], row['artist'], api_calls)

        # If the album exists on Spotify
        if album_id is not None:
            album_features, api_calls = get_album_features(spotify, album_id, api_calls)
            for feature in desired_features:
                df.at[index, feature] = album_features[feature]

        count += 1

    # Export dataframe to csv
    df.to_csv('spotify_and_pitchfork.csv', index=False)

    # Close the database
    con.close()

if __name__ == '__main__':
    main()
