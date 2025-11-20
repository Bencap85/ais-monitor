-- Create main table
CREATE TABLE port (
    dummy VARCHAR(10),
    country_code CHAR(2),
    location_code VARCHAR(3),
    name VARCHAR(100),
    name_local VARCHAR(100),
    subdivision VARCHAR(10),
    function VARCHAR(10),
    status VARCHAR(5),
    date_code VARCHAR(10),
    iata_code VARCHAR(10),
    coordinates VARCHAR(20),
    remarks VARCHAR(255),
    port_id VARCHAR(10) GENERATED ALWAYS AS (country_code || location_code) STORED
);

-- Unique index on port_id for conflict handling
CREATE UNIQUE INDEX idx_port_id ON port(port_id);

-- Create staging table (no generated column, no constraints)
CREATE TABLE port_stage (
    dummy VARCHAR(10),
    country_code CHAR(2),
    location_code VARCHAR(3),
    name VARCHAR(100),
    name_local VARCHAR(100),
    subdivision VARCHAR(10),
    function VARCHAR(10),
    status VARCHAR(5),
    date_code VARCHAR(10),
    iata_code VARCHAR(10),
    coordinates VARCHAR(20),
    remarks VARCHAR(255)
);

-- ============================
-- Load Part 1
-- ============================
TRUNCATE port_stage;
COPY port_stage FROM '/data/CodeListPart1-utf8.csv' DELIMITER ',' CSV HEADER;

INSERT INTO port (
    dummy, country_code, location_code, name, name_local,
    subdivision, function, status, date_code,
    iata_code, coordinates, remarks
)
SELECT DISTINCT ON (country_code, location_code)
    dummy, country_code, location_code, name, name_local,
    subdivision, function, status, date_code,
    iata_code, coordinates, remarks
FROM port_stage
ORDER BY country_code, location_code, date_code DESC
ON CONFLICT (port_id) DO UPDATE
SET name = EXCLUDED.name,
    name_local = EXCLUDED.name_local,
    subdivision = EXCLUDED.subdivision,
    function = EXCLUDED.function,
    status = EXCLUDED.status,
    date_code = EXCLUDED.date_code,
    iata_code = EXCLUDED.iata_code,
    coordinates = EXCLUDED.coordinates,
    remarks = EXCLUDED.remarks;

-- ============================
-- Load Part 2
-- ============================
TRUNCATE port_stage;
COPY port_stage FROM '/data/CodeListPart2-utf8.csv' DELIMITER ',' CSV HEADER;

INSERT INTO port (
    dummy, country_code, location_code, name, name_local,
    subdivision, function, status, date_code,
    iata_code, coordinates, remarks
)
SELECT DISTINCT ON (country_code, location_code)
    dummy, country_code, location_code, name, name_local,
    subdivision, function, status, date_code,
    iata_code, coordinates, remarks
FROM port_stage
ORDER BY country_code, location_code, date_code DESC
ON CONFLICT (port_id) DO UPDATE
SET name = EXCLUDED.name,
    name_local = EXCLUDED.name_local,
    subdivision = EXCLUDED.subdivision,
    function = EXCLUDED.function,
    status = EXCLUDED.status,
    date_code = EXCLUDED.date_code,
    iata_code = EXCLUDED.iata_code,
    coordinates = EXCLUDED.coordinates,
    remarks = EXCLUDED.remarks;

-- ============================
-- Load Part 3
-- ============================
TRUNCATE port_stage;
COPY port_stage FROM '/data/CodeListPart3-utf8.csv' DELIMITER ',' CSV HEADER;

INSERT INTO port (
    dummy, country_code, location_code, name, name_local,
    subdivision, function, status, date_code,
    iata_code, coordinates, remarks
)
SELECT DISTINCT ON (country_code, location_code)
    dummy, country_code, location_code, name, name_local,
    subdivision, function, status, date_code,
    iata_code, coordinates, remarks
FROM port_stage
ORDER BY country_code, location_code, date_code DESC
ON CONFLICT (port_id) DO UPDATE
SET name = EXCLUDED.name,
    name_local = EXCLUDED.name_local,
    subdivision = EXCLUDED.subdivision,
    function = EXCLUDED.function,
    status = EXCLUDED.status,
    date_code = EXCLUDED.date_code,
    iata_code = EXCLUDED.iata_code,
    coordinates = EXCLUDED.coordinates,
    remarks = EXCLUDED.remarks;