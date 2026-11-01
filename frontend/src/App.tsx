import React, { useState } from 'react'
import { Header } from './components/Header'
import { NetworkCards } from './components/NetworkCards'
import { TrainLanMonitor } from './components/TrainLanMonitor'
import { PredictiveAlerts } from './components/PredictiveAlerts'
import { RouteMap } from './components/RouteMap'
import { TelemetryCharts } from './components/TelemetryCharts'
import { SimulationControls } from './components/SimulationControls'
import { EventLog } from './components/EventLog'
import { TripPlayback } from './components/TripPlayback'
import { useWebSocket } from './hooks/useWebSocket'
import { SystemState } from './types/telemetry'
import { Wifi, RefreshCw } from 'lucide-react'

export function App() {
  const { data: liveData, status, history, sendControl } = useWebSocket()
  const [replayedState, setReplayedState] = useState<SystemState | null>(null)

  // Display either the historical scrubbed snapshot or live streaming data
  const currentState = replayedState || liveData

  const handleToggleAutoFailover = (enabled: boolean) => {
    sendControl({ action: 'toggle_auto_failover', enabled })
  }

  const handleToggleMlProactive = (enabled: boolean) => {
    sendControl({ action: 'toggle_ml_proactive', enabled })
  }

  const handleManualSwitch = (targetLinkId: string) => {
    sendControl({ action: 'manual_switch', target_link_id: targetLinkId })
  }

  const handleInjectDisruption = (type: string, durationSeconds: number) => {
    sendControl({
      action: 'inject_disruption',
      disruption_type: type,
      duration_seconds: durationSeconds,
    })
  }

  const handleClearDisruption = () => {
    sendControl({ action: 'clear_disruption' })
  }

  const handleSetTrainSpeed = (speed: number) => {
    sendControl({ action: 'set_train_speed', train_speed: speed })
  }

  const handleResetRoute = () => {
    sendControl({ action: 'reset_route' })
  }

  if (!currentState) {
    return (
      <div className="min-h-screen bg-[#070d18] flex items-center justify-center p-4">
        <div className="flex flex-col items-center gap-3 text-slate-300">
          <div className="relative">
            <div className="w-12 h-12 rounded-full border-2 border-cyan-500/20 border-t-cyan-400 animate-spin" />
            <Wifi className="w-5 h-5 text-cyan-400 absolute inset-0 m-auto" />
          </div>
          <span className="font-mono text-sm tracking-wide text-slate-400">
            Initializing RailConnect 2.0 Telemetry Stream...
          </span>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#070d18] text-slate-100 flex flex-col">
      {/* Top Navigation & Status Bar */}
      <Header
        state={currentState}
        status={status}
        onToggleAutoFailover={handleToggleAutoFailover}
        onToggleMlProactive={handleToggleMlProactive}
      />

      {/* Main Mission Control Content */}
      <main className="flex-1 max-w-[1600px] w-full mx-auto p-4 lg:p-6 space-y-6">
        {/* ML Proactive Risk & Recommendation Alert Banner */}
        <PredictiveAlerts
          prediction={currentState.prediction}
          activeLinkId={currentState.active_link_id}
          onSwitchToRecommended={handleManualSwitch}
        />

        {/* 4 Multi-WAN Telemetry Cards */}
        <NetworkCards
          links={currentState.links}
          activeLinkId={currentState.active_link_id}
          onManualSwitch={handleManualSwitch}
        />

        {/* Onboard Train LAN & Dynamic Coach Traffic Distribution */}
        <TrainLanMonitor
          lan={currentState.lan}
          activeLink={currentState.links[currentState.active_link_id]}
          trainSpeed={currentState.train.speed_kmh}
        />

        {/* Route Map (Corridor schematic + Train position) */}
        <RouteMap
          train={currentState.train}
          activeLinkId={currentState.active_link_id}
        />

        {/* Real-time Telemetry Charts */}
        <TelemetryCharts history={history} />

        {/* Interactive Scenario Disruption Lab */}
        <SimulationControls
          disruption={currentState.disruption}
          train={currentState.train}
          onInjectDisruption={handleInjectDisruption}
          onClearDisruption={handleClearDisruption}
          onSetTrainSpeed={handleSetTrainSpeed}
          onResetRoute={handleResetRoute}
        />

        {/* Audit Log of Failover Handover Events */}
        <EventLog events={currentState.recent_events || []} />

        {/* Timeline Scrubber & CSV Exporter */}
        <TripPlayback
          history={history}
          onSelectHistoricalState={(snap) => setReplayedState(snap)}
        />
      </main>

      {/* System Footer */}
      <footer className="border-t border-slate-800/80 bg-[#060c16] px-4 py-4 text-xs font-mono text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-2">
        <div className="flex items-center gap-3">
          <span>RailConnect Autonomous Multi-WAN Engine</span>
          <span>•</span>
          <span className="text-cyan-500/80">SQLite Time-Series Active</span>
          <span>•</span>
          <span>FastAPI + WebSocket Live Push</span>
        </div>
        <div>
          Train Telemetry Frequency: 1.0 Hz • Latency: &lt;5ms
        </div>
      </footer>
    </div>
  )
}
export default App
