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
        * { box-sizing: border-box; }

        body {
            margin: 0;
            font-family: Inter, Arial, sans-serif;
            background:
                radial-gradient(circle at 10% 0%, rgba(30,64,175,.22), transparent 32%),
                radial-gradient(circle at 90% 20%, rgba(14,116,144,.16), transparent 28%),
                #07111f;
            color: #e5eef9;
            min-height: 100vh;
        }

        .header {
            padding: 28px 40px 24px;
            background: rgba(8,18,32,.96);
            border-bottom: 1px solid #23344a;
            box-shadow: 0 8px 30px rgba(0,0,0,.22);
        }

        .header h1 { margin: 0; font-size: 34px; letter-spacing: .3px; }
        .header p { color: #8fa4bc; margin: 7px 0 0; font-size: 15px; }

        .container {
            max-width: 1280px;
            margin: auto;
            padding: 28px;
        }

        .train-card, .network, .ml-performance {
            background: rgba(18,32,52,.90);
            border: 1px solid #29405c;
            box-shadow: 0 12px 30px rgba(0,0,0,.20);
            backdrop-filter: blur(8px);
        }

        .train-card {
            padding: 22px 25px;
            border-radius: 16px;
            margin-bottom: 22px;
        }

        .train-card h2 { margin: 0 0 16px; font-size: 18px; }

        .train-info {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
        }

        .train-info > div {
            background: #0d1a2b;
            border: 1px solid #243852;
            border-radius: 10px;
            padding: 13px 15px;
        }

        .networks {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 22px;
        }

        .network {
            border-radius: 18px;
            padding: 24px;
            transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
        }

        .network:hover { transform: translateY(-2px); }

        .network.active {
            border-color: #22c55e;
            box-shadow: 0 0 0 1px rgba(34,197,94,.25), 0 14px 35px rgba(34,197,94,.10);
        }

        .network h2 { margin: 0 0 14px; font-size: 20px; }

        .score {
            font-size: 58px;
            line-height: 1;
            font-weight: 800;
            letter-spacing: -2px;
        }

        .status {
            display: inline-block;
            margin: 12px 0 18px;
            padding: 6px 11px;
            border-radius: 999px;
            background: #17283d;
            color: #b9c9da;
            font-size: 13px;
            font-weight: 700;
            letter-spacing: .6px;
        }

        .metric {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #263a53;
            color: #9eb1c6;
        }

        .metric span:last-child { color: #edf5ff; font-weight: 700; }

        .active-box {
            margin-top: 22px;
            background: linear-gradient(135deg, #073b27, #0b5b38);
            border: 1px solid #20a967;
            padding: 24px;
            border-radius: 17px;
            text-align: center;
            box-shadow: 0 12px 30px rgba(16,185,129,.10);
        }

        .active-box h2 {
            margin: 0 0 8px;
            font-size: 13px;
            letter-spacing: 1.8px;
            color: #a7f3d0;
        }

        .active-network { font-size: 34px; font-weight: 800; }

        .prediction {
            margin-top: 22px;
            background: linear-gradient(135deg, #3b2507, #4d2d05);
            border: 1px solid #a16207;
            padding: 24px;
            border-radius: 17px;
            box-shadow: 0 12px 30px rgba(245,158,11,.08);
        }

        .prediction h2, .ml-performance h2 { margin: 0 0 12px; font-size: 19px; }

        #prediction { color: #fde68a; font-size: 18px; line-height: 1.5; }

        .ml-performance {
            margin-top: 22px;
            padding: 24px;
            border-radius: 17px;
        }

        .ml-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
            margin-top: 16px;
        }

        .ml-card {
            background: #0b1727;
            border: 1px solid #263d57;
            padding: 18px 12px;
            border-radius: 13px;
            text-align: center;
        }

        .ml-card > div:first-child {
            color: #8fa4bc;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .ml-card .value {
            font-size: 29px;
            font-weight: 800;
            margin-top: 7px;
            color: #7dd3fc;
        }

        .ml-note {
            margin-top: 15px;
            color: #8196ad;
            font-size: 13px;
            line-height: 1.5;
        }

        .online { color: #4ade80; }
        .warning { color: #fbbf24; }
        .error { color: #f87171; }

        @media(max-width: 900px) {
            .ml-grid { grid-template-columns: 1fr 1fr; }
        }

        @media(max-width: 700px) {
            .header { padding: 22px; }
            .container { padding: 18px; }
            .networks { grid-template-columns: 1fr; }
            .train-info { grid-template-columns: 1fr; }
            .ml-grid { grid-template-columns: 1fr 1fr; }
        }

        @media(max-width: 480px) {
            .ml-grid { grid-template-columns: 1fr; }
            .score { font-size: 48px; }
        }
    </style>

</head>

<body>

<div class="header">

    <h1>🚆 RailConnect</h1>

    <p>
        Intelligent Railway Connectivity Control Center
    </p>

    <div style="margin-top:14px;display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
        <span style="display:inline-flex;align-items:center;gap:7px;padding:7px 12px;border-radius:999px;background:#052e16;border:1px solid #16a34a;color:#86efac;font-size:12px;font-weight:800;letter-spacing:.8px;">
            <span style="width:8px;height:8px;border-radius:50%;background:#22c55e;box-shadow:0 0 10px #22c55e;"></span>
            LIVE MONITORING
        </span>
        <span style="color:#71869e;font-size:12px;">Dual-WAN • Intelligent failover • ML prediction</span>
    </div>

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
