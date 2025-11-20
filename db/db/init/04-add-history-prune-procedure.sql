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
