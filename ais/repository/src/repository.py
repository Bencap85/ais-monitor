import os
import json
import time
from datetime import datetime, timezone
from kafka import KafkaConsumer
import uuid
import psycopg2
from psycopg2 import OperationalError
from psycopg2.extras import execute_values
import connect_as_kafka_consumer
import threading


def schedule_prune(conn, interval=600, max_records=10):
    def job():
        try:
            with conn.cursor() as cur:
                cur.execute("CALL prune_ais_ships_history(%s);", (max_records,))
                conn.commit()
                print(f"Pruned ais_ships_history to keep {max_records} records per ship")
        except Exception as e:
            print(f"Prune failed: {e}")
        finally:
            # reschedule itself
            threading.Timer(interval, job).start()

    # kick off the first run
    threading.Timer(interval, job).start()


def connect_to_database():
    print("Attempting to connect to database...")
    try:
        connection = psycopg2.connect(
            dbname="ais_data",
            user="postgres",
            password="postgres",
            host="host.docker.internal",
            port="5432"     
        )
        print("Connected to database")
        return connection
    except OperationalError as e:
        print(f"Database connection failed: {e}")
        return None
    

def batch_upsert_ships(conn, ship_batch):
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

def batch_update_history(conn, ship_batch):
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


def prune_history(conn, max_records=10):
    with conn.cursor() as cur:
        # Call the stored procedure
        
        start = time.time()
        cur.execute("CALL prune_ais_ships_history(%s);", (max_records,))
        conn.commit()
        print(f"Pruned ais_ships_history to keep {max_records} records per ship in {time.time() - start:.2f} seconds")

def batch_upsert_static_data(conn, static_batch):
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
            spare
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
            spare = EXCLUDED.spare;
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
                static_record["Type"],
                json.dumps(static_record.get('Dimension', {})),
                static_record["FixType"],
                json.dumps(static_record.get('Eta', {})),
                static_record["MaximumStaticDraught"],
                static_record["Destination"],
                static_record["Dte"],
                static_record["Spare"]
            )
            for static_record in static_batch
        ]

        execute_values(cur, query, values)
        conn.commit()
        print(f"Successfully inserted/updated {len(static_batch)} static ship records")

def main():

    consumer = connect_as_kafka_consumer.connect(os.getenv("KAFKA_ADDRESS", "localhost:9092"), 2)

    connection = connect_to_database()
    if connection is None:
        return
    
    schedule_prune(connection, interval=600, max_records=int(os.getenv("MAX_HISTORY_RECORDS_PER_SHIP"), 10))

    message_count = 0
    batch_ships = {}
    batch_history = []
    batch_static = {}

    POSITION_REPORT_IDS = [ 1, 2, 3 ] 
    STATIC_DATA_IDS = [ 5 ]

    try:
        for message in consumer:
            # print(f"Recieved message @{datetime.now(timezone.utc)}")
            ship_data = message.value

            # Add data to bath as determined by message type
            if ship_data['MessageID'] in STATIC_DATA_IDS:
                batch_static[ship_data['UserID']] = ship_data

            elif ship_data['MessageID'] in POSITION_REPORT_IDS:
                batch_ships[ship_data['UserID']] = ship_data
                batch_history.append(ship_data)

            message_count += 1
            if message_count % 2000 == 0:
                print(f"{message_count}th message received ************************")
                batch_upsert_ships(connection, batch_ships.values())
                batch_update_history(connection, batch_history)
                batch_upsert_static_data(connection, batch_static.values())

                batch_ships = {}
                batch_history = []
                batch_static = {}

    except KeyboardInterrupt:
        print("\nConsumer stopped.")

main()