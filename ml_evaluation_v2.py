from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List

import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

from ml_predictor import WanChangePredictor, MODEL_WINDOW_SECONDS, STEPS_AHEAD

CSV_PATH = Path("network_history.csv")


def load_history(path: Path = CSV_PATH) -> List[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open(newline="") as f:
        for r in csv.DictReader(f):
            rows.append({
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
    return rows


def evaluate(path: Path = CSV_PATH) -> Dict:
    rows = load_history(path)
    minimum = STEPS_AHEAD + 2

    if len(rows) < minimum:
        return {
            "status": "INSUFFICIENT_DATA",
            "message": f"Need at least {minimum} samples. Currently have {len(rows)}.",
            "samples": len(rows),
        }

    # Predictor is trained independently on synthetic bootstrap sequences.
    # Evaluation uses the actual logged sequence only as unseen test data.
    predictor = WanChangePredictor(str(path))

    y_true_switch, y_pred_switch = [], []
    y_true_wan, y_pred_wan = [], []

    for i in range(1, len(rows) - STEPS_AHEAD):
        current = rows[i]
        previous = rows[i - 1]
        future = rows[i + STEPS_AHEAD]

        x = np.asarray([predictor._features_from_history(current, previous)])
        switch_probability = float(predictor.model.predict_proba(x)[0][1])
        wan_b_probability = float(predictor.wan_model.predict_proba(x)[0][1])

        predicted_switch = switch_probability >= 0.5
        predicted_wan = "WAN B" if wan_b_probability >= 0.5 else "WAN A"

        actual_wan = future["active_network"]
        actual_switch = actual_wan != current["active_network"]

        y_true_switch.append(int(actual_switch))
        y_pred_switch.append(int(predicted_switch))
        y_true_wan.append(int(actual_wan == "WAN B"))
        y_pred_wan.append(int(predicted_wan == "WAN B"))

    s_acc = accuracy_score(y_true_switch, y_pred_switch)
    s_prec = precision_score(y_true_switch, y_pred_switch, zero_division=0)
    s_rec = recall_score(y_true_switch, y_pred_switch, zero_division=0)
    s_f1 = f1_score(y_true_switch, y_pred_switch, zero_division=0)
    w_acc = accuracy_score(y_true_wan, y_pred_wan)
    cm = confusion_matrix(y_true_switch, y_pred_switch, labels=[0, 1])

    return {
        "status": "READY",
        "model": "Random Forest",
        "training_source": predictor.training_source,
        "trend_features": True,
        "prediction_horizon_seconds": MODEL_WINDOW_SECONDS,
        "logged_samples": len(rows),
        "evaluated_samples": len(y_true_switch),
        "switch_prediction": {
            "accuracy": round(float(s_acc), 4),
            "precision": round(float(s_prec), 4),
            "recall": round(float(s_rec), 4),
            "f1": round(float(s_f1), 4),
            "confusion_matrix": cm.tolist(),
        },
        "wan_prediction": {"accuracy": round(float(w_acc), 4)},
        "actual_switches": int(sum(y_true_switch)),
        "predicted_switches": int(sum(y_pred_switch)),
        "message": (
            "Each prediction uses current telemetry plus the previous 5-second "
            "movement and is compared with the actual WAN 10 seconds later."
        ),
    }


if __name__ == "__main__":
    result = evaluate()

    print("\n========================================")
    print("RAILCONNECT ML MODEL EVALUATION")
    print("========================================")

    if result["status"] != "READY":
        print(result["message"])
    else:
        s = result["switch_prediction"]
        w = result["wan_prediction"]

        print(f"Model:              {result['model']}")
        print(f"Training source:    {result['training_source']}")
        print(f"Trend features:     {result['trend_features']}")
        print(f"Logged samples:     {result['logged_samples']}")
        print(f"Evaluated samples:  {result['evaluated_samples']}")
        print(f"Prediction horizon: {result['prediction_horizon_seconds']} sec")
        print()
        print("NEXT-WAN-CHANGE PREDICTION")
        print(f"Accuracy:           {s['accuracy'] * 100:.2f}%")
        print(f"Precision:          {s['precision'] * 100:.2f}%")
        print(f"Recall:             {s['recall'] * 100:.2f}%")
        print(f"F1 Score:           {s['f1'] * 100:.2f}%")
        print()
        print("WHICH WAN IS PREDICTED")
        print(f"Accuracy:           {w['accuracy'] * 100:.2f}%")
        print()
        print(f"Actual switches:    {result['actual_switches']}")
        print(f"Predicted switches: {result['predicted_switches']}")
        print()
        print("Confusion matrix [[TN, FP], [FN, TP]]:")
        print(result["switch_prediction"]["confusion_matrix"])
        print("========================================\n")
