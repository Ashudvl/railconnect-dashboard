export type WanLinkType = 'cellular' | 'satellite' | 'wifi'
export type WanStatus = 'active' | 'standby' | 'degraded' | 'offline'

export interface WanTelemetry {
  id: string
  name: string
  type: WanLinkType
  band: string
  bandwidth: number
  latency: number
  packet_loss: number
  jitter: number
  signal: number
  score: number
  status: WanStatus
  is_active: boolean
  color: string
}

export interface TrainTelemetry {
  train_id: string
  name: string
  line: string
  speed_kmh: number
  max_speed_kmh: number
  lat: number
  lng: number
  progress_pct: number
  current_zone: string
  zone_type: 'urban' | 'rural' | 'gorge' | 'tunnel' | 'station'
  tunnel_depth_m: number | null
  next_station: string
  eta_next_station_min: number
  active_link_id: string
}

export interface FailoverEvent {
  id: string
  timestamp: string
  from_link: string
  to_link: string
  from_link_name: string
  to_link_name: string
  reason: string
  trigger: 'ml_proactive' | 'threshold_policy' | 'manual_override'
  duration_ms: number
  quality_gain: number
}

export interface FactorItem {
  factor: string
  impact: number
}

export interface MlPrediction {
  timestamp: string
  imminent_failover: boolean
  risk_score: number
  predicted_link: string
  predicted_link_name: string
  confidence: number
  reasoning: string
  top_factors: FactorItem[]
}

export interface DisruptionState {
  type: 'tunnel' | 'carrier_fade' | 'satellite_obstruction' | 'packet_storm' | null
  intensity: number
  time_remaining_s: number
  manual_link_lock: string | null
}

export interface CoachLanStatus {
  coach_id: string
  name: string
  connected_clients: number
  ap_status: 'healthy' | 'throttled' | 'failsafe' | 'offline'
  allocated_mbps: number
  rx_mbps: number
  tx_mbps: number
}

export interface TrainLanTelemetry {
  lan_gateway_ip: string
  subnet: string
  total_connected_clients: number
  total_lan_throughput_mbps: number
  lan_health_pct: number
  qos_mode: 'unconstrained' | 'adaptive_throttling' | 'critical_only_failsafe'
  critical_ops_mbps: number
  train_systems_mbps: number
  passenger_wifi_mbps: number
  coaches: CoachLanStatus[]
}

export interface SystemState {
  timestamp: string
  train: TrainTelemetry
  links: Record<string, WanTelemetry>
  active_link_id: string
  prediction: MlPrediction
  lan: TrainLanTelemetry
  recent_events: FailoverEvent[]
  disruption: DisruptionState
  auto_failover_enabled: boolean
  ml_proactive_enabled: boolean
}

export interface RouteStation {
  id: string
  name: string
  km: number
  lat: number
  lng: number
  has_station_wifi: boolean
}

export interface RouteZone {
  name: string
  type: string
  start_km: number
  end_km: number
  length_km?: number
}

export interface RouteTower {
  id: string
  name: string
  carrier: string
  km: number
  range_km: number
  lat: number
  lng: number
}

export interface RouteWaypoint {
  km: number
  lat: number
  lng: number
}

export interface RouteCorridor {
  name: string
  total_length_km: number
  stations: RouteStation[]
  zones: RouteZone[]
  cell_towers: RouteTower[]
  waypoints: RouteWaypoint[]
}
