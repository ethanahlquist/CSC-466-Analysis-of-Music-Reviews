import pandas as pd
import time
import sqlite3
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from requests.exceptions import ReadTimeout
# Spotify Auth Token: BQBbnJKCwwoNfE2ezbZaeLDfYKQQikPOp96FmU2vrbCYe64KZ907Oga0C80
client_id = '98bd16fb0f01483aace2c3bf79f041a0'
client_secret = '8891a8f08d304b2fb1863d1c1df873c5'
# export SPOTIPY_CLIENT_ID='98bd16fb0f01483aace2c3bf79f041a0'
# export SPOTIPY_CLIENT_SECRET='8891a8f08d304b2fb1863d1c1df873c5'

def get_track_id(spotify, title, artist, api_calls):
    title = title.lower()
    artist = artist.lower()
    api_calls += 1
    results = spotify.search(q=title, type='track')
    items = results['tracks']['items']
    track_info = {}
    for item in items:
        artists = []
        for i in range(len(item['artists'])):
            artists.append(item['artists'][i]['name'].lower())
        track_info['artists'] = artists
        # print(f"artists: {artists}, track: {item['name'].lower()}, track_id: {item['id']}")
        if artist in artists and title == item['name'].lower():
            return item['id'], api_calls
    return None, api_calls

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
        

def get_album_tracklist(spotify, album_id, api_calls):
    results = spotify.album_tracks(album_id)
    api_calls += 1
    track_ids = []
    for track in results:
        track_ids.append(track['id'])
    return track_ids, api_calls

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

# Read sqlite query results into a pandas DataFrame
con = sqlite3.connect("pitchfork.sqlite")
df = pd.read_sql_query("SELECT * from reviews", con)

# Boot up the spotify client
spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(), requests_timeout=10, retries=10)

# Search for Little Dragon - Lover Chanting - Edit
# track = 'Freelance'
# artist = 'Toro y Moi'
# print(track, artist)
# track_id = get_track_id(spotify, track, artist)
# print(track_id)
# track_features = get_track_features(spotify, track_id)
# print(track_features)
# print()

# Search for Little Dragon - Lover Chanting - Edit
# album = 'Outer Peace'
# artist = 'Toro y Moi'
# album_id = get_album_id(spotify, album, artist)
# album_features = get_album_features(spotify, album_id)
# print(album_features)

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

    # print(f"{row['artist']} - {row['title']}")

    # Get the album id so we can search for album features
    album_id, api_calls = get_album_id(spotify, row['title'], row['artist'], api_calls)

    # If the album exists on Spotify
    if album_id is not None:
        album_features, api_calls = get_album_features(spotify, album_id, api_calls)
        for feature in desired_features:
            df.at[index, feature] = album_features[feature]

    count += 1

# Verify that result of SQL query is stored in the dataframe
print(df.head())

# Export dataframe to csv
df.head().to_csv('pitchfork_spotify.csv', index=False)

# Close the database
con.close()
