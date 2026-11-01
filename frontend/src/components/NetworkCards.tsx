import React from 'react'
import { Radio, Satellite, Wifi, CheckCircle2, AlertCircle, ArrowUpRight, SignalHigh, WifiOff } from 'lucide-react'
import { WanTelemetry } from '../types/telemetry'

interface NetworkCardsProps {
  links: Record<string, WanTelemetry>
  activeLinkId: string
  onManualSwitch: (linkId: string) => void
}

export const NetworkCards: React.FC<NetworkCardsProps> = ({
  links,
  activeLinkId,
  onManualSwitch,
}) => {
  const getLinkIcon = (type: string) => {
    switch (type) {
      case 'satellite':
        return <Satellite className="w-4 h-4 text-amber-400" />
      case 'wifi':
        return <Wifi className="w-4 h-4 text-emerald-400" />
      case 'cellular':
      default:
        return <Radio className="w-4 h-4 text-cyan-400" />
    }
  }

  const getScoreColor = (score: number, status: string) => {
    if (status === 'offline' || score <= 10) return 'text-rose-400 border-rose-500/40 bg-rose-500/10'
    if (score >= 75) return 'text-emerald-400 border-emerald-500/40 bg-emerald-500/10'
    return 'text-amber-400 border-amber-500/40 bg-amber-500/10'
  }

  const getStatusBadge = (status: string, isActive: boolean) => {
    if (isActive) {
      return (
        <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-[0_0_12px_rgba(6,182,212,0.3)]">
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
          ACTIVE LINK
        </span>
      )
    }
    switch (status) {
      case 'standby':
        return (
          <span className="px-2 py-0.5 rounded-full text-[11px] font-medium bg-slate-800 text-slate-300 border border-slate-700">
            STANDBY READY
          </span>
        )
      case 'degraded':
        return (
          <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/40">
            DEGRADED
          </span>
        )
      case 'offline':
      default:
        return (
          <span className="px-2 py-0.5 rounded-full text-[11px] font-medium bg-rose-500/20 text-rose-300 border border-rose-500/40">
            OFFLINE / NO LOS
          </span>
        )
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {Object.values(links).map((link) => {
        const isActive = link.id === activeLinkId
        const isOffline = link.status === 'offline'

        return (
          <div
            key={link.id}
            className={`relative rounded-xl p-4 transition-all duration-300 border backdrop-blur-md ${
              isActive
                ? 'bg-gradient-to-b from-[#0e1d33] to-[#0a1526] border-cyan-500/60 shadow-[0_0_25px_rgba(6,182,212,0.18)] ring-1 ring-cyan-500/30'
                : 'bg-slate-900/60 border-slate-800/80 hover:border-slate-700 hover:bg-slate-900/90'
            }`}
          >
            {/* Top row: Name & Active badge */}
            <div className="flex items-start justify-between gap-2 mb-3">
              <div className="flex items-center gap-2">
                <div className={`p-2 rounded-lg ${isActive ? 'bg-cyan-500/20' : 'bg-slate-800'}`}>
                  {getLinkIcon(link.type)}
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-white leading-tight">{link.name}</h3>
                  <span className="text-[11px] font-mono text-slate-400">{link.band}</span>
                </div>
              </div>
              {getStatusBadge(link.status, isActive)}
            </div>

            {/* Score & Signal bars */}
            <div className="flex items-center justify-between py-2 border-y border-slate-800/60 my-3">
              <div>
                <span className="text-[10px] uppercase font-mono tracking-wider text-slate-400 block">Health Score</span>
                <span className={`text-2xl font-bold font-mono ${getScoreColor(link.score, link.status).split(' ')[0]}`}>
                  {link.score.toFixed(0)}
                  <span className="text-xs text-slate-500 font-normal"> / 100</span>
                </span>
              </div>

              {/* Signal strength bar */}
              <div className="text-right">
                <span className="text-[10px] uppercase font-mono tracking-wider text-slate-400 block">RF Signal</span>
                <div className="flex items-center justify-end gap-1 mt-1">
                  {[20, 40, 60, 80, 100].map((step, idx) => (
                    <div
                      key={idx}
                      className={`w-1.5 rounded-sm transition-all duration-300 ${
                        link.signal >= step
                          ? link.signal > 60
                            ? 'bg-emerald-400'
                            : 'bg-amber-400'
                          : 'bg-slate-800'
                      }`}
                      style={{ height: `${(idx + 1) * 3 + 4}px` }}
                    />
                  ))}
                  <span className="text-xs font-mono text-slate-300 ml-1.5">{link.signal.toFixed(0)}%</span>
                </div>
              </div>
            </div>

            {/* Metrics 2x2 Grid */}
            <div className="grid grid-cols-2 gap-2 text-xs font-mono mb-3.5">
              <div className="p-2 rounded-lg bg-slate-950/40 border border-slate-800/40">
                <span className="text-[10px] text-slate-400 block font-sans">Bandwidth</span>
                <span className="text-sm font-semibold text-white">
                  {isOffline ? '0.0' : link.bandwidth.toFixed(1)} <span className="text-[10px] text-slate-400">Mbps</span>
                </span>
              </div>

              <div className="p-2 rounded-lg bg-slate-950/40 border border-slate-800/40">
                <span className="text-[10px] text-slate-400 block font-sans">Latency (RTT)</span>
                <span className={`text-sm font-semibold ${link.latency > 150 ? 'text-rose-400' : 'text-slate-200'}`}>
                  {isOffline ? '---' : `${link.latency.toFixed(0)} ms`}
                </span>
              </div>

              <div className="p-2 rounded-lg bg-slate-950/40 border border-slate-800/40">
                <span className="text-[10px] text-slate-400 block font-sans">Packet Loss</span>
                <span className={`text-sm font-semibold ${link.packet_loss > 3 ? 'text-rose-400' : 'text-slate-200'}`}>
                  {isOffline ? '100%' : `${link.packet_loss.toFixed(2)}%`}
                </span>
              </div>

              <div className="p-2 rounded-lg bg-slate-950/40 border border-slate-800/40">
                <span className="text-[10px] text-slate-400 block font-sans">Jitter</span>
                <span className="text-sm font-semibold text-slate-200">
                  {isOffline ? '---' : `${link.jitter.toFixed(1)} ms`}
                </span>
              </div>
            </div>

            {/* Action button */}
            <button
              onClick={() => onManualSwitch(link.id)}
              disabled={isActive || isOffline}
              className={`w-full py-1.5 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all ${
                isActive
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 cursor-default'
                  : isOffline
                  ? 'bg-slate-900 text-slate-600 border border-slate-800 cursor-not-allowed'
                  : 'bg-slate-800 hover:bg-cyan-600/30 text-slate-300 hover:text-cyan-200 border border-slate-700 hover:border-cyan-500/50'
              }`}
            >
              {isActive ? (
                <>
                  <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                  Currently Routing
                </>
              ) : isOffline ? (
                <>
                  <WifiOff className="w-3.5 h-3.5" />
                  Unavailable
                </>
              ) : (
                <>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                  Force Handover
                </>
              )}
            </button>
          </div>
        )
      })}
    </div>
  )
}
