import React from 'react'
import {
  Network,
  ShieldCheck,
  Smartphone,
  Video,
  Radio,
  Users,
  Cpu,
  Layers,
  Activity,
  AlertCircle,
  Wifi,
} from 'lucide-react'
import { TrainLanTelemetry, WanTelemetry } from '../types/telemetry'

interface TrainLanMonitorProps {
  lan: TrainLanTelemetry | undefined
  activeLink: WanTelemetry | undefined
  trainSpeed: number
}

export const TrainLanMonitor: React.FC<TrainLanMonitorProps> = ({
  lan,
  activeLink,
  trainSpeed,
}) => {
  if (!lan) return null

  const getQoSBadge = (mode: string) => {
    switch (mode) {
      case 'unconstrained':
        return (
          <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
            UNCONSTRAINED LAN (FULL CAPACITY)
          </span>
        )
      case 'adaptive_throttling':
        return (
          <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/40 animate-pulse">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
            ADAPTIVE SIM THROTTLING (SPEED DAMPENING)
          </span>
        )
      case 'critical_only_failsafe':
      default:
        return (
          <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/20 text-rose-300 border border-rose-500/40">
            <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
            FAILSAFE: CRITICAL OPS ONLY (SIM STARVATION)
          </span>
        )
    }
  }

  const activeBw = activeLink?.bandwidth || 0
  const isSimSlow = activeBw < 35.0

  return (
    <div className="rounded-xl border border-slate-800/80 bg-slate-900/70 backdrop-blur-md p-4 lg:p-5">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Network className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
              Onboard Train LAN & Dynamic Coach Distribution
            </h3>
            <span className="text-xs text-slate-400">
              Gigabit Train Consist Backbone (IEC 61375) • Gateway {lan.lan_gateway_ip} ({lan.subnet})
            </span>
          </div>
        </div>

        {getQoSBadge(lan.qos_mode)}
      </div>

      {/* Speed & SIM Impact Context Banner */}
      <div className="p-3 rounded-lg bg-[#070f1e] border border-cyan-500/20 mb-4 flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2.5">
          <Activity className="w-4 h-4 text-cyan-400 shrink-0" />
          <span className="text-slate-300">
            At high speed (<strong className="text-white">{trainSpeed} km/h</strong>), cellular SIMs experience Doppler shift & frequent cell handovers.
            Active WAN delivers <strong className="text-cyan-300">{activeBw.toFixed(1)} Mbps</strong>.
            {isSimSlow ? (
              <span className="text-amber-300 font-semibold ml-1">
                Train LAN QoS is dynamically shielding signaling & compressing passenger streaming to prevent drops.
              </span>
            ) : (
              <span className="text-emerald-300 font-semibold ml-1">
                Train LAN is operating at optimal throughput across all coaches.
              </span>
            )}
          </span>
        </div>

        <div className="flex items-center gap-3 text-slate-400 font-mono shrink-0">
          <span>Active LAN Clients: <strong className="text-white">{lan.total_connected_clients}</strong></span>
          <span>•</span>
          <span>LAN Health: <strong className="text-emerald-400">{lan.lan_health_pct}%</strong></span>
        </div>
      </div>

      {/* Traffic Slicing & Priority Breakdown 3-Column */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-5">
        {/* 1. Critical Operational LAN */}
        <div className="p-3.5 rounded-lg bg-slate-950/60 border border-emerald-500/30">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-300">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Critical Train Operational LAN</span>
            </div>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              100% SLA
            </span>
          </div>
          <div className="text-xl font-bold font-mono text-white mb-1">
            {lan.critical_ops_mbps.toFixed(1)} <span className="text-xs text-slate-400 font-normal">Mbps</span>
          </div>
          <p className="text-[11px] text-slate-400 leading-snug">
            Signaling, Driver Radio VoIP, ETCS Safety, and Train Diagnostics. Never throttled.
          </p>
        </div>

        {/* 2. Train Systems LAN */}
        <div className="p-3.5 rounded-lg bg-slate-950/60 border border-cyan-500/30">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-cyan-300">
              <Video className="w-4 h-4 text-cyan-400" />
              <span>Train Systems & Security LAN</span>
            </div>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
              PRIORITY 2
            </span>
          </div>
          <div className="text-xl font-bold font-mono text-white mb-1">
            {lan.train_systems_mbps.toFixed(1)} <span className="text-xs text-slate-400 font-normal">Mbps</span>
          </div>
          <p className="text-[11px] text-slate-400 leading-snug">
            Onboard CCTV compression, Passenger Info Screens (PIS), and Ticket Validation gates.
          </p>
        </div>

        {/* 3. Passenger Wi-Fi LAN */}
        <div className="p-3.5 rounded-lg bg-slate-950/60 border border-purple-500/30">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-purple-300">
              <Smartphone className="w-4 h-4 text-purple-400" />
              <span>Passenger Wi-Fi LAN (Coaches)</span>
            </div>
            <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border ${
              isSimSlow ? 'bg-amber-500/20 text-amber-300 border-amber-500/30' : 'bg-purple-500/20 text-purple-300 border-purple-500/30'
            }`}>
              {isSimSlow ? 'THROTTLED' : 'ACTIVE'}
            </span>
          </div>
          <div className="text-xl font-bold font-mono text-white mb-1">
            {lan.passenger_wifi_mbps.toFixed(1)} <span className="text-xs text-slate-400 font-normal">Mbps</span>
          </div>
          <p className="text-[11px] text-slate-400 leading-snug">
            Passenger internet browsing & media. Dynamically shaped to match fluctuating external SIM throughput.
          </p>
        </div>
      </div>

      {/* Coach-by-Coach Car Consist Distribution */}
      <div>
        <h4 className="text-xs font-mono font-semibold uppercase text-slate-400 mb-2.5 flex items-center gap-1.5">
          <Layers className="w-3.5 h-3.5 text-cyan-400" />
          Train Consist Coach Access Points (AP) Status
        </h4>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2.5">
          {lan.coaches.map((coach) => (
            <div
              key={coach.coach_id}
              className={`p-3 rounded-lg border transition-all ${
                coach.ap_status === 'healthy'
                  ? 'bg-slate-950/50 border-slate-800 hover:border-slate-700'
                  : coach.ap_status === 'throttled'
                  ? 'bg-amber-950/20 border-amber-500/40'
                  : 'bg-rose-950/20 border-rose-500/40'
              }`}
            >
              <div className="flex items-start justify-between gap-1 mb-1.5">
                <span className="text-xs font-semibold text-white leading-tight">{coach.name}</span>
                <span
                  className={`w-2 h-2 rounded-full mt-0.5 ${
                    coach.ap_status === 'healthy'
                      ? 'bg-emerald-400'
                      : coach.ap_status === 'throttled'
                      ? 'bg-amber-400 animate-pulse'
                      : 'bg-rose-400'
                  }`}
                  title={`AP Status: ${coach.ap_status}`}
                />
              </div>

              <div className="flex items-baseline justify-between text-xs font-mono my-1">
                <span className="text-slate-400 text-[11px]">LAN Bandwidth:</span>
                <span className="font-bold text-cyan-300">{coach.allocated_mbps} Mbps</span>
              </div>

              <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-1 border-t border-slate-800/80">
                <span className="flex items-center gap-1">
                  <Users className="w-3 h-3 text-slate-500" />
                  {coach.connected_clients} clients
                </span>
                <span className="text-[10px] uppercase font-bold text-slate-500">
                  {coach.ap_status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
