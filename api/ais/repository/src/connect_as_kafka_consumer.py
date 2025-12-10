import time
import json
import os
import logging
from kafka import KafkaConsumer
import uuid
from settings import Settings


logger = logging.getLogger(__name__)

logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

settings = Settings()

def connect():
    while True:
        try:
            group_id = f"ais_listener_{uuid.uuid4()}"
            
            logger.info(f"Connecting to broker @{settings.kafka_address}...")
            consumer = KafkaConsumer(
                settings.kafka_topic,
                bootstrap_servers=settings.kafka_address,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id=group_id,
                fetch_max_wait_ms=100,   # Wait max 100ms before returning
                fetch_min_bytes=1
            )
            logger.info("Consumer connected")
            break
        except:
            logger.info(f"failed to connect to Kafka. Retrying in {settings.kafka_retry_delay} secs")
            time.sleep(settings.kafka_retry_delay)

    return consumer