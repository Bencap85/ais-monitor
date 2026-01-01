import eventlet
eventlet.monkey_patch()
import math
import json
import logging
from flask import Flask, request, jsonify, current_app
from flask_socketio import SocketIO, join_room, leave_room
from tile_utils import get_intersecting_tiles


logger = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")

def get_tile_id(lat, lon, zoom=6):
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
    
@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    metrics = current_app.consumer.get_metrics()
    return metrics

@app.route("/health", methods=["GET"])
def health_check():
    return {"status": "ok"}, 200

@socketio.on("connect")
def handle_connect():
    logger.info("Client connected")

@socketio.on("disconnect")
def handle_disconnect():
    logger.info("Client disconnected")

@socketio.on("subscribe_tiles")
def handle_subscribe_tiles(data):
    tiles = data.get("tiles", [])
    for tile_id in tiles:
        join_room(tile_id, sid=request.sid)
    logger.info(f"{request.sid} subscribed to: {tiles}")

@socketio.on("unsubscribe_tiles")
def handle_unsubscribe_tiles(data):
    tiles = data.get("tiles", [])
    for tile_id in tiles:
        leave_room(tile_id, sid=request.sid)
    logger.info(f"{request.sid} unsubscribed from: {tiles}")