from flask import Flask, render_template_string
import requests

app = Flask(__name__)

WINDOWS_API = "http://127.0.0.1:8000/network"

HTML = """
<!DOCTYPE html>
<html>
<head>

    <title>RailConnect Control Center</title>

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #0f172a;
            color: white;
        }

        .header {
            padding: 25px 40px;
            background: #111827;
            border-bottom: 1px solid #334155;
        }

        .header h1 {
            margin: 0;
            font-size: 32px;
        }

        .header p {
            color: #94a3b8;
            margin-bottom: 0;
        }

        .container {
            max-width: 1200px;
            margin: auto;
            padding: 30px;
        }

        .train-card {
            background: #1e293b;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 25px;
        }

        .train-info {
            display: flex;
            justify-content: space-between;
        }

        .networks {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
        }

        .network {
            background: #1e293b;
            border-radius: 15px;
            padding: 25px;
            border: 2px solid #334155;
        }

        .network.active {
            border-color: #22c55e;
        }

        .network h2 {
            margin-top: 0;
        }

        .score {
            font-size: 55px;
            font-weight: bold;
        }

        .status {
            font-size: 18px;
            margin-bottom: 20px;
        }

        .metric {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #334155;
        }

        .active-box {
            margin-top: 25px;
            background: #14532d;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
        }

        .active-network {
            font-size: 32px;
            font-weight: bold;
        }

        .prediction {
            margin-top: 25px;
            background: #422006;
            padding: 25px;
            border-radius: 15px;
        }

        .ml-performance {
            margin-top: 25px;
            background: #1e293b;
            padding: 25px;
            border-radius: 15px;
        }

        .ml-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-top: 15px;
        }

        .ml-card {
            background: #0f172a;
            padding: 16px;
            border-radius: 10px;
            text-align: center;
        }

        .ml-card .value {
            font-size: 26px;
            font-weight: bold;
            margin-top: 6px;
        }

        .ml-note {
            margin-top: 15px;
            color: #94a3b8;
            font-size: 14px;
        }

        @media(max-width: 900px) {
            .ml-grid {
                grid-template-columns: 1fr 1fr;
            }
        }

        @media(max-width: 700px) {
            .ml-grid {
                grid-template-columns: 1fr;
            }
        }

        .online {
            color: #22c55e;
        }

        .warning {
            color: #f59e0b;
        }

        .error {
            color: #ef4444;
        }

        @media(max-width: 700px) {

            .networks {
                grid-template-columns: 1fr;
            }

            .train-info {
                flex-direction: column;
            }

        }

    </style>

</head>

<body>

<div class="header">

    <h1>🚆 RailConnect</h1>

    <p>
        Intelligent Railway Connectivity Control Center
    </p>

</div>


<div class="container">

    <div class="train-card">

        <h2>Train Status</h2>

        <div class="train-info">

            <div>
                <b>Train:</b> 12045
            </div>

            <div>
                <b>Route:</b> Delhi → Chandigarh
            </div>

            <div>
                <b>Speed:</b> 108 km/h
            </div>

        </div>

    </div>


    <div class="networks">


        <div id="wan-a" class="network">

            <h2>📡 WAN A</h2>

            <div id="score-a" class="score">
                --
            </div>

            <div id="status-a" class="status">
                Loading...
            </div>

            <div class="metric">
                <span>Bandwidth</span>
                <span id="bandwidth-a">--</span>
            </div>

            <div class="metric">
                <span>Latency</span>
                <span id="latency-a">--</span>
            </div>

            <div class="metric">
                <span>Packet Loss</span>
                <span id="loss-a">--</span>
            </div>

            <div class="metric">
                <span>Signal</span>
                <span id="signal-a">--</span>
            </div>

        </div>


        <div id="wan-b" class="network">

            <h2>📡 WAN B</h2>

            <div id="score-b" class="score">
                --
            </div>

            <div id="status-b" class="status">
                Loading...
            </div>

            <div class="metric">
                <span>Bandwidth</span>
                <span id="bandwidth-b">--</span>
            </div>

            <div class="metric">
                <span>Latency</span>
                <span id="latency-b">--</span>
            </div>

            <div class="metric">
                <span>Packet Loss</span>
                <span id="loss-b">--</span>
            </div>

            <div class="metric">
                <span>Signal</span>
                <span id="signal-b">--</span>
            </div>

        </div>

    </div>


    <div class="active-box">

        <h2>ACTIVE NETWORK</h2>

        <div id="active-network" class="active-network">
            Connecting...
        </div>

    </div>


    <div class="prediction">

        <h2>🧠 RailConnect Intelligence</h2>

        <div id="prediction">
            Analyzing network conditions...
        </div>

    </div>


    <div class="ml-performance">

        <h2>📊 ML Model Performance</h2>

        <div id="ml-training">
            Loading model evaluation...
        </div>

        <div class="ml-grid">

            <div class="ml-card">
                <div>Accuracy</div>
                <div id="ml-accuracy" class="value">--</div>
            </div>

            <div class="ml-card">
                <div>Precision</div>
                <div id="ml-precision" class="value">--</div>
            </div>

            <div class="ml-card">
                <div>Recall</div>
                <div id="ml-recall" class="value">--</div>
            </div>

            <div class="ml-card">
                <div>F1 Score</div>
                <div id="ml-f1" class="value">--</div>
            </div>

        </div>

        <div class="ml-note" id="ml-details">
            Evaluation uses the logged network history and the 10-second prediction horizon.
        </div>

    </div>

</div>


<script>

async function updateDashboard() {

    try {

        const response =
            await fetch("/network");

        const data = await response.json();


        // WAN A

        document.getElementById("score-a").innerText =
            data.wan_a.score;

        document.getElementById("status-a").innerText =
            data.wan_a.status;

        document.getElementById("bandwidth-a").innerText =
            data.wan_a.bandwidth + " Mbps";

        document.getElementById("latency-a").innerText =
            data.wan_a.latency + " ms";

        document.getElementById("loss-a").innerText =
            data.wan_a.packet_loss;

        document.getElementById("signal-a").innerText =
            data.wan_a.signal;


        // WAN B

        document.getElementById("score-b").innerText =
            data.wan_b.score;

        document.getElementById("status-b").innerText =
            data.wan_b.status;

        document.getElementById("bandwidth-b").innerText =
            data.wan_b.bandwidth + " Mbps";

        document.getElementById("latency-b").innerText =
            data.wan_b.latency + " ms";

        document.getElementById("loss-b").innerText =
            data.wan_b.packet_loss;

        document.getElementById("signal-b").innerText =
            data.wan_b.signal;


        // Active network

        document.getElementById("active-network").innerText =
            "🟢 " + data.active_network;


        // Highlight active network

        document.getElementById("wan-a")
            .classList.remove("active");

        document.getElementById("wan-b")
            .classList.remove("active");


        if (data.active_network === "WAN A") {

            document.getElementById("wan-a")
                .classList.add("active");

        } else {

            document.getElementById("wan-b")
                .classList.add("active");

        }


        // ML prediction

        if (data.prediction && data.prediction.status === "READY") {
            const p = data.prediction;
            const confidence = Math.round((p.confidence || 0) * 100);

            if (p.switch_predicted) {
                document.getElementById("prediction").innerHTML =
                    "🤖 <b>ML PREDICTION:</b> Switch to " +
                    p.predicted_wan + " likely within ~" +
                    p.horizon_seconds + " seconds. Confidence: " +
                    confidence + "%";
            } else {
                document.getElementById("prediction").innerHTML =
                    "🤖 <b>ML PREDICTION:</b> No WAN change expected " +
                    "within ~" + p.horizon_seconds +
                    " seconds. Confidence: " + confidence + "%";
            }
        } else {
            document.getElementById("prediction").innerText =
                "🧠 ML model is preparing...";
        }

    }

    catch (error) {

        document.getElementById("active-network")
            .innerText = "🔴 Gateway Offline";

        document.getElementById("prediction")
            .innerText =
            "Unable to communicate with RailConnect Gateway.";

    }

}



async function updateMetrics() {

    try {

        const response = await fetch("/ml_metrics");
        const metrics = await response.json();

        if (metrics.status !== "READY") {
            document.getElementById("ml-training").innerText =
                "📚 " + (metrics.message || "Collecting more data...");
            return;
        }

        const s = metrics.switch_prediction;
        const w = metrics.wan_prediction;

        document.getElementById("ml-training").innerText =
            "Model: " + metrics.model +
            "  •  Training: " + metrics.training_source +
            "  •  Trend features: " + (metrics.trend_features ? "ON" : "OFF");

        document.getElementById("ml-accuracy").innerText =
            (s.accuracy * 100).toFixed(1) + "%";

        document.getElementById("ml-precision").innerText =
            (s.precision * 100).toFixed(1) + "%";

        document.getElementById("ml-recall").innerText =
            (s.recall * 100).toFixed(1) + "%";

        document.getElementById("ml-f1").innerText =
            (s.f1 * 100).toFixed(1) + "%";

        document.getElementById("ml-details").innerText =
            "Evaluated " + metrics.evaluated_samples +
            " samples • " +
            metrics.actual_switches + " actual switches • " +
            metrics.predicted_switches + " predicted switches • " +
            "Horizon: " + metrics.prediction_horizon_seconds + " sec";

    } catch (error) {

        document.getElementById("ml-training").innerText =
            "ML evaluation temporarily unavailable.";

    }

}


// Initial update

updateDashboard();
updateMetrics();


// Update every 2 seconds

setInterval(updateDashboard, 2000);
setInterval(updateMetrics, 10000);

</script>


</body>
</html>
"""


@app.route("/")
def dashboard():

    return render_template_string(HTML)


@app.route("/ml_metrics")
def ml_metrics():
    try:
        from ml_evaluation import evaluate
        return evaluate()
    except Exception as e:
        return {
            "status": "ERROR",
            "message": str(e)
        }, 500


@app.route("/network")
def network():
    try:
        response = requests.get(WINDOWS_API, timeout=5)
        return response.text, response.status_code, {
            "Content-Type": "application/json"
        }
    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5001,
        debug=False
    )
