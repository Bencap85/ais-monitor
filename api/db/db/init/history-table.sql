CREATE TABLE ais_ships_history (
    mmsi BIGINT NOT NULL,
    sog_knots INT,
    navigational_status INT,
    true_heading INT,
    position GEOGRAPHY(Point, 4326),
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_history_mmsi_timestamp ON ais_ships_history(mmsi, timestamp DESC);

-- Stored procedure for pruning
CREATE OR REPLACE PROCEDURE prune_ais_ships_history(max_records_per_ship INT)
LANGUAGE plpgsql
AS $$
BEGIN
    WITH ranked AS (
        SELECT id,
               ROW_NUMBER() OVER (PARTITION BY mmsi ORDER BY timestamp DESC) AS rn
        FROM ais_ships_history
    )
    DELETE FROM ais_ships_history h
    USING ranked r
    WHERE h.id = r.id
      AND r.rn > max_records_per_ship;

    RAISE NOTICE 'Pruned ais_ships_history to keep % records per ship', max_records_per_ship;
END;
$$;
