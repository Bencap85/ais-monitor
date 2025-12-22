import eventlet
eventlet.monkey_patch()
import math
import logging
from flask import Flask, request, jsonify
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

@app.route("/api/relevant-rooms", methods=["POST"])
def get_rooms_for_bounds():
    """
    Get the rooms the client needs to connect to in order to receive AIS updates for a
    particular region. Probably going to move this logic client-side.

    Parameters:
        {
            geojson: {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-76.37221,36.96841],
                            [-76.37221,36.981301],
                            [-76.354526,36.981301],
                            [-76.354526,36.96841],
                            [-76.37221,36.96841]
                        ]
                    ]
                }
            }
        }

    Returns:
        List with room ids:
        [
            "1_1_1",
            "1_1_2",
            "1_1_3"
        ]


    """
    try:
        geojson = request.get_json().get("geojson")
        room_ids = get_intersecting_tiles(geojson, zoom=6)
        return jsonify(room_ids)
    except Exception as e:
        logger.error(f"Error in /api/relevant-rooms: {e}")
        return jsonify({"error": "Internal server error"}), 500

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