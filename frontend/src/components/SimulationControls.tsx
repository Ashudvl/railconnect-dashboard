import React from 'react'
import {
  Sliders,
  Mountain,
  WifiOff,
  CloudRain,
  Flame,
  RotateCcw,
  Gauge,
  Wifi,
} from 'lucide-react'
import { DisruptionState, TrainTelemetry } from '../types/telemetry'

interface SimulationControlsProps {
  disruption: DisruptionState | undefined
  train: TrainTelemetry | undefined
  onInjectDisruption: (type: string, durationSeconds: number) => void
  onClearDisruption: () => void
  onSetTrainSpeed: (speed: number) => void
  onResetRoute: () => void
}

export const SimulationControls: React.FC<SimulationControlsProps> = ({
  disruption,
  train,
  onInjectDisruption,
  onClearDisruption,
  onSetTrainSpeed,
  onResetRoute,
}) => {
  return (
    <div className="rounded-xl border border-slate-800/80 bg-slate-900/70 backdrop-blur-md p-4 lg:p-5">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Sliders className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
              Scenario Disruption & Control Lab
            </h3>
            <span className="text-xs text-slate-400">
              Inject real-world anomalies to stress-test failover logic
            </span>
          </div>
        </div>

        {disruption?.type && (
          <button
            onClick={onClearDisruption}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold bg-rose-500/20 text-rose-300 border border-rose-500/40 hover:bg-rose-500/30 transition-all cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Clear Disruption ({disruption.time_remaining_s}s)
          </button>
        )}
      </div>

      {/* Disruption Buttons Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2.5 mb-5">
        <button
          onClick={() => onInjectDisruption('tunnel', 20)}
          className={`p-3 rounded-lg border text-left transition-all cursor-pointer flex flex-col justify-between ${
            disruption?.type === 'tunnel'
              ? 'bg-rose-500/20 border-rose-500/60 ring-1 ring-rose-500/50'
              : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900'
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <Mountain className="w-4 h-4 text-rose-400" />
            <span className="text-[10px] font-mono text-slate-400">20s</span>
          </div>
          <div>
            <div className="text-xs font-semibold text-white">Tunnel Entrance</div>
            <div className="text-[10px] text-slate-400 leading-tight mt-0.5">Cellular & Satellite drop</div>
          </div>
        </button>

        <button
          onClick={() => onInjectDisruption('carrier_fade', 15)}
          className={`p-3 rounded-lg border text-left transition-all cursor-pointer flex flex-col justify-between ${
            disruption?.type === 'carrier_fade'
              ? 'bg-amber-500/20 border-amber-500/60 ring-1 ring-amber-500/50'
              : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900'
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <WifiOff className="w-4 h-4 text-amber-400" />
            <span className="text-[10px] font-mono text-slate-400">15s</span>
          </div>
          <div>
            <div className="text-xs font-semibold text-white">5G Alpha Fade</div>
            <div className="text-[10px] text-slate-400 leading-tight mt-0.5">Carrier tower congestion</div>
          </div>
        </button>

        <button
          onClick={() => onInjectDisruption('satellite_obstruction', 15)}
          className={`p-3 rounded-lg border text-left transition-all cursor-pointer flex flex-col justify-between ${
            disruption?.type === 'satellite_obstruction'
              ? 'bg-purple-500/20 border-purple-500/60 ring-1 ring-purple-500/50'
              : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900'
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <CloudRain className="w-4 h-4 text-purple-400" />
            <span className="text-[10px] font-mono text-slate-400">15s</span>
          </div>
          <div>
            <div className="text-xs font-semibold text-white">Starlink Rain Fade</div>
            <div className="text-[10px] text-slate-400 leading-tight mt-0.5">Atmospheric storm</div>
          </div>
        </button>

        <button
          onClick={() => onInjectDisruption('packet_storm', 12)}
          className={`p-3 rounded-lg border text-left transition-all cursor-pointer flex flex-col justify-between ${
            disruption?.type === 'packet_storm'
              ? 'bg-red-500/20 border-red-500/60 ring-1 ring-red-500/50'
              : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900'
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <Flame className="w-4 h-4 text-red-400" />
            <span className="text-[10px] font-mono text-slate-400">12s</span>
          </div>
          <div>
            <div className="text-xs font-semibold text-white">Packet Loss Storm</div>
            <div className="text-[10px] text-slate-400 leading-tight mt-0.5">Spikes loss to 20%</div>
          </div>
        </button>

        <button
          onClick={onResetRoute}
          className="p-3 rounded-lg border border-slate-800 bg-slate-950/60 hover:border-slate-700 hover:bg-slate-900 text-left transition-all cursor-pointer flex flex-col justify-between"
        >
          <div className="flex items-center justify-between mb-2">
            <RotateCcw className="w-4 h-4 text-cyan-400" />
            <span className="text-[10px] font-mono text-slate-400">km 0</span>
          </div>
          <div>
            <div className="text-xs font-semibold text-white">Reset Train Route</div>
            <div className="text-[10px] text-slate-400 leading-tight mt-0.5">Return to Central Union</div>
          </div>
        </button>
      </div>

      {/* Train Speed Slider & Manual Throttle */}
      <div className="p-3.5 rounded-lg bg-slate-950/60 border border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Gauge className="w-5 h-5 text-cyan-400" />
          <div>
            <div className="text-xs font-semibold text-white">Train Speed Regulator</div>
            <div className="text-[10px] text-slate-400">Simulate acceleration, cruising speed, or station dwell</div>
          </div>
        </div>

        <div className="flex items-center gap-3 flex-1 max-w-md">
          <input
            type="range"
            min="0"
            max="300"
            step="10"
            value={train?.speed_kmh || 0}
            onChange={(e) => onSetTrainSpeed(parseFloat(e.target.value))}
            className="w-full accent-cyan-400 cursor-pointer"
          />
          <span className="text-sm font-mono font-bold text-cyan-300 whitespace-nowrap min-w-[70px] text-right">
            {train?.speed_kmh || 0} km/h
          </span>
        </div>
      </div>
    </div>
  )
}
