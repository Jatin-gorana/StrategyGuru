'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import MetricsCard from '@/components/MetricsCard'
import EquityChart from '@/components/EquityChart'
import TradesTable from '@/components/TradesTable'
import {
  BacktestResponse,
  Trade,
  BacktestMetrics,
  EquityCurvePoint,
} from '@/lib/api'
import {
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Target,
  Zap,
  AlertCircle,
} from 'lucide-react'

export default function ResultsPage() {
  const router = useRouter()
  const [results, setResults] = useState<BacktestResponse | null>(null)
  const [params, setParams] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const resultsData = sessionStorage.getItem('backtest_results')
    const paramsData = sessionStorage.getItem('backtest_params')

    if (!resultsData || !paramsData) {
      router.push('/')
      return
    }

    try {
      setResults(JSON.parse(resultsData))
      setParams(JSON.parse(paramsData))
    } catch (err) {
      console.error('Failed to parse results:', err)
      router.push('/')
    } finally {
      setIsLoading(false)
    }
  }, [router])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary via-secondary to-primary flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-accent border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-400">Loading results...</p>
        </div>
      </div>
    )
  }

  if (!results || !params) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary via-secondary to-primary flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <p className="text-slate-400">No results found</p>
          <Link href="/" className="text-accent hover:underline mt-4 inline-block">
            Go back to home
          </Link>
        </div>
      </div>
    )
  }

  const metrics = results.metrics
  const isPositive = metrics.total_return >= 0
  const finalEquity = params.initial_capital + metrics.total_return

  return (
    <main className="min-h-screen bg-gradient-to-br from-primary via-secondary to-primary">
      {/* Header */}
      <header className="border-b border-slate-700 bg-primary/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link
                href="/"
                className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
                Back
              </Link>
              <div>
                <h1 className="text-3xl font-bold text-white">
                  Backtest Results
                </h1>
                <p className="text-slate-400 mt-1">
                  {params.stock_symbol} • {params.start_date} to {params.end_date}
                </p>
              </div>
            </div>
            <div
              className={`text-right ${
                isPositive ? 'text-green-400' : 'text-red-400'
              }`}
            >
              <p className="text-sm text-slate-400">Total Return</p>
              <p className="text-3xl font-bold">
                {isPositive ? '+' : ''}
                {metrics.total_return_percent.toFixed(2)}%
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Strategy Info */}
        <div className="mb-8 p-6 bg-secondary/50 border border-slate-700 rounded-lg">
          <h2 className="text-lg font-semibold text-white mb-3">Strategy</h2>
          <p className="text-slate-300 font-mono text-sm bg-primary/50 p-3 rounded">
            {params.strategy_text}
          </p>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <MetricsCard
            title="Total Return"
            value={`$${metrics.total_return.toLocaleString('en-US', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}`}
            unit={`(${metrics.total_return_percent.toFixed(2)}%)`}
            icon={<TrendingUp className="w-6 h-6" />}
            trend={isPositive ? 'up' : 'down'}
            subtitle={`Final: $${finalEquity.toLocaleString('en-US', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}`}
          />

          <MetricsCard
            title="Sharpe Ratio"
            value={metrics.sharpe_ratio.toFixed(4)}
            icon={<Zap className="w-6 h-6" />}
            trend={metrics.sharpe_ratio > 1 ? 'up' : 'neutral'}
            subtitle="Risk-adjusted return"
          />

          <MetricsCard
            title="Max Drawdown"
            value={`${metrics.max_drawdown_percent.toFixed(2)}%`}
            icon={<TrendingDown className="w-6 h-6" />}
            trend="down"
            subtitle="Peak to trough decline"
          />

          <MetricsCard
            title="Win Rate"
            value={`${metrics.win_rate.toFixed(2)}%`}
            icon={<Target className="w-6 h-6" />}
            trend={metrics.win_rate > 50 ? 'up' : 'down'}
            subtitle={`${metrics.winning_trades}/${metrics.total_trades} trades`}
          />
        </div>

        {/* Equity Curve */}
        <div className="mb-8">
          <EquityChart
            data={results.equity_curve}
            initialCapital={params.initial_capital}
          />
        </div>

        {/* Trade Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <MetricsCard
            title="Total Trades"
            value={metrics.total_trades}
            icon={<BarChart3 className="w-6 h-6" />}
            subtitle={`${metrics.winning_trades} wins, ${metrics.losing_trades} losses`}
          />

          <MetricsCard
            title="Profit Factor"
            value={metrics.profit_factor.toFixed(2)}
            subtitle="Gross profit / Gross loss"
            trend={metrics.profit_factor > 1 ? 'up' : 'down'}
          />

          <MetricsCard
            title="Avg Win/Loss"
            value={`$${metrics.avg_win.toLocaleString('en-US', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}`}
            unit={`/ $${Math.abs(metrics.avg_loss).toLocaleString('en-US', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}`}
            subtitle="Average per trade"
          />
        </div>

        {/* Trades Table */}
        {results.trades.length > 0 && (
          <div className="mb-8">
            <TradesTable trades={results.trades} />
          </div>
        )}

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          <div className="p-6 bg-secondary/50 border border-slate-700 rounded-lg">
            <h3 className="text-lg font-semibold text-white mb-4">
              Performance Summary
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Initial Capital</span>
                <span className="text-white font-semibold">
                  ${params.initial_capital.toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Final Equity</span>
                <span className="text-white font-semibold">
                  ${finalEquity.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Total Profit/Loss</span>
                <span
                  className={`font-semibold ${
                    isPositive ? 'text-green-400' : 'text-red-400'
                  }`}
                >
                  ${metrics.total_return.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </span>
              </div>
              <div className="border-t border-slate-700 pt-3 flex justify-between items-center">
                <span className="text-slate-400">Return %</span>
                <span
                  className={`text-lg font-bold ${
                    isPositive ? 'text-green-400' : 'text-red-400'
                  }`}
                >
                  {isPositive ? '+' : ''}
                  {metrics.total_return_percent.toFixed(2)}%
                </span>
              </div>
            </div>
          </div>

          <div className="p-6 bg-secondary/50 border border-slate-700 rounded-lg">
            <h3 className="text-lg font-semibold text-white mb-4">
              Risk Metrics
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Max Drawdown</span>
                <span className="text-red-400 font-semibold">
                  {metrics.max_drawdown_percent.toFixed(2)}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Sharpe Ratio</span>
                <span className="text-white font-semibold">
                  {metrics.sharpe_ratio.toFixed(4)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Win Rate</span>
                <span className="text-white font-semibold">
                  {metrics.win_rate.toFixed(2)}%
                </span>
              </div>
              <div className="border-t border-slate-700 pt-3 flex justify-between items-center">
                <span className="text-slate-400">Profit Factor</span>
                <span className="text-white font-semibold">
                  {metrics.profit_factor.toFixed(2)}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4 justify-center">
          <Link
            href="/"
            className="px-6 py-3 bg-accent hover:bg-blue-600 text-white font-semibold rounded-lg transition-colors"
          >
            Run Another Backtest
          </Link>
          <button
            onClick={() => {
              const data = {
                strategy: params.strategy_text,
                symbol: params.stock_symbol,
                period: `${params.start_date} to ${params.end_date}`,
                metrics: metrics,
              }
              const element = document.createElement('a')
              element.setAttribute(
                'href',
                'data:text/plain;charset=utf-8,' +
                  encodeURIComponent(JSON.stringify(data, null, 2))
              )
              element.setAttribute('download', 'backtest_results.json')
              element.style.display = 'none'
              document.body.appendChild(element)
              element.click()
              document.body.removeChild(element)
            }}
            className="px-6 py-3 bg-secondary hover:bg-secondary/80 text-white font-semibold rounded-lg border border-slate-700 transition-colors"
          >
            Download Results
          </button>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-700 bg-primary/50 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 text-center text-sm text-slate-400">
          <p>© 2024 Trading Strategy Backtester. All rights reserved.</p>
        </div>
      </footer>
    </main>
  )
}
