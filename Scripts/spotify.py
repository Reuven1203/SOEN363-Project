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

playlist_uri = 'https://open.spotify.com/playlist/6jTSS2KyX9EEcSwJkJSHao?si=53ca44c6b8b04247'
for track in get_playlist_tracks(playlist_uri):
    print(f"ID: {track['song_id']}, Song: {track['song_name']}, Artists: {', '.join(track['artists'])}, Album: {track['album_name']}")

genders = ["M", "F", "O"]
nationalities = [
    "American", "Argentinian", "Australian", "Brazilian", "Canadian",
    "Chinese", "Danish", "Egyptian", "Finnish", "French", "German",
    "Greek", "Indian", "Italian", "Japanese", "Mexican", "Nigerian",
    "Norwegian", "Polish", "Russian", "South African", "Spanish",
    "Swedish", "Thai", "Turkish", "British", "Vietnamese"
]


connection = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host
    )
connection.autocommit = False

cursor = connection.cursor()

try:
    # For every song create a person, artist, genre, and song record

    connection.commit()

    print("Connection to the database was successful")
except Exception as e:

    if connection:
        connection.rollback()
    print(f"An error occurred: {e}")
finally:
    if cursor:
        cursor.close()
    if connection:
        connection.close()

# CREATE TABLE People
# (
#     person_id SERIAL PRIMARY KEY,
#     name VARCHAR(100) NOT NULL ,
#     gender CHAR(1),
#     years_of_experience INT,
#     nationality VARCHAR(100)
# );

# CREATE TABLE Artist
# (
#     artist_id SERIAL PRIMARY KEY,
#     person_id INT,
#     spotify_id VARCHAR(100),
#     FOREIGN KEY (person_id) REFERENCES People(person_id)
# );
#

# CREATE TABLE Genre
# (
#     genre_id SERIAL PRIMARY KEY,
#     name VARCHAR(100)
# );

# CREATE TABLE Songs
# (
#     artist_id INT, -- get this from the artist table based on the artist name
#     song_id SERIAL PRIMARY KEY,
#     spotify_id VARCHAR(100), -- id
#     music_brainz_id VARCHAR(100), --(update running the music_brainz script)
#     title VARCHAR(100) NOT NULL , -- name
#     album_name VARCHAR(100), -- album.name
#     track_number INT, --track_number
#     runtime INT NOT NULL, -- duration_ms
#     release_date DATE, --release_date
#     genre_id INT, --(random from the existing genres)
#     FOREIGN KEY (genre_id) REFERENCES Genre(genre_id),
#     FOREIGN KEY (artist_id) REFERENCES Artist(artist_id)
#
# );


# DO THIS AFTER THE CREATION

# CREATE TABLE Label
# (
#     label_id SERIAL PRIMARY KEY,
#     name VARCHAR(100) NOT NULL
# );

# CREATE TABLE Producer
# (
#     producer_id SERIAL PRIMARY KEY,
#     person_id INT,
#     label_id INT,
#     FOREIGN KEY (person_id) REFERENCES People(person_id),
#     FOREIGN KEY (label_id) REFERENCES Label(label_id)
# );

# First iterate over artists in the songs array, create the artist records,
# Iterate create the genre records,
# then iterate again and create the songs in the same order,
# Then create the songs and refer to the artist_id and genre_id


# Create the artists
# Create the songs
# Verify that the album trigger worked
