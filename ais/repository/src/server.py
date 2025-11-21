import psycopg2
import psycopg2.extras
from psycopg2 import OperationalError
from flask import Flask, request, jsonify, make_response
import threading
import os
import json
import requests
from flask_cors import CORS
from db import connect_to_database
    
def create_api() -> Flask:

    app = Flask(__name__)
    CORS(app)

    connection = connect_to_database()

    @app.post("/api/ships-within-bounds")
    def ships_within_bounds():
        geojson = request.json.get("geojson")
        if not geojson:
            return jsonify({"error": "Missing GeoJSON"}), 400
        
        geometry = geojson.get("geometry")
        if not geometry:
            return jsonify({"error": "GeoJSON is missing required 'geometry' object"}), 400

        try:
            cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            query = """
                SELECT
                    ais_ships.id,
                    ais_ships.mmsi AS "UserID",
                    ais_ships.navigational_status AS "NavigationalStatus",
                    ST_Y(position::geometry) AS "Latitude",
                    ST_X(position::geometry) AS "Longitude",
                    ais_ships.sog_knots AS "Sog",
                    ais_ships.timestamp AS "Timestamp",
                    ais_ships.true_heading AS "TrueHeading",
                    ship_static_data.name AS "Name",
                    ship_static_data.call_sign AS "CallSign",
                    ship_type.type_name AS "ShipTypeName"
                FROM ais_ships 
                LEFT JOIN ship_static_data
                    ON ais_ships.mmsi = ship_static_data.mmsi
                LEFT JOIN ship_type
                    ON ship_static_data.ship_type = ship_type.type_code
                WHERE ST_Within(position::geometry, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326));
            """
            print("Executing spatial query with geometry:", json.dumps(geometry))
            cursor.execute(query, (json.dumps(geometry),))
            results = cursor.fetchall()
            return jsonify(results)
        
        except Exception as e:
            print("Query failed:", e)
            return jsonify({"error": "Query failed"}), 500
        
    @app.route('/api/history/<int:mmsi>', methods=['GET'])
    def get_history(mmsi: int):
        try:
            cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            query = """
                SELECT
                    id,
                    mmsi AS "UserID",
                    navigational_status AS "NavigationalStatus",
                    ST_Y(position::geometry) AS "Latitude",
                    ST_X(position::geometry) AS "Longitude",
                    sog_knots AS "Sog",
                    timestamp AS "Timestamp",
                    true_heading AS "TrueHeading"
                FROM ais_ships_history
                WHERE mmsi = %s
                ORDER BY timestamp DESC;
            """
            cursor.execute(query, (mmsi,))
            results = cursor.fetchall()
            return jsonify(results), 200

        except Exception as e:
            return jsonify({"error": "Failed to retrieve history data", "details": str(e)}), 500
    
    return app
    