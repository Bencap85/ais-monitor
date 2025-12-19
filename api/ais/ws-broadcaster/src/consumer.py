import logging
import time
import math
import boto3
import json
from concurrent.futures import ThreadPoolExecutor
from settings import Settings
from app import socketio


logger = logging.getLogger(__name__)
settings = Settings()

POSITION_REPORT_IDS = [ 1, 2, 3 ]

class AisConsumer():

    def __init__(self):
        self.sqs_client = boto3.client(
            "sqs",
            region_name=settings.aws_region_name,
            endpoint_url=settings.aws_url
        )
        self.queue_url = settings.sqs_url
        self.message_count = 0

    def get_tile_id(self, lat, lon, zoom=6):
        try:
            if lat is None or lon is None:
                raise ValueError("Latitude or longitude is None")
            if not (-85.0511 <= lat <= 85.0511):
                raise ValueError(f"Latitude {lat} out of bounds")
            if not (-180 <= lon <= 180):
                raise ValueError(f"Longitude {lon} out of bounds")
        except Exception as e:
            logger.error(str(e))
            return None
        
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        x_tile = int((lon + 180.0) / 360.0 * n)
        y_tile = int((1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2.0 * n)
        return f"{zoom}_{x_tile}_{y_tile}"

    def _handle_message(self, message: dict) -> None:
        self.message_count += 1

        ship_data = message
        message_type = ship_data.get("MessageID", -1)
        if message_type not in POSITION_REPORT_IDS:
            return

        lat = ship_data.get("Latitude")
        lon = ship_data.get("Longitude")

        tile_id = self.get_tile_id(lat, lon)
        socketio.emit('ais_update', ship_data, room=tile_id)

        if self.message_count % 1000 == 0:
            logger.info(f"{self.message_count}th message received ************************")

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

