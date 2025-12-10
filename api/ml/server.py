from flask import Flask, request, jsonify, make_response
import threading
import os
import json
import requests
from flask_cors import CORS
from model import model_utils
from pipeline import pipeline, pipeline_store

app = Flask(__name__)
CORS(app)


# Create a folder to store tiles
TILE_FOLDER = 'tiles'
os.makedirs(TILE_FOLDER, exist_ok=True)

API_KEY = "52kfErgC1p25crhLeyFZ"

# Replace with your actual tile server URL and API key if needed
TILE_URL_TEMPLATE = "https://api.maptiler.com/maps/satellite/{z}/{x}/{y}.jpg?key={API_KEY}"

@app.route('/api/detect', methods=['POST'])
def detect_tiles():
    data = request.get_json()
    geojson_bounds = data.get("geojson")
    zoom_levels = data.get("zoomLevels")
    pipeline_id = pipeline_store.create_new_pipeline_id()

    # Run pipeline in a background thread
    thread = threading.Thread(target=pipeline.run_pipeline, args=(geojson_bounds, pipeline_id, zoom_levels))
    thread.start()

    response = {
        "pipelineId": pipeline_id,
        "pipelineStatusUrl": f"/api/{pipeline_id}/status",
        "pipelineResultUrl": f"/api/{pipeline_id}/result"
    }

    return make_response(jsonify(response), 202)
    

@app.route('/api/<pipeline_id>/status', methods=['GET'])
def get_pipeline_status(pipeline_id: str):
    status = pipeline_store.get_pipeline_status(pipeline_id)
    if not status:
        return make_response(jsonify({"error": "Pipeline ID not found"}), 404)

    response = {
        "stage": str(status["stage"]),
        "progress": status["progress"]
    }

    return make_response(jsonify(response), 200)


@app.route('/api/<pipeline_id>/result', methods=['GET'])
def get_pipeline_result(pipeline_id):
    result = pipeline_store.get_pipeline_result(pipeline_id)
    if not result:
        return make_response(jsonify({"error": "Pipeline ID not found"}), 404)

    return make_response(jsonify(result), 200)



if __name__ == '__main__':
    model_utils.load_models()
    app.run(host='0.0.0.0', port=8080)
