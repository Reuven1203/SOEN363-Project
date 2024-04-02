-- Views

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

-- Domains

CREATE DOMAIN GenderDomain CHAR(1) CHECK(VALUE IN ('M', 'F', 'O'));

CREATE DOMAIN ReleaseDateDomain VARCHAR(100) CHECK(VALUE >= '1900-01-01');

CREATE DOMAIN SpotifyIDDomain VARCHAR(100) CHECK(VALUE ~ '^[a-zA-Z0-9]*$');

CREATE DOMAIN TrackNumberDomain INT CHECK(VALUE > 0);

-- Types

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
