import requests
import time

# change this to update the records and add the music_brains_id

def get_music_brainz_id(recording_name, artist_name):
    query = f'artist:{artist_name}%20AND%20recording:{recording_name}'
    response = requests.get(f'https://musicbrainz.org/ws/2/recording?query={query}&fmt=json')
    response.raise_for_status()
    data = response.json()
    if data['count'] == 0:
        return None
    return data['recordings'][0]['id']

with(open('spotify_data.csv', 'r')) as file:
    for line in file:
        song_id, song_name, artist_name = line.strip().split(',')
        music_brainz_id = get_music_brainz_id(song_name, artist_name)
        time.sleep(1.2)
        if music_brainz_id:
            print(f"Song: {song_name}, Artist: {artist_name}, MusicBrainz ID: {music_brainz_id}")
        else:
            print(f"Song: {song_name}, Artist: {artist_name}, MusicBrainz ID not found")