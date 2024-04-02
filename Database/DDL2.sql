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


-- Example of a VIEW with Hard-Coded Criteria
CREATE VIEW AmericanArtists AS
SELECT Artist.artist_id, Artist.spotify_id, People.person_id, People.name, People.gender, People.years_of_experience, People.nationality
FROM Artist
JOIN People ON Artist.person_id = People.person_id
WHERE nationality = 'American';


-- Domains

CREATE DOMAIN GenderDomain CHAR(1) CHECK(VALUE IN ('M', 'F', 'O'));

CREATE DOMAIN ReleaseDateDomain VARCHAR(100) CHECK(VALUE >= '1900-01-01');

CREATE DOMAIN SpotifyIDDomain VARCHAR(100) CHECK(VALUE ~ '^[a-zA-Z0-9]*$');

CREATE DOMAIN TrackNumberDomain INT CHECK(VALUE > 0);

-- Types

