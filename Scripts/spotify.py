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

    simplified_tracks = []
    for item in tracks:
        track = item.get('track')  # Use .get to avoid KeyError if 'track' does not exist
        if track and track.get('artists'):  # Ensure 'track' and 'track['artists']' are not None
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

def check_song_exists(spotify_id):
    query = "SELECT EXISTS(SELECT 1 FROM songs WHERE spotify_id = %s)"
    cursor.execute(query, (spotify_id,))
    return cursor.fetchone()[0]


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


def get_artist_albums(artist_id):
    results = sp.artist_albums(artist_id)
    albums = results['items']
    while results['next']:
        results = sp.next(results)
        albums.extend(results['items'])
    return albums


def get_album_songs(album_id):
    results = sp.album_tracks(album_id)
    songs = results['items']
    while results['next']:
        results = sp.next(results)
        songs.extend(results['items'])
    return songs


def get_song_information_from_trackID(id):
    results = sp.track(id)
    return results


def populate_songs_with_username(user):
    try:
        for playlist in get_user_playlists(user):
            for track in get_playlist_tracks(playlist['uri']):
                if track:  # Ensure track is not None
                    spotify_id = track.get('song_id')
                    if spotify_id and not check_song_exists(spotify_id):  # Check if song does not exist
                        try:
                            artist_id = ensure_artist_exists(track)
                            print(f"Artist ID: {artist_id}")

                            genre_name = random.choice(genres)
                            genre_id = ensure_genre_exists(genre_name)
                            print(f"Genre ID: {genre_id}")

                            title = track['title']
                            album_name = track['album_name']
                            track_number = track['track_number']
                            runtime = track['runtime']
                            release_date = track['release_date']

                            song_id = insert_song(artist_id, spotify_id, title, album_name, track_number, runtime, release_date, genre_id)
                            print(f"Inserted song with ID: {song_id}")

                        except Exception as e:
                            print(f"An error occurred while processing track {spotify_id}: {e}")
                    else:
                        print(f"Skipping insertion for existing song with Spotify ID: {spotify_id}")

        connection.commit()
    finally:
        # Final clean-up
        if cursor:
            cursor.close()
        if connection:
            connection.close()




def populate_songs_with_artist(artist_uri):
    try:
        albums = get_artist_albums(artist_uri)
        for album in albums:
            try:
                songs = get_album_songs(album['id'])
                for song in songs:
                    try:
                        # Assume ensure_artist_exists, ensure_genre_exists, and insert_song are predefined functions
                        song_id = get_song_information_from_trackID(song['id'])
                        artist_id = ensure_artist_exists(song_id)
                        print(f"Artist ID: {artist_id}")
                        # Insert the song with all details
                        song_spotify_id = song['id']
                        title = song['name']
                        album_name = album['name']
                        track_number = song['track_number']
                        runtime = song['duration_ms']
                        release_date = album['release_date']

                        # Assume a list of genres is predefined
                        genre_name = random.choice(genres)
                        genre_id = ensure_genre_exists(genre_name)
                        print(f"Genre ID: {genre_id}")

                        artist_id = find_artist_by_spotify_id(artist_id)
                        song_id = insert_song(artist_id, song_spotify_id, title, album_name, track_number, runtime,
                                              release_date, genre_id)
                        print(f"Inserted song with ID: {song_id}")

                    except Exception as e:
                        print(f"An error occurred while processing song {song['id']}: {e}")

                # Commit after each album is processed successfully
                connection.commit()

            except Exception as e:
                print(f"An error occurred while processing album {album['id']}: {e}")

    except Exception as e:
        print(f"An error occurred while retrieving albums for artist {artist_id}: {e}")

    # Final clean-up outside the loop
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def get_album_id(artist_name, album_name):
    """
    Search for an album by the given artist and album name and return the album's Spotify ID.

    :param artist_name: The name of the artist.
    :param album_name: The name of the album.
    :return: The Spotify ID of the album.
    """
    query = f"artist:{artist_name} album:{album_name}"
    result = sp.search(q=query, type='album', limit=1)

    # Check if any albums were found
    if result['albums']['items']:
        # Return the ID of the first album found
        album_id = result['albums']['items'][0]['id']
        print(f"Album ID for '{album_name}' by '{artist_name}': {album_id}")
        return album_id
    else:
        print(f"No results found for album '{album_name}' by '{artist_name}'")
        return None


def get_album_id(artist_name, album_name):
    """
    Fetch the Spotify album ID based on the artist name and album name.
    """
    query = f"artist:{artist_name} album:{album_name}"
    result = sp.search(q=query, type='album', limit=1)
    if result['albums']['items']:
        return result['albums']['items'][0]['id']
    return None


def get_album_label(album_id):
    """
    Retrieve the label name for a given album ID from Spotify.
    """
    if album_id:
        album_details = sp.album(album_id)
        return album_details.get('label', None)
    return None


def update_database():
    """
    Update the Label and Album tables in the database with label information fetched from Spotify.
    """
    # Retrieve all albums without label information
    cursor.execute("SELECT artist_id, name FROM Album WHERE label_id IS NULL;")
    albums = cursor.fetchall()

    for artist_id, album_name in albums:
        # Get the artist's Spotify ID
        cursor.execute("SELECT spotify_id FROM Artist WHERE artist_id = %s;", (artist_id,))
        artist_spotify_id = cursor.fetchone()[0]

        # Get the artist's name using the Spotify ID
        artist_info = sp.artist(artist_spotify_id)
        artist_name = artist_info['name']

        # Get the album's Spotify ID and label
        album_id = get_album_id(artist_name, album_name)
        label_name = get_album_label(album_id)

        if label_name:
            # Check if the label already exists in the database
            cursor.execute("SELECT label_id FROM Label WHERE name = %s;", (label_name,))
            label_result = cursor.fetchone()

            if label_result:
                label_id = label_result[0]
            else:
                # Insert the new label into the Label table
                cursor.execute("INSERT INTO Label (name) VALUES (%s) RETURNING label_id;", (label_name,))
                label_id = cursor.fetchone()[0]
                connection.commit()

            # Update the Album table with the new label_id
            cursor.execute("UPDATE Album SET label_id = %s WHERE artist_id = %s AND name = %s;",
                           (label_id, artist_id, album_name))
            connection.commit()


username = 'spotify'
populate_songs_with_username(username)

# update_database()
