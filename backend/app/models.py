from __future__ import annotations
from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class WanTelemetry(BaseModel):
    id: str
    name: str
    type: Literal["cellular", "satellite", "wifi"]
    band: str
    bandwidth: float = Field(..., description="Throughput in Mbps")
    latency: float = Field(..., description="Round-trip time in ms")
    packet_loss: float = Field(..., description="Packet loss in percentage")
    jitter: float = Field(default=0.0, description="Jitter in ms")
    signal: float = Field(..., description="Signal strength percentage (0-100)")
    score: float = Field(..., description="Computed composite quality score (0-100)")
    status: Literal["active", "standby", "degraded", "offline"]
    is_active: bool = False
    color: str = "#38bdf8"

class TrainTelemetry(BaseModel):
    train_id: str = "RC-709"
    name: str = "AeroSpeed Express X-1"
    line: str = "Pacific Alpine Corridor"
    speed_kmh: float
    max_speed_kmh: float = 300.0
    lat: float
    lng: float
    progress_pct: float
    current_zone: str
    zone_type: Literal["urban", "rural", "ridge", "gorge", "tunnel", "station"]
    tunnel_depth_m: Optional[float] = None
    next_station: str
    eta_next_station_min: float
    active_link_id: str

class FailoverEvent(BaseModel):
    id: str
    timestamp: str
    from_link: str
    to_link: str
    from_link_name: str
    to_link_name: str
    reason: str
    trigger: Literal["ml_proactive", "threshold_policy", "manual_override"]
    duration_ms: float = 45.0
    quality_gain: float = 0.0

class FactorItem(BaseModel):
    factor: str
    impact: float

class MlPrediction(BaseModel):
    timestamp: str
    imminent_failover: bool
    risk_score: float = Field(..., description="Risk of link failure in next 10s (0-100)")
    predicted_link: str
    predicted_link_name: str
    confidence: float = Field(..., description="Model confidence 0-100%")
    reasoning: str
    top_factors: List[FactorItem] = []

class DisruptionState(BaseModel):
    type: Optional[Literal["tunnel", "carrier_fade", "satellite_obstruction", "packet_storm"]] = None
    intensity: float = 1.0 # 0.0 to 1.0
    time_remaining_s: int = 0
    manual_link_lock: Optional[str] = None

class CoachLanStatus(BaseModel):
    coach_id: str # e.g. "Locomotive Unit", "Coach C1 (Exec)", "Coach C2 (Standard)", "Coach C3", "Pantry & Systems"
    name: str
    connected_clients: int
    ap_status: Literal["healthy", "throttled", "failsafe", "offline"]
    allocated_mbps: float
    rx_mbps: float
    tx_mbps: float

class TrainLanTelemetry(BaseModel):
    lan_gateway_ip: str = "10.120.0.1"
    subnet: str = "10.120.0.0/16"
    total_connected_clients: int = 348
    total_lan_throughput_mbps: float
    lan_health_pct: float
    qos_mode: Literal["unconstrained", "adaptive_throttling", "critical_only_failsafe"]
    # Dynamic QoS Traffic Breakdown:
    critical_ops_mbps: float # Signaling, Driver intercom, Train Diagnostics (Highest priority, 100% SLA)
    train_systems_mbps: float # CCTV compression, Passenger Information Displays (Medium priority)
    passenger_wifi_mbps: float # Guest browsing & streaming (Low priority, dynamically throttled when SIMs drop)
    coaches: List[CoachLanStatus] = []

class SystemState(BaseModel):
    timestamp: str
    train: TrainTelemetry
    links: Dict[str, WanTelemetry]
    active_link_id: str
    prediction: MlPrediction
    lan: TrainLanTelemetry
    recent_events: List[FailoverEvent]
    disruption: DisruptionState
    auto_failover_enabled: bool = True
    ml_proactive_enabled: bool = True

class ControlCommand(BaseModel):
    action: Literal[
        "inject_disruption",
        "clear_disruption",
        "manual_switch",
        "toggle_auto_failover",
        "toggle_ml_proactive",
        "set_train_speed",
        "reset_route"
    ]
    disruption_type: Optional[str] = None
    duration_seconds: Optional[int] = 15
    target_link_id: Optional[str] = None
    train_speed: Optional[float] = None
    enabled: Optional[bool] = None
