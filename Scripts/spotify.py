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


def get_user_playlists(username):
    playlists = sp.user_playlists(username)
    # return just the playlists uri and name
    return [{'uri': playlist['uri'], 'name': playlist['name']} for playlist in playlists['items']]


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


# playlist_uri = 'https://open.spotify.com/playlist/0kSX5DGE1vONa5udHz8BWi?si=1b36c13ce8c14857'

genders = ["M", "F", "O"]
nationalities = [
    "American", "Argentinian", "Australian", "Brazilian", "Canadian",
    "Chinese", "Danish", "Egyptian", "Finnish", "French", "German",
    "Greek", "Indian", "Italian", "Japanese", "Mexican", "Nigerian",
    "Norwegian", "Polish", "Russian", "South African", "Spanish",
    "Swedish", "Thai", "Turkish", "British", "Vietnamese"
]
genres = [
    'Grime', 'Techno', 'Heavy Metal', 'Classical', 'Pop', 'House',
    'Experimental', 'Electronic', 'Hip Hop', 'Disco', 'Rock',
    'Blues', 'Reggae', 'Soul', 'Indie', 'Opera', 'Dubstep',
    'World', 'Ambient', 'Jazz', 'Punk', 'Ska', 'Trance',
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


# Inserting data into the database

def insert_person(name, gender, years, nationality):
    query = """
        INSERT INTO people (name, gender, years_of_experience, nationality)
        VALUES (%s, %s, %s, %s)
        RETURNING person_id;
        """
    cursor.execute(query, (name, gender, years, nationality))
    # Get the ID of the person that was just inserted
    person_id = cursor.fetchone()[0]
    return person_id


def insert_artist(person_id, spotify_id):
    query = """
        INSERT INTO artist (person_id, spotify_id)
        VALUES (%s, %s)
        RETURNING artist_id;
        """
    cursor.execute(query, (person_id, spotify_id))
    artist_id = cursor.fetchone()[0]
    return artist_id


def insert_genre(name):
    query = """
        INSERT INTO genre (name)
        VALUES (%s)
        RETURNING genre_id;
        """
    cursor.execute(query, (name,))
    genre_id = cursor.fetchone()[0]
    return genre_id


def insert_song(artist_id, spotify_id, title, album_name, track_number, runtime, release_date, genre_id):
    query = """
        INSERT INTO songs (artist_id, spotify_id, title, album_name, track_number, runtime, release_date, genre_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING song_id;
        """
    cursor.execute(query, (artist_id, spotify_id, title, album_name, track_number, runtime, release_date, genre_id))
    song_id = cursor.fetchone()[0]
    return song_id


# Checking if records already exist
def find_artist_by_spotify_id(spotify_id):
    query = """
        SELECT artist_id FROM Artist WHERE spotify_id = %s;
    """
    cursor.execute(query, (spotify_id,))
    result = cursor.fetchone()
    return result[0] if result else None


def ensure_artist_exists(track):
    artist_spotify_id = track['artist_id']
    existing_artist_id = find_artist_by_spotify_id(artist_spotify_id)
    if existing_artist_id is not None:
        return existing_artist_id
    else:
        # Insert the person
        person_name = track['artists'][0]
        person_gender = random.choice(genders)
        person_years = random.randint(0, 50)
        person_nationality = random.choice(nationalities)
        person_id = insert_person(person_name, person_gender, person_years, person_nationality)

        # Insert the artist with the new person_id
        artist_id = insert_artist(person_id, artist_spotify_id)
        return artist_id


def find_genre_by_name(genre_name):
    query = """
        SELECT genre_id FROM Genre WHERE name = %s;
    """
    cursor.execute(query, (genre_name,))
    result = cursor.fetchone()
    return result[0] if result else None


def ensure_genre_exists(genre_name):
    existing_genre_id = find_genre_by_name(genre_name)
    if existing_genre_id is not None:
        return existing_genre_id
    else:
        return insert_genre(genre_name)

user = 'reuven1203'
for playlist in get_user_playlists(user):
    # For every song create a person, artist, genre, and song record
    for track in get_playlist_tracks(playlist['uri']):

        try:
            artist_id = ensure_artist_exists(track)
            print(f"Artist ID: {artist_id}")

            # Check or insert genre
            genre_name = random.choice(genres)
            genre_id = ensure_genre_exists(genre_name)
            print(f"Genre ID: {genre_id}")

            # Insert the song with all details
            song_spotify_id = track['song_id']
            title = track['title']
            album_name = track['album_name']
            track_number = track['track_number']
            runtime = track['runtime']
            release_date = track['release_date']

            song_id = insert_song(artist_id, song_spotify_id, title, album_name, track_number, runtime,
                                  release_date, genre_id)
            print(f"Inserted song with ID: {song_id}")

        except Exception as e:
            print(f"An error occurred while processing track {track['song_id']}: {e}")

    connection.commit()

# Final clean-up outside the loop
if cursor:
    cursor.close()
if connection:
    connection.close()


