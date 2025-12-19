import logging
from typing import Dict, Any, Iterable, Optional
from datetime import datetime, timezone
import os
import boto3
import time
import json
from concurrent.futures import ThreadPoolExecutor
import psycopg2.extras
from psycopg2.extensions import connection
from settings import Settings
from db import batch_update_history, batch_upsert_ships, batch_upsert_static_data

logger = logging.getLogger(__name__)

logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

settings = Settings()

POSITION_REPORT_IDS = {1, 2, 3}
STATIC_DATA_IDS = {5}

class AisConsumer():
    def __init__(self, conn: connection):
        self.conn = conn
        self.sqs_client = boto3.client(
            "sqs",
            region_name=settings.aws_region_name,
            endpoint_url=settings.aws_url
        )
        self.queue_url = settings.sqs_url                          

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
        if self.message_count % 1000 == 0:
            logger.info(f"{self.message_count}th message received ************************")
            self._flush_ships()
        
    def _delete_messages(self, messages: list) -> None:
        entries = []
        for i, msg in enumerate(messages):
            entries.append({
                "Id": str(i),  # unique ID for this delete request
                "ReceiptHandle": msg["ReceiptHandle"]
            })

        if entries:
            resp = self.sqs_client.delete_message_batch(
                QueueUrl=self.queue_url,
                Entries=entries
            )

    def run(self):
        while True:
            try:
                response = self.sqs_client.receive_message(
                    QueueUrl=self.queue_url,
                    MaxNumberOfMessages=10,   # up to 10 SQS messages at once
                    WaitTimeSeconds=2         # long polling
                )
                
                messages = response.get("Messages", [])
                if not messages:
                    logger.info("No messages available, waiting...")
                    continue

                for msg in messages:
                    body = msg["Body"]

                    # SNS wraps the payload in its own envelope
                    sns_envelope = json.loads(body)
                    batch_payload = json.loads(sns_envelope["Message"])

                    # logger.info(f"Received batch of {len(batch_payload)} AIS messages")

                    # Process each AIS message individually
                    for ais_message in batch_payload:
                        self._handle_message(ais_message)

                    # Delete message from queue after processing
                    # self.sqs_client.delete_message(
                    #     QueueUrl=self.queue_url,
                    #     ReceiptHandle=msg["ReceiptHandle"]
                    # )

                self._delete_messages(messages)

            except Exception as e:
                logger.error(f"Error consuming messages: {e}")
                time.sleep(5)
            

