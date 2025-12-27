import logging
from settings import Settings
from app import app, socketio
from consumer import AisConsumer


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

logger = logging.getLogger(__name__)
settings = Settings()

if __name__ == "__main__":
    consumer = AisConsumer()
    socketio.start_background_task(consumer.run)

    app.consumer = consumer

    logger.info("""
          *******************************
          *    HTTP + WebSocket Server  *
          *******************************
          """)
    socketio.run(app, host="0.0.0.0", port=settings.broadcaster_port)
    