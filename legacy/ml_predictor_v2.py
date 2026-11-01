from __future__ import annotations

from collections import deque
from pathlib import Path
import csv
import random
from typing import Dict, List

import numpy as np
from sklearn.ensemble import RandomForestClassifier

MODEL_WINDOW_SECONDS = 10
SAMPLE_INTERVAL_SECONDS = 5
STEPS_AHEAD = MODEL_WINDOW_SECONDS // SAMPLE_INTERVAL_SECONDS
HISTORY_SIZE = 100

# Current values + short-term trends.
FEATURE_NAMES = [
    "a_bandwidth", "a_latency", "a_packet_loss", "a_signal", "a_score",
    "b_bandwidth", "b_latency", "b_packet_loss", "b_signal", "b_score",
    "score_gap", "active_is_a",
    "a_bandwidth_delta", "a_latency_delta", "a_loss_delta", "a_signal_delta", "a_score_delta",
    "b_bandwidth_delta", "b_latency_delta", "b_loss_delta", "b_signal_delta", "b_score_delta",
    "score_gap_delta",
]


class WanChangePredictor:
    """
    Random Forest predictor for a WAN change within the next 10 seconds.

    The model uses both the current telemetry and recent movement (trend)
    over the previous sample. The live prototype still uses synthetic
    bootstrap training; real router telemetry can replace this later.
    """

    def __init__(self, csv_path="network_history.csv"):
        self.csv_path = Path(csv_path)
        self.history = deque(maxlen=HISTORY_SIZE)

        self.model = RandomForestClassifier(
            n_estimators=220,
            max_depth=10,
            min_samples_leaf=2,
            random_state=42,
            class_weight="balanced",
        )
        self.wan_model = RandomForestClassifier(
            n_estimators=220,
            max_depth=10,
            min_samples_leaf=2,
            random_state=43,
            class_weight="balanced",
        )

        self.ready = False
        self.training_source = "synthetic bootstrap + trend features"

        self._load_live_history()
        self._bootstrap_model()

    @staticmethod
    def _score(bw, latency, loss, signal):
        return round(
            min(bw / 100, 1) * 100 * 0.30
            + max(0, 100 - latency) * 0.30
            + max(0, 100 - loss * 100) * 0.25
            + signal * 0.15,
            2,
        )

    @staticmethod
    def _base_features(row):
        a, b = row["wan_a"], row["wan_b"]
        gap = float(a["score"] - b["score"])
        return [
            float(a["bandwidth"]),
            float(a["latency"]),
            float(a["packet_loss"]),
            float(a["signal"]),
            float(a["score"]),
            float(b["bandwidth"]),
            float(b["latency"]),
            float(b["packet_loss"]),
            float(b["signal"]),
            float(b["score"]),
            gap,
            1.0 if row["active_network"] == "WAN A" else 0.0,
        ]

    @staticmethod
    def _delta(current, previous):
        a, b = current["wan_a"], current["wan_b"]
        pa, pb = previous["wan_a"], previous["wan_b"]
        return [
            float(a["bandwidth"] - pa["bandwidth"]),
            float(a["latency"] - pa["latency"]),
            float(a["packet_loss"] - pa["packet_loss"]),
            float(a["signal"] - pa["signal"]),
            float(a["score"] - pa["score"]),
            float(b["bandwidth"] - pb["bandwidth"]),
            float(b["latency"] - pb["latency"]),
            float(b["packet_loss"] - pb["packet_loss"]),
            float(b["signal"] - pb["signal"]),
            float(b["score"] - pb["score"]),
            float((a["score"] - b["score"]) - (pa["score"] - pb["score"])),
        ]

    def _features_from_history(self, row, previous=None):
        features = self._base_features(row)
        if previous is None:
            features.extend([0.0] * 11)
        else:
            features.extend(self._delta(row, previous))
        return features

    def _features(self, row):
        previous = self.history[-1] if self.history else None
        return self._features_from_history(row, previous)

    def _row_from_csv(self, r):
        return {
            "wan_a": {
                "bandwidth": float(r["a_bandwidth"]),
                "latency": float(r["a_latency"]),
                "packet_loss": float(r["a_packet_loss"]),
                "signal": float(r["a_signal"]),
                "score": float(r["a_score"]),
            },
            "wan_b": {
                "bandwidth": float(r["b_bandwidth"]),
                "latency": float(r["b_latency"]),
                "packet_loss": float(r["b_packet_loss"]),
                "signal": float(r["b_signal"]),
                "score": float(r["b_score"]),
            },
            "active_network": r["active_network"],
        }

    def _load_live_history(self):
        if not self.csv_path.exists():
            return
        try:
            with self.csv_path.open(newline="") as f:
                for r in csv.DictReader(f):
                    self.history.append(self._row_from_csv(r))
        except (KeyError, ValueError, OSError):
            pass

    def _make_synthetic_sequence(self, rng, length=30):
        sequence = []
        phase = rng.randrange(10)

        for _ in range(length):
            if phase <= 9:
                a_bw = max(5, 90 - phase * 9 + rng.randint(-3, 3))
                a_lat = max(5, 25 + phase * 8 + rng.randint(-3, 3))
                a_loss = min(0.30, max(0, 0.01 + phase * 0.03 + rng.uniform(-0.006, 0.006)))
                a_sig = max(10, 90 - phase * 8 + rng.randint(-3, 3))
            else:
                a_bw = rng.randint(70, 90)
                a_lat = rng.randint(25, 40)
                a_loss = rng.uniform(0.01, 0.03)
                a_sig = rng.randint(75, 90)

            b_bw = rng.randint(45, 65)
            b_lat = rng.randint(35, 50)
            b_loss = rng.uniform(0.01, 0.04)
            b_sig = rng.randint(65, 85)

            a_score = self._score(a_bw, a_lat, a_loss, a_sig)
            b_score = self._score(b_bw, b_lat, b_loss, b_sig)

            sequence.append({
                "wan_a": {
                    "bandwidth": a_bw, "latency": a_lat,
                    "packet_loss": a_loss, "signal": a_sig, "score": a_score,
                },
                "wan_b": {
                    "bandwidth": b_bw, "latency": b_lat,
                    "packet_loss": b_loss, "signal": b_sig, "score": b_score,
                },
                "active_network": "WAN A" if a_score >= b_score else "WAN B",
            })

            phase += 1
            if phase > 12:
                phase = 0

        return sequence

    def _bootstrap_model(self):
        rng = random.Random(42)
        X, y_switch, y_wan = [], [], []

        # Build independent continuous sequences so trend features are meaningful.
        for _ in range(180):
            sequence = self._make_synthetic_sequence(rng, length=32)

            for i in range(1, len(sequence) - STEPS_AHEAD):
                current = sequence[i]
                previous = sequence[i - 1]
                future = sequence[i + STEPS_AHEAD]

                X.append(self._features_from_history(current, previous))
                y_switch.append(
                    int(future["active_network"] != current["active_network"])
                )
                y_wan.append(int(future["active_network"] == "WAN B"))

        self.model.fit(np.asarray(X), np.asarray(y_switch))
        self.wan_model.fit(np.asarray(X), np.asarray(y_wan))
        self.ready = True

    def observe(self, data):
        self.history.append({
            "wan_a": dict(data["wan_a"]),
            "wan_b": dict(data["wan_b"]),
            "active_network": data["active_network"],
        })

    def predict(self, data):
        if not self.ready:
            return {
                "status": "TRAINING",
                "switch_predicted": False,
                "predicted_wan": data["active_network"],
                "confidence": 0.0,
                "horizon_seconds": MODEL_WINDOW_SECONDS,
            }

        x = np.asarray([self._features(data)])

        switch_probability = float(self.model.predict_proba(x)[0][1])
        wan_b_probability = float(self.wan_model.predict_proba(x)[0][1])

        predicted_wan = "WAN B" if wan_b_probability >= 0.5 else "WAN A"
        current = data["active_network"]
        confidence = max(wan_b_probability, 1.0 - wan_b_probability)

        return {
            "status": "READY",
            "switch_predicted": predicted_wan != current,
            "predicted_wan": predicted_wan,
            "confidence": round(confidence, 3),
            "switch_probability": round(switch_probability, 3),
            "horizon_seconds": MODEL_WINDOW_SECONDS,
            "model": "Random Forest",
            "training_source": self.training_source,
            "live_samples": len(self.history),
            "trend_features": True,
            "message": (
                f"Likely switch to {predicted_wan} within ~{MODEL_WINDOW_SECONDS} seconds."
                if predicted_wan != current
                else f"No WAN switch predicted in the next ~{MODEL_WINDOW_SECONDS} seconds."
            ),
        }
