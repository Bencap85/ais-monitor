from flask import Flask, request, jsonify, make_response, current_app
from flask_cors import CORS
from config import settings


BASE_PATH = settings.base_path

def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    @app.route(f"{BASE_PATH}/metrics", methods=["GET"])
    def get_metrics():
        metrics = current_app.producer.get_metrics()
        return metrics
    
    @app.route(f"{BASE_PATH}/health", methods=["GET"])
    def health_check():
        return {"status": "ok"}, 200
    
    return app