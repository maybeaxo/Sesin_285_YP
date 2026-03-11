-- Normalized SQL schema for WARPOINT VR Kiosk
-- Compatible with PostgreSQL 15+ (uses GENERATED AS IDENTITY)

CREATE TABLE age_ratings (
  id            SERIAL PRIMARY KEY,
  label         VARCHAR(8) NOT NULL UNIQUE,
  numeric_value SMALLINT   NOT NULL CHECK (numeric_value BETWEEN 0 AND 21)
);

CREATE TABLE durations (
  id      SERIAL PRIMARY KEY,
  label   VARCHAR(32) NOT NULL UNIQUE,
  minutes INTEGER      NOT NULL CHECK (minutes >= 0)
);

CREATE TABLE genres (
  id   SERIAL PRIMARY KEY,
  name VARCHAR(64) NOT NULL UNIQUE
);

CREATE TABLE platforms (
  id   SERIAL PRIMARY KEY,
  name VARCHAR(32) NOT NULL UNIQUE
);

CREATE TABLE languages (
  id   SERIAL PRIMARY KEY,
  name VARCHAR(32) NOT NULL UNIQUE
);

CREATE TABLE features (
  id   SERIAL PRIMARY KEY,
  name VARCHAR(64) NOT NULL UNIQUE
);

CREATE TABLE games (
  id            SERIAL PRIMARY KEY,
  title         VARCHAR(150) NOT NULL,
  developer     VARCHAR(120) NOT NULL,
  rating        NUMERIC(3,1) NOT NULL CHECK (rating BETWEEN 0 AND 10),
  release_date  DATE,
  description   TEXT,
  image_url     TEXT,
  video_url     TEXT,
  availability  BOOLEAN      NOT NULL DEFAULT TRUE,
  players_label VARCHAR(32),
  players_num   SMALLINT,
  duration_id   INTEGER NOT NULL REFERENCES durations(id),
  age_rating_id INTEGER NOT NULL REFERENCES age_ratings(id)
);

CREATE TABLE screenshots (
  id      SERIAL PRIMARY KEY,
  game_id INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
  url     TEXT    NOT NULL,
  sort_order SMALLINT NOT NULL DEFAULT 1,
  UNIQUE (game_id, sort_order)
);

CREATE TABLE promo_banners (
  id      SERIAL PRIMARY KEY,
  title   VARCHAR(150) NOT NULL,
  image   TEXT         NOT NULL,
  link    TEXT,
  game_id INTEGER REFERENCES games(id)
);

CREATE TABLE game_genres (
  game_id INTEGER NOT NULL REFERENCES games(id)   ON DELETE CASCADE,
  genre_id INTEGER NOT NULL REFERENCES genres(id) ON DELETE CASCADE,
  PRIMARY KEY (game_id, genre_id)
);

CREATE TABLE game_platforms (
  game_id INTEGER NOT NULL REFERENCES games(id)     ON DELETE CASCADE,
  platform_id INTEGER NOT NULL REFERENCES platforms(id) ON DELETE CASCADE,
  PRIMARY KEY (game_id, platform_id)
);

CREATE TABLE game_languages (
  game_id INTEGER NOT NULL REFERENCES games(id)     ON DELETE CASCADE,
  language_id INTEGER NOT NULL REFERENCES languages(id) ON DELETE CASCADE,
  PRIMARY KEY (game_id, language_id)
);

CREATE TABLE game_features (
  game_id INTEGER NOT NULL REFERENCES games(id)    ON DELETE CASCADE,
  feature_id INTEGER NOT NULL REFERENCES features(id) ON DELETE CASCADE,
  PRIMARY KEY (game_id, feature_id)
);

-- Example seed data (trimmed). Remove if you plan to ETL from db.json
INSERT INTO age_ratings (label, numeric_value) VALUES
  ('6+', 6), ('12+', 12), ('16+', 16), ('18+', 18)
ON CONFLICT DO NOTHING;

INSERT INTO durations (label, minutes) VALUES
  ('До 1 часа', 60),
  ('1-3 часа', 180),
  ('3-6 часов', 360),
  ('6-12 часов', 720),
  ('12+ часов', 1000),
  ('Бесконечная', 9999)
ON CONFLICT DO NOTHING;

