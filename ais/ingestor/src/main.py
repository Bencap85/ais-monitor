import asyncio
import json
from datetime import datetime, timezone
import time
import random
import os
import threading
import logging
from kafka import KafkaProducer
from ingestor import AisIngestor
from settings import Settings


logger = logging.getLogger(__name__)
settings = Settings()

logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

def start_ingestor():
    producer = None

    while True:
        try:            
            logger.info("Consumer is attempting to connect to Kafka broker...")
            producer = KafkaProducer(
                bootstrap_servers=settings.kafka_address,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                request_timeout_ms=5000,
                retries=0
            )
            logger.info("Connected to kafka. Connecting via websocket now...")
            break
        except:
            logger.info("Failed to connect to Kafka. Retrying in 5s")

    if producer is None:
        return

    ingestor = AisIngestor(producer)
    ingestor.run()

def main():

    ingestor_thread = threading.Thread(target=start_ingestor, daemon=False)
    ingestor_thread.start()

if __name__ == "__main__":
    main()