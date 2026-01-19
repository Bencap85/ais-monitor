import threading
import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from server import create_api
from consumer import AisConsumer
from db import connect_to_database
from config import settings


logger = logging.getLogger(__name__)
logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

def start_history_pruner() -> None:
    def prune_job()-> None:
        PRUNE_QUERY_NAME = 'prune_ais_ships_history'

        connection = connect_to_database()
        if connection is None:
            logger.error("Error connecting to the database to run history prune")
            return
        
        cursor = connection.cursor()
        try:
            logger.info("Prune job initiated")
            cursor.execute(f"CALL {PRUNE_QUERY_NAME}(%s)", (settings.max_history_per_mmsi,))
            connection.commit()
            logger.info("Prune job completed")
        except Exception as e:
            logger.error("History prune job failed: " + str(e))
            cursor.close()
            connection.close()
        finally:
            cursor.close()
            connection.close()

    scheduler = BackgroundScheduler()
    scheduler.add_job(prune_job, "interval", minutes=int(settings.history_prune_query_interval))
    scheduler.start()

    logger.info("History pruner scheduler started")

    

def main():

    connection = connect_to_database()
    if connection is None:
        logger.error("Error connecting to database")
        return
    
    consumer = AisConsumer(connection)

    consumer_thread = threading.Thread(target=consumer.run, daemon=True)
    consumer_thread.start()
    logger.info("Consumer thread started")

    if settings.history_prune_enabled:
        logger.info("Starting history pruner thread...")
        history_pruner_thread = threading.Thread(target=start_history_pruner, daemon=True)
        history_pruner_thread.start()
        logger.info("History pruner thread started")
    else:
        logger.info("History prune disabled. Skipping setup...")

    logger.info("Starting HTTP server...")
    api = create_api()
    api.consumer = consumer
    api.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    main()
