import logging
from datetime import datetime, timezone
import time
import math
import boto3
import json
from concurrent.futures import ThreadPoolExecutor
from config import settings
from app import socketio
from tile_utils import get_tile_id


logger = logging.getLogger(__name__)

POSITION_REPORT_IDS = [ 1, 2, 3 ]

kwargs = {"region_name": settings.aws_region_name} 
if settings.aws_url: # only set in LocalStack 
    kwargs["endpoint_url"] = settings.aws_url

class AisConsumer():

    def __init__(self):
        self.sqs_client = boto3.client("sqs", **kwargs)
        self.queue_url = settings.broadcaster_queue_url
        self.stats = {
            "ais_message_count": 0,
            "sqs_message_count": 0,
            "start_time": None,
            "ais_messages_per_second": 0,
            "sqs_messages_per_second": 0
        }


    def _handle_message(self, message: dict) -> None:

        ship_data = message
        message_type = ship_data.get("MessageID", -1)
        if message_type not in POSITION_REPORT_IDS:
            return

        lat = ship_data.get("Latitude")
        lon = ship_data.get("Longitude")

        tile_id = get_tile_id(lat, lon)
        socketio.emit('ais_update', ship_data, room=tile_id)

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

    def get_metrics(self) -> dict:
        return self.stats

    def run(self):
        self.stats["start_time"] = datetime.now(timezone.utc)
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

                    self.stats["sqs_message_count"] += 1
                    if self.stats["sqs_message_count"] % 1000 == 0:
                        # Calculate sqs messages/second
                        elapsed_time = datetime.now(timezone.utc) - self.stats["start_time"]
                        elapsed_seconds = elapsed_time.total_seconds()
                        sqs_messages_per_second = self.stats["sqs_message_count"] / elapsed_seconds
                        
                        self.stats["sqs_messages_per_second"] = sqs_messages_per_second
                            
                    body = msg["Body"]

                    # SNS wraps the payload in its own envelope
                    sns_envelope = json.loads(body)
                    batch_payload = json.loads(sns_envelope["Message"])

                    # Process each AIS message individually
                    for ais_message in batch_payload:

                        self.stats["ais_message_count"] += 1
                        if self.stats["ais_message_count"] % 1000 == 0:

                            # Calculate messages/second
                            elapsed_time = datetime.now(timezone.utc) - self.stats["start_time"]
                            elapsed_seconds = elapsed_time.total_seconds()
                            ais_messages_per_second = self.stats["ais_message_count"] / elapsed_seconds
                            
                            self.stats["ais_messages_per_second"] = ais_messages_per_second
                            logger.info(str(self.stats))

                        self._handle_message(ais_message)

                self._delete_messages(messages)

            except Exception as e:
                logger.error(f"Error consuming messages: {e}")
                time.sleep(5)

