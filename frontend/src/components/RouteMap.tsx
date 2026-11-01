import React, { useState, useEffect } from 'react'
import { MapPin, Radio, Wifi, Mountain, Train, Navigation, Info, ShieldAlert } from 'lucide-react'
import { TrainTelemetry, RouteCorridor, RouteStation, RouteTower } from '../types/telemetry'

interface RouteMapProps {
  train: TrainTelemetry | undefined
  activeLinkId: string
}

export const RouteMap: React.FC<RouteMapProps> = ({ train, activeLinkId }) => {
  const [route, setRoute] = useState<RouteCorridor | null>(null)
  const [selectedItem, setSelectedItem] = useState<{ title: string; desc: string } | null>(null)

  useEffect(() => {
    fetch('/api/route')
      .then((res) => res.json())
      .then((data: RouteCorridor) => setRoute(data))
      .catch((err) => console.warn('Failed to load route corridor data:', err))
  }, [])

  if (!route) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 flex items-center justify-center min-h-[320px]">
        <div className="flex items-center gap-2 text-slate-400 text-sm font-mono">
          <Navigation className="w-4 h-4 animate-spin text-cyan-400" />
          Loading Rail Corridor Map...
        </div>
      </div>
    )
  }

  // Map progress: 0 to totalKm mapped to horizontal or SVG track coordinates
  const totalKm = route.total_length_km
  const progressPct = train?.progress_pct || 0
  const tunnelZone = route.zones.find(z => z.type === 'tunnel') || { start_km: 7.5, end_km: 11.0, name: 'Mountain Tunnel' }

  return (
    <div className="rounded-xl border border-slate-800/80 bg-slate-900/70 backdrop-blur-md p-4 lg:p-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Navigation className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
              Live Corridor Route & RF Infrastructure Map
            </h3>
            <span className="text-xs text-slate-400">
              {route.name} ({totalKm.toFixed(1)} km Demonstration Corridor)
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3 text-xs font-mono text-slate-400">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
            Train Pos: <strong className="text-white">{((progressPct / 100) * totalKm).toFixed(1)} km</strong>
          </span>
          <span className="text-slate-600">•</span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-rose-500/80" />
            {tunnelZone.name} (km {tunnelZone.start_km}–{tunnelZone.end_km})
          </span>
        </div>
      </div>

      {/* Interactive Schematic Route Canvas */}
      <div className="relative bg-[#070e1b] rounded-xl border border-slate-800/80 p-6 overflow-hidden">
        {/* Mountain Tunnel Background Strip */}
        <div
          className="absolute top-0 bottom-0 bg-rose-950/20 border-x border-rose-500/30 flex flex-col items-center justify-between py-2 text-[10px] font-mono text-rose-400/70"
          style={{
            left: `${(tunnelZone.start_km / totalKm) * 100}%`,
            width: `${((tunnelZone.end_km - tunnelZone.start_km) / totalKm) * 100}%`,
          }}
          title={`${tunnelZone.name} (RF Dead Zone)`}
        >
          <span className="flex items-center gap-1">
            <Mountain className="w-3 h-3 text-rose-400" /> Tunnel
          </span>
          <span className="text-[9px] uppercase tracking-wider text-rose-500/60 font-semibold">
            No Cellular LOS
          </span>
        </div>

        {/* The Track Line */}
        <div className="relative my-10 h-2 bg-slate-800 rounded-full">
          {/* Progress fill */}
          <div
            className="h-full bg-gradient-to-r from-cyan-500 via-blue-500 to-cyan-400 rounded-full transition-all duration-700 shadow-[0_0_12px_rgba(6,182,212,0.6)]"
            style={{ width: `${progressPct}%` }}
          />

          {/* Cell Towers (Above track) */}
          {route.cell_towers.map((tower) => {
            const towerPct = (tower.km / totalKm) * 100
            const isAlpha = tower.carrier === 'wan_5g_primary'
            return (
              <div
                key={tower.id}
                className="absolute -top-7 -translate-x-1/2 group cursor-pointer"
                style={{ left: `${towerPct}%` }}
                onClick={() =>
                  setSelectedItem({
                    title: tower.name,
                    desc: `Location: km ${tower.km} | Carrier: ${isAlpha ? '5G Alpha (C-Band)' : '5G Beta (Sub-6)'} | Radius: ${tower.range_km} km`,
                  })
                }
              >
                <div
                  className={`p-1 rounded-full border transition-all duration-200 group-hover:scale-125 ${
                    isAlpha
                      ? 'bg-sky-950 border-sky-400 text-sky-300'
                      : 'bg-purple-950 border-purple-400 text-purple-300'
                  }`}
                  title={`${tower.name} (km ${tower.km})`}
                >
                  <Radio className="w-3 h-3" />
                </div>
              </div>
            )
          })}

          {/* Stations (Below track) */}
          {route.stations.map((st) => {
            const stPct = (st.km / totalKm) * 100
            return (
              <div
                key={st.id}
                className="absolute top-4 -translate-x-1/2 flex flex-col items-center group cursor-pointer"
                style={{ left: `${stPct}%` }}
                onClick={() =>
                  setSelectedItem({
                    title: st.name,
                    desc: `Milestone: km ${st.km} | Wi-Fi 6E: ${st.has_station_wifi ? 'Gigabit Trackside Available (850+ Mbps)' : 'None'}`,
                  })
                }
              >
                <div
                  className={`w-3 h-3 rounded-full border-2 border-[#070e1b] transition-transform duration-200 group-hover:scale-125 ${
                    st.has_station_wifi ? 'bg-emerald-400 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-slate-400'
                  }`}
                />
                <span className="text-[10px] font-medium text-slate-300 whitespace-nowrap mt-1 group-hover:text-cyan-300">
                  {st.name}
                </span>
                {st.has_station_wifi && (
                  <span className="text-[8px] font-mono px-1 py-0.2 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-0.5 mt-0.5">
                    <Wifi className="w-2.5 h-2.5" /> Wi-Fi
                  </span>
                )}
              </div>
            )
          })}

          {/* The Moving Train Indicator */}
          <div
            className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 transition-all duration-1000 z-20 group cursor-pointer"
            style={{ left: `${progressPct}%` }}
          >
            <div className="relative flex items-center justify-center">
              <div className="absolute w-8 h-8 rounded-full bg-cyan-400/30 animate-ping" />
              <div className="relative w-7 h-7 rounded-full bg-cyan-500 border-2 border-white shadow-[0_0_15px_rgba(6,182,212,0.9)] flex items-center justify-center text-slate-950">
                <Train className="w-4 h-4 fill-current" />
              </div>
            </div>

            {/* Floating Train Tag */}
            <div className="absolute -top-10 left-1/2 -translate-x-1/2 bg-slate-900 border border-cyan-500/50 px-2 py-0.5 rounded shadow-lg text-[10px] font-mono text-cyan-300 whitespace-nowrap flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
              {train?.speed_kmh} km/h
            </div>
          </div>
        </div>

        {/* Selected Item Detail banner if clicked */}
        {selectedItem && (
          <div className="mt-14 p-2.5 rounded-lg bg-slate-900/90 border border-slate-700/80 text-xs flex items-center justify-between animate-fadeIn">
            <div className="flex items-center gap-2">
              <Info className="w-4 h-4 text-cyan-400" />
              <div>
                <strong className="text-white font-semibold">{selectedItem.title}</strong>
                <span className="text-slate-400 ml-2 font-mono text-[11px]">{selectedItem.desc}</span>
              </div>
            </div>
            <button
              onClick={() => setSelectedItem(null)}
              className="text-slate-400 hover:text-white text-xs px-2 py-0.5"
            >
              ✕
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
