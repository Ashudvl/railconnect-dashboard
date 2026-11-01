import math
import random
import time
from datetime import datetime
from typing import Dict, List, Optional
import uuid

from .config import WAN_LINKS_CONFIG
from .models import (
    WanTelemetry, TrainTelemetry, FailoverEvent, MlPrediction,
    DisruptionState, SystemState, ControlCommand, CoachLanStatus, TrainLanTelemetry
)
from .route_data import (
    ROUTE_CORRIDOR, get_position_at_km, get_zone_at_km, get_next_station_info
)
from .database import record_telemetry, record_failover_event
from .ml_engine import FailoverPredictor

class TrainNetworkSimulator:
    def __init__(self):
        self.train_id = "RC-709"
        self.train_name = "AeroSpeed Express X-1"
        self.current_km = 4.0
        self.speed_kmh = 220.0
        self.direction = 1 # 1: forward, -1: reverse

        # WAN States
        self.active_link_id = "wan_5g_primary"
        self.auto_failover_enabled = True
        self.ml_proactive_enabled = True

        # Disruption injection
        self.disruption = DisruptionState()

        # ML Engine
        self.ml_engine = FailoverPredictor()
        self.latest_prediction: Optional[MlPrediction] = None

        # History of recent failovers
        self.recent_events: List[FailoverEvent] = []
        self.last_switch_time = time.time() - 30.0

        # Initial link state
        self.current_links: Dict[str, WanTelemetry] = {}
        self.update_telemetry(0.0)

    def calculate_link_metrics(self, link_id: str, current_km: float, zone_type: str, dist_to_station: float) -> WanTelemetry:
        cfg = WAN_LINKS_CONFIG[link_id]
        noise = random.uniform(-0.04, 0.04)

        bandwidth = cfg["nominal_bandwidth"]
        latency = cfg["nominal_latency"]
        jitter = cfg["nominal_jitter"]
        loss = cfg["nominal_loss"]
        signal = 85.0

        # Dynamic Route Progression along 16.0 km corridor:

        # PHASE 1: km 0.0 to 2.5 (Metro Departure: Alpha starts strong, then fades; Beta climbs to #1)
        if current_km < 2.5:
            if link_id == "wan_5g_primary":
                if current_km < 0.9:
                    bandwidth = 72.0
                    latency = 19.0
                    signal = 95.0
                else:
                    # Alpha carrier fading rapidly as train departs city mast
                    decay = (current_km - 0.9) / 1.6
                    bandwidth = max(10.0, 72.0 - decay * 62.0)
                    latency = 19.0 + decay * 75.0
                    loss = 0.2 + decay * 3.8
                    signal = max(24.0, 95.0 - decay * 71.0)
            elif link_id == "wan_5g_secondary":
                # Beta carrier climbing to peak as train approaches Beta Ridge Tower (km 3.8)
                climb = min(1.0, current_km / 2.5)
                bandwidth = 48.0 + climb * 40.0 # reaches 88.0 Mbps
                latency = 28.0 - climb * 9.0 # reaches 19.0 ms
                loss = 0.15
                signal = 65.0 + climb * 31.0 # reaches 96%
            elif link_id == "wan_satellite":
                # Starlink has catenary & overpass attenuation in metro/suburban area
                bandwidth = 38.0
                latency = 65.0
                loss = 1.5
                signal = 62.0

        # PHASE 2: km 2.5 to 5.5 (Ridge Sector: Beta is undisputed King!)
        elif 2.5 <= current_km < 5.5:
            if link_id == "wan_5g_primary":
                # Alpha is out of range / congested
                bandwidth = 11.0 + random.uniform(-2, 2)
                latency = 98.0 + random.uniform(-5, 10)
                loss = 3.8 + random.uniform(0, 0.5)
                signal = 25.0
            elif link_id == "wan_5g_secondary":
                # Beta is prime (Sub-6 GHz Ridge Tower)
                bandwidth = 88.0 + random.uniform(-3, 4)
                latency = 19.0 + random.uniform(-1, 2)
                loss = 0.1
                signal = 96.0
            elif link_id == "wan_satellite":
                bandwidth = 45.0
                latency = 58.0
                loss = 1.0
                signal = 68.0

        # PHASE 3: km 5.5 to 7.5 (Canyon / Mountain Gorge: Cellular fades, Starlink dominates)
        elif 5.5 <= current_km < 7.5:
            if link_id == "wan_5g_primary":
                bandwidth = max(4.0, 11.0 - (current_km - 5.5) * 3.5)
                latency = 125.0 + (current_km - 5.5) * 35.0
                loss = 4.2 + (current_km - 5.5) * 2.0
                signal = max(14.0, 25.0 - (current_km - 5.5) * 6.0)
            elif link_id == "wan_5g_secondary":
                # Beta shadow fading in canyon
                decay = (current_km - 5.5) / 2.0
                bandwidth = max(11.0, 88.0 - decay * 77.0)
                latency = 19.0 + decay * 105.0
                loss = 0.1 + decay * 4.2
                signal = max(22.0, 96.0 - decay * 74.0)
            elif link_id == "wan_satellite":
                # Clear open sky overhead in canyon!
                bandwidth = 165.0 + random.uniform(-5, 10)
                latency = 34.0 + random.uniform(-2, 2)
                loss = 0.1
                signal = 98.0

        # PHASE 4: km 7.5 to 11.0 (Mount Kestrel Tunnel: Complete WAN Blackout!)
        elif 7.5 <= current_km < 11.0:
            if link_id in ["wan_5g_primary", "wan_5g_secondary"]:
                # Deep granite tunnel attenuates cellular signals completely
                signal = max(2.0, random.uniform(3.0, 8.0))
                bandwidth = random.uniform(0.5, 1.8)
                latency = random.uniform(260.0, 420.0)
                jitter = random.uniform(40.0, 80.0)
                loss = random.uniform(18.0, 32.0)
            elif link_id == "wan_satellite":
                # Zero line of sight inside solid mountain tunnel
                signal = 0.0
                bandwidth = 0.0
                latency = 999.0
                jitter = 0.0
                loss = 100.0
            elif link_id == "wan_trackside_wifi":
                signal = 0.0
                bandwidth = 0.0
                latency = 999.0
                loss = 100.0

        # PHASE 5: km 11.0 to 16.0 (Tunnel Egress & Station Arrival)
        else:
            if link_id == "wan_satellite":
                bandwidth = 145.0 + random.uniform(-5, 8)
                latency = 37.0
                signal = 92.0
            elif link_id == "wan_5g_primary":
                bandwidth = 55.0 + random.uniform(-4, 5)
                latency = 28.0
                signal = 75.0
            elif link_id == "wan_5g_secondary":
                bandwidth = 65.0 + random.uniform(-4, 6)
                latency = 25.0
                signal = 82.0

        # Trackside Station Wi-Fi 6E (active near Central Union km 0 or Alpine Grand km 16)
        if link_id == "wan_trackside_wifi":
            if current_km < 7.5 or current_km >= 11.0:
                if dist_to_station < 0.8:
                    signal = 98.0
                    bandwidth = 850.0 + random.uniform(-30, 40)
                    latency = 4.2 + random.uniform(-0.4, 0.6)
                    jitter = 0.8
                    loss = 0.01
                elif dist_to_station < 1.6:
                    ratio = (1.6 - dist_to_station) / 0.8
                    signal = 65.0 * ratio
                    bandwidth = 350.0 * ratio
                    latency = 10.0
                    loss = 0.4
                else:
                    signal = 0.0
                    bandwidth = 0.0
                    latency = 999.0
                    loss = 100.0
            else:
                signal = 0.0
                bandwidth = 0.0
                latency = 999.0
                loss = 100.0

        # Apply manual disruptions if any
        if self.disruption.type:
            if self.disruption.type == "tunnel":
                if link_id in ["wan_5g_primary", "wan_5g_secondary"]:
                    signal = min(signal, 10.0)
                    bandwidth = min(bandwidth, 1.5)
                    latency = max(latency, 310.0)
                    loss = max(loss, 22.0)
                elif link_id == "wan_satellite":
                    signal = 0.0
                    bandwidth = 0.0
                    latency = 999.0
                    loss = 100.0

            elif self.disruption.type == "carrier_fade" and link_id == "wan_5g_primary":
                signal = 18.0
                bandwidth = 4.5
                latency = 310.0
                jitter = 45.0
                loss = 14.5

            elif self.disruption.type == "satellite_obstruction" and link_id == "wan_satellite":
                signal = 15.0
                bandwidth = 8.0
                latency = 420.0
                loss = 22.0

            elif self.disruption.type == "packet_storm" and link_id == self.active_link_id:
                loss = max(loss, 19.5)
                latency = max(latency, 195.0)
                bandwidth = bandwidth * 0.25

        # Small natural variance
        if signal > 0:
            bandwidth = max(0.5, bandwidth * (1 + noise))
            latency = max(3.0, latency * (1 + noise * 0.5))
            signal = max(0.0, min(100.0, signal + noise * 10.0))

        # Composite Quality Score calculation (0 to 100)
        if signal <= 2.0 or loss >= 90.0:
            score = 0.0
            status = "offline"
        else:
            lat_score = max(0.0, min(100.0, 100.0 - (latency - 5.0) * (100.0 / 220.0)))
            bw_score = max(0.0, min(100.0, (bandwidth / 150.0) * 100.0))
            loss_score = max(0.0, min(100.0, 100.0 - loss * 10.0))
            sig_score = signal

            score = round(
                0.35 * bw_score +
                0.30 * lat_score +
                0.25 * loss_score +
                0.10 * sig_score,
                1
            )
            score = max(0.0, min(100.0, score))

            if score >= 70.0:
                status = "active" if link_id == self.active_link_id else "standby"
            elif score >= 42.0:
                status = "degraded"
            else:
                status = "offline"

        return WanTelemetry(
            id=link_id,
            name=cfg["name"],
            type=cfg["type"],
            band=cfg["band"],
            bandwidth=round(bandwidth, 1),
            latency=round(latency, 1),
            jitter=round(jitter, 1),
            packet_loss=round(loss, 2),
            signal=round(signal, 1),
            score=score,
            status=status,
            is_active=(link_id == self.active_link_id),
            color=cfg["color"]
        )

    def trigger_failover(self, target_link_id: str, reason: str, trigger_type: str):
        if target_link_id == self.active_link_id:
            return

        from_link_id = self.active_link_id
        from_link = self.current_links.get(from_link_id)
        to_link = self.current_links.get(target_link_id)

        from_name = from_link.name if from_link else from_link_id
        to_name = to_link.name if to_link else target_link_id
        quality_gain = round((to_link.score - (from_link.score if from_link else 0)), 1)

        event = FailoverEvent(
            id=f"fo-{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now().strftime("%H:%M:%S"),
            from_link=from_link_id,
            to_link=target_link_id,
            from_link_name=from_name,
            to_link_name=to_name,
            reason=reason,
            trigger=trigger_type,
            duration_ms=round(random.uniform(28.0, 52.0), 1),
            quality_gain=quality_gain
        )

        self.active_link_id = target_link_id
        self.last_switch_time = time.time()
        self.recent_events.insert(0, event)
        if len(self.recent_events) > 30:
            self.recent_events.pop()

        record_failover_event(event)
        print(f"[{event.timestamp}] FAILOVER: {from_name} -> {to_name} ({trigger_type}) | Reason: {reason}")

    def calculate_lan_telemetry(self, active_bw: float, is_offline: bool) -> TrainLanTelemetry:
        """
        Dynamically adapts onboard Train LAN traffic shaping & QoS
        based on fluctuating cellular SIM speeds at high train velocities.
        """
        if is_offline or active_bw <= 2.0:
            qos_mode = "critical_only_failsafe"
            crit = min(active_bw, 1.2)
            sys_mbps = max(0.0, active_bw - crit)
            pax = 0.0
            health = 18.0
            ap_state = "failsafe"
        elif active_bw < 30.0:
            # High-speed SIM throttling mode
            qos_mode = "adaptive_throttling"
            crit = 3.5
            sys_mbps = 5.5
            pax = max(0.8, active_bw - crit - sys_mbps)
            health = 68.0
            ap_state = "throttled"
        else:
            qos_mode = "unconstrained"
            crit = 4.2
            sys_mbps = 14.5
            pax = active_bw - crit - sys_mbps
            health = 96.0
            ap_state = "healthy"

        total_throughput = round(crit + sys_mbps + pax, 1)

        coaches = [
            CoachLanStatus(
                coach_id="ENG-01",
                name="Loco / Driver Cabin",
                connected_clients=6,
                ap_status="healthy",
                allocated_mbps=round(crit * 0.9, 1),
                rx_mbps=round(crit * 0.7, 1),
                tx_mbps=round(crit * 0.2, 1)
            ),
            CoachLanStatus(
                coach_id="C1-EXEC",
                name="Coach C1 (Executive)",
                connected_clients=52,
                ap_status=ap_state,
                allocated_mbps=round(pax * 0.32, 1),
                rx_mbps=round(pax * 0.28, 1),
                tx_mbps=round(pax * 0.04, 1)
            ),
            CoachLanStatus(
                coach_id="C2-STD",
                name="Coach C2 (Standard)",
                connected_clients=84,
                ap_status=ap_state,
                allocated_mbps=round(pax * 0.26, 1),
                rx_mbps=round(pax * 0.23, 1),
                tx_mbps=round(pax * 0.03, 1)
            ),
            CoachLanStatus(
                coach_id="C3-STD",
                name="Coach C3 (Standard)",
                connected_clients=88,
                ap_status=ap_state,
                allocated_mbps=round(pax * 0.24, 1),
                rx_mbps=round(pax * 0.21, 1),
                tx_mbps=round(pax * 0.03, 1)
            ),
            CoachLanStatus(
                coach_id="PANTRY-SYS",
                name="Pantry & CCTV Server Car",
                connected_clients=48,
                ap_status="healthy" if sys_mbps > 4.0 else "throttled",
                allocated_mbps=round(sys_mbps + pax * 0.18, 1),
                rx_mbps=round(sys_mbps * 0.8, 1),
                tx_mbps=round(sys_mbps * 0.2, 1)
            ),
        ]

        return TrainLanTelemetry(
            lan_gateway_ip="10.120.0.1",
            subnet="10.120.0.0/16",
            total_connected_clients=278,
            total_lan_throughput_mbps=total_throughput,
            lan_health_pct=health,
            qos_mode=qos_mode,
            critical_ops_mbps=round(crit, 1),
            train_systems_mbps=round(sys_mbps, 1),
            passenger_wifi_mbps=round(pax, 1),
            coaches=coaches
        )

    def update_telemetry(self, delta_seconds: float = 1.0):
        # 1. Update train position along corridor (at ~3.0x demo multiplier so full cycle takes ~75s)
        if self.speed_kmh > 0:
            dist_traveled = (self.speed_kmh / 3600.0) * delta_seconds * 3.0
            self.current_km += dist_traveled * self.direction
            
            # Loop route
            if self.current_km >= ROUTE_CORRIDOR["total_length_km"]:
                self.current_km = 0.0 # reset to start
            elif self.current_km < 0:
                self.current_km = ROUTE_CORRIDOR["total_length_km"]

        # 2. Get route context
        lat, lng = get_position_at_km(self.current_km)
        zone_name, zone_type = get_zone_at_km(self.current_km)
        next_station, eta_min = get_next_station_info(self.current_km, self.speed_kmh)

        # Distance to upcoming tunnel (Mount Kestrel is km 7.5 to 11.0)
        if self.current_km < 7.5:
            dist_to_tunnel = 7.5 - self.current_km
        elif 7.5 <= self.current_km <= 11.0:
            dist_to_tunnel = 0.0
        else:
            dist_to_tunnel = 999.0

        # Distance to closest station with Wi-Fi
        dist_to_wifi_station = min([
            abs(st["km"] - self.current_km)
            for st in ROUTE_CORRIDOR["stations"]
            if st.get("has_station_wifi")
        ])

        # 3. Handle disruption timer
        if self.disruption.time_remaining_s > 0:
            self.disruption.time_remaining_s -= int(delta_seconds)
            if self.disruption.time_remaining_s <= 0:
                self.disruption.type = None

        # 4. Calculate metrics for all 4 links with location-specific dynamics
        for link_id in WAN_LINKS_CONFIG:
            self.current_links[link_id] = self.calculate_link_metrics(
                link_id, self.current_km, zone_type, dist_to_wifi_station
            )

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 5. Build TrainTelemetry model
        train = TrainTelemetry(
            train_id=self.train_id,
            name=self.train_name,
            speed_kmh=round(self.speed_kmh, 1),
            lat=round(lat, 4),
            lng=round(lng, 4),
            progress_pct=round((self.current_km / ROUTE_CORRIDOR["total_length_km"]) * 100.0, 1),
            current_zone=f"{zone_name} (km {self.current_km:.1f})",
            zone_type=zone_type,
            tunnel_depth_m=280.0 if zone_type == "tunnel" else None,
            next_station=next_station,
            eta_next_station_min=eta_min,
            active_link_id=self.active_link_id
        )

        # 6. Run ML Failover Predictor
        self.latest_prediction = self.ml_engine.evaluate(
            timestamp=now_str,
            active_link_id=self.active_link_id,
            links=self.current_links,
            train=train,
            dist_to_tunnel_km=dist_to_tunnel
        )

        # 7. Check Proactive or Threshold Failover Decisions
        active_link = self.current_links[self.active_link_id]
        time_since_last_switch = time.time() - self.last_switch_time

        # Allow immediate failover if current link is dead/offline, or after 2.5s hysteresis
        is_link_critical = (active_link.status == "offline" or active_link.score < 30.0)
        can_switch = is_link_critical or (time_since_last_switch >= 2.5)

        if self.auto_failover_enabled and can_switch:
            wifi_link = self.current_links.get("wan_trackside_wifi")
            
            # Check station Wi-Fi opportunity: if available and score > 85
            if wifi_link and wifi_link.score > 85.0 and self.active_link_id != "wan_trackside_wifi":
                self.trigger_failover(
                    "wan_trackside_wifi",
                    f"Ultra-high speed Trackside Wi-Fi detected at {next_station} (850+ Mbps)",
                    "threshold_policy"
                )

            # ML Proactive Switch:
            elif (
                self.ml_proactive_enabled and
                self.latest_prediction.imminent_failover and
                self.latest_prediction.risk_score >= 65.0 and
                self.latest_prediction.predicted_link != self.active_link_id
            ):
                target_link = self.current_links[self.latest_prediction.predicted_link]
                if target_link.score > 55.0:
                    self.trigger_failover(
                        self.latest_prediction.predicted_link,
                        f"ML Proactive Handover: {self.latest_prediction.reasoning}",
                        "ml_proactive"
                    )

            # Reactive Threshold Switch: if current link has degraded
            elif active_link.score < 50.0 or active_link.status == "offline":
                best_candidate = max(self.current_links.values(), key=lambda l: l.score)
                if best_candidate.id != self.active_link_id and best_candidate.score >= 50.0:
                    self.trigger_failover(
                        best_candidate.id,
                        f"Reactive Failover: {active_link.name} degraded (score {active_link.score:.0f})",
                        "threshold_policy"
                    )

        # Refresh is_active flag
        for lid in self.current_links:
            self.current_links[lid].is_active = (lid == self.active_link_id)

        # 8. Dynamically Calculate Onboard Train LAN Telemetry
        active_link_obj = self.current_links.get(self.active_link_id)
        active_bw = active_link_obj.bandwidth if active_link_obj else 0.0
        is_off = (active_link_obj.status == "offline") if active_link_obj else True
        lan_state = self.calculate_lan_telemetry(active_bw, is_off)

        # 9. Record snapshot in SQLite
        snapshot_dict = {
            "timestamp": now_str,
            "train": train.model_dump(),
            "links": {k: v.model_dump() for k, v in self.current_links.items()},
            "active_link_id": self.active_link_id,
            "prediction": self.latest_prediction.model_dump(),
            "lan": lan_state.model_dump(),
            "recent_events": [e.model_dump() for e in self.recent_events[:10]],
            "disruption": self.disruption.model_dump(),
            "auto_failover_enabled": self.auto_failover_enabled,
            "ml_proactive_enabled": self.ml_proactive_enabled
        }
        record_telemetry(snapshot_dict)

        return snapshot_dict

    def ingest_live_telemetry(self, payload: dict) -> dict:
        """
        Accepts real external telemetry from physical train gateways / modems.
        Calculates scores, evaluates ML failover prediction, logs to SQLite,
        and returns updated snapshot.
        """
        if "train_id" in payload:
            self.train_id = str(payload["train_id"])
        if "name" in payload:
            self.train_name = str(payload["name"])
        if "speed_kmh" in payload:
            self.speed_kmh = float(payload["speed_kmh"])

        lat = float(payload.get("lat", 47.6000))
        lng = float(payload.get("lng", -122.3300))
        current_zone = str(payload.get("current_zone", "Active Track"))
        next_station = str(payload.get("next_station", "Upcoming Depot"))
        eta_min = float(payload.get("eta_next_station_min", 12.0))

        # Update WAN links from payload
        input_links = payload.get("links", {})
        for link_id, metrics in input_links.items():
            if link_id in WAN_LINKS_CONFIG:
                cfg = WAN_LINKS_CONFIG[link_id]
                bw = float(metrics.get("bandwidth", cfg["nominal_bandwidth"]))
                lat_ms = float(metrics.get("latency", cfg["nominal_latency"]))
                loss = float(metrics.get("packet_loss", cfg["nominal_loss"]))
                jitter = float(metrics.get("jitter", cfg["nominal_jitter"]))
                sig = float(metrics.get("signal", 80.0))

                # Composite score
                if sig <= 2.0 or loss >= 90.0:
                    score = 0.0
                    status = "offline"
                else:
                    lat_score = max(0.0, min(100.0, 100.0 - (lat_ms - 5.0) * (100.0 / 220.0)))
                    bw_score = max(0.0, min(100.0, (bw / 200.0) * 100.0))
                    loss_score = max(0.0, min(100.0, 100.0 - loss * 10.0))
                    score = round(0.35 * bw_score + 0.30 * lat_score + 0.25 * loss_score + 0.10 * sig, 1)
                    score = max(0.0, min(100.0, score))
                    status = "active" if link_id == self.active_link_id else ("standby" if score >= 70 else "degraded")

                self.current_links[link_id] = WanTelemetry(
                    id=link_id,
                    name=cfg["name"],
                    type=cfg["type"],
                    band=cfg["band"],
                    bandwidth=round(bw, 1),
                    latency=round(lat_ms, 1),
                    jitter=round(jitter, 1),
                    packet_loss=round(loss, 2),
                    signal=round(sig, 1),
                    score=score,
                    status=status,
                    is_active=(link_id == self.active_link_id),
                    color=cfg["color"]
                )

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        train = TrainTelemetry(
            train_id=self.train_id,
            name=self.train_name,
            speed_kmh=round(self.speed_kmh, 1),
            lat=round(lat, 4),
            lng=round(lng, 4),
            progress_pct=round(payload.get("progress_pct", 50.0), 1),
            current_zone=current_zone,
            zone_type=payload.get("zone_type", "rural"),
            tunnel_depth_m=payload.get("tunnel_depth_m", None),
            next_station=next_station,
            eta_next_station_min=eta_min,
            active_link_id=self.active_link_id
        )

        # Run ML engine on real incoming telemetry
        self.latest_prediction = self.ml_engine.evaluate(
            timestamp=now_str,
            active_link_id=self.active_link_id,
            links=self.current_links,
            train=train,
            dist_to_tunnel_km=float(payload.get("dist_to_tunnel_km", 999.0))
        )

        # Proactive failover evaluation
        if self.auto_failover_enabled and self.ml_proactive_enabled and self.latest_prediction.imminent_failover:
            target = self.latest_prediction.predicted_link
            if target != self.active_link_id and self.current_links.get(target) and self.current_links[target].score > 55.0:
                self.trigger_failover(target, f"Proactive Ingest: {self.latest_prediction.reasoning}", "ml_proactive")

        for lid in self.current_links:
            self.current_links[lid].is_active = (lid == self.active_link_id)

        active_link_obj = self.current_links.get(self.active_link_id)
        active_bw = active_link_obj.bandwidth if active_link_obj else 0.0
        is_off = (active_link_obj.status == "offline") if active_link_obj else True
        lan_state = self.calculate_lan_telemetry(active_bw, is_off)

        snapshot_dict = {
            "timestamp": now_str,
            "train": train.model_dump(),
            "links": {k: v.model_dump() for k, v in self.current_links.items()},
            "active_link_id": self.active_link_id,
            "prediction": self.latest_prediction.model_dump(),
            "lan": lan_state.model_dump(),
            "recent_events": [e.model_dump() for e in self.recent_events[:10]],
            "disruption": self.disruption.model_dump(),
            "auto_failover_enabled": self.auto_failover_enabled,
            "ml_proactive_enabled": self.ml_proactive_enabled
        }
        record_telemetry(snapshot_dict)
        return snapshot_dict

    def handle_command(self, cmd: ControlCommand) -> dict:
        if cmd.action == "inject_disruption":
            self.disruption.type = cmd.disruption_type or "tunnel"
            self.disruption.time_remaining_s = cmd.duration_seconds or 15
            return {"status": "ok", "message": f"Injected disruption: {self.disruption.type} for {self.disruption.time_remaining_s}s"}

        elif cmd.action == "clear_disruption":
            self.disruption.type = None
            self.disruption.time_remaining_s = 0
            return {"status": "ok", "message": "Disruptions cleared"}

        elif cmd.action == "manual_switch":
            if cmd.target_link_id and cmd.target_link_id in self.current_links:
                self.trigger_failover(
                    cmd.target_link_id,
                    f"Operator manual override switch to {cmd.target_link_id}",
                    "manual_override"
                )
                return {"status": "ok", "message": f"Switched to {cmd.target_link_id}"}
            return {"status": "error", "message": "Invalid link ID"}

        elif cmd.action == "toggle_auto_failover":
            self.auto_failover_enabled = cmd.enabled if cmd.enabled is not None else not self.auto_failover_enabled
            return {"status": "ok", "auto_failover_enabled": self.auto_failover_enabled}

        elif cmd.action == "toggle_ml_proactive":
            self.ml_proactive_enabled = cmd.enabled if cmd.enabled is not None else not self.ml_proactive_enabled
            return {"status": "ok", "ml_proactive_enabled": self.ml_proactive_enabled}

        elif cmd.action == "set_train_speed":
            if cmd.train_speed is not None:
                self.speed_kmh = max(0.0, min(320.0, cmd.train_speed))
            return {"status": "ok", "speed_kmh": self.speed_kmh}

        elif cmd.action == "reset_route":
            self.current_km = 0.0
            self.active_link_id = "wan_5g_primary"
            self.last_switch_time = 0.0
            return {"status": "ok", "message": "Train reset to start of route with 5G Carrier Alpha"}

        return {"status": "error", "message": f"Unknown action: {cmd.action}"}

# Global simulator singleton
simulator_engine = TrainNetworkSimulator()
