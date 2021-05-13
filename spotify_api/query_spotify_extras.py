''' 
Left over code from query_spotify that isn't used for anything anymore.
I just want to keep it for reference.
'''

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

def get_album_tracklist(spotify, album_id, api_calls):
    results = spotify.album_tracks(album_id)
    api_calls += 1
    track_ids = []
    for track in results:
        track_ids.append(track['id'])
    return track_ids, api_calls

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