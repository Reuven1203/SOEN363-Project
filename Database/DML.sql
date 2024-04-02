-- Basic SELECT with Simple WHERE Clause
SELECT *
FROM People
WHERE gender = 'M';

-- Basic SELECT with Simple GROUP BY Clause without HAVING Clause
SELECT nationality, COUNT(*) AS number_of_people
FROM People
GROUP BY nationality;

-- Basic SELECT with Simple GROUP BY Clause with HAVING Clause
SELECT nationality, COUNT(*) AS number_of_people
FROM People
GROUP BY nationality
HAVING COUNT(*) > 5;

-- A Simple JOIN SELECT Query using Cartesian Product and WHERE Clause
SELECT *
FROM Artist, People
WHERE Artist.person_id = People.person_id;

-- A Simple JOIN SELECT Query using JOIN ON
SELECT *
FROM Artist
JOIN People ON Artist.person_id = People.person_id;

-- Different JOIN Types

-- INNER JOIN
SELECT *
FROM Artist
INNER JOIN People ON Artist.person_id = People.person_id;

-- LEFT OUTER JOIN
SELECT *
FROM Artist
LEFT JOIN People ON Artist.person_id = People.person_id;

-- RIGHT OUTER JOIN
SELECT *
FROM Artist
RIGHT JOIN People ON Artist.person_id = People.person_id;

-- FULL OUTER JOIN
SELECT *
FROM Artist
FULL OUTER JOIN People ON Artist.person_id = People.person_id;


-- Examples of Correlated Queries

-- Example 1
SELECT P.name, (SELECT COUNT(*) FROM Songs S WHERE S.artist_id = A.artist_id) AS number_of_songs
FROM Artist A
JOIN People P ON A.person_id = P.person_id;

-- Example 2
SELECT name
FROM People P
WHERE EXISTS (SELECT 1 FROM Artist A WHERE A.person_id = P.person_id);

-- Set Operations WITH Set Operations

-- INTERSECT
-- Using INTERSECT
SELECT title FROM Songs WHERE genre_id = (SELECT genre_id FROM Genre WHERE name = 'Pop')
INTERSECT
SELECT title FROM Songs WHERE genre_id = (SELECT genre_id FROM Genre WHERE name = 'Rock');

-- Without using INTERSECT
SELECT DISTINCT s1.title
FROM Songs s1
JOIN Genre g1 ON s1.genre_id = g1.genre_id AND g1.name = 'Pop'
JOIN Songs s2 ON s1.title = s2.title
JOIN Genre g2 ON s2.genre_id = g2.genre_id AND g2.name = 'Rock';

-- UNION
-- Using UNION
SELECT title FROM Songs WHERE genre_id = (SELECT genre_id FROM Genre WHERE name = 'Pop')
UNION
SELECT title FROM Songs WHERE genre_id = (SELECT genre_id FROM Genre WHERE name = 'Jazz');

-- Without Using UNION
SELECT DISTINCT title
FROM Songs
WHERE genre_id IN (SELECT genre_id FROM Genre WHERE name IN ('Pop', 'Jazz'));

-- EXCEPT
-- Using EXCEPT
SELECT title FROM Songs WHERE genre_id = (SELECT genre_id FROM Genre WHERE name = 'Electronic')
EXCEPT
SELECT title FROM Songs WHERE genre_id = (SELECT genre_id FROM Genre WHERE name = 'Hip-Hop');

-- Without Using EXCEPT Using NOT IN
SELECT title
FROM Songs
WHERE genre_id = (SELECT genre_id FROM Genre WHERE name = 'Electronic')
  AND title NOT IN (
      SELECT title FROM Songs WHERE genre_id = (SELECT genre_id FROM Genre WHERE name = 'Hip-Hop')
  );

-- WIthout Using EXCEPT Using NOT EXISTS
SELECT s1.title
FROM Songs s1
WHERE s1.genre_id = (SELECT genre_id FROM Genre WHERE name = 'Electronic')
  AND NOT EXISTS (
      SELECT 1
      FROM Songs s2
      JOIN Genre g ON s2.genre_id = g.genre_id AND g.name = 'Hip-Hop'
      WHERE s1.title = s2.title
  );


-- Division Operator
-- Using NOT IN
SELECT artist_id
FROM Songs
WHERE genre_id NOT IN (SELECT genre_id FROM Genre WHERE name = 'Pop');

-- Correlated nested query using NOT EXISTS and EXCEPT
SELECT artist_id
FROM Songs S1
WHERE NOT EXISTS (
    SELECT genre_id FROM Genre WHERE name = 'Pop'
    EXCEPT
    SELECT S2.genre_id FROM Songs S2 WHERE S2.artist_id = S1.artist_id
);

-- Queries Demonstrating Covering/Overlapping Constraints
-- Overlapping Constraint
-- This query spots overlaps by detecting songs by the same artist with the same release dates.
SELECT s1.artist_id, s1.title AS song1, s2.title AS song2, s1.release_date
FROM Songs s1
JOIN Songs s2 ON s1.artist_id = s2.artist_id AND s1.song_id != s2.song_id
WHERE s1.release_date = s2.release_date
ORDER BY s1.artist_id, s1.release_date;

-- Covering Constraint
-- Since all artists are also people then it is a covering constraint. This will return all people/artists.
SELECT A.artist_id, A.spotify_id, P.name, P.gender, P.nationality
FROM Artist A
JOIN People P ON A.person_id = P.person_id;
