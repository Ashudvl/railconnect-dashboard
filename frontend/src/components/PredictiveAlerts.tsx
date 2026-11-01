import React from 'react'
import { BrainCircuit, AlertTriangle, CheckCircle, TrendingUp, Sparkles, ArrowRight } from 'lucide-react'
import { MlPrediction } from '../types/telemetry'

interface PredictiveAlertsProps {
  prediction: MlPrediction | undefined
  activeLinkId: string
  onSwitchToRecommended: (targetLinkId: string) => void
}

export const PredictiveAlerts: React.FC<PredictiveAlertsProps> = ({
  prediction,
  activeLinkId,
  onSwitchToRecommended,
}) => {
  if (!prediction) return null

  const isHighRisk = prediction.risk_score >= 65 || prediction.imminent_failover
  const isMediumRisk = prediction.risk_score >= 35 && prediction.risk_score < 65

  return (
    <div
      className={`rounded-xl p-4 transition-all duration-300 border backdrop-blur-md ${
        isHighRisk
          ? 'bg-gradient-to-r from-rose-950/40 via-purple-950/30 to-slate-900/60 border-rose-500/50 shadow-[0_0_20px_rgba(244,63,94,0.15)]'
          : isMediumRisk
          ? 'bg-gradient-to-r from-amber-950/30 via-slate-900/60 to-slate-900/60 border-amber-500/40'
          : 'bg-gradient-to-r from-cyan-950/20 via-slate-900/60 to-slate-900/60 border-cyan-500/30'
      }`}
    >
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        {/* Left side: ML Header & Reasoning */}
        <div className="flex items-start gap-3.5 flex-1">
          <div
            className={`p-2.5 rounded-xl border ${
              isHighRisk
                ? 'bg-rose-500/20 border-rose-500/40 text-rose-400 animate-pulse'
                : isMediumRisk
                ? 'bg-amber-500/20 border-amber-500/40 text-amber-400'
                : 'bg-cyan-500/20 border-cyan-500/40 text-cyan-400'
            }`}
          >
            {isHighRisk ? (
              <AlertTriangle className="w-5 h-5" />
            ) : (
              <BrainCircuit className="w-5 h-5" />
            )}
          </div>

          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs font-mono font-bold tracking-wider uppercase text-cyan-400 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5" />
                Random Forest ML Failover Predictor (10s Horizon)
              </span>
              <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                Confidence: <strong className="text-white">{prediction.confidence}%</strong>
              </span>
            </div>

            <p className="text-sm font-medium text-slate-200 mt-1 leading-relaxed">
              {prediction.reasoning}
            </p>

            {/* Feature impact tags */}
            {prediction.top_factors && prediction.top_factors.length > 0 && (
              <div className="flex items-center gap-2 mt-2 flex-wrap">
                <span className="text-[11px] font-mono text-slate-400">Drivers:</span>
                {prediction.top_factors.map((item, i) => (
                  <span
                    key={i}
                    className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800/90 text-slate-300 border border-slate-700/80"
                  >
                    {item.factor}: <strong className="text-cyan-300">+{item.impact}</strong>
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right side: Risk Score & Action */}
        <div className="flex items-center gap-4 self-end lg:self-center border-t lg:border-t-0 lg:border-l border-slate-800/80 pt-3 lg:pt-0 lg:pl-6">
          <div className="text-right">
            <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block">Failover Risk</span>
            <div className="flex items-baseline justify-end gap-1">
              <span
                className={`text-2xl font-bold font-mono ${
                  isHighRisk ? 'text-rose-400' : isMediumRisk ? 'text-amber-400' : 'text-emerald-400'
                }`}
              >
                {prediction.risk_score.toFixed(0)}%
              </span>
            </div>
          </div>

          {prediction.imminent_failover && prediction.predicted_link !== activeLinkId && (
            <button
              onClick={() => onSwitchToRecommended(prediction.predicted_link)}
              className="py-2 px-3.5 rounded-lg text-xs font-semibold bg-gradient-to-r from-rose-500 to-purple-600 hover:from-rose-600 hover:to-purple-700 text-white flex items-center gap-1.5 shadow-lg shadow-rose-500/20 transition-all cursor-pointer"
            >
              <span>Execute Handover</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
