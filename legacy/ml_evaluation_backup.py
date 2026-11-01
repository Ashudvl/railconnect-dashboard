from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

from ml_predictor import WanChangePredictor, MODEL_WINDOW_SECONDS


CSV_PATH = Path("network_history.csv")
STEPS_AHEAD = max(1, MODEL_WINDOW_SECONDS // 5)


def load_history(path: Path = CSV_PATH) -> List[dict]:
    """Load logged simulator observations from network_history.csv."""
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
    """
    Evaluate the same prediction logic used by the live dashboard.

    A sample at time t is evaluated against the actual active network
    STEPS_AHEAD samples later. With a 5-second simulator interval and
    a 10-second prediction horizon, this compares t with t+2.
    """
    rows = load_history(path)

    if len(rows) <= STEPS_AHEAD:
        return {
            "status": "INSUFFICIENT_DATA",
            "message": (
                f"Need at least {STEPS_AHEAD + 1} logged samples. "
                f"Currently have {len(rows)}."
            ),
            "samples": len(rows),
        }

    predictor = WanChangePredictor(str(path))

    y_true_switch = []
    y_pred_switch = []
    y_true_wan = []
    y_pred_wan = []

    for i in range(len(rows) - STEPS_AHEAD):
        current = rows[i]
        future = rows[i + STEPS_AHEAD]

        prediction = predictor.predict(current)

        actual_wan = future["active_network"]
        actual_switch = actual_wan != current["active_network"]

        y_true_switch.append(int(actual_switch))
        y_pred_switch.append(int(prediction["switch_predicted"]))

        y_true_wan.append(1 if actual_wan == "WAN B" else 0)
        y_pred_wan.append(1 if prediction["predicted_wan"] == "WAN B" else 0)

    switch_accuracy = accuracy_score(y_true_switch, y_pred_switch)
    switch_precision = precision_score(
        y_true_switch, y_pred_switch, zero_division=0
    )
    switch_recall = recall_score(
        y_true_switch, y_pred_switch, zero_division=0
    )
    switch_f1 = f1_score(
        y_true_switch, y_pred_switch, zero_division=0
    )

    wan_accuracy = accuracy_score(y_true_wan, y_pred_wan)
    cm = confusion_matrix(y_true_switch, y_pred_switch, labels=[0, 1])

    return {
        "status": "READY",
        "model": "Random Forest",
        "training_source": predictor.training_source,
        "prediction_horizon_seconds": MODEL_WINDOW_SECONDS,
        "logged_samples": len(rows),
        "evaluated_samples": len(y_true_switch),
        "switch_prediction": {
            "accuracy": round(float(switch_accuracy), 4),
            "precision": round(float(switch_precision), 4),
            "recall": round(float(switch_recall), 4),
            "f1": round(float(switch_f1), 4),
            "confusion_matrix": cm.tolist(),
        },
        "wan_prediction": {
            "accuracy": round(float(wan_accuracy), 4),
        },
        "actual_switches": int(sum(y_true_switch)),
        "predicted_switches": int(sum(y_pred_switch)),
        "message": (
            "Metrics are calculated by comparing each prediction with "
            "the actual active WAN 10 seconds later."
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
