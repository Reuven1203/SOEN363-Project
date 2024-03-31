CREATE TABLE People
(
    person_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL ,
    gender CHAR(1),
    years_of_experience INT,
    nationality VARCHAR(100)
);

CREATE TABLE Artist
(
    artist_id SERIAL PRIMARY KEY,
    person_id INT UNIQUE NOT NULL,
    spotify_id VARCHAR(100) UNIQUE NOT NULL,
    FOREIGN KEY (person_id) REFERENCES People(person_id)
);


CREATE TABLE Genre
(
    genre_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE Songs
(
    artist_id INT,
    song_id SERIAL PRIMARY KEY,
    spotify_id VARCHAR(100) NOT NULL,
    music_brainz_id VARCHAR(100),
    title VARCHAR(100) NOT NULL ,
    album_name VARCHAR(100),
    track_number INT,
    runtime INT NOT NULL,
    release_date VARCHAR(100) NOT NULL,
    genre_id INT,
    FOREIGN KEY (genre_id) REFERENCES Genre(genre_id),
    FOREIGN KEY (artist_id) REFERENCES Artist(artist_id)

);

CREATE TABLE Label
(
    label_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE Producer
(
    producer_id SERIAL PRIMARY KEY,
    person_id INT,
    label_id INT,
    FOREIGN KEY (person_id) REFERENCES People(person_id),
    FOREIGN KEY (label_id) REFERENCES Label(label_id)
);

CREATE TABLE Album
(
    artist_id INT,
    name VARCHAR(100),
    num_tracks INT,
    release_date DATE,
    label_id INT,
    FOREIGN KEY (artist_id) REFERENCES Artist(artist_id),
    FOREIGN KEY (label_id) REFERENCES Label(label_id),
    PRIMARY KEY (artist_id, name)
);
CREATE OR REPLACE FUNCTION create_album_if_not_exists()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if the album already exists
    IF NOT EXISTS (SELECT 1 FROM Album WHERE artist_id = NEW.artist_id AND name = NEW.album_name) THEN
        -- Insert the new album if it doesn't exist
        INSERT INTO Album (artist_id, name, num_tracks, release_date, label_id)
        VALUES (NEW.artist_id, NEW.album_name, NULL, NULL, NULL);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_create_album_after_song_insert
AFTER INSERT ON Songs
FOR EACH ROW
EXECUTE FUNCTION create_album_if_not_exists();