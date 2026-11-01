from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = os.getenv("RAILCONNECT_DB", str(DATA_DIR / "railconnect.db"))
TICK_INTERVAL_SECONDS = float(os.getenv("TICK_INTERVAL", "1.0"))
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

WAN_LINKS_CONFIG = {
    "wan_5g_primary": {
        "name": "5G Carrier Alpha",
        "type": "cellular",
        "band": "5G C-Band (High Band)",
        "nominal_bandwidth": 65.0, # Realistic high-speed cellular throughput
        "nominal_latency": 26.0,
        "nominal_jitter": 5.0,
        "nominal_loss": 0.3,
        "color": "#38bdf8", # Sky blue
    },
    "wan_5g_secondary": {
        "name": "5G Carrier Beta",
        "type": "cellular",
        "band": "5G Sub-6 GHz (Coverage Band)",
        "nominal_bandwidth": 78.0, # Better in outer sectors
        "nominal_latency": 24.0,
        "nominal_jitter": 4.0,
        "nominal_loss": 0.2,
        "color": "#a855f7", # Purple
    },
    "wan_satellite": {
        "name": "Starlink LEO Rail-Link",
        "type": "satellite",
        "band": "Ku/Ka Band LEO",
        "nominal_bandwidth": 140.0,
        "nominal_latency": 38.0,
        "nominal_jitter": 7.0,
        "nominal_loss": 0.4,
        "color": "#f59e0b", # Amber
    },
    "wan_trackside_wifi": {
        "name": "Trackside Station Wi-Fi 6E",
        "type": "wifi",
        "band": "6 GHz 802.11ax Gigabit",
        "nominal_bandwidth": 850.0,
        "nominal_latency": 4.5,
        "nominal_jitter": 1.0,
        "nominal_loss": 0.02,
        "color": "#10b981", # Emerald green
    },
}
