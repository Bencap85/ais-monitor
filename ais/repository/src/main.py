import threading
import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
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

def start_history_pruner() -> None:
    def prune_job()-> None:
        PRUNE_QUERY_NAME = 'prune_ais_ships_history'
        MAX_HISTORY_RECORDS = 100

        connection = connect_to_database()
        if connection is None:
            logger.error("Error connecting to the database to run history prune")
            return
        
        cursor = connection.cursor()
        try:
            logger.info("Prune job initiated")
            cursor.execute(f"CALL {PRUNE_QUERY_NAME}(%s)", (MAX_HISTORY_RECORDS,))
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
    scheduler.add_job(prune_job, "interval", minutes=2)
    scheduler.start()

    logger.info("History pruner scheduler started")

    

def main():

    consumer_thread = threading.Thread(target=start_consumer, daemon=True)
    consumer_thread.start()
    logger.info("Consumer thread started")

    history_pruner_thread = threading.Thread(target=start_history_pruner, daemon=True)
    history_pruner_thread.start()
    logger.info("History pruner thread started")

    print("Starting HTTP server...")
    api = create_api()
    api.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    main()
