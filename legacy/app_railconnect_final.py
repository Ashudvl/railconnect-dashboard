from flask import Flask, render_template_string, jsonify
import requests
from datetime import datetime

app = Flask(__name__)
WINDOWS_API = "http://127.0.0.1:8000/network"

# Server-side in-memory audit logs. They survive page refreshes while Flask is running.
FAILOVER_EVENTS = []
PREDICTION_HISTORY = []
LAST_ACTIVE_NETWORK = None
LAST_PREDICTION_KEY = None
MAX_EVENTS = 20
MAX_PREDICTIONS = 20

HTML = r'''
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RailConnect | Network Control Center</title>
<style>
*{box-sizing:border-box}body{margin:0;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;background:#07101d;color:#e8f0f8;min-height:100vh}.topbar{height:74px;background:#091625;border-bottom:1px solid #20344a;display:flex;align-items:center;justify-content:space-between;padding:0 34px;position:sticky;top:0;z-index:10}.brand{display:flex;align-items:center;gap:13px}.brand-mark{width:40px;height:40px;border-radius:11px;background:#123a5c;display:grid;place-items:center;font-size:22px;border:1px solid #2b5878}.brand h1{font-size:20px;margin:0;letter-spacing:.3px}.brand small{display:block;color:#7f95ab;margin-top:2px}.live{display:flex;align-items:center;gap:8px;padding:8px 13px;border:1px solid #1e8d59;background:#082a1b;border-radius:999px;color:#79e2a9;font-size:11px;font-weight:800;letter-spacing:1px}.dot{width:8px;height:8px;border-radius:50%;background:#31d17b;box-shadow:0 0 12px #31d17b}.wrap{max-width:1380px;margin:auto;padding:25px}.hero{display:grid;grid-template-columns:1.55fr .7fr .7fr;gap:15px;margin-bottom:18px}.hero-card,.panel{background:#0d1b2b;border:1px solid #213950;border-radius:16px;box-shadow:0 12px 35px rgba(0,0,0,.18)}.hero-card{padding:19px}.eyebrow{font-size:10px;color:#7891a8;text-transform:uppercase;letter-spacing:1.5px;font-weight:800}.hero-title{font-size:26px;font-weight:800;margin:6px 0}.hero-sub{color:#8da2b7;font-size:13px}.mini-value{font-size:25px;font-weight:800;margin-top:8px}.mini-good{color:#65e6a0}.mini-blue{color:#72c9ff}.section-title{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}.section-title h2{margin:0;font-size:15px;letter-spacing:.4px}.section-title span{font-size:11px;color:#7189a0}.wan-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.wan{padding:21px;position:relative;overflow:hidden}.wan.active{border-color:#22b96b;box-shadow:0 0 0 1px rgba(34,185,107,.22),0 18px 45px rgba(34,185,107,.08)}.wan.active:after{content:"ACTIVE";position:absolute;right:16px;top:16px;padding:5px 8px;border-radius:5px;background:#0a3a25;color:#63e7a0;font-size:10px;font-weight:900;letter-spacing:1px}.wan-head{display:flex;justify-content:space-between;align-items:center}.wan-name{font-size:18px;font-weight:800}.wan-icon{font-size:21px}.score-row{display:flex;align-items:end;gap:12px;margin:18px 0}.score{font-size:56px;line-height:.9;font-weight:900;letter-spacing:-3px}.score-label{color:#758da4;font-size:11px;padding-bottom:5px}.status{display:inline-block;padding:5px 10px;border-radius:999px;background:#17283a;color:#b9c9d9;font-size:10px;font-weight:900;letter-spacing:1px}.metrics{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin-top:18px}.metric{background:#091625;border:1px solid #1c3045;border-radius:10px;padding:12px}.metric label{display:block;color:#71879d;font-size:10px;text-transform:uppercase;letter-spacing:.8px}.metric strong{display:block;margin-top:5px;font-size:16px}.bar{height:5px;background:#1b2d40;border-radius:10px;margin-top:9px;overflow:hidden}.bar i{display:block;height:100%;width:0;background:#54c8ff;border-radius:10px;transition:width .5s}.active-strip{margin-top:18px;padding:17px 20px;border-radius:14px;background:linear-gradient(90deg,#073a27,#0c2f2a);border:1px solid #1a8d5a;display:flex;align-items:center;justify-content:space-between}.active-label{color:#79b99d;font-size:10px;font-weight:900;letter-spacing:1.4px}.active-main{font-size:23px;font-weight:900;color:#73e2a5;margin-top:4px}.active-score{font-size:12px;color:#9cb3c8}.content-grid{display:grid;grid-template-columns:1.4fr .8fr;gap:18px;margin-top:18px}.panel{padding:19px}.chart-wrap{height:255px;background:#091625;border:1px solid #1b3045;border-radius:12px;padding:10px}.chart{width:100%;height:100%}.legend{display:flex;gap:18px;margin-top:9px;font-size:10px;color:#8399ae}.legend b{display:inline-block;width:18px;height:3px;margin-right:5px;vertical-align:middle}.pred{background:linear-gradient(135deg,#171b32,#101d2e);border-color:#344b72}.pred-main{padding:16px;border-radius:12px;background:#0a1524;border:1px solid #263c55}.pred-status{display:flex;justify-content:space-between;align-items:center}.pred-badge{padding:5px 9px;border-radius:5px;background:#182f4b;color:#78caff;font-size:10px;font-weight:900;letter-spacing:1px}.pred-value{font-size:28px;font-weight:900;margin:12px 0 3px}.confidence{font-size:13px;color:#a6b9ca}.confidence strong{color:#75d8ff}.progress{height:8px;background:#1c2c3e;border-radius:10px;margin-top:12px;overflow:hidden}.progress i{display:block;width:0;height:100%;background:#55c7ff;border-radius:10px}.prediction-note{color:#778da3;font-size:11px;margin-top:12px;line-height:1.5}.history{margin-top:18px}.history-table{width:100%;border-collapse:collapse;font-size:11px}.history-table th{text-align:left;color:#6f879e;text-transform:uppercase;letter-spacing:.7px;font-size:9px;padding:8px;border-bottom:1px solid #20354a}.history-table td{padding:10px 8px;border-bottom:1px solid #172b3e}.tag{padding:4px 7px;border-radius:5px;background:#17293c;color:#b9cbe0;font-weight:800}.switch-tag{background:#3b2511;color:#ffd28a}.events{margin-top:18px}.event{display:grid;grid-template-columns:72px 1fr auto;gap:10px;padding:11px 0;border-bottom:1px solid #172b3e;align-items:center;font-size:11px}.event-time{color:#6e879f}.event-title{font-weight:800}.event-reason{color:#788fa5;margin-top:3px;font-size:10px}.event-ok{color:#68dda0;font-weight:900}.ml{margin-top:18px}.ml-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.ml-card{background:#091625;border:1px solid #1d3248;border-radius:11px;padding:14px;text-align:center}.ml-card span{display:block;color:#71879d;font-size:9px;text-transform:uppercase;letter-spacing:1px}.ml-card strong{display:block;font-size:23px;margin-top:5px;color:#7dd5ff}.ml-meta{margin-top:13px;color:#7d93a8;font-size:10px;line-height:1.6}.footer{padding:20px 0 5px;color:#516a81;font-size:10px;text-align:center}.offline{color:#ff7d7d!important}.warning{color:#ffd26b!important}@media(max-width:1050px){.hero{grid-template-columns:1fr 1fr}.hero-card:first-child{grid-column:1/-1}.content-grid{grid-template-columns:1fr}}@media(max-width:750px){.topbar{padding:0 16px}.wrap{padding:16px}.wan-grid{grid-template-columns:1fr}.hero{grid-template-columns:1fr}.hero-card:first-child{grid-column:auto}.ml-grid{grid-template-columns:1fr 1fr}.metrics{grid-template-columns:1fr 1fr}}@media(max-width:480px){.ml-grid{grid-template-columns:1fr}.metrics{grid-template-columns:1fr}.score{font-size:48px}}
</style>
</head>
<body>
<header class="topbar"><div class="brand"><div class="brand-mark">🚆</div><div><h1>RailConnect Control Center</h1><small>Dual-WAN railway connectivity intelligence</small></div></div><div class="live"><span class="dot"></span> LIVE MONITORING</div></header>
<main class="wrap">
<section class="hero">
<div class="hero-card"><div class="eyebrow">Train operations</div><div class="hero-title">Train 12045 · Delhi → Chandigarh</div><div class="hero-sub">Operational connectivity supervision · 108 km/h · automated WAN intelligence</div></div>
<div class="hero-card"><div class="eyebrow">Active link</div><div id="hero-active" class="mini-value mini-good">Connecting...</div><div class="hero-sub">Current route</div></div>
<div class="hero-card"><div class="eyebrow">Gateway</div><div id="gateway" class="mini-value mini-blue">ONLINE</div><div class="hero-sub">Live telemetry feed</div></div>
</section>
<section class="section-title"><h2>NETWORK HEALTH</h2><span id="last-update">Waiting for telemetry…</span></section>
<section class="wan-grid">
<div id="wan-a" class="panel wan"><div class="wan-head"><div class="wan-name">📡 WAN A</div><div id="status-a" class="status">LOADING</div></div><div class="score-row"><div id="score-a" class="score">--</div><div class="score-label">/ 100 health score</div></div><div class="metrics"><div class="metric"><label>Bandwidth</label><strong id="bandwidth-a">--</strong><div class="bar"><i id="bar-bandwidth-a"></i></div></div><div class="metric"><label>Signal</label><strong id="signal-a">--</strong><div class="bar"><i id="bar-signal-a"></i></div></div><div class="metric"><label>Latency</label><strong id="latency-a">--</strong></div><div class="metric"><label>Packet loss</label><strong id="loss-a">--</strong></div></div></div>
<div id="wan-b" class="panel wan"><div class="wan-head"><div class="wan-name">📡 WAN B</div><div id="status-b" class="status">LOADING</div></div><div class="score-row"><div id="score-b" class="score">--</div><div class="score-label">/ 100 health score</div></div><div class="metrics"><div class="metric"><label>Bandwidth</label><strong id="bandwidth-b">--</strong><div class="bar"><i id="bar-bandwidth-b"></i></div></div><div class="metric"><label>Signal</label><strong id="signal-b">--</strong><div class="bar"><i id="bar-signal-b"></i></div></div><div class="metric"><label>Latency</label><strong id="latency-b">--</strong></div><div class="metric"><label>Packet loss</label><strong id="loss-b">--</strong></div></div></div>
</section>
<div class="active-strip"><div><div class="active-label">ACTIVE NETWORK</div><div id="active-network" class="active-main">Connecting...</div></div><div id="active-score" class="active-score">Telemetry pending</div></div>
<section class="content-grid">
<div class="panel"><div class="section-title"><h2>LIVE TELEMETRY TREND</h2><span>Health score · last ~60 samples</span></div><div class="chart-wrap"><canvas id="chart" class="chart"></canvas></div><div class="legend"><span><b style="background:#54c8ff"></b>WAN A score</span><span><b style="background:#7be0a5"></b>WAN B score</span></div></div>
<div class="panel pred"><div class="section-title"><h2>🤖 ML NEXT-WAN PREDICTION</h2><span id="model-status">MODEL</span></div><div class="pred-main"><div class="pred-status"><span class="eyebrow">Prediction horizon</span><span id="pred-badge" class="pred-badge">ANALYZING</span></div><div id="pred-value" class="pred-value">Preparing model…</div><div class="confidence">Confidence <strong id="pred-confidence">--</strong></div><div class="progress"><i id="pred-progress"></i></div><div id="pred-note" class="prediction-note">The model evaluates current WAN conditions and trend features.</div></div></div>
</section>
<section class="content-grid">
<div class="panel history"><div class="section-title"><h2>🧠 PREDICTION HISTORY</h2><span>Latest decisions</span></div><table class="history-table"><thead><tr><th>Time</th><th>Prediction</th><th>Confidence</th><th>Horizon</th></tr></thead><tbody id="history-body"><tr><td colspan="4" style="color:#667f96;padding:18px 8px">Collecting predictions…</td></tr></tbody></table></div>
<div class="panel events"><div class="section-title"><h2>🔄 FAILOVER EVENT LOG</h2><span>Detected locally</span></div><div id="events-body"><div style="color:#667f96;padding:12px 0;font-size:11px">Waiting for network changes…</div></div></div>
</section>
<section class="panel ml"><div class="section-title"><h2>📊 ML MODEL PERFORMANCE</h2><span id="ml-ready">EVALUATION</span></div><div class="ml-grid"><div class="ml-card"><span>Accuracy</span><strong id="ml-accuracy">--</strong></div><div class="ml-card"><span>Precision</span><strong id="ml-precision">--</strong></div><div class="ml-card"><span>Recall</span><strong id="ml-recall">--</strong></div><div class="ml-card"><span>F1 Score</span><strong id="ml-f1">--</strong></div></div><div id="ml-meta" class="ml-meta">Loading evaluation metrics…</div></section>
<div class="footer">RailConnect Dashboard · Live dual-WAN telemetry · ML-assisted failover prediction</div>
</main>
<script>
const historyData=[];const events=[];let previousActive=null;let previousScores={a:null,b:null};let lastPredictionKey=null;
function esc(s){return String(s).replace(/[&<>\"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]))}
function setBar(id,value,max){document.getElementById(id).style.width=Math.max(0,Math.min(100,(Number(value)||0)/max*100))}
function updateWan(prefix,w){document.getElementById('score-'+prefix).innerText=Number(w.score).toFixed(1);document.getElementById('status-'+prefix).innerText=w.status||'UNKNOWN';document.getElementById('bandwidth-'+prefix).innerText=w.bandwidth+' Mbps';document.getElementById('latency-'+prefix).innerText=w.latency+' ms';document.getElementById('loss-'+prefix).innerText=w.packet_loss;document.getElementById('signal-'+prefix).innerText=w.signal;setBar('bar-bandwidth-'+prefix,w.bandwidth,100);setBar('bar-signal-'+prefix,w.signal,100)}
function renderHistory(){const body=document.getElementById('history-body');if(!historyData.length){body.innerHTML='<tr><td colspan="4" style="color:#667f96;padding:18px 8px">No predictions recorded yet.</td></tr>';return}body.innerHTML=historyData.map(x=>`<tr><td>${x.time}</td><td><span class="tag ${x.switch?'switch-tag':''}">${esc(x.text)}</span></td><td>${x.conf}%</td><td>${x.horizon}s</td></tr>`).join('')}
function renderEvents(){const body=document.getElementById('events-body');if(!events.length){body.innerHTML='<div style="color:#667f96;padding:12px 0;font-size:11px">No failover changes detected yet.</div>';return}body.innerHTML=events.map(x=>`<div class="event"><div class="event-time">${x.time}</div><div><div class="event-title">${esc(x.from)} → ${esc(x.to)}</div><div class="event-reason">${esc(x.reason||'WAN path changed')}</div></div><div class="event-ok">FAILOVER</div></div>`).join('')}
function drawChart(){const c=document.getElementById('chart'),r=c.getBoundingClientRect(),d=devicePixelRatio||1;c.width=r.width*d;c.height=r.height*d;const x=c.getContext('2d');x.scale(d,d);const w=r.width,h=r.height;x.clearRect(0,0,w,h);x.strokeStyle='#1b3045';x.lineWidth=1;for(let i=0;i<5;i++){const y=15+i*(h-30)/4;x.beginPath();x.moveTo(0,y);x.lineTo(w,y);x.stroke()}const draw=(key,stroke)=>{const vals=historyData.slice().reverse().map(v=>v[key]).filter(v=>typeof v==='number');if(vals.length<2)return;x.strokeStyle=stroke;x.lineWidth=2;x.beginPath();vals.forEach((v,i)=>{const px=i*(w-12)/(Math.max(1,vals.length-1))+6;const py=h-15-(Math.max(0,Math.min(100,v))/100)*(h-30);i?x.lineTo(px,py):x.moveTo(px,py)});x.stroke()};draw('a','#54c8ff');draw('b','#7be0a5')}
async function loadLogs(){
 try{
  const [hr,er]=await Promise.all([fetch('/prediction_history'),fetch('/failover_events')]);
  const h=await hr.json(),e=await er.json();
  historyData.length=0; (h.predictions||[]).forEach(x=>historyData.push({time:x.time,text:x.prediction,conf:x.confidence,horizon:x.horizon,switch:x.switch_predicted}));
  events.length=0; (e.events||[]).forEach(x=>events.push(x));
  renderHistory(); renderEvents(); drawChart();
 }catch(e){}
}

async function updateDashboard(){try{const response=await fetch('/network');const data=await response.json();updateWan('a',data.wan_a);updateWan('b',data.wan_b);const active=data.active_network;document.getElementById('active-network').innerText='🟢 '+active;document.getElementById('hero-active').innerText=active;document.getElementById('active-score').innerText='Score '+Number(active==='WAN A'?data.wan_a.score:data.wan_b.score).toFixed(1);document.getElementById('gateway').innerText='ONLINE';document.getElementById('gateway').className='mini-value mini-good';document.getElementById('wan-a').classList.toggle('active',active==='WAN A');document.getElementById('wan-b').classList.toggle('active',active==='WAN B');const now=new Date();document.getElementById('last-update').innerText='Updated '+now.toLocaleTimeString();previousActive=active;previousScores={a:data.wan_a.score,b:data.wan_b.score};if(data.prediction&&data.prediction.status==='READY'){const p=data.prediction;const conf=Math.round((p.confidence||0)*100);const text=p.switch_predicted?'Switch to '+p.predicted_wan+' likely':'No WAN change expected';document.getElementById('pred-value').innerText=text;document.getElementById('pred-confidence').innerText=conf+'%';document.getElementById('pred-progress').style.width=conf+'%';document.getElementById('pred-badge').innerText=p.switch_predicted?'SWITCH ALERT':'STABLE';document.getElementById('model-status').innerText=p.model||'RANDOM FOREST';document.getElementById('pred-note').innerText=(p.switch_predicted?'The model detects a likely WAN transition ':'The model expects the active WAN to remain stable ')+'within ~'+p.horizon_seconds+' seconds.';const key=(p.switch_predicted?'S':'N')+'|'+(p.predicted_wan||'NONE')+'|'+conf;lastPredictionKey=key;}else{document.getElementById('pred-value').innerText='Preparing model…';document.getElementById('pred-badge').innerText='ANALYZING'}}catch(e){document.getElementById('gateway').innerText='OFFLINE';document.getElementById('gateway').className='mini-value offline';document.getElementById('active-network').innerText='🔴 Gateway Offline';document.getElementById('pred-value').innerText='Gateway unavailable';}}
async function updateMetrics(){try{const response=await fetch('/ml_metrics');const metrics=await response.json();if(metrics.status!=='READY'){document.getElementById('ml-meta').innerText='📚 '+(metrics.message||'Collecting more data…');return}const s=metrics.switch_prediction;document.getElementById('ml-ready').innerText='READY';document.getElementById('ml-accuracy').innerText=(s.accuracy*100).toFixed(2)+'%';document.getElementById('ml-precision').innerText=(s.precision*100).toFixed(2)+'%';document.getElementById('ml-recall').innerText=(s.recall*100).toFixed(2)+'%';document.getElementById('ml-f1').innerText=(s.f1*100).toFixed(2)+'%';document.getElementById('ml-meta').innerText='Model: '+metrics.model+' · Training: '+metrics.training_source+' · Trend features: '+(metrics.trend_features?'ON':'OFF')+' · Evaluated: '+metrics.evaluated_samples+' samples · Horizon: '+metrics.prediction_horizon_seconds+' sec'}catch(e){document.getElementById('ml-meta').innerText='ML evaluation temporarily unavailable.'}}
updateDashboard();updateMetrics();loadLogs();setInterval(updateDashboard,2000);setInterval(updateMetrics,10000);setInterval(loadLogs,2000);window.addEventListener('resize',drawChart);
</script>
</body></html>
'''

@app.route('/')
def dashboard():
    return render_template_string(HTML)

@app.route('/failover_events')
def failover_events():
    return jsonify({'events': FAILOVER_EVENTS})


@app.route('/prediction_history')
def prediction_history():
    return jsonify({'predictions': PREDICTION_HISTORY})


@app.route('/ml_metrics')
def ml_metrics():
    try:
        from ml_evaluation import evaluate
        return evaluate()
    except Exception as e:
        return {'status':'ERROR','message':str(e)},500

@app.route('/network')
def network():
    global LAST_ACTIVE_NETWORK, LAST_PREDICTION_KEY
    try:
        response=requests.get(WINDOWS_API,timeout=5)
        if response.ok:
            try:
                data=response.json()
                now=datetime.now().strftime('%H:%M:%S')
                active=data.get('active_network')

                # Persist actual active-WAN transitions on the server.
                if LAST_ACTIVE_NETWORK and active and active != LAST_ACTIVE_NETWORK:
                    old_score=data.get('wan_a',{}).get('score') if LAST_ACTIVE_NETWORK=='WAN A' else data.get('wan_b',{}).get('score')
                    new_score=data.get('wan_a',{}).get('score') if active=='WAN A' else data.get('wan_b',{}).get('score')
                    FAILOVER_EVENTS.insert(0,{
                        'time':now,
                        'from':LAST_ACTIVE_NETWORK,
                        'to':active,
                        'reason':f'Active route changed · new WAN score {float(new_score):.1f}' if new_score is not None else 'Active route changed according to gateway telemetry',
                        'from_score':old_score,
                        'to_score':new_score
                    })
                    del FAILOVER_EVENTS[MAX_EVENTS:]
                LAST_ACTIVE_NETWORK=active

                # Persist each materially new ML decision.
                p=data.get('prediction') or {}
                if p.get('status')=='READY':
                    conf=round((p.get('confidence') or 0)*100)
                    key=f"{'S' if p.get('switch_predicted') else 'N'}|{p.get('predicted_wan') or 'NONE'}|{conf}"
                    if key != LAST_PREDICTION_KEY:
                        PREDICTION_HISTORY.insert(0,{
                            'time':now,
                            'prediction':'Switch to '+str(p.get('predicted_wan'))+' likely' if p.get('switch_predicted') else 'No WAN change expected',
                            'confidence':conf,
                            'horizon':p.get('horizon_seconds'),
                            'switch_predicted':bool(p.get('switch_predicted')),
                            'model':p.get('model','Random Forest')
                        })
                        del PREDICTION_HISTORY[MAX_PREDICTIONS:]
                        LAST_PREDICTION_KEY=key

                return jsonify(data)
            except ValueError:
                pass
        return response.text,response.status_code,{'Content-Type':'application/json'}
    except Exception as e:
        return {'error':str(e)},500

if __name__=='__main__':
    app.run(host='0.0.0.0',port=5001,debug=False)
