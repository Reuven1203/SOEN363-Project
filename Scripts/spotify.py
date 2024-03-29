# This is a script to populate a database with Spotify data

import spotipy
import os
from dotenv import load_dotenv
import psycopg2

from spotipy import SpotifyClientCredentials

# Set up the Spotify API
load_dotenv()
client_id = os.environ['SPOTIFY_CLIENT_ID']
client_secret = os.environ['SPOTIFY_CLIENT_SECRET']
db_name = os.environ['DB_NAME']
db_user = os.environ['DB_USER']
db_password = os.environ['DB_PASSWORD']
db_host = os.environ['DB_HOST']

sp = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))


# Get tracks from a playlist url

def get_playlist_tracks(uri):
    results = sp.playlist_items(uri)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    # Extracting only the desired information: song ID, song name, and artist(s) but only if there's exactly one artist
    simplified_tracks = []
    for item in tracks:
        track = item['track']
        if len(track['artists']) == 1:  # Check if there's exactly one artist
            track_info = {
                'song_id': track['id'],
                'song_name': track['name'],
                'album_name': track['album']['name'],
                'artists': [artist['name'] for artist in track['artists']]
            }
            simplified_tracks.append(track_info)

    return simplified_tracks



playlist_uri = 'https://open.spotify.com/playlist/37i9dQZF1DWY4xHQp97fN6'
for track in get_playlist_tracks(playlist_uri):
    print(f"ID: {track['song_id']}, Song: {track['song_name']}, Artists: {', '.join(track['artists'])}, Album: {track['album_name']}")

with open('spotify_data.csv', 'w') as file:
    file.write("ID,Song,Artists,Album\n")
    for track in get_playlist_tracks(playlist_uri):
        file.write(f"{track['song_id']},{track['song_name']},{', '.join(track['artists'])},{track['album_name']}\n")

try:
    connection = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host
    )
    print("Connection to the database was successful")
except Exception as e:
    print(f"An error occurred: {e}")




