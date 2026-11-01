"""
High-Speed Railway Corridor Route Data & Infrastructure Map
Optimized 16.0 km Demonstration Corridor for Rapid Failover & LAN Adaptation
"""

ROUTE_CORRIDOR = {
    "name": "High-Speed Mountain Express (Demo Corridor)",
    "total_length_km": 16.0,
    "stations": [
        {"id": "st-1", "name": "Central Union Terminal", "km": 0.0, "lat": 47.6000, "lng": -122.3300, "has_station_wifi": False},
        {"id": "st-2", "name": "Canyon Junction", "km": 5.0, "lat": 47.6700, "lng": -122.1200, "has_station_wifi": False},
        {"id": "st-3", "name": "Summit Tunnel Depot", "km": 7.5, "lat": 47.7400, "lng": -121.8500, "has_station_wifi": False},
        {"id": "st-4", "name": "Alpine Grand Terminal", "km": 16.0, "lat": 47.8400, "lng": -121.1800, "has_station_wifi": True},
    ],
    "zones": [
        {"name": "Metro Departure (Alpha Strong)", "type": "urban", "start_km": 0.0, "end_km": 2.5},
        {"name": "Ridge Sector (Beta Dominant)", "type": "ridge", "start_km": 2.5, "end_km": 5.5},
        {"name": "Gorge Canyon (Starlink Open Sky)", "type": "gorge", "start_km": 5.5, "end_km": 7.5},
        {"name": "Mount Kestrel Deep Tunnel", "type": "tunnel", "start_km": 7.5, "end_km": 11.0, "length_km": 3.5},
        {"name": "Alpine Terminal District", "type": "station", "start_km": 11.0, "end_km": 16.0},
    ],
    "cell_towers": [
        {"id": "t-1", "name": "Alpha City Mast", "carrier": "wan_5g_primary", "km": 0.8, "range_km": 2.0, "lat": 47.61, "lng": -122.30},
        {"id": "t-2", "name": "Beta Ridge High Mast", "carrier": "wan_5g_secondary", "km": 3.8, "range_km": 3.2, "lat": 47.66, "lng": -122.14},
        {"id": "t-3", "name": "Beta Canyon Relay", "carrier": "wan_5g_secondary", "km": 5.2, "range_km": 2.0, "lat": 47.72, "lng": -121.90},
        # Gap between km 7.5 and 11.0: 3.5 km mountain tunnel zone!
        {"id": "t-4", "name": "Alpha Valley Mast", "carrier": "wan_5g_primary", "km": 12.5, "range_km": 3.0, "lat": 47.80, "lng": -121.40},
        {"id": "t-5", "name": "Beta Grand Hub", "carrier": "wan_5g_secondary", "km": 15.2, "range_km": 2.5, "lat": 47.83, "lng": -121.20},
    ],
    # Waypoints mapping km to GPS coordinates
    "waypoints": [
        {"km": 0.0, "lat": 47.6000, "lng": -122.3300},
        {"km": 2.0, "lat": 47.6320, "lng": -122.2500},
        {"km": 4.0, "lat": 47.6700, "lng": -122.1200},
        {"km": 5.5, "lat": 47.7180, "lng": -121.9600},
        {"km": 7.5, "lat": 47.7400, "lng": -121.8500}, # Tunnel Portal Ingress
        {"km": 9.2, "lat": 47.7650, "lng": -121.7200}, # Tunnel Interior
        {"km": 11.0, "lat": 47.7880, "lng": -121.5500}, # Tunnel Portal Egress
        {"km": 13.5, "lat": 47.8180, "lng": -121.3400},
        {"km": 16.0, "lat": 47.8400, "lng": -121.1800}, # Alpine Grand
    ]
}

def get_position_at_km(km: float):
    wps = ROUTE_CORRIDOR["waypoints"]
    km = max(0.0, min(km, ROUTE_CORRIDOR["total_length_km"]))
    
    for i in range(len(wps) - 1):
        p1 = wps[i]
        p2 = wps[i + 1]
        if p1["km"] <= km <= p2["km"]:
            seg_len = p2["km"] - p1["km"]
            if seg_len == 0:
                return p1["lat"], p1["lng"]
            ratio = (km - p1["km"]) / seg_len
            lat = p1["lat"] + ratio * (p2["lat"] - p1["lat"])
            lng = p1["lng"] + ratio * (p2["lng"] - p1["lng"])
            return lat, lng
            
    return wps[-1]["lat"], wps[-1]["lng"]

def get_zone_at_km(km: float):
    for z in ROUTE_CORRIDOR["zones"]:
        if z["start_km"] <= km <= z["end_km"]:
            return z["name"], z["type"]
    return "Corridor Route", "rural"

def get_next_station_info(km: float, speed_kmh: float):
    for st in ROUTE_CORRIDOR["stations"]:
        if st["km"] > km:
            dist = st["km"] - km
            eta = (dist / max(speed_kmh, 10.0)) * 60.0
            return st["name"], round(eta, 1)
    first_st = ROUTE_CORRIDOR["stations"][0]
    return first_st["name"], 0.0
