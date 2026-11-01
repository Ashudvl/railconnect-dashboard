from __future__ import annotations
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from typing import Dict, List, Any, Optional
from collections import deque
from .models import WanTelemetry, MlPrediction, TrainTelemetry

class FailoverPredictor:
    """
    Real-time Machine Learning Predictive Failover Engine.
    Evaluates degradation trends, RF signal degradation rates, latency variance,
    and route geographic features (e.g. upcoming tunnel or canyon).
    """

    def __init__(self):
        self.history: deque = deque(maxlen=30)
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=6,
            random_state=42,
            class_weight="balanced"
        )
        self._bootstrap_model()

    def _bootstrap_model(self):
        # Generate synthetic training scenarios (normal vs imminent degrade)
        # Features: [latency, latency_delta, packet_loss, loss_delta, signal, signal_delta, score, is_tunnel_approaching]
        np.random.seed(42)
        X = []
        y = []

        # Normal scenarios
        for _ in range(300):
            lat = np.random.uniform(15, 40)
            lat_delta = np.random.uniform(-2, 2)
            loss = np.random.uniform(0, 0.5)
            loss_delta = np.random.uniform(-0.1, 0.1)
            sig = np.random.uniform(65, 95)
            sig_delta = np.random.uniform(-3, 3)
            score = np.random.uniform(80, 98)
            tunnel_approaching = 0.0
            X.append([lat, lat_delta, loss, loss_delta, sig, sig_delta, score, tunnel_approaching])
            y.append(0) # No failover needed

        # Imminent Degradation Scenarios (latency spiking, signal crashing, or approaching tunnel)
        for _ in range(300):
            lat = np.random.uniform(50, 150)
            lat_delta = np.random.uniform(10, 40)
            loss = np.random.uniform(2.0, 15.0)
            loss_delta = np.random.uniform(1.0, 5.0)
            sig = np.random.uniform(10, 45)
            sig_delta = np.random.uniform(-15, -5)
            score = np.random.uniform(20, 60)
            tunnel_approaching = float(np.random.choice([0.0, 1.0]))
            X.append([lat, lat_delta, loss, loss_delta, sig, sig_delta, score, tunnel_approaching])
            y.append(1) # Failover imminent!

        self.model.fit(np.array(X), np.array(y))

    def evaluate(
        self,
        timestamp: str,
        active_link_id: str,
        links: Dict[str, WanTelemetry],
        train: TrainTelemetry,
        dist_to_tunnel_km: float
    ) -> MlPrediction:
        active_link = links.get(active_link_id)
        if not active_link:
            return MlPrediction(
                timestamp=timestamp,
                imminent_failover=False,
                risk_score=0.0,
                predicted_link=active_link_id,
                predicted_link_name=active_link_id,
                confidence=95.0,
                reasoning="Link operating normally",
                top_factors=[]
            )

        # Record into short-term rolling window
        current_sample = {
            "link_id": active_link_id,
            "latency": active_link.latency,
            "loss": active_link.packet_loss,
            "signal": active_link.signal,
            "score": active_link.score,
        }
        self.history.append(current_sample)

        # Calculate short-term deltas
        if len(self.history) >= 2:
            prev = self.history[-2]
            lat_delta = current_sample["latency"] - prev["latency"]
            loss_delta = current_sample["loss"] - prev["loss"]
            sig_delta = current_sample["signal"] - prev["signal"]
        else:
            lat_delta = 0.0
            loss_delta = 0.0
            sig_delta = 0.0

        tunnel_approaching = 1.0 if (0.0 < dist_to_tunnel_km < 3.0) else 0.0

        feat_vector = np.array([[
            active_link.latency,
            lat_delta,
            active_link.packet_loss,
            loss_delta,
            active_link.signal,
            sig_delta,
            active_link.score,
            tunnel_approaching
        ]])

        probs = self.model.predict_proba(feat_vector)[0]
        # prob of class 1 (failover needed)
        failover_prob = float(probs[1]) if len(probs) > 1 else 0.0

        # Route-based geofence boost: if 5G is active and tunnel is within 1.5 km
        if tunnel_approaching and active_link.type == "cellular":
            failover_prob = max(failover_prob, 0.88)

        # Find best alternative link
        candidates = [l for k, l in links.items() if k != active_link_id and l.status != "offline"]
        if candidates:
            best_alt = max(candidates, key=lambda l: l.score)
        else:
            best_alt = active_link

        is_imminent = (failover_prob > 0.65) or (active_link.score < 55.0)

        # Dynamic reasoning text
        reasons = []
        if active_link.packet_loss > 3.0:
            reasons.append(f"packet loss elevated ({active_link.packet_loss:.1f}%)")
        if active_link.latency > 80.0 or lat_delta > 15:
            reasons.append(f"latency rising (+{lat_delta:.1f}ms delta)")
        if active_link.signal < 45.0 or sig_delta < -8:
            reasons.append(f"RF signal decay ({sig_delta:.1f} dBm/s)")
        if tunnel_approaching and active_link.type == "cellular":
            reasons.append(f"approaching Mountain Tunnel in {dist_to_tunnel_km:.1f} km")

        if not reasons:
            reason_str = f"Stable connection on {active_link.name}; all telemetry nominal."
        else:
            reason_str = f"Warning: {', '.join(reasons)}. Recommend proactive handover to {best_alt.name}."

        top_factors = [
            {"factor": "RF Signal Attenuation Rate", "impact": round(abs(sig_delta) * 4.2 + (100 - active_link.signal) * 0.4, 1)},
            {"factor": "Packet Jitter & Loss", "impact": round(active_link.packet_loss * 12.0 + max(0, lat_delta) * 1.5, 1)},
            {"factor": "Geofenced Hazard Proximity", "impact": round(90.0 if tunnel_approaching else 10.0, 1)},
        ]

        return MlPrediction(
            timestamp=timestamp,
            imminent_failover=is_imminent,
            risk_score=round(failover_prob * 100.0, 1),
            predicted_link=best_alt.id if is_imminent else active_link.id,
            predicted_link_name=best_alt.name if is_imminent else active_link.name,
            confidence=round(max(failover_prob, 1 - failover_prob) * 100.0, 1),
            reasoning=reason_str,
            top_factors=top_factors
        )
