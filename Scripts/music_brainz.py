import requests
import psycopg2
import os
from dotenv import load_dotenv
import time

# change this to update the records and add the music_brains_id
load_dotenv()

db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')

connection = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host
    )
# connection.autocommit = False

cursor = connection.cursor()

def get_music_brainz_id(recording_name, artist_name):
    query = f'artist:{artist_name}%20AND%20recording:{recording_name}'
    response = requests.get(f'https://musicbrainz.org/ws/2/recording?query={query}&fmt=json')
    response.raise_for_status()
    data = response.json()
    if data['count'] == 0:
        return None
    return data['recordings'][0]['id']


def update_songs_with_music_brainz_id():
    cursor.execute("""
        SELECT s.song_id, s.title, p.name
        FROM Songs s
        JOIN Artist a ON s.artist_id = a.artist_id
        JOIN People p ON a.person_id = p.person_id
        WHERE s.music_brainz_id IS NULL
    """)
    songs = cursor.fetchall()

    for song_id, title, artist_name in songs:
        music_brainz_id = get_music_brainz_id(title, artist_name)

        if music_brainz_id:
            cursor.execute("""
                UPDATE Songs
                SET music_brainz_id = %s
                WHERE song_id = %s
            """, (music_brainz_id, song_id))
            connection.commit()
        time.sleep(1.2)

    cursor.close()
    connection.close()

update_songs_with_music_brainz_id()