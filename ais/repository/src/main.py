import threading
import os
import logging
from server import create_api
from consumer import AisConsumer
from db import connect_to_database

logger = logging.getLogger(__name__)

def start_consumer() -> None:
    connection = connect_to_database()
    if connection is None:
        logger.error("Error connecting to database")
        return
    
    consumer = AisConsumer(connection)
    consumer.run()

def main():

    consumer_thread = threading.Thread(target=start_consumer, daemon=True)
    consumer_thread.start()
    logger.info("Consumer thread started")

    print("Starting HTTP server...")
    api = create_api()
    api.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    main()
