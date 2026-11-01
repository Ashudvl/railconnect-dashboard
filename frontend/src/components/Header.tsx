import React from 'react'
import { Activity, ShieldCheck, Zap, Radio, Train, Gauge, AlertTriangle } from 'lucide-react'
import { SystemState } from '../types/telemetry'
import { ConnectionStatus } from '../hooks/useWebSocket'

interface HeaderProps {
  state: SystemState | null
  status: ConnectionStatus
  onToggleAutoFailover: (enabled: boolean) => void
  onToggleMlProactive: (enabled: boolean) => void
}

export const Header: React.FC<HeaderProps> = ({
  state,
  status,
  onToggleAutoFailover,
  onToggleMlProactive,
}) => {
  const train = state?.train
  const activeLink = state?.links && state.active_link_id ? state.links[state.active_link_id] : null
  const disruption = state?.disruption

  return (
    <header className="border-b border-slate-800 bg-[#091120]/90 backdrop-blur-md sticky top-0 z-50 px-4 lg:px-8 py-3.5 shadow-xl">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        {/* Brand & Train identity */}
        <div className="flex items-center gap-4">
          <div className="relative flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-600/30 border border-cyan-500/40 shadow-[0_0_20px_rgba(6,182,212,0.25)]">
            <Train className="w-6 h-6 text-cyan-400" />
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${status === 'connected' ? 'bg-emerald-400' : 'bg-amber-400'}`} />
              <span className={`relative inline-flex rounded-full h-3 w-3 ${status === 'connected' ? 'bg-emerald-500' : 'bg-amber-500'}`} />
            </span>
          </div>

          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                RailConnect <span className="text-xs px-2 py-0.5 font-mono font-semibold rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">v2.0 PRO</span>
              </h1>
              <span className="text-xs text-slate-500">|</span>
              <span className="text-sm font-semibold text-slate-300 font-mono">{train?.train_id || 'RC-709'}</span>
              <span className="hidden sm:inline-block text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                {train?.line || 'Pacific Alpine Corridor'}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5 flex items-center gap-3">
              <span>Next Station: <strong className="text-slate-200">{train?.next_station || '---'}</strong> (~{train?.eta_next_station_min || 0}m)</span>
              <span className="text-slate-600">•</span>
              <span>Zone: <strong className="text-cyan-400">{train?.current_zone || 'Calculating...'}</strong></span>
            </p>
          </div>
        </div>

        {/* Speedometer & Active WAN Pill */}
        <div className="flex items-center flex-wrap gap-3">
          {/* Active Disruption Badge if any */}
          {disruption?.type && (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-rose-500/15 border border-rose-500/40 text-rose-300 text-xs font-semibold animate-pulse">
              <AlertTriangle className="w-4 h-4 text-rose-400" />
              <span>DISRUPTION: {disruption.type.replace('_', ' ').toUpperCase()} ({disruption.time_remaining_s}s)</span>
            </div>
          )}

          {/* Speed badge */}
          <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-slate-200 font-mono text-sm">
            <Gauge className="w-4 h-4 text-cyan-400" />
            <span>Speed: <strong className="text-white text-base">{train?.speed_kmh || 0}</strong> <span className="text-xs text-slate-400">km/h</span></span>
          </div>

          {/* Active Link Pill */}
          <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-slate-900/80 border border-cyan-500/30 text-xs">
            <Radio className="w-4 h-4 text-cyan-400 animate-pulse" />
            <div className="flex flex-col">
              <span className="text-[10px] uppercase text-slate-400 font-mono leading-none">Active Uplink</span>
              <span className="font-semibold text-cyan-300 leading-tight">{activeLink?.name || 'Searching...'}</span>
            </div>
            {activeLink && (
              <span className="ml-1 font-mono font-bold px-1.5 py-0.5 rounded text-[11px] bg-cyan-500/20 text-cyan-300">
                {activeLink.score} PTS
              </span>
            )}
          </div>

          {/* Master Toggles */}
          <div className="flex items-center gap-2 border-l border-slate-800 pl-3">
            <button
              onClick={() => onToggleAutoFailover(!state?.auto_failover_enabled)}
              className={`flex items-center gap-1.5 text-xs font-medium px-2.5 py-1.5 rounded-lg border transition-all ${
                state?.auto_failover_enabled
                  ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-300 hover:bg-emerald-500/25'
                  : 'bg-slate-800 border-slate-700 text-slate-400 hover:bg-slate-700'
              }`}
              title="Automatically switch WANs when health drops"
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Auto-Failover</span>
            </button>

            <button
              onClick={() => onToggleMlProactive(!state?.ml_proactive_enabled)}
              className={`flex items-center gap-1.5 text-xs font-medium px-2.5 py-1.5 rounded-lg border transition-all ${
                state?.ml_proactive_enabled
                  ? 'bg-purple-500/20 border-purple-500/40 text-purple-300 hover:bg-purple-500/30 shadow-[0_0_12px_rgba(168,85,247,0.2)]'
                  : 'bg-slate-800 border-slate-700 text-slate-400 hover:bg-slate-700'
              }`}
              title="ML predictive proactive switching ahead of degradation"
            >
              <Zap className="w-3.5 h-3.5" />
              <span>ML Proactive</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}
