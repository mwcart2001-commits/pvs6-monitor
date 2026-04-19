from flask import Flask, jsonify, render_template_string
import sqlite3
import datetime

app = Flask(__name__)

DB_PATH = "pvs6.db"

def get_latest_reading():
    """Fetch the most recent reading from the database."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT ts, solar, home, grid FROM readings ORDER BY ts DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if row:
        ts, solar, home, grid = row
        return {"timestamp": ts, "solar": solar, "home": home, "grid": grid}
    return None

@app.route("/")
def dashboard():
    """Serve a simple HTML dashboard."""
    reading = get_latest_reading()
    if not reading:
        return "<h1>No data yet</h1><p>Run the polling script first.</p>"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>PVS6 Solar Dashboard</title>
        <meta http-equiv="refresh" content="30">  <!-- Auto-refresh every 30s -->
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .metric {{ background: #f0f0f0; padding: 10px; margin: 10px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>PVS6 Solar Monitor</h1>
        <p>Last updated: {reading['timestamp']}</p>
        <div class="metric">
            <h2>Solar Production</h2>
            <p>{reading['solar']} W</p>
        </div>
        <div class="metric">
            <h2>Home Consumption</h2>
            <p>{reading['home']} W</p>
        </div>
        <div class="metric">
            <h2>Grid</h2>
            <p>{reading['grid']} W</p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route("/api/latest")
def api_latest():
    """Serve latest reading as JSON."""
    reading = get_latest_reading()
    if reading:
        return jsonify(reading)
    return jsonify({"error": "No data"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
