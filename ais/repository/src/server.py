import psycopg2
import psycopg2.extras
from psycopg2 import OperationalError, pool
from flask import Flask, request, jsonify, make_response
import threading
import os
import json
import requests
from flask_cors import CORS
from db import connect_to_database, find_ships_within_bounds, history_for_mmsi
from query_manager import QueryManager
from settings import Settings


settings = Settings()
    
def create_api() -> Flask:

    app = Flask(__name__)
    CORS(app)

    pg_pool = pool.SimpleConnectionPool(
        minconn=settings.pg_minconn,
        maxconn=settings.pg_maxconn,
        dsn=f"dbname={settings.db_name} user={settings.db_user} password={settings.db_password} host={settings.db_host}"
    )

    query_manager = QueryManager(pg_pool)

    @app.post("/api/ships-within-bounds")
    def ships_within_bounds():
        client_id = request.headers.get("X-Client-ID") or request.remote_addr
        geojson = request.json.get("geojson")
        if not geojson:
            return jsonify({"error": "Missing GeoJSON"}), 400
        
        geometry = geojson.get("geometry")
        if not geometry:
            return jsonify({"error": "GeoJSON is missing required 'geometry' object"}), 400

        try:
            results = query_manager.execute_query(find_ships_within_bounds, client_id, geometry)
            return jsonify(results)
        except psycopg2.errors.QueryCanceled as e:
            print(f"Query for client {client_id} was cancelled")
            return jsonify([])
        except Exception as e:
            print("Query failed:", e)
            return jsonify({"error": "Query failed"}), 500
        
    @app.route('/api/history/<int:mmsi>', methods=['GET'])
    def get_history(mmsi: int):
        try:
            connection = pg_pool.getconn()
            results = history_for_mmsi(mmsi, connection)
            return jsonify(results), 200

        except Exception as e:
            return jsonify({"error": "Failed to retrieve history data", "details": str(e)}), 500
    
        finally:
            pg_pool.putconn(connection)

    return app
    