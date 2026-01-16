from flask import Flask, g, redirect, url_for, abort, render_template, request, jsonify
from shapely.geometry import shape, Point
from datetime import datetime, timedelta
import json, time, os, re
import numpy as np
from collections import Counter
import psycopg2


app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    points = dict()
    points = []

    # All high traffic volume locations
    connection = psycopg2.connect(host = '127.0.0.1', database = 'postgres', user = 'postgres', password = 'postgres')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM realtimetraffic WHERE level = %s;', ('High',))
    result = cursor.fetchall()
    for x in result:
        points.append({"latitude": x[2], "longitude": x[3], "extra": x[8]-x[9]})
    return render_template("index.html", title="TrafficAdvisor: Real-Time Traffic Monitoring", points=points)




@app.route("/search")
def search():
    coordinate = request.args.get("coordinate")

    # ✅ validate input
    if not coordinate or "," not in coordinate:
        return jsonify({"error": "Invalid coordinate"}), 400

    lat_str, lon_str = coordinate.split(",")
    try:
        lat = float(lat_str.strip())
        lon = float(lon_str.strip())
    except ValueError:
        return jsonify({"error": "Coordinate must be numeric"}), 400

    connection = psycopg2.connect(
        host="127.0.0.1",
        database="postgres",
        user="postgres",
        password="postgres"
    )
    cursor = connection.cursor()

    # ✅ Use PostGIS distance nearest point
    sql = """
        SELECT
            location, current, historical, level, type, highway, lane,
            ST_Distance(
                ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                geom
            ) AS distance
        FROM realtimetraffic
        WHERE geom IS NOT NULL
        ORDER BY distance
        LIMIT 1;
    """

    cursor.execute(sql, (lon, lat))
    row = cursor.fetchone()

    cursor.close()
    connection.close()

    # ✅ If table empty OR no geom rows
    if row is None:
        return jsonify({
            "location": "No data available",
            "current": 0,
            "historical": 0,
            "level": "No Data",
            "type": "-",
            "highway": "-",
            "lane": 0
        }), 200

    # ✅ row mapping
    results = {
        "location": row[0],
        "current": row[1] if row[1] is not None else 0,
        "historical": row[2] if row[2] is not None else 0,
        "level": row[3] if row[3] is not None else "Unknown",
        "type": row[4] if row[4] is not None else "-",
        "highway": row[5] if row[5] is not None else "-",
        "lane": row[6] if row[6] is not None else 0
    }

    return jsonify(results)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
