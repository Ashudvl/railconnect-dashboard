import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import List, Set

from .config import TICK_INTERVAL_SECONDS, BASE_DIR
from .database import (
    init_db, get_telemetry_history, get_recent_failover_events, export_csv_stream
)
from .models import ControlCommand
from .simulator import simulator_engine
from .route_data import ROUTE_CORRIDOR

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, message: dict):
        dead_connections = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.add(connection)
        for dead in dead_connections:
            self.active_connections.discard(dead)

ws_manager = ConnectionManager()

# Background simulator loop
async def simulation_worker():
    while True:
        try:
            snapshot = simulator_engine.update_telemetry(TICK_INTERVAL_SECONDS)
            await ws_manager.broadcast(snapshot)
        except Exception as e:
            print(f"Simulation loop error: {e}")
        await asyncio.sleep(TICK_INTERVAL_SECONDS)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    sim_task = asyncio.create_task(simulation_worker())
    yield
    # Shutdown
    sim_task.cancel()

app = FastAPI(
    title="RailConnect Control Center API",
    version="2.0.0",
    description="Intelligent Multi-WAN Telemetry, Predictive Failover, and Fleet Orchestration Platform",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/status")
async def get_status():
    """Returns current live system telemetry."""
    return simulator_engine.update_telemetry(0.0)

@app.get("/api/route")
async def get_route():
    """Returns railway corridor infrastructure, stations, and towers."""
    return ROUTE_CORRIDOR

@app.get("/api/history")
async def get_history(limit: int = 60):
    """Returns recent time-series telemetry snapshots for charts and playback."""
    return get_telemetry_history(limit)

@app.get("/api/events")
async def get_events(limit: int = 30):
    """Returns log of network failover events."""
    return get_recent_failover_events(limit)

@app.post("/api/control")
async def send_control(cmd: ControlCommand):
    """Executes manual operator override or scenario disruption injection."""
    result = simulator_engine.handle_command(cmd)
    # Broadcast state change immediately
    snapshot = simulator_engine.update_telemetry(0.0)
    await ws_manager.broadcast(snapshot)
    return result

@app.post("/api/telemetry/ingest")
async def ingest_telemetry(payload: dict):
    """
    Ingests live external telemetry from physical train gateways / edge routers.
    Calculates link scores, runs ML failover prediction, and streams to connected dashboards.
    """
    snapshot = simulator_engine.ingest_live_telemetry(payload)
    await ws_manager.broadcast(snapshot)
    return {"status": "success", "active_link": snapshot["active_link_id"], "risk_score": snapshot["prediction"]["risk_score"]}

@app.get("/api/export", response_class=PlainTextResponse)
async def export_csv():
    """Exports all recorded telemetry to CSV format."""
    csv_data = export_csv_stream()
    return PlainTextResponse(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=railconnect_telemetry_export.csv"}
    )

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    """Real-time 1Hz streaming WebSocket endpoint for frontend dashboards."""
    await ws_manager.connect(websocket)
    try:
        # Immediately send current state on connect
        snapshot = simulator_engine.update_telemetry(0.0)
        await websocket.send_json(snapshot)
        while True:
            # Client can send control messages or keep-alive pings
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)

# Serve built frontend if dist exists
FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(FRONTEND_DIST / "index.html"))
