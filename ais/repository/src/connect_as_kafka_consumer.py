import time
import json
import os
from kafka import KafkaConsumer
import uuid


def connect(kafka_address: str,  retry_delay: int=2):
    while True:
        try:
            group_id = f"ais_listener_{uuid.uuid4()}"
            
            print(f"Connecting to broker @{kafka_address}...")
            consumer = KafkaConsumer(
                'ais_message',
                bootstrap_servers=kafka_address,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id=group_id,
                fetch_max_wait_ms=100,   # Wait max 100ms before returning
                fetch_min_bytes=1
            )
            print("Consumer connected")
            break
        except:
            print(f"failed to connect to Kafka. Retrying in {retry_delay} secs")
            time.sleep(retry_delay)

    return consumer