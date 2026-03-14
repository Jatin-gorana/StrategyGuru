'use client'

import { useState } from 'react'
import { X, Loader2, Copy, Check, AlertCircle, Lightbulb } from 'lucide-react'
import api, { BacktestMetrics, StrategyImprovement } from '@/lib/api'

interface StrategyImprovementModalProps {
  isOpen: boolean
  onClose: () => void
  strategyText: string
  metrics: BacktestMetrics
  tradesCount: number
  onApplyImprovement?: (improvedStrategy: string) => void
}

export default function StrategyImprovementModal({
  isOpen,
  onClose,
  strategyText,
  metrics,
  tradesCount,
  onApplyImprovement,
}: StrategyImprovementModalProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [improvement, setImprovement] = useState<StrategyImprovement | null>(null)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)

  const handleImprove = async () => {
    setIsLoading(true)
    setError('')

    try {
      // Check authentication before making request
      const token = localStorage.getItem('access_token')
      if (!token) {
        setError('Please login to improve strategies')
        setIsLoading(false)
        return
      }

      const result = await api.improveStrategy(strategyText, metrics, tradesCount)
      setImprovement(result)
    } catch (err: any) {
      // Extract error message safely
      let errorMessage = 'Failed to improve strategy'
      
      if (err.response?.status === 401) {
        errorMessage = 'Your session has expired. Please login again.'
        localStorage.removeItem('access_token')
      } else if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail
      } else if (err.message) {
        errorMessage = err.message
      } else if (typeof err === 'string') {
        errorMessage = err
      }
      
      setError(errorMessage)
      console.error('Improvement error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCopyStrategy = () => {
    if (improvement?.improved_strategy) {
      navigator.clipboard.writeText(improvement.improved_strategy)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleApplyImprovement = () => {
    if (improvement?.improved_strategy && onApplyImprovement) {
      onApplyImprovement(improvement.improved_strategy)
      onClose()
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-secondary border border-slate-700 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 flex items-center justify-between p-6 border-b border-slate-700 bg-secondary">
          <div className="flex items-center gap-3">
            <Lightbulb className="w-6 h-6 text-accent" />
            <h2 className="text-xl font-bold text-white">Improve Strategy</h2>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Current Strategy */}
          <div>
            <h3 className="text-sm font-semibold text-white mb-2">Current Strategy</h3>
            <div className="p-4 bg-primary/50 border border-slate-700 rounded-lg">
              <p className="text-sm text-slate-300 font-mono">{strategyText}</p>
            </div>
          </div>

          {/* Current Metrics */}
          <div>
            <h3 className="text-sm font-semibold text-white mb-2">Current Performance</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="p-3 bg-primary/50 border border-slate-700 rounded-lg">
                <p className="text-xs text-slate-400">Return</p>
                <p
                  className={`text-lg font-bold ${
                    metrics.total_return_percent >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}
                >
                  {metrics.total_return_percent >= 0 ? '+' : ''}
                  {metrics.total_return_percent.toFixed(2)}%
                </p>
              </div>
              <div className="p-3 bg-primary/50 border border-slate-700 rounded-lg">
                <p className="text-xs text-slate-400">Sharpe</p>
                <p className="text-lg font-bold text-white">
                  {metrics.sharpe_ratio.toFixed(2)}
                </p>
              </div>
              <div className="p-3 bg-primary/50 border border-slate-700 rounded-lg">
                <p className="text-xs text-slate-400">Drawdown</p>
                <p className="text-lg font-bold text-red-400">
                  {metrics.max_drawdown_percent.toFixed(2)}%
                </p>
              </div>
              <div className="p-3 bg-primary/50 border border-slate-700 rounded-lg">
                <p className="text-xs text-slate-400">Win Rate</p>
                <p className="text-lg font-bold text-white">
                  {metrics.win_rate.toFixed(2)}%
                </p>
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
              <p className="text-sm text-red-400">{error}</p>
            </div>
          )}

          {/* Improvement Results */}
          {improvement && (
            <div className="space-y-4">
              {/* Improved Strategy */}
              <div>
                <h3 className="text-sm font-semibold text-white mb-2">Improved Strategy</h3>
                <div className="p-4 bg-primary/50 border border-accent/30 rounded-lg">
                  <p className="text-sm text-slate-300 font-mono mb-3">
                    {improvement.improved_strategy}
                  </p>
                  <button
                    onClick={handleCopyStrategy}
                    className="flex items-center gap-2 text-xs text-accent hover:text-blue-400 transition-colors"
                  >
                    {copied ? (
                      <>
                        <Check className="w-4 h-4" />
                        Copied!
                      </>
                    ) : (
                      <>
                        <Copy className="w-4 h-4" />
                        Copy Strategy
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Improvements List */}
              <div>
                <h3 className="text-sm font-semibold text-white mb-2">Suggested Improvements</h3>
                <ul className="space-y-2">
                  {improvement.improvements.map((imp, idx) => (
                    <li key={idx} className="flex items-start gap-3 p-3 bg-primary/50 border border-slate-700 rounded-lg">
                      <span className="text-accent font-bold flex-shrink-0">•</span>
                      <span className="text-sm text-slate-300">{imp}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Reasoning */}
              <div>
                <h3 className="text-sm font-semibold text-white mb-2">Reasoning</h3>
                <p className="text-sm text-slate-300 p-4 bg-primary/50 border border-slate-700 rounded-lg">
                  {improvement.reasoning}
                </p>
              </div>

              {/* Risk Level */}
              <div className="flex items-center gap-3 p-4 bg-primary/50 border border-slate-700 rounded-lg">
                <span className="text-sm text-slate-400">Risk Level:</span>
                <span
                  className={`text-sm font-bold px-3 py-1 rounded ${
                    improvement.risk_level === 'Low'
                      ? 'bg-green-500/20 text-green-400'
                      : improvement.risk_level === 'Medium'
                      ? 'bg-yellow-500/20 text-yellow-400'
                      : 'bg-red-500/20 text-red-400'
                  }`}
                >
                  {improvement.risk_level}
                </span>
              </div>
            </div>
          )}

          {/* Loading State */}
          {isLoading && (
            <div className="flex flex-col items-center justify-center py-8">
              <Loader2 className="w-8 h-8 text-accent animate-spin mb-3" />
              <p className="text-slate-400">Analyzing strategy with AI...</p>
            </div>
          )}

          {/* No Results Yet */}
          {!improvement && !isLoading && !error && (
            <div className="text-center py-8">
              <p className="text-slate-400 mb-4">
                Click the button below to get AI-powered suggestions for improving your strategy
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 flex items-center justify-between p-6 border-t border-slate-700 bg-secondary gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-secondary hover:bg-secondary/80 text-white rounded-lg border border-slate-700 transition-colors"
          >
            Close
          </button>
          <div className="flex gap-3">
            {improvement && onApplyImprovement && (
              <button
                onClick={handleApplyImprovement}
                className="px-4 py-2 bg-accent hover:bg-blue-600 text-white rounded-lg transition-colors"
              >
                Apply Improvement
              </button>
            )}
            {!improvement && !isLoading && (
              <button
                onClick={handleImprove}
                disabled={isLoading}
                className="px-4 py-2 bg-accent hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center gap-2"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Lightbulb className="w-4 h-4" />
                    Get Suggestions
                  </>
                )}
              </button>
            )}
            {improvement && !isLoading && (
              <button
                onClick={handleImprove}
                className="px-4 py-2 bg-secondary hover:bg-secondary/80 text-white rounded-lg border border-slate-700 transition-colors"
              >
                Get More Suggestions
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
