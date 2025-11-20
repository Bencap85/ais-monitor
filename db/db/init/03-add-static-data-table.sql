

-- Main table
CREATE TABLE ship_static_data (
    message_id INTEGER,
    repeat_indicator INTEGER,
    mmsi BIGINT PRIMARY KEY,
    valid BOOLEAN,
    ais_version INTEGER,
    imo_number INTEGER,
    call_sign TEXT,
    name TEXT,
    ship_type INTEGER,
    dimensions JSONB,
    fix_type INTEGER,
    eta JSONB,
    max_static_draught REAL,
    destination TEXT,
    dte BOOLEAN,
    spare BOOLEAN
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_ship_static_data_mmsi ON ship_static_data(mmsi);
