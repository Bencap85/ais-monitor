from flask import Flask, request, jsonify, make_response
import threading
import os
import json
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/api/detect', methods=['POST'])
def detect_tiles():
    try:
        response = requests.post(f"{os.getenv('ML_SERVICE_URL')}/api/detect", json=request.get_json())
        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to connect to ML service", "details": str(e)}), 502
    

@app.route('/api/<pipeline_id>/status', methods=['GET'])
def get_pipeline_status(pipeline_id: str):
    try:
        target_url = f"{os.getenv('ML_SERVICE_URL')}/api/{pipeline_id}/status"
        response = requests.get(target_url)
        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to connect to ml service", "details": str(e)}), 502
    

@app.route('/api/<pipeline_id>/result', methods=['GET'])
def get_pipeline_result(pipeline_id: str):
    try:
        target_url = f"{os.getenv('ML_SERVICE_URL')}/api/{pipeline_id}/result"
        response = requests.get(target_url)
        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to connect to ml service", "details": str(e)}), 502
    

# Make call to broadcaster service
@app.route('/api/ais/relevant-rooms', methods=['POST'])
def get_tile_rooms_for_viewport():
    """
    Get the rooms the client needs to connect to in order to receive AIS updates for a
    particular region. Forwards this request to the ws-broadcaster service to keep these
    implementation-specific details (the room-naming conventions) contained.

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
        target_url = f"{os.getenv('BROADCASTER_SERVICE_URL')}/api/relevant-rooms"
        response = requests.post(target_url, json=request.get_json())
        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to connect to {target_url}", "details": str(e)}), 502
    

# Make call to broadcaster service
@app.route('/api/ais/ships-within-bounds', methods=['POST'])
def get_ships_within_bounds():
    """
    Returns AIS-detected ships contained within a particular region. Forwards this request
    to the repository service to keep database access restricted to repository.

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
        List of ships

    """
    try:
        target_url = f"{os.getenv('REPOSITORY_SERVICE_URL')}/api/ships-within-bounds"
        headers = dict(request.headers)
        response = requests.post(target_url, headers=headers, json=request.get_json())
        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to connect to {target_url}", "details": str(e)}), 502
    

@app.route('/api/ais/history/<int:mmsi>', methods=['GET'])
def get_history(mmsi: int):
    try:
        target_url = f"{os.getenv('REPOSITORY_SERVICE_URL')}/api/history/{mmsi}"
        response = requests.get(target_url)
        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to connect to {target_url}", "details": str(e)}), 502
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
