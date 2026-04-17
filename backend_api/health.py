from fastapi import APIRouter
from datetime import datetime
import sqlite3
import os

router = APIRouter()

# Path to your SQLite DB (same as collector)
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "pvs6_data.db")

@router.get("/api/health")
def health_check():
    status = {
        "api": "ok",
        "database": "unknown",
        "collector": "unknown",
        "last_reading_timestamp": None,
        "age_seconds": None,
    }

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT timestamp FROM readings ORDER BY timestamp DESC LIMIT 1")
        row = cur.fetchone()
        conn.close()

        status["database"] = "ok"

        if row:
            ts = row[0]
            status["last_reading_timestamp"] = ts
            age = datetime.now() - datetime.fromtimestamp(ts)
            status["age_seconds"] = age.total_seconds()

            # Collector freshness check (20s interval → allow up to 40s)
            if age.total_seconds() < 40:
                status["collector"] = "ok"
            else:
                status["collector"] = "stale"
        else:
            status["collector"] = "no_data"

    except Exception as e:
        status["database"] = f"error: {e}"

    return status
