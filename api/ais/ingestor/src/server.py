from flask import Flask, request, jsonify, make_response, current_app
from flask_cors import CORS


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    @app.route("/api/metrics", methods=["GET"])
    def get_metrics():
        metrics = current_app.producer.get_metrics()
        return metrics
    
    return app