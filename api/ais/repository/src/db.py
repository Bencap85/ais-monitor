import json
import logging
import datetime
from datetime import datetime, timezone
import psycopg2
import psycopg2.extras
from psycopg2.extras import execute_values
import psycopg2.extensions
from psycopg2.extensions import connection
from typing import Iterable, Dict, Any, List
from config import settings


logger = logging.getLogger(__name__)

def connect_to_database() -> connection:
    logger.info("Attempting to connect to database...")
    try:
        connection = psycopg2.connect(
            dbname=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            host=settings.db_host,
            port=int(settings.db_port)     
        )
        logger.info("Connected to database")
        return connection
    except OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        return None
    

def batch_upsert_ships(conn: connection, ship_batch: List) -> None:
    with conn.cursor() as cur:
        query = """
        INSERT INTO ais_ships (mmsi, sog_knots, navigational_status, true_heading, position)
        VALUES %s
        ON CONFLICT (mmsi) DO UPDATE SET
            sog_knots = EXCLUDED.sog_knots,
            navigational_status = EXCLUDED.navigational_status,
            true_heading = EXCLUDED.true_heading,
            position = EXCLUDED.position,
            timestamp = CURRENT_TIMESTAMP;
        """
        values = [
            (
                ship["UserID"],
                ship["Sog"],
                ship["NavigationalStatus"],
                ship["TrueHeading"],
                ship["Longitude"],
                ship["Latitude"]
            )
            for ship in ship_batch
        ]
        execute_values(cur, query, values, template="(%s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))")
        conn.commit()
        print(f"Successfully inserted/updated {len(ship_batch)} records into database")

def batch_update_history(conn: connection, ship_batch: List) -> None:
    with conn.cursor() as cur:
        query = """
        INSERT INTO ais_ships_history (mmsi, sog_knots, navigational_status, true_heading, position)
        VALUES %s
        """
        values = [
            (
                ship["UserID"],
                ship["Sog"],
                ship["NavigationalStatus"],
                ship["TrueHeading"],
                ship["Longitude"],
                ship["Latitude"]
            )
            for ship in ship_batch
        ]
        execute_values(cur, query, values, template="(%s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))")
        conn.commit()
        print(f"Successfully inserted/updated {len(ship_batch)} HISTORY records into database")


def batch_upsert_static_data(conn: connection, static_batch: List) -> None:
    with conn.cursor() as cur:
        query = """
        INSERT INTO ship_static_data (
            message_id,
            repeat_indicator,
            mmsi,
            valid,
            ais_version,
            imo_number,
            call_sign,
            name,
            ship_type,
            dimensions,
            fix_type,
            eta,
            max_static_draught,
            destination,
            dte,
            spare,
            ship_length
        )
        VALUES %s
        ON CONFLICT (mmsi) DO UPDATE SET
            message_id = EXCLUDED.message_id,
            repeat_indicator = EXCLUDED.repeat_indicator,
            valid = EXCLUDED.valid,
            ais_version = EXCLUDED.ais_version,
            imo_number = EXCLUDED.imo_number,
            call_sign = EXCLUDED.call_sign,
            name = EXCLUDED.name,
            ship_type = EXCLUDED.ship_type,
            dimensions = EXCLUDED.dimensions,
            fix_type = EXCLUDED.fix_type,
            eta = EXCLUDED.eta,
            max_static_draught = EXCLUDED.max_static_draught,
            destination = EXCLUDED.destination,
            dte = EXCLUDED.dte,
            spare = EXCLUDED.spare,
            ship_length = EXCLUDED.ship_length;
        """

        values = [
            (
                static_record["MessageID"],
                static_record["RepeatIndicator"],
                static_record["UserID"],
                static_record["Valid"],
                static_record["AisVersion"],
                static_record["ImoNumber"],
                static_record["CallSign"],
                static_record["Name"],
                validate_ship_type(static_record["Type"]),
                json.dumps(static_record.get('Dimension', {})),
                static_record["FixType"],
                json.dumps(static_record.get('Eta', {})),
                static_record["MaximumStaticDraught"],
                static_record["Destination"],
                static_record["Dte"],
                static_record["Spare"],
                determine_ship_length(static_record.get('Dimension', {}))
            )
            for static_record in static_batch
        ]

        execute_values(cur, query, values)
        conn.commit()
        print(f"Successfully inserted/updated {len(static_batch)} static ship records")

def find_ships_within_bounds(cursor: any, geometry: dict, start_time: str, end_time: str) -> list:
    try:
        query = """
            SELECT
                ais_ships.id,
                ais_ships.mmsi AS "UserID",
                ais_ships.navigational_status AS "NavigationalStatus",
                ST_Y(position::geometry) AS "Latitude",
                ST_X(position::geometry) AS "Longitude",
                ais_ships.sog_knots AS "Sog",
                ais_ships.timestamp AS "Timestamp",
                ais_ships.true_heading AS "TrueHeading",
                ship_static_data.name AS "Name",
                ship_static_data.call_sign AS "CallSign",
                ship_type.type_name AS "ShipTypeName",
                ship_static_data.ship_length AS "ShipLength"
            FROM ais_ships 
            LEFT JOIN ship_static_data
                ON ais_ships.mmsi = ship_static_data.mmsi
            LEFT JOIN ship_type
                ON ship_static_data.ship_type = ship_type.type_code
            WHERE ais_ships.position && ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326)
                AND ST_Intersects(
                    ais_ships.position::geometry,
                    ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326)
                )
                AND ais_ships.timestamp >= (%s)
                AND ais_ships.timestamp <= (%s);
        """
        logger.info(f"Executing spatial query with geometry: {json.dumps(geometry)}, start_time: {start_time}, end_time: {end_time}")
        query_start_time = datetime.now(timezone.utc)
     
        cursor.execute( 
            query, ( 
                json.dumps(geometry), 
                json.dumps(geometry), 
                start_time, 
                end_time
            )
        )

        elapsed_time = datetime.now(timezone.utc) - query_start_time
        elapsed_seconds = elapsed_time.total_seconds()  
        logger.info(f"Query took {elapsed_seconds} seconds") 
                        
        results = cursor.fetchall()
        return results
    
    except Exception as e:
        raise Exception(e)
    
def history_for_mmsi(mmsi: int, connection: connection) -> List:
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    query = """
        SELECT
            id,
            mmsi AS "UserID",
            navigational_status AS "NavigationalStatus",
            ST_Y(position::geometry) AS "Latitude",
            ST_X(position::geometry) AS "Longitude",
            sog_knots AS "Sog",
            timestamp AS "Timestamp",
            true_heading AS "TrueHeading"
        FROM ais_ships_history
        WHERE mmsi = %s
        ORDER BY timestamp DESC;
    """
    cursor.execute(query, (mmsi,))
    results = cursor.fetchall()
    return results
    
def validate_ship_type(ship_type: int) -> int:
    if ship_type is not None and -1 < ship_type < 100:
        return ship_type
    return 0

def determine_ship_length(dimensions: dict) -> int:
    if dimensions is not None and "A" in dimensions and "B" in dimensions:
        return dimensions["A"] + dimensions["B"]
    return 0
