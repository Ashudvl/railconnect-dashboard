from pathlib import Path
from flask import Flask, jsonify
import random
import threading
import time
import csv
from datetime import datetime
from ml_predictor import WanChangePredictor

app = Flask(__name__)

predictor = WanChangePredictor("network_history.csv")
LOG_FILE = "network_history.csv"
LOG_FIELDS = [
    "timestamp", "a_bandwidth", "a_latency", "a_packet_loss", "a_signal", "a_score", "a_status",
    "b_bandwidth", "b_latency", "b_packet_loss", "b_signal", "b_score", "b_status", "active_network"
]

def log_network_data(data):
    exists = False
    try:
        exists = Path(LOG_FILE).exists() and Path(LOG_FILE).stat().st_size > 0
    except OSError:
        pass
    row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "a_bandwidth": data["wan_a"]["bandwidth"],
        "a_latency": data["wan_a"]["latency"],
        "a_packet_loss": data["wan_a"]["packet_loss"],
        "a_signal": data["wan_a"]["signal"],
        "a_score": data["wan_a"]["score"],
        "a_status": data["wan_a"]["status"],
        "b_bandwidth": data["wan_b"]["bandwidth"],
        "b_latency": data["wan_b"]["latency"],
        "b_packet_loss": data["wan_b"]["packet_loss"],
        "b_signal": data["wan_b"]["signal"],
        "b_score": data["wan_b"]["score"],
        "b_status": data["wan_b"]["status"],
        "active_network": data["active_network"],
    }
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow(row)

current_data = {
    "wan_a": {
        "name": "WAN A",
        "bandwidth": 75,
        "latency": 35,
        "packet_loss": 0.02,
        "signal": 82,
        "score": 78.8,
        "status": "EXCELLENT"
    },
    "wan_b": {
        "name": "WAN B",
        "bandwidth": 55,
        "latency": 45,
        "packet_loss": 0.03,
        "signal": 72,
        "score": 68.05,
        "status": "GOOD"
    },
    "active_network": "WAN A"
}


def calculate_score(bandwidth, latency, packet_loss, signal):
    bandwidth_score = min(bandwidth / 100, 1) * 100
    latency_score = max(0, 100 - latency)
    loss_score = max(0, 100 - (packet_loss * 100))
    signal_score = signal

    score = (
        bandwidth_score * 0.30
        + latency_score * 0.30
        + loss_score * 0.25
        + signal_score * 0.15
    )

    return round(score, 2)


def get_status(score):
    if score >= 70:
        return "EXCELLENT"
    elif score >= 50:
        return "GOOD"
    elif score >= 30:
        return "POOR"
    else:
        return "CRITICAL"


def simulator():
    global current_data

    step = 0

    while True:
        # WAN A gradually gets worse, then resets
        if step <= 9:
            wan_a_bandwidth = max(5, 90 - step * 9)
            wan_a_latency = 25 + step * 8
            wan_a_packet_loss = min(0.30, 0.01 + step * 0.03)
            wan_a_signal = max(10, 90 - step * 8)
        else:
            wan_a_bandwidth = random.randint(70, 90)
            wan_a_latency = random.randint(25, 40)
            wan_a_packet_loss = random.uniform(0.01, 0.03)
            wan_a_signal = random.randint(75, 90)

        # WAN B stays relatively stable
        wan_b_bandwidth = random.randint(45, 65)
        wan_b_latency = random.randint(35, 50)
        wan_b_packet_loss = random.uniform(0.01, 0.04)
        wan_b_signal = random.randint(65, 85)

        score_a = calculate_score(
            wan_a_bandwidth,
            wan_a_latency,
            wan_a_packet_loss,
            wan_a_signal
        )

        score_b = calculate_score(
            wan_b_bandwidth,
            wan_b_latency,
            wan_b_packet_loss,
            wan_b_signal
        )

        current_data = {
            "wan_a": {
                "name": "WAN A",
                "bandwidth": wan_a_bandwidth,
                "latency": wan_a_latency,
                "packet_loss": round(wan_a_packet_loss, 2),
                "signal": wan_a_signal,
                "score": score_a,
                "status": get_status(score_a)
            },
            "wan_b": {
                "name": "WAN B",
                "bandwidth": wan_b_bandwidth,
                "latency": wan_b_latency,
                "packet_loss": round(wan_b_packet_loss, 2),
                "signal": wan_b_signal,
                "score": score_b,
                "status": get_status(score_b)
            },
            "active_network": "WAN A" if score_a >= score_b else "WAN B"
        }

        predictor.observe(current_data)
        current_data["prediction"] = predictor.predict(current_data)
        log_network_data(current_data)

        print(
            f"WAN A | Score: {score_a} | "
            f"Latency: {wan_a_latency} ms | "
            f"Signal: {wan_a_signal} | {get_status(score_a)}"
        )

        print(
            f"WAN B | Score: {score_b} | "
            f"Latency: {wan_b_latency} ms | "
            f"Signal: {wan_b_signal} | {get_status(score_b)}"
        )

        print(f"ACTIVE NETWORK → {current_data['active_network']}")
        print()

        step += 1

        if step > 9:
            step = 0

        time.sleep(5)


@app.route("/network")
def network():
    return jsonify(current_data)


if __name__ == "__main__":
    thread = threading.Thread(target=simulator, daemon=True)
    thread.start()

    print("================================")
    print("RAILCONNECT NETWORK SIMULATOR")
    print("API running on port 8000")
    print("================================")

    app.run(host="0.0.0.0", port=8000)
