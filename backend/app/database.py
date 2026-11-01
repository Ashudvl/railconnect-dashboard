import sqlite3
import json
import io
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from .config import DB_PATH
from .models import FailoverEvent

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS telemetry_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                train_id TEXT,
                train_km REAL,
                speed_kmh REAL,
                lat REAL,
                lng REAL,
                zone TEXT,
                zone_type TEXT,
                active_link_id TEXT,
                data_json TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS failover_events (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                from_link TEXT NOT NULL,
                to_link TEXT NOT NULL,
                from_link_name TEXT,
                to_link_name TEXT,
                reason TEXT,
                trigger TEXT,
                duration_ms REAL,
                quality_gain REAL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_telemetry_ts ON telemetry_history(timestamp);
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_ts ON failover_events(timestamp);
        """)
    conn.close()

# Ensure tables exist immediately
init_db()

def record_telemetry(snapshot: Dict[str, Any]):
    try:
        conn = get_connection()
        train = snapshot["train"]
        with conn:
            conn.execute("""
                INSERT INTO telemetry_history 
                (timestamp, train_id, train_km, speed_kmh, lat, lng, zone, zone_type, active_link_id, data_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                snapshot["timestamp"],
                train.get("train_id", "RC-709"),
                train.get("progress_pct", 0.0),
                train.get("speed_kmh", 0.0),
                train.get("lat", 0.0),
                train.get("lng", 0.0),
                train.get("current_zone", ""),
                train.get("zone_type", "rural"),
                snapshot.get("active_link_id", ""),
                json.dumps(snapshot)
            ))
            # Keep table from growing indefinitely (e.g. max 5000 records)
            conn.execute("""
                DELETE FROM telemetry_history WHERE id IN (
                    SELECT id FROM telemetry_history ORDER BY id DESC LIMIT -1 OFFSET 5000
                )
            """)
        conn.close()
    except Exception as e:
        print(f"Error recording telemetry: {e}")

def record_failover_event(event: FailoverEvent):
    try:
        conn = get_connection()
        with conn:
            conn.execute("""
                INSERT INTO failover_events 
                (id, timestamp, from_link, to_link, from_link_name, to_link_name, reason, trigger, duration_ms, quality_gain)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.id,
                event.timestamp,
                event.from_link,
                event.to_link,
                event.from_link_name,
                event.to_link_name,
                event.reason,
                event.trigger,
                event.duration_ms,
                event.quality_gain
            ))
            conn.execute("""
                DELETE FROM failover_events WHERE id NOT IN (
                    SELECT id FROM failover_events ORDER BY timestamp DESC LIMIT 500
                )
            """)
        conn.close()
    except Exception as e:
        print(f"Error recording failover event: {e}")

def get_telemetry_history(limit: int = 60) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT data_json FROM telemetry_history ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    # Return in chronological order
    results = [json.loads(r["data_json"]) for r in reversed(rows)]
    return results

def get_recent_failover_events(limit: int = 20) -> List[FailoverEvent]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM failover_events ORDER BY timestamp DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    events = []
    for r in rows:
        events.append(FailoverEvent(
            id=r["id"],
            timestamp=r["timestamp"],
            from_link=r["from_link"],
            to_link=r["to_link"],
            from_link_name=r["from_link_name"] or r["from_link"],
            to_link_name=r["to_link_name"] or r["to_link"],
            reason=r["reason"] or "",
            trigger=r["trigger"] or "threshold_policy",
            duration_ms=r["duration_ms"] or 45.0,
            quality_gain=r["quality_gain"] or 0.0
        ))
    return events

def export_csv_stream() -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT timestamp, train_km, speed_kmh, lat, lng, zone, active_link_id, data_json 
        FROM telemetry_history ORDER BY id ASC LIMIT 2000
    """)
    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "timestamp", "train_km", "speed_kmh", "lat", "lng", "zone", "active_link",
        "5g_alpha_bandwidth", "5g_alpha_latency", "5g_alpha_loss", "5g_alpha_score",
        "5g_beta_bandwidth", "5g_beta_latency", "5g_beta_loss", "5g_beta_score",
        "starlink_bandwidth", "starlink_latency", "starlink_loss", "starlink_score",
        "station_wifi_bandwidth", "station_wifi_score"
    ])

    for r in rows:
        try:
            data = json.loads(r["data_json"])
            links = data.get("links", {})
            p = links.get("wan_5g_primary", {})
            s = links.get("wan_5g_secondary", {})
            sat = links.get("wan_satellite", {})
            wf = links.get("wan_trackside_wifi", {})

            writer.writerow([
                r["timestamp"],
                r["train_km"],
                r["speed_kmh"],
                r["lat"],
                r["lng"],
                r["zone"],
                r["active_link_id"],
                p.get("bandwidth", 0), p.get("latency", 0), p.get("packet_loss", 0), p.get("score", 0),
                s.get("bandwidth", 0), s.get("latency", 0), s.get("packet_loss", 0), s.get("score", 0),
                sat.get("bandwidth", 0), sat.get("latency", 0), sat.get("packet_loss", 0), sat.get("score", 0),
                wf.get("bandwidth", 0), wf.get("score", 0),
            ])
        except Exception:
            continue

    return output.getvalue()
