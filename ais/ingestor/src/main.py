import asyncio
import json
from datetime import datetime, timezone
import time
import random
import os
import threading
from kafka import KafkaProducer
from ingestor import AisIngestor


def start_ingestor():
    producer = None

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

    if producer is None:
        return

    ingestor = AisIngestor(producer)
    ingestor.run()

def main():

    ingestor_thread = threading.Thread(target=start_ingestor, daemon=False)
    ingestor_thread.start()

if __name__ == "__main__":
    main()