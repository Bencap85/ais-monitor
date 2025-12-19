import logging
from app import app, socketio
from consumer import AisConsumer

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

if __name__ == "__main__":
    consumer = AisConsumer()
    # socketio.start_background_task(consumer.run)
    for i in range(3):
        socketio.start_background_task(consumer.run)
        logger.info("Started background task " + str(i))

    print("""
          *******************************
          *    HTTP + WebSocket Server  *
          *******************************
          """)
    socketio.run(app, host="0.0.0.0", port=5000)