# This is a script to populate a database with Spotify data

import spotipy

from spotipy import SpotifyClientCredentials

# Set up the Spotify API
# client_id = os.environ['SPOTIFY_CLIENT_ID']
client_id = 'd8c4c8c178e14d8dbfd607f19eacbd57'
client_secret = 'bdf5a7bf00604be8914edf740177d765'

sp = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))


# Get tracks from a playlist url

def get_playlist_tracks(uri):
    results = sp.playlist_items(uri)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    # Extracting only the desired information: song ID, song name, and artist(s)
    simplified_tracks = []
    for item in tracks:
        track = item['track']
        track_info = {
            'song_id': track['id'],
            'song_name': track['name'],
            'artists': [artist['name'] for artist in track['artists']]
        }
        simplified_tracks.append(track_info)

    return simplified_tracks


playlist_uri = '5gmYyeyFR3X6f4TfCYWrz8'
for track in get_playlist_tracks(playlist_uri):
    print(f"ID: {track['song_id']}, Song: {track['song_name']}, Artists: {', '.join(track['artists'])}")

