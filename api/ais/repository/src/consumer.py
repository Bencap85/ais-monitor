import logging
from typing import Dict, Any, Iterable, Optional
from datetime import datetime, timezone
import os
import psycopg2.extras
from psycopg2.extensions import connection
import connect_as_kafka_consumer
from db import batch_update_history, batch_upsert_ships, batch_upsert_static_data

logger = logging.getLogger(__name__)

logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

POSITION_REPORT_IDS = {1, 2, 3}
STATIC_DATA_IDS = {5}

class AisConsumer():
    def __init__(self, conn: connection):
        self.conn = conn
        self.consumer = connect_as_kafka_consumer.connect()

        self.batch_ships = {}
        self.batch_history = []
        self.batch_static = {}
        self.message_count = 0

    def _flush_ships(self) -> None:
        batch_upsert_ships(self.conn, self.batch_ships.values())
        batch_update_history(self.conn, self.batch_history)
        batch_upsert_static_data(self.conn, self.batch_static.values())

        self.batch_ships = {}
        self.batch_history = []
        self.batch_static = {}

    def _handle_message(self, message_data: Dict) -> None:
        if message_data is None:
            logger.info("Received empty message")
            return
        
        ship_data = message_data

        message_type = ship_data['MessageID']

        # Add data to batch as determined by message type
        if message_type in STATIC_DATA_IDS:
            self.batch_static[ship_data['UserID']] = ship_data

        elif message_type in POSITION_REPORT_IDS:
            self.batch_ships[ship_data['UserID']] = ship_data
            self.batch_history.append(ship_data)

        else:
            logger.info(f"Unsupported message type! Received {message_type}")

        self.message_count += 1
        if self.message_count % 2000 == 0:
            logger.info(f"{self.message_count}th message received ************************")
            self._flush_ships()
        

    def run(self) -> None:
        try:
            for message in self.consumer:
                if message is None or message.value is None:
                    logger.info("Received empty message")
                    continue
                
                self._handle_message(message.value)

        except KeyboardInterrupt:
            logger.info("Shutting down consumer...")

        except Exception as e:
            logger.error(e)

            


