import React, { useState } from 'react'
import { Download, Play, Pause, RotateCcw, FastForward, Film } from 'lucide-react'
import { SystemState } from '../types/telemetry'

interface TripPlaybackProps {
  history: SystemState[]
  onSelectHistoricalState?: (state: SystemState | null) => void
}

export const TripPlayback: React.FC<TripPlaybackProps> = ({
  history,
  onSelectHistoricalState,
}) => {
  const [isReplaying, setIsReplaying] = useState(false)
  const [scrubberIndex, setScrubberIndex] = useState<number | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)

  const handleToggleReplay = () => {
    if (isReplaying) {
      // Exit replay mode, go live
      setIsReplaying(false)
      setIsPlaying(false)
      setScrubberIndex(null)
      onSelectHistoricalState?.(null)
    } else {
      // Enter replay mode at latest or start
      setIsReplaying(true)
      const lastIdx = Math.max(0, history.length - 1)
      setScrubberIndex(lastIdx)
      if (history[lastIdx]) {
        onSelectHistoricalState?.(history[lastIdx])
      }
    }
  }

  const handleScrubberChange = (idx: number) => {
    setScrubberIndex(idx)
    if (history[idx]) {
      onSelectHistoricalState?.(history[idx])
    }
  }

  const handleDownloadCsv = () => {
    window.location.href = '/api/export'
  }

  const currentSnap =
    scrubberIndex !== null && history[scrubberIndex]
      ? history[scrubberIndex]
      : null

  return (
    <div className="rounded-xl border border-slate-800/80 bg-slate-900/70 backdrop-blur-md p-4 lg:p-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Film className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
              Trip Scrubber & Telemetry Data Export
            </h3>
            <span className="text-xs text-slate-400">
              Replay recorded corridor timeline or export SQLite snapshots to CSV
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={handleToggleReplay}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all cursor-pointer ${
              isReplaying
                ? 'bg-amber-500/20 border-amber-500/40 text-amber-300'
                : 'bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700'
            }`}
          >
            <Film className="w-3.5 h-3.5" />
            {isReplaying ? 'Exit Replay (Go Live)' : 'Enter Timeline Scrubber'}
          </button>

          <button
            onClick={handleDownloadCsv}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-cyan-500/20 border border-cyan-500/40 text-cyan-300 hover:bg-cyan-500/30 transition-all cursor-pointer shadow-sm"
          >
            <Download className="w-3.5 h-3.5" />
            Export CSV
          </button>
        </div>
      </div>

      {/* Scrubber controls when replay is active */}
      {isReplaying && (
        <div className="p-3.5 rounded-lg bg-slate-950/80 border border-amber-500/30 animate-fadeIn">
          <div className="flex items-center justify-between text-xs font-mono text-slate-300 mb-2">
            <span className="text-amber-400 font-semibold flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
              SCRUBBER ACTIVE
            </span>
            <span>
              Timestamp:{' '}
              <strong className="text-white">
                {currentSnap ? currentSnap.timestamp : '---'}
              </strong>
            </span>
            <span>
              Snapshot {scrubberIndex !== null ? scrubberIndex + 1 : 0} of {history.length}
            </span>
          </div>

          <input
            type="range"
            min={0}
            max={Math.max(0, history.length - 1)}
            value={scrubberIndex ?? 0}
            onChange={(e) => handleScrubberChange(parseInt(e.target.value))}
            className="w-full accent-amber-400 cursor-pointer"
          />

          <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 mt-1">
            <span>Oldest (Past)</span>
            <span>Latest (Present)</span>
          </div>
        </div>
      )}
    </div>
  )
}
