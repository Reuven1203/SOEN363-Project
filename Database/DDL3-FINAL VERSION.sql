-- DOMAINS

CREATE DOMAIN GenderDomain CHAR(1) CHECK(VALUE IN ('M', 'F', 'O'));

CREATE DOMAIN ReleaseDateDomain VARCHAR(100) CHECK(VALUE >= '1900-01-01');

CREATE DOMAIN SpotifyIDDomain VARCHAR(100) CHECK(VALUE ~ '^[a-zA-Z0-9]*$');

CREATE DOMAIN TrackNumberDomain INT CHECK(VALUE > 0);

-- TYPES

CREATE TYPE AlbumType AS (
    name VARCHAR(100),
    num_tracks INT,
    release_date DATE
);
CREATE TYPE ProducerType AS (
    name VARCHAR(100),
    gender CHAR(1),
    years_of_experience INT,
    nationality VARCHAR(100)
);
CREATE TYPE SongType AS (
    title VARCHAR(100),
    album_name VARCHAR(100),
    track_number INT,
    runtime INT,
    release_date DATE
);
CREATE TYPE ArtistType AS (
    name VARCHAR(100),
    gender CHAR(1),
    years_of_experience INT,
    nationality VARCHAR(100)
);
CREATE TYPE LabelType AS (
    name VARCHAR(100)
);


-- TABLES CREATION

CREATE TABLE People
(
    person_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL ,
    gender GenderDomain,
    years_of_experience INT,
    nationality VARCHAR(100)
);

CREATE TABLE Artist
(
    artist_id SERIAL PRIMARY KEY,
    person_id INT UNIQUE NOT NULL,
    spotify_id SpotifyIDDomain UNIQUE NOT NULL,
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
    spotify_id SpotifyIDDomain UNIQUE NOT NULL,
    music_brainz_id VARCHAR(100),
    title VARCHAR(100) NOT NULL ,
    album_name VARCHAR(100),
    track_number TrackNumberDomain,
    runtime INT NOT NULL,
    release_date ReleaseDateDomain NOT NULL,
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
    release_date ReleaseDateDomain,
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


-- VIEWS
CREATE VIEW SongWithArtist AS
SELECT s.song_id, s.title, a.name AS artist_name
FROM Songs s
INNER JOIN Artist ar ON s.artist_id = ar.artist_id
INNER JOIN People a ON ar.person_id = a.person_id;

CREATE VIEW AlbumDetails AS
SELECT a.name AS album_name, a.num_tracks, a.release_date, p.name AS artist_name
FROM Album a
INNER JOIN Artist ar ON a.artist_id = ar.artist_id
INNER JOIN People p ON ar.person_id = p.person_id;

CREATE VIEW LabelArtistAlbumView AS
SELECT l.name AS label_name, p.name AS artist_name, a.name AS album_name, a.release_date
FROM Label l
JOIN Album a ON l.label_id = a.label_id
JOIN Artist ar ON a.artist_id = ar.artist_id
JOIN People p ON ar.person_id = p.person_id;


-- Example of a VIEW with Hard-Coded Criteria
CREATE VIEW AmericanArtists AS
SELECT Artist.artist_id, Artist.spotify_id, People.person_id, People.name, People.gender, People.years_of_experience, People.nationality
FROM Artist
JOIN People ON Artist.person_id = People.person_id
WHERE nationality = 'American';
