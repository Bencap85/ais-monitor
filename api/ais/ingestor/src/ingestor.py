import asyncio
import json
from datetime import datetime, timezone
import time
import random
import os
import logging
import sys
import boto3
from websocket import create_connection
from websocket._exceptions import WebSocketConnectionClosedException
from config import settings


logger = logging.getLogger(__name__)

ACCEPTED_MESSAGE_TYPES = { "PositionReport", "ShipStaticData" }

kwargs = { "region_name": settings.aws_region_name }
if settings.aws_url:
    kwargs["endpoint_url"] = settings.aws_url

class AisIngestor:

    def _connect_to_ws(self):
        ws = create_connection(settings.ws_api_url)
        subscribe_message = {
            "APIKey": settings.ws_api_key,
            "BoundingBoxes": [[[-90, -180], [90, 180]]],
            "FilterMessageTypes": list(ACCEPTED_MESSAGE_TYPES)
        }
        ws.send(json.dumps(subscribe_message))
        return ws
    
    def __init__(self):
        self.ws_connection = self._connect_to_ws()
        self.sns_client = boto3.client("sns", **kwargs)
        self.topic_arn = settings.sns_topic_arn

        self.buffer = []
        self.batch_size = int(settings.ais_message_batch_size)
        
        self.stats = {
            "ais_message_count": 0,
            "sns_message_count": 0,
            "lag_seconds": 0,
            "ais_messages_per_second": 0,
            "start_time": None,
            "total_throughput_bytes": 0
        }

    def _queue_message(self, ais_message: dict) -> None:
        self.buffer.append(ais_message)

        if (len(self.buffer) >= self.batch_size):
            try:
                payload = json.dumps(self.buffer)
                self.sns_client.publish(
                    TopicArn=self.topic_arn,
                    Message=payload
                )

                self.stats["sns_message_count"] += 1

            except Exception as e:
                logger.error(f"Failed to publish batch {payload}: {e}")
        
            self.buffer.clear()


    def _handle_message(self, message: dict) -> None:
        if message is None:
            logger.info("Received empty message")
            return
        
        self.stats["total_throughput_bytes"] += len(json.dumps(message).encode('utf-8'))

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

    def get_metrics(self) -> dict:
        return self.stats

    def run(self) -> None:
        self.stats["start_time"] = datetime.now(timezone.utc)
        try:
            while True:
                try:
                    message_json = self.ws_connection.recv()
                    message = json.loads(message_json)
                    self._handle_message(message)

                    self.stats["ais_message_count"] += 1
                    if self.stats["ais_message_count"] % 1000 == 0:

                        # Calculate lag
                        sent_time = self._convert_metadata_string_to_datetime(message["MetaData"]["time_utc"])
                        lag = datetime.now(timezone.utc) - sent_time

                        # Calculate messages/second
                        elapsed_time = datetime.now(timezone.utc) - self.stats["start_time"]
                        elapsed_seconds = elapsed_time.total_seconds()
                        ais_messages_per_second = self.stats["ais_message_count"] / elapsed_seconds
                        
                        self.stats["lag_seconds"] = lag.total_seconds()
                        self.stats["ais_messages_per_second"] = ais_messages_per_second

                        logger.info(str(self.stats))

                except KeyboardInterrupt as k:
                    print("Exiting...")
                    logger.info("Exiting...")

                except WebSocketConnectionClosedException as we:
                    logger.info("WebSocket connection lost.")
                    logger.error(f"Exception: {we}")
                    logger.info(f"Reconnecting in {settings.ws_retry_seconds} seconds...")
                    self.ws_connection.close()
                    time.sleep(settings.ws_retry_seconds)
                    self.ws_connection = self._connect_to_ws()
                    if self.ws_connection is not None:
                        logger.info(f"Reconnected successfully: {str(self.ws_connection)}")

                except Exception as e:
                    logger.error(f"Unexpected error: {e}.") 
                    logger.info(f"Reconnecting in {settings.ws_retry_seconds} seconds...")
                    self.ws_connection.close()
                    time.sleep(settings.ws_retry_seconds)
                    self.ws_connection = self._connect_to_ws()
                    if self.ws_connection is not None:
                        logger.info(f"Reconnected successfully: {str(self.ws_connection)}")

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self.ws_connection.close()
                
