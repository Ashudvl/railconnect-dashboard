from __future__ import annotations
from collections import deque
from pathlib import Path
import csv
import random
from typing import Dict, List
import numpy as np
from sklearn.ensemble import RandomForestClassifier

FEATURE_NAMES = [
    "a_bandwidth", "a_latency", "a_packet_loss", "a_signal", "a_score",
    "b_bandwidth", "b_latency", "b_packet_loss", "b_signal", "b_score",
    "score_gap", "active_is_a",
]
MODEL_WINDOW_SECONDS = 10

class WanChangePredictor:
    """Random Forest predictor for a WAN change within the next 10 seconds."""

    def __init__(self, csv_path="network_history.csv"):
        self.csv_path = Path(csv_path)
        self.history = deque(maxlen=100)
        self.model = RandomForestClassifier(
            n_estimators=160, max_depth=8, min_samples_leaf=2,
            random_state=42, class_weight="balanced"
        )
        self.wan_model = RandomForestClassifier(
            n_estimators=160, max_depth=8, min_samples_leaf=2,
            random_state=43, class_weight="balanced"
        )
        self.ready = False
        self.training_source = "synthetic bootstrap"
        self._load_live_history()
        self._bootstrap_model()

    @staticmethod
    def _features(row):
        a, b = row["wan_a"], row["wan_b"]
        return [
            float(a["bandwidth"]), float(a["latency"]),
            float(a["packet_loss"]), float(a["signal"]), float(a["score"]),
            float(b["bandwidth"]), float(b["latency"]),
            float(b["packet_loss"]), float(b["signal"]), float(b["score"]),
            float(a["score"] - b["score"]),
            1.0 if row["active_network"] == "WAN A" else 0.0,
        ]

    def _load_live_history(self):
        if not self.csv_path.exists():
            return
        try:
            with self.csv_path.open(newline="") as f:
                for r in csv.DictReader(f):
                    self.history.append({
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
                    })
        except (KeyError, ValueError, OSError):
            pass

    @staticmethod
    def _score(bw, latency, loss, signal):
        return round(
            min(bw / 100, 1) * 100 * 0.30
            + max(0, 100 - latency) * 0.30
            + max(0, 100 - loss * 100) * 0.25
            + signal * 0.15, 2
        )

    def _bootstrap_model(self):
        rng = random.Random(42)
        sequences = []
        # Generate many synthetic sequences, with future labels.
        for _ in range(140):
            for phase in range(12):
                a_bw = max(5, 90 - phase * 8 + rng.randint(-3, 3)) if phase <= 9 else rng.randint(70, 90)
                a_lat = max(5, 25 + phase * 8 + rng.randint(-3, 3)) if phase <= 9 else rng.randint(25, 40)
                a_loss = min(0.30, max(0, 0.01 + phase * 0.03 + rng.uniform(-0.006, 0.006))) if phase <= 9 else rng.uniform(0.01, 0.03)
                a_sig = max(10, 90 - phase * 8 + rng.randint(-3, 3)) if phase <= 9 else rng.randint(75, 90)
                b_bw, b_lat = rng.randint(45, 65), rng.randint(35, 50)
                b_loss, b_sig = rng.uniform(0.01, 0.04), rng.randint(65, 85)
                a_score = self._score(a_bw, a_lat, a_loss, a_sig)
                b_score = self._score(b_bw, b_lat, b_loss, b_sig)
                sequences.append({
                    "wan_a": {"bandwidth": a_bw, "latency": a_lat, "packet_loss": a_loss, "signal": a_sig, "score": a_score},
                    "wan_b": {"bandwidth": b_bw, "latency": b_lat, "packet_loss": b_loss, "signal": b_sig, "score": b_score},
                    "active_network": "WAN A" if a_score >= b_score else "WAN B",
                })

        X, y_switch, y_wan = [], [], []
        for i in range(len(sequences) - 2):
            X.append(self._features(sequences[i]))
            future = sequences[i + 2]  # 2 x 5 seconds = 10-second horizon
            current = sequences[i]
            y_switch.append(int(future["active_network"] != current["active_network"]))
            y_wan.append(int(future["active_network"] == "WAN B"))

        self.model.fit(np.asarray(X), np.asarray(y_switch))
        self.wan_model.fit(np.asarray(X), np.asarray(y_wan))
        self.ready = True

    def observe(self, data):
        self.history.append({
            "wan_a": data["wan_a"], "wan_b": data["wan_b"],
            "active_network": data["active_network"],
        })

    def predict(self, data):
        if not self.ready:
            return {"status": "TRAINING", "switch_predicted": False,
                    "predicted_wan": data["active_network"], "confidence": 0.0,
                    "horizon_seconds": MODEL_WINDOW_SECONDS}
        x = np.asarray([self._features(data)])
        switch_probability = float(self.model.predict_proba(x)[0][1])
        wan_b_probability = float(self.wan_model.predict_proba(x)[0][1])
        predicted_wan = "WAN B" if wan_b_probability >= 0.5 else "WAN A"
        current = data["active_network"]
        confidence = max(wan_b_probability, 1 - wan_b_probability)
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
            "message": (
                f"Likely switch to {predicted_wan} within ~{MODEL_WINDOW_SECONDS} seconds."
                if predicted_wan != current
                else f"No WAN switch predicted in the next ~{MODEL_WINDOW_SECONDS} seconds."
            ),
        }
