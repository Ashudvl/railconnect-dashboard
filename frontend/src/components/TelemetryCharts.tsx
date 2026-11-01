import React, { useState } from 'react'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts'
import { Activity, BarChart3, Clock } from 'lucide-react'
import { SystemState } from '../types/telemetry'

interface TelemetryChartsProps {
  history: SystemState[]
}

export const TelemetryCharts: React.FC<TelemetryChartsProps> = ({ history }) => {
  const [activeTab, setActiveTab] = useState<'bandwidth' | 'latency' | 'scores'>('bandwidth')

  // Transform system state history into chart series points
  const chartData = history.slice(-30).map((snap) => {
    const timeLabel = snap.timestamp.includes(' ')
      ? snap.timestamp.split(' ')[1]
      : snap.timestamp
    const links = snap.links || {}
    const p = links['wan_5g_primary']
    const s = links['wan_5g_secondary']
    const sat = links['wan_satellite']
    const wf = links['wan_trackside_wifi']

    return {
      time: timeLabel,
      // Bandwidths
      '5G Alpha BW': p ? p.bandwidth : 0,
      '5G Beta BW': s ? s.bandwidth : 0,
      'Starlink BW': sat ? sat.bandwidth : 0,
      'Station Wi-Fi BW': wf ? wf.bandwidth : 0,
      // Latencies
      '5G Alpha Lat': p ? (p.status === 'offline' ? 300 : p.latency) : 0,
      '5G Beta Lat': s ? (s.status === 'offline' ? 300 : s.latency) : 0,
      'Starlink Lat': sat ? (sat.status === 'offline' ? 300 : sat.latency) : 0,
      'Station Wi-Fi Lat': wf ? (wf.status === 'offline' ? 300 : wf.latency) : 0,
      // Scores
      '5G Alpha Score': p ? p.score : 0,
      '5G Beta Score': s ? s.score : 0,
      'Starlink Score': sat ? sat.score : 0,
      'Station Wi-Fi Score': wf ? wf.score : 0,
    }
  })

  return (
    <div className="rounded-xl border border-slate-800/80 bg-slate-900/70 backdrop-blur-md p-4 lg:p-5">
      {/* Chart Header & Tab selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
              Live Real-Time Telemetry Trends
            </h3>
            <span className="text-xs text-slate-400">
              30-Second Rolling Window • 1Hz Sampling
            </span>
          </div>
        </div>

        <div className="flex items-center gap-1.5 bg-slate-950/70 p-1 rounded-lg border border-slate-800">
          <button
            onClick={() => setActiveTab('bandwidth')}
            className={`px-3 py-1 rounded text-xs font-semibold transition-all ${
              activeTab === 'bandwidth'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Bandwidth (Mbps)
          </button>
          <button
            onClick={() => setActiveTab('latency')}
            className={`px-3 py-1 rounded text-xs font-semibold transition-all ${
              activeTab === 'latency'
                ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Latency (ms)
          </button>
          <button
            onClick={() => setActiveTab('scores')}
            className={`px-3 py-1 rounded text-xs font-semibold transition-all ${
              activeTab === 'scores'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Composite Health Score
          </button>
        </div>
      </div>

      {/* Chart container */}
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 10, fill: '#64748b' }} />
            <YAxis stroke="#64748b" tick={{ fontSize: 10, fill: '#64748b' }} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#091120',
                borderColor: '#334155',
                borderRadius: '8px',
                fontSize: '12px',
                fontFamily: 'JetBrains Mono',
              }}
            />
            <Legend
              wrapperStyle={{ fontSize: '11px', fontFamily: 'Plus Jakarta Sans', paddingTop: '10px' }}
            />

            {activeTab === 'bandwidth' && (
              <>
                <Line type="monotone" dataKey="5G Alpha BW" stroke="#38bdf8" strokeWidth={2} dot={false} isAnimationActive={false} />
                <Line type="monotone" dataKey="5G Beta BW" stroke="#a855f7" strokeWidth={2} dot={false} isAnimationActive={false} />
                <Line type="monotone" dataKey="Starlink BW" stroke="#f59e0b" strokeWidth={2} dot={false} isAnimationActive={false} />
                <Line type="monotone" dataKey="Station Wi-Fi BW" stroke="#10b981" strokeWidth={2} dot={false} isAnimationActive={false} />
              </>
            )}

            {activeTab === 'latency' && (
              <>
                <Line type="monotone" dataKey="5G Alpha Lat" stroke="#38bdf8" strokeWidth={2} dot={false} isAnimationActive={false} />
                <Line type="monotone" dataKey="5G Beta Lat" stroke="#a855f7" strokeWidth={2} dot={false} isAnimationActive={false} />
                <Line type="monotone" dataKey="Starlink Lat" stroke="#f59e0b" strokeWidth={2} dot={false} isAnimationActive={false} />
                <Line type="monotone" dataKey="Station Wi-Fi Lat" stroke="#10b981" strokeWidth={2} dot={false} isAnimationActive={false} />
              </>
            )}

            {activeTab === 'scores' && (
              <>
                <Line type="monotone" dataKey="5G Alpha Score" stroke="#38bdf8" strokeWidth={2} dot={false} isAnimationActive={false} />
                <Line type="monotone" dataKey="5G Beta Score" stroke="#a855f7" strokeWidth={2} dot={false} isAnimationActive={false} />
                <Line type="monotone" dataKey="Starlink Score" stroke="#f59e0b" strokeWidth={2} dot={false} isAnimationActive={false} />
                <Line type="monotone" dataKey="Station Wi-Fi Score" stroke="#10b981" strokeWidth={2} dot={false} isAnimationActive={false} />
              </>
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
