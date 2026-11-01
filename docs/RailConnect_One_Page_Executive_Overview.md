# 🚄 RailConnect 2.0: One-Page Executive Overview
**Autonomous Multi-WAN Failover & Dynamic Train LAN QoS Orchestration for High-Speed Rail**

---

### 1. Mission & Core Objectives
High-speed rail (160–350 km/h) onboard connectivity is severely disrupted by Doppler frequency shift, carriage metal penetration loss, and rapid cell tower handoffs every 15–25 seconds. 

**RailConnect 2.0** is an intelligent edge platform designed to guarantee **100% operational uptime for train signaling, telemetry, and driver communications** while dynamically maximizing passenger Wi-Fi throughput. It solves link dropouts through a 4-link heterogeneous uplink matrix, predictive Machine Learning failover (10s lookahead), and dynamic Train LAN QoS traffic shaping.

---

### 2. Architecture & Information Flow

```
[ HETEROGENEOUS WAN UPLINKS ]
 • 5G Carrier Alpha (C-Band / mmWave, 72 Mbps)
 • 5G Carrier Beta (Sub-6 GHz Wide Coverage, 88 Mbps)
 • Starlink LEO Satellite (Ku/Ka Band, 165 Mbps)
 • Trackside Station Wi-Fi 6E (6 GHz Gigabit, 850 Mbps)
                   │
                   ▼
[ RAILCONNECT CORE EDGE ENGINE ]
 • Random Forest ML Predictor (10s lookahead horizon)
 • Sub-50ms Seamless Handover (Zero packet loss / session drop)
 • FastAPI + WebSockets (1.0 Hz live telemetry streaming)
 • SQLite Time-Series Store (Auditable transition log)
                   │
                   ▼
[ ONBOARD TRAIN CONSIST LAN (IEC 61375) ]
 🛡️ Critical Operational LAN: Signaling, Driver VoIP, Diagnostics (100% Guaranteed SLA)
 📹 Train Systems LAN: CCTV Compression, Passenger Information Displays (PIS)
 📱 Passenger Wi-Fi LAN: Adaptive Throttling (dynamically modulated during SIM fades)
 🚆 Coach Consist APs: Locomotive Cab, Coach C1 (Exec), Coach C2-C3, Pantry Car
```

---

### 3. Key Innovations & Differentiators

1. **ML Proactive Switching (vs Reactive Drops)**: Rather than waiting for a connection to crash, RailConnect tracks RF signal decay rates and upcoming track hazards (tunnels/canyons) to switch uplinks **10 seconds ahead of failure**.
2. **Dynamic LAN Traffic Slicing**: When cellular SIM speeds drop at high speeds, the Onboard LAN automatically compresses heavy passenger video streaming to **strictly shield train safety systems**.
3. **Blackout & Tunnel Resilience**: Solid rock tunnels automatically engage **Critical Failsafe Mode**, restoring to unconstrained Gigabit throughput as soon as station Wi-Fi 6E is detected.

---

### 4. Telemetry Data Collaboration Request

To calibrate and benchmark predictive algorithms against physical rail corridors, we are seeking operational modem telemetry datasets from railway administrations, transit operators, and hardware OEMs (Peplink, Cradlepoint, Cisco, Advantech).

- **Requested Data**: 1 to 3 past trip logs (CSV or router logs) containing:
  - Timestamp (UTC), GPS Coordinates, Train Speed (km/h)
  - Cellular modem parameters: RSRP (dBm), RSRQ (dB), SINR (dB), Latency (ms), Throughput (Mbps), Cell ID
- **Privacy & Security Guarantee**: Strictly physical RF layer metrics are requested. **Zero passenger PII, MAC addresses, or browsing history is ever collected.** All datasets can be anonymized and protected under a mutual Non-Disclosure Agreement (NDA).
- **Return Deliverable**: Participating partners receive a complimentary **Corridor RF Health & Predictive Handover Audit Report**, detailing dead-zone heatmaps and projected connectivity gains.

---

**Contact**: RailConnect Research & Engineering Group  
**Email**: `contact@railconnect.io` • **Repository**: `github.com/ashuyadav/railconnect-dashboard`  
**Live Prototype Instance**: `http://localhost:8000`
