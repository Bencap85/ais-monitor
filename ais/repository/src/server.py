import psycopg2
import psycopg2.extras
from psycopg2 import OperationalError
from flask import Flask, request, jsonify, make_response
import threading
import os
import json
import requests
from flask_cors import CORS


def connect_to_database():
    print("Attempting to connect to database...")
    try:
        connection = psycopg2.connect(
            dbname="ais_data",
            user="postgres",
            password="postgres",
            host="host.docker.internal",
            port="5432"     
        )
        print("Connected to database")
        return connection
    except OperationalError as e:
        print(f"Database connection failed: {e}")
        return None
    

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
                id,
                mmsi AS "UserID",
                navigational_status AS "NavigationalStatus",
                ST_Y(position::geometry) AS "Latitude",
                ST_X(position::geometry) AS "Longitude",
                sog_knots AS "Sog",
                timestamp AS "Timestamp",
                true_heading AS "TrueHeading"
            FROM ais_ships
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
    


if __name__ == '__main__':
    print("Starting http server...")
    app.run(host='0.0.0.0', port=8080)
    