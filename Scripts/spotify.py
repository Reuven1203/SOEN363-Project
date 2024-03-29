# This is a script to populate a database with Spotify data

import spotipy
import os
from dotenv import load_dotenv
import psycopg2
import random

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
                'title': track['name'],
                'album_name': track['album']['name'],
                'artists': [artist['name'] for artist in track['artists']],
                'artist_id': track['artists'][0]['id'],
                'track_number': track['track_number'],
                'runtime': track['duration_ms'],
                'release_date': track['album']['release_date'],
            }
            simplified_tracks.append(track_info)
    return simplified_tracks

playlist_uri = 'https://open.spotify.com/playlist/0kSX5DGE1vONa5udHz8BWi?si=1b36c13ce8c14857'

genders = ["M", "F", "O"]
nationalities = [
    "American", "Argentinian", "Australian", "Brazilian", "Canadian",
    "Chinese", "Danish", "Egyptian", "Finnish", "French", "German",
    "Greek", "Indian", "Italian", "Japanese", "Mexican", "Nigerian",
    "Norwegian", "Polish", "Russian", "South African", "Spanish",
    "Swedish", "Thai", "Turkish", "British", "Vietnamese"
]
genres = [
    'Grime','Techno','Heavy Metal','Classical','Pop','House',
    'Experimental', 'Electronic','Hip Hop','Disco','Rock',
    'Blues','Reggae','Soul','Indie', 'Opera', 'Dubstep',
    'World','Ambient', 'Jazz', 'Punk', 'Ska', 'Trance',
     'Folk', 'Funk', 'Country', 'R&B', 'Drum and Bass',
     'New Age', 'Gospel'
]

connection = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host
    )
# connection.autocommit = False

cursor = connection.cursor()

def insert_person(name, gender, years, nationality):
    query = """
        INSERT INTO people (name, gender, years_of_experience, nationality)
        VALUES (%s, %s, %s, %s);
        """
    cursor.execute(query, (name, gender, years, nationality))
    connection.commit()
    person_id = cursor.fetchone()[0]
    return person_id

def insert_artist(person_id, spotify_id):
    query = """
        INSERT INTO artist (person_id, spotify_id)
        VALUES (%s, %s);
        """
    cursor.execute(query, (person_id, spotify_id))
    connection.commit()
    artist_id = cursor.fetchone()[0]
    return artist_id

def insert_genre(name):
    query = """
        INSERT INTO genre (name)
        VALUES (%s);
        """
    cursor.execute(query, (name,))
    connection.commit()
    genre_id = cursor.fetchone()[0]
    return genre_id

def insert_song(artist_id, spotify_id, title, album_name, track_number, runtime, release_date, genre_id):
    query = """
        INSERT INTO songs (artist_id, spotify_id, title, album_name, track_number, runtime, release_date, genre_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
    cursor.execute(query, (artist_id, spotify_id, title, album_name, track_number, runtime, release_date, genre_id))
    connection.commit()
    song_id = cursor.fetchone()[0]
    return song_id

try:
    # For every song create a person, artist, genre, and song record
    for track in get_playlist_tracks(playlist_uri):

        # Insert the person
        person_name = track['artists'][0]
        person_gender = random.choice(genders)
        person_years = random.randint(0, 50)
        person_nationality = random.choice(nationalities)
        person_id = insert_person(person_name, person_gender, person_years, person_nationality)

        print(f"Inserted person with ID: {person_id}")

        # Insert the artist
        artist_person_id = person_id
        artist_spotify_id = track['artist_id']
        artist_id = insert_artist(artist_person_id, artist_spotify_id)

        print(f"Inserted artist with ID: {artist_id}")

        # Insert the genre
        name = random.choice(genres)
        genre_id = insert_genre(name)

        print(f"Inserted genre with ID: {genre_id}")

        # Insert the song
        artist_id = track['artist_id']
        song_spotify_id = track['id']
        title = track['name']
        album_name = track['album_name']
        track_number = track['track_number']
        runtime = track['duration_ms']
        release_date = track['release_date']
        genre_id = genre_id
        insert_song(artist_id, song_spotify_id, title, album_name, track_number, runtime, release_date, genre_id)

        print(f"Inserted song with ID: {cursor.lastrowid}")

    # connection.commit()

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