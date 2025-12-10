import logging
import time
import math
import connect_as_kafka_consumer
from app import socketio


logger = logging.getLogger(__name__)
POSITION_REPORT_IDS = [ 1, 2, 3 ]

class AisConsumer():
    def __init__(self):
        self.kafka_consumer = connect_as_kafka_consumer.connect()
        self.message_count = 0

    def get_tile_id(self, lat, lon, zoom=6):
        try:
            if lat is None or lon is None:
                raise ValueError("Latitude or longitude is None")
            if not (-85.0511 <= lat <= 85.0511):
                raise ValueError(f"Latitude {lat} out of bounds")
            if not (-180 <= lon <= 180):
                raise ValueError(f"Longitude {lon} out of bounds")
        except Exception as e:
            logger.error(str(e))
            return None
        
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        x_tile = int((lon + 180.0) / 360.0 * n)
        y_tile = int((1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2.0 * n)
        return f"{zoom}_{x_tile}_{y_tile}"

    def _handle_message(self, message: dict) -> None:
        self.message_count += 1

        ship_data = message.value
        message_type = ship_data.get("MessageID", -1)
        if message_type not in POSITION_REPORT_IDS:
            return

        lat = ship_data.get("Latitude")
        lon = ship_data.get("Longitude")

        tile_id = self.get_tile_id(lat, lon)
        socketio.emit('ais_update', ship_data, room=tile_id)

        if self.message_count % 1000 == 0:
            logger.info(f"{self.message_count}th message received ************************")

    def run(self):
        for message in self.kafka_consumer:
            self._handle_message(message)
