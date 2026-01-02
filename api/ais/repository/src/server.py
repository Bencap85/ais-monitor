import psycopg2
import psycopg2.extras
from psycopg2 import OperationalError, pool
from flask import Flask, request, jsonify, make_response, current_app
import threading
import os
import json
import logging
import requests
from flask_cors import CORS
from db import connect_to_database, find_ships_within_bounds, history_for_mmsi
from query_manager import QueryManager
from config import settings
from coordinate_utils.utils import normalize_coordinates

logger = logging.getLogger(__name__)

BASE_PATH = settings.base_path
    
def create_api() -> Flask:

    app = Flask(__name__)
    CORS(app)

    pg_pool = pool.SimpleConnectionPool(
        minconn=settings.pg_minconn,
        maxconn=settings.pg_maxconn,
        dsn=f"dbname={settings.db_name} user={settings.db_user} password={settings.db_password} host={settings.db_host}"
    )

    query_manager = QueryManager(pg_pool)

    @app.post(f"{BASE_PATH}/ships-within-bounds")
    def ships_within_bounds():
        """
        Returns ships detected via AIS within a particular region.

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
        client_id = request.headers.get("X-Client-ID") or request.remote_addr

        try:
            geojson = request.json.get("geojson")
            geometry = geojson["geometry"]
            coordinates = geometry["coordinates"]
        except (KeyError, TypeError) as k:
            logger.info(f"Invalid request, {request.json}")
            return jsonify({"error": "Invalid request", "reason": str(k)}), 400

        try:
            normalized_coordinates = normalize_coordinates(coordinates)
            geometry["coordinates"] = normalized_coordinates
            results = query_manager.execute_query(find_ships_within_bounds, client_id, geometry)
            return jsonify(results)
        
        except psycopg2.errors.QueryCanceled as e:
            logger.info(f"Query for client {client_id} was cancelled")
            return jsonify([])
        except Exception as e:
            logger.error("Request failed:", e)
            return jsonify({"error": "Request failed"}), 500
        
    @app.route(f'{BASE_PATH}/history/<int:mmsi>', methods=['GET'])
    def get_history(mmsi: int):
        try:
            connection = pg_pool.getconn()
            results = history_for_mmsi(mmsi, connection)
            return jsonify(results), 200

        except Exception as e:
            return jsonify({"error": "Failed to retrieve history data", "details": str(e)}), 500
    
        finally:
            pg_pool.putconn(connection)

    @app.route(f"{BASE_PATH}/metrics", methods=["GET"])
    def get_metrics():
        metrics = current_app.consumer.get_metrics()
        return metrics
    
    @app.route(f"{BASE_PATH}/health", methods=["GET"])
    def health_check():
        return {"status": "ok"}, 200

    return app
    