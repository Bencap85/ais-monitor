import asyncio
import json
from datetime import datetime, timezone
import time
import random
import os
from kafka import KafkaProducer
from websocket import create_connection
from websocket._exceptions import WebSocketConnectionClosedException

API_KEY = "90ebcd12a02888b382cf2c013bfd3336b2b82108"

def convert_metadata_string_to_datetime(raw_time: str) -> datetime:
    cleaned = raw_time.replace(" UTC", "")
    parts = cleaned.split(".")
    if len(parts) == 2:
        timestamp = parts[0] + "." + parts[1][:6]
    else:
        timestamp = cleaned

    msg_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
    return msg_time.replace(tzinfo=timezone.utc)

def queue_message(producer, ais_message):
    producer.send("ais_message", value=ais_message)

def connect_ais_stream(producer: KafkaProducer):

    def connect():
        ws = create_connection("wss://stream.aisstream.io/v0/stream")
        subscribe_message = {
            "APIKey": API_KEY,
            "BoundingBoxes": [[[-90, -180], [90, 180]]],
            "FilterMessageTypes": ["PositionReport", "ShipStaticData"]
        }
        ws.send(json.dumps(subscribe_message))
        return ws
    
    ws = connect()

    message_count = 0
    start_time = datetime.now(timezone.utc)

    try:
        while True:
            
            try:
                message_json = ws.recv()
                message = json.loads(message_json)
                message_type = message.get("MessageType")

                if message_type == "PositionReport" or message_type == "ShipStaticData":
                    ais_message = message["Message"][message_type]
                    queue_message(producer, ais_message)

                    message_count += 1
                    if message_count % 1000 == 0:
                        print(f"{message_count}th message sent ****************************")
                        sent_time = convert_metadata_string_to_datetime(message["MetaData"]["time_utc"])
                        lag = datetime.now(timezone.utc) - sent_time
                        print(f"Lag: {lag.total_seconds():.2f} seconds")

                        # Calculate messages/second
                        elapsed_time = datetime.now(timezone.utc) - start_time
                        elapsed_seconds = elapsed_time.total_seconds()
                        messages_per_second = message_count / elapsed_seconds
                        print(f"Recieving {messages_per_second} messages per second")

            except WebSocketConnectionClosedException as we:
                print("WebSocket connection lost. Reconnecting in 5 seconds...")
                print(f"Exception: {we}")
                ws.close()
                time.sleep(1)
                ws = connect()
                if ws is not None:
                    print(f"Reconnected successfully: {str(ws)}")
            except Exception as e:
                print(f"Unexpected error: {e}. Reconnecting in 5 seconds...")
                ws.close()
                time.sleep(1)
                ws = connect()
                if ws is not None:
                    print(f"Reconnected successfully: {str(ws)}")

    except KeyboardInterrupt:
        print("Stream stopped.")
    finally:
        ws.close()

def main():
    while True:
        try:
            kafka_address = os.getenv("KAFKA_ADDRESS", "localhost:9092")
            
            print("Consumer is attempting to connect to Kafka broker...")
            producer = KafkaProducer(
                bootstrap_servers=kafka_address,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                request_timeout_ms=5000,
                retries=0
            )
            print("Connected to kafka. Connecting via websocket now...")
            break
        except:
            print("Failed to connect to Kafka. Retrying in ")

    connect_ais_stream(producer)

if __name__ == "__main__":
    main()