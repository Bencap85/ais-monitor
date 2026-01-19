-- Partitions ais_history table by timestamp to maintain query performance as the table grows.
-- The retention policy of 7 days discards data (partitions) older than 7 days
CREATE EXTENSION IF NOT EXISTS timescaledb;

SELECT create_hypertable(
    'ais_ships_history',
    'timestamp',
    chunk_time_interval => INTERVAL '1 day'
);
 
-- Retention policy
SELECT add_retention_policy(
    'ais_ships_history',
    INTERVAL '7 days'
);
