
import os
import math
import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, join_room, leave_room
import connect_as_kafka_consumer
from tile_utils import get_intersecting_tiles

# Flask + SocketIO setup
app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

POSITION_REPORT_IDS = [ 1, 2, 3 ]

def get_tile_id(lat, lon, zoom=6):
    try:
        if lat is None or lon is None:
            raise ValueError("Latitude or longitude is None")
        if not (-85.0511 <= lat <= 85.0511):
            raise ValueError(f"Latitude {lat} out of bounds")
        if not (-180 <= lon <= 180):
            raise ValueError(f"Longitude {lon} out of bounds")
    except Exception as e:
        print(str(e))
        return
    
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    x_tile = int((lon + 180.0) / 360.0 * n)
    y_tile = int((1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2.0 * n)
    return f"{zoom}_{x_tile}_{y_tile}"

def start_consumer():
    kafka_address = os.getenv("KAFKA_ADDRESS", "localhost:9092")
    consumer = connect_as_kafka_consumer.connect(kafka_address, 2)

    message_count = 0
    for message in consumer:
        
        ship_data = message.value
        message_count += 1

        message_type = ship_data.get("MessageID", -1)
        if message_type not in POSITION_REPORT_IDS:
            continue

        lat = ship_data.get("Latitude")
        lon = ship_data.get("Longitude")

        tile_id = get_tile_id(lat, lon)
        socketio.emit('ais_update', ship_data, room=tile_id)

        if message_count % 1000 == 0:
            print(f"{message_count}th message received ************************")


@app.route('/api/relevant-rooms', methods=['POST'])
def get_rooms_for_bounds():
    print("Received request to determine room ids...")
    try:
        geojson = request.get_json().get("geojson")
        room_ids = get_intersecting_tiles(geojson, zoom=6)
        print("Room IDs: " + str(room_ids))
        return jsonify(room_ids)
    except Exception as e:
        print(f"Error in /api/relevant-rooms: {e}")
        return jsonify({"error": "Internal server error"}), 500

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@socketio.on('subscribe_tiles')
def handle_subscribe_tiles(data):
    tiles = data.get("tiles", [])
    for tile_id in tiles:
        join_room(tile_id, sid=request.sid)
    print(f"{request.sid} subscribed to: {tiles}")

@socketio.on('unsubscribe_tiles')
def handle_unsubscribe_tiles(data):
    tiles = data.get("tiles", [])
    for tile_id in tiles:
        leave_room(tile_id, sid=request.sid)
    print(f"{request.sid} unsubscribed from: {tiles}")

# Start server and background Kafka consumer
if __name__ == '__main__':
    socketio.start_background_task(start_consumer)
    print("""
          *******************************
          *    HTTP server starting     *
          *******************************
          """)
    socketio.run(app, host='0.0.0.0', port=5000)