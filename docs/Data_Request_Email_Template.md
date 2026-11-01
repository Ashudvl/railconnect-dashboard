# ✉️ Email Template for Requesting Test Data from Organizations

You can copy and paste this email directly when reaching out to railway administrations, transit authorities, research labs, or router hardware OEMs (e.g. Peplink, Cradlepoint, Advantech, Cisco).

---

**Subject:** Collaboration & Telemetry Data Request: Autonomous Multi-WAN High-Speed Rail Project (RailConnect)

**Dear [Contact Name / Operations Team / Technical Director],**

I hope this email finds you well.

I am writing from the **RailConnect Research & Development Project**, where we are developing an autonomous multi-link onboard network control platform designed specifically for high-speed passenger rail (160–350 km/h).

### The Challenge We Address:
At high train speeds, cellular SIM connections suffer from severe Doppler frequency shift, rapid cell handovers every 15–30 seconds, and carriage metal shielding. RailConnect addresses this by binding multiple heterogeneous uplinks (Dual 5G Cellular SIMs, Starlink LEO Satellite, and Trackside Wi-Fi 6E) with a **Random Forest Predictive Failover Engine (10-second lookahead)** and dynamic **Train LAN QoS traffic shaping** to guarantee 100% uptime for train signaling while protecting passenger internet quality.

### Our Request:
To validate and benchmark our predictive handover model against real-world rail corridors, we are looking to analyze **1 to 3 sample trip logs** (CSV, router telemetry export, or NetFlow logs). The specific fields of interest are:
- **Timestamp (UTC), GPS Coordinates, and Train Speed (km/h)**
- **Cellular Modem Metrics**: RSRP (dBm), RSRQ (dB), SINR (dB), Ping Latency (ms), Throughput (Mbps), and Cell ID / PCI
- **Failover / WAN transition logs** (if available)

### Confidentiality & Mutual Value Commitment:
1. **Zero Passenger PII**: We strictly require physical RF and network-layer parameters. No passenger browsing data, MAC addresses, or personal identifiable information (PII) is collected or processed.
2. **Confidentiality / NDA**: We are glad to sign a mutual Non-Disclosure Agreement (NDA). Coordinates and cell IDs can be pseudonymized or normalized prior to sharing.
3. **Value Delivered Back to Your Organization**: In return, we will provide a comprehensive **Corridor RF Quality & Dead-Zone Heatmap Audit Report**, including benchmark handover metrics, simulated QoS improvements, and router optimization recommendations tailored to your fleet.

### Attached Documents:
- **RailConnect Technical Project Report (PDF)** — Full engineering specification, architecture, and simulation validation.
- **One-Page Executive Overview (PDF)** — High-level architecture, objectives, and data request scope.

We would be grateful for the opportunity to have a brief 15-minute call or email exchange to discuss whether your team could share sample logs.

Thank you very much for your time and consideration.

Warm regards,

**[Your Name]**  
Lead Engineer / Researcher, RailConnect Autonomous Systems  
Email: [Your Email] | Phone: [Your Phone]  
Project Repository: `github.com/ashuyadav/railconnect-dashboard`  
Live Demo: `http://localhost:8000`
