# 🚄 RailConnect 2.0 — Intelligent Autonomous Multi-WAN Control Center

**RailConnect 2.0** is an enterprise-grade high-speed railway onboard network management and failover orchestration platform. It continuously evaluates multiple heterogeneous wireless uplinks (**Dual 5G Cellular carriers**, **Starlink LEO Satellite**, and **Gigabit Trackside Wi-Fi 6E**), predicting signal degradation and performing seamless, proactive handovers before passenger connectivity drops.

---

## 🌟 Key Features

### 1. 📡 Multi-Link Autonomous Uplink Matrix
Expands far beyond legacy dual-WAN into 4 concurrent heterogeneous links:
- **5G Carrier Alpha**: C-Band / mmWave high-throughput cellular (up to 350 Mbps, ~18ms latency).
- **5G Carrier Beta**: Sub-6 GHz wide-area cellular for robust coverage.
- **Starlink LEO Rail-Link**: Low-Earth Orbit satellite link providing uninterrupted open-country & mountain canyon connectivity (up to 220 Mbps).
- **Trackside Station Wi-Fi 6E**: Gigabit ultra-low-latency trackside connectivity automatically engaged at station stops (~850 Mbps, 4ms latency).

### 2. 🧠 Random Forest ML Proactive Failover Engine
- Evaluates real-time RF signal decay rate, latency ramp-up deltas, packet loss surges, and geofenced hazards.
- Provides a **10-second lookahead horizon**: predicts impending link failure *before* it impacts user sessions.
- Generates causal reasoning statements and feature attribution impact metrics.

### 3. 🗺️ Live 120 km High-Speed Corridor Map
- **Pacific Alpine Corridor (Line A1)**: Visualizes 120 kilometers of electrified high-speed track.
- Real-time train positioning, speed, milestone tracking, and station arrival countdowns.
- Infrastructure overlay displaying 10 cellular base stations with coverage radii and the **Mount Kestrel 10 km Deep Mountain Tunnel (RF Dead Zone)**.

### 4. 🎛️ Interactive Disruption & Stress-Testing Lab
Test failover algorithms with one-click scenario injection:
- 🚇 **Tunnel Entrance**: Simulates cellular and satellite line-of-sight blackout.
- 📡 **5G Carrier Fade**: Injects severe tower congestion and RF attenuation.
- ⛈️ **Starlink Rain Fade**: Simulates severe atmospheric storm degradation.
- 💥 **Packet Storm**: Triggers artificial 20% packet loss.
- 🚄 **Train Speed Regulator**: Adjust cruising speed from 0 to 300 km/h.

### 5. 📊 Real-Time Rolling Telemetry & Historical Playback
- **Live Recharts Telemetry**: 30-second rolling charts for Bandwidth throughput, Latency RTT, and Composite Health Scores.
- **Historical Timeline Scrubber**: Scrub back through past trip events with instant dashboard replay.
- **1-Click CSV Export**: Download time-series telemetry directly from SQLite.

---

## 🏗️ Architecture

```
railconnect-dashboard/
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI app, WebSocket broadcaster & REST endpoints
│   │   ├── config.py           # Multi-WAN configurations & server parameters
│   │   ├── models.py           # Pydantic schemas (WAN telemetry, ML predictions, commands)
│   │   ├── simulator.py        # Physics-based corridor route & RF environmental simulator
│   │   ├── ml_engine.py        # Random Forest predictive failover engine
│   │   ├── route_data.py       # Corridor coordinates, stations, cell towers, tunnels
│   │   └── database.py         # SQLite time-series storage & CSV streaming
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx              # Train speedometer, active link pill, master toggles
│   │   │   ├── NetworkCards.tsx        # 4 WAN telemetry health gauges & manual switch
│   │   │   ├── PredictiveAlerts.tsx    # ML failover risk score & causal reasoning
│   │   │   ├── RouteMap.tsx            # Live corridor route map with towers and tunnels
│   │   │   ├── TelemetryCharts.tsx     # Real-time Recharts rolling trend lines
│   │   │   ├── SimulationControls.tsx  # Disruption injection buttons & speed regulator
│   │   │   ├── EventLog.tsx            # Audit table of seamless handovers
│   │   │   └── TripPlayback.tsx        # Interactive scrubber & CSV export
│   │   ├── hooks/useWebSocket.ts       # 1Hz auto-reconnecting WebSocket client
│   │   ├── types/telemetry.ts          # TypeScript interfaces
│   │   ├── App.tsx                     # Mission control dashboard layout
│   │   └── index.css                   # Tailwind CSS styling & animations
│   ├── package.json
│   └── vite.config.ts
├── legacy/                             # Archived legacy single-file scripts
├── start.sh                            # One-click startup script
└── requirements.txt
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 2. Setup & Installation
```bash
# Clone or enter repository directory
cd railconnect-dashboard

# Install Python backend dependencies
pip install -r requirements.txt

# Install frontend dependencies and build assets
cd frontend
npm install
npm run build
cd ..
```

### 3. Run the Platform
To launch the production server:
```bash
./start.sh
```
Or manually run with uvicorn:
```bash
python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser!

### 4. Development Mode (Hot Reloading)
For active development with Vite HMR:
```bash
# Terminal 1: Backend
python3 -m uvicorn backend.app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```
Open **[http://localhost:5173](http://localhost:5173)** (Vite proxies API & WebSocket traffic to port 8000).

---

## 📡 API Reference

| Endpoint | Protocol | Description |
|---|---|---|
| `/ws/telemetry` | WebSocket | 1.0 Hz real-time streaming telemetry push |
| `GET /api/status` | REST GET | Current system snapshot (train, all links, prediction) |
| `GET /api/route` | REST GET | Corridor waypoints, stations, cell towers, hazard zones |
| `GET /api/history?limit=60` | REST GET | Historical telemetry snapshots |
| `GET /api/events?limit=30` | REST GET | Audit log of failover events |
| `POST /api/control` | REST POST | Manual override, speed change, or disruption injection |
| `GET /api/export` | REST GET | Downloads SQLite telemetry as CSV |

---

## 📜 Legacy Archive
The previous single-file Flask prototypes (`app_*.py`, `simulator_ml.py`, etc.) have been safely organized under `legacy/` for historical reference.
