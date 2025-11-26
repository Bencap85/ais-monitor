import asyncio
import json
from datetime import datetime, timezone
import time
import random
import os
import logging
from kafka import KafkaProducer
from websocket import create_connection
from websocket._exceptions import WebSocketConnectionClosedException
import sys

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    stream=sys.stdout     
)

logger = logging.getLogger(__name__)
API_KEY = "90ebcd12a02888b382cf2c013bfd3336b2b82108"

ACCEPTED_MESSAGE_TYPES = { "PositionReport", "ShipStaticData" }

class AisIngestor:

    def _connect_to_ws(self):
        ws = create_connection("wss://stream.aisstream.io/v0/stream")
        subscribe_message = {
            "APIKey": API_KEY,
            "BoundingBoxes": [[[-90, -180], [90, 180]]],
            "FilterMessageTypes": ["PositionReport", "ShipStaticData"]
        }
        ws.send(json.dumps(subscribe_message))
        return ws
    
    def __init__(self, kafka_producer: KafkaProducer):
        self.ws_connection = self._connect_to_ws()
        self.kafka_producer = kafka_producer
        
        self.stats = {
            "message_count": 0,
            "lag_seconds": 0,
            "messages_per_second": 0,
            "start_time": None
        }

    def _queue_message(self, ais_message: dict) -> None:
        self.kafka_producer.send("ais_message", value=ais_message)

    def _handle_message(self, message: dict) -> None:
        if message is None:
            logger.info("Received empty message")
            return
        
        message_type = message.get("MessageType")
        if message_type in ACCEPTED_MESSAGE_TYPES:
            ais_message = message["Message"][message_type]
            self._queue_message(ais_message)

    def _convert_metadata_string_to_datetime(self, raw_time: str) -> datetime:
        cleaned = raw_time.replace(" UTC", "")
        parts = cleaned.split(".")
        if len(parts) == 2:
            timestamp = parts[0] + "." + parts[1][:6]
        else:
            timestamp = cleaned

        msg_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
        return msg_time.replace(tzinfo=timezone.utc)


    def run(self) -> None:
        self.stats["start_time"] = datetime.now(timezone.utc)
        try:
            while True:
                try:
                    message_json = self.ws_connection.recv()
                    message = json.loads(message_json)
                    self._handle_message(message)

                    self.stats["message_count"] += 1
                    if self.stats["message_count"] % 1000 == 0:

                        # Calculate lag
                        sent_time = self._convert_metadata_string_to_datetime(message["MetaData"]["time_utc"])
                        lag = datetime.now(timezone.utc) - sent_time

                        # Calculate messages/second
                        elapsed_time = datetime.now(timezone.utc) - self.stats["start_time"]
                        elapsed_seconds = elapsed_time.total_seconds()
                        messages_per_second = self.stats["message_count"] / elapsed_seconds
                        
                        self.stats["lag_seconds"] = lag.total_seconds()
                        self.stats["messages_per_second"] = messages_per_second

                        logger.info(str(self.stats))

                except KeyboardInterrupt as k:
                    print("Exiting...")
                    logger.info("Exiting...")

                except WebSocketConnectionClosedException as we:
                    logger.info("WebSocket connection lost.")
                    logger.error(f"Exception: {we}")
                    logger.info("Reconnecting in 2 seconds...")
                    self.ws_connection.close()
                    time.sleep(2)
                    self.ws_connection = self._connect_to_ws()
                    if self.ws_connection is not None:
                        logger.info(f"Reconnected successfully: {str(self.ws_connection)}")

                except Exception as e:
                    logger.error(f"Unexpected error: {e}.") 
                    logger.info("Reconnecting in 2 seconds...")
                    self.ws_connection.close()
                    time.sleep(2)
                    self.ws_connection = self._connect_to_ws()
                    if self.ws_connection is not None:
                        logger.info(f"Reconnected successfully: {str(self.ws_connection)}")

        except Exception as e:
            logger.error(f"Unexpected error: {e}. Reconnecting in 5 seconds...")
            self.ws_connection.close()
                
