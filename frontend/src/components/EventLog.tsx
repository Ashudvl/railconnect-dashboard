import React from 'react'
import { History, ArrowRight, Zap, ShieldCheck, UserCheck } from 'lucide-react'
import { FailoverEvent } from '../types/telemetry'

interface EventLogProps {
  events: FailoverEvent[]
}

export const EventLog: React.FC<EventLogProps> = ({ events }) => {
  const getTriggerBadge = (trigger: string) => {
    switch (trigger) {
      case 'ml_proactive':
        return (
          <span className="flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-purple-500/20 text-purple-300 border border-purple-500/30">
            <Zap className="w-3 h-3 text-purple-400" />
            ML PROACTIVE
          </span>
        )
      case 'manual_override':
        return (
          <span className="flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-blue-500/20 text-blue-300 border border-blue-500/30">
            <UserCheck className="w-3 h-3 text-blue-400" />
            MANUAL
          </span>
        )
      case 'threshold_policy':
      default:
        return (
          <span className="flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
            <ShieldCheck className="w-3 h-3 text-emerald-400" />
            POLICY FAILOVER
          </span>
        )
    }
  }

  return (
    <div className="rounded-xl border border-slate-800/80 bg-slate-900/70 backdrop-blur-md p-4 lg:p-5">
      <div className="flex items-center justify-between mb-3.5">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <History className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
              Failover & Handover Audit Log
            </h3>
            <span className="text-xs text-slate-400">
              Audit trail of autonomous and operator-directed WAN transitions
            </span>
          </div>
        </div>

        <span className="text-xs font-mono text-slate-400">
          Showing {events.length} events
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-mono">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 text-[11px] uppercase tracking-wider">
              <th className="py-2.5 px-3">Time</th>
              <th className="py-2.5 px-3">Transition</th>
              <th className="py-2.5 px-3">Trigger</th>
              <th className="py-2.5 px-3">Duration</th>
              <th className="py-2.5 px-3">Health Gain</th>
              <th className="py-2.5 px-3">Causal Reason</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {events.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-6 text-center text-slate-500 italic font-sans">
                  No failover events recorded yet. Connections are stable.
                </td>
              </tr>
            ) : (
              events.map((ev) => (
                <tr key={ev.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-2.5 px-3 text-slate-400 whitespace-nowrap">{ev.timestamp}</td>
                  <td className="py-2.5 px-3 whitespace-nowrap">
                    <div className="flex items-center gap-1.5 font-semibold">
                      <span className="text-slate-400">{ev.from_link_name}</span>
                      <ArrowRight className="w-3 h-3 text-cyan-400" />
                      <span className="text-cyan-300">{ev.to_link_name}</span>
                    </div>
                  </td>
                  <td className="py-2.5 px-3 whitespace-nowrap">{getTriggerBadge(ev.trigger)}</td>
                  <td className="py-2.5 px-3 text-slate-300 whitespace-nowrap">{ev.duration_ms} ms</td>
                  <td className="py-2.5 px-3 whitespace-nowrap">
                    <span
                      className={`font-semibold ${
                        ev.quality_gain >= 0 ? 'text-emerald-400' : 'text-rose-400'
                      }`}
                    >
                      {ev.quality_gain >= 0 ? `+${ev.quality_gain}` : ev.quality_gain} pts
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-slate-300 font-sans max-w-xs truncate" title={ev.reason}>
                    {ev.reason}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
