CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS ais_ships (
    id SERIAL PRIMARY KEY,
    mmsi BIGINT UNIQUE NOT NULL,
    sog_knots INT,
    navigational_status INT,
    true_heading INT,
    position GEOGRAPHY(Point, 4326),
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ais_position
ON ais_ships USING GIST (position);

