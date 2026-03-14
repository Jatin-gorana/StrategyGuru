'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import ProfileCard from '@/components/ProfileCard'
import MetricsCard from '@/components/MetricsCard'
import EquityChart from '@/components/EquityChart'
import TradesTable from '@/components/TradesTable'
import PerformanceChart from '@/components/PerformanceChart'
import DrawdownChart from '@/components/DrawdownChart'
import StrategyImprovementModal from '@/components/StrategyImprovementModal'
import api, {
  BacktestResponse,
  BacktestMetrics,
} from '@/lib/api'
import {
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Target,
  Zap,
  AlertCircle,
  Download,
  RefreshCw,
  Lightbulb,
  Loader2,
} from 'lucide-react'

export default function DashboardPage() {
  const router = useRouter()
  const [results, setResults] = useState<BacktestResponse | null>(null)
  const [params, setParams] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isRunningBacktest, setIsRunningBacktest] = useState(false)
  const [activeTab, setActiveTab] = useState<'overview' | 'trades' | 'analysis'>('overview')
  const [showImprovementModal, setShowImprovementModal] = useState(false)

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
          <p className="text-slate-400">Loading dashboard...</p>
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

  const handleDownload = () => {
    const data = {
      strategy: params.strategy_text,
      symbol: params.stock_symbol,
      period: `${params.start_date} to ${params.end_date}`,
      initial_capital: params.initial_capital,
      final_equity: finalEquity,
      metrics: metrics,
      trades: results.trades,
      timestamp: new Date().toISOString(),
    }
    const element = document.createElement('a')
    element.setAttribute(
      'href',
      'data:text/plain;charset=utf-8,' +
        encodeURIComponent(JSON.stringify(data, null, 2))
    )
    element.setAttribute('download', `backtest_${params.stock_symbol}_${new Date().toISOString().split('T')[0]}.json`)
    element.style.display = 'none'
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  const handleApplyImprovement = async (improvedStrategyText: string) => {
    setShowImprovementModal(false)
    setIsRunningBacktest(true)

    try {
      // Check authentication before making request
      const token = localStorage.getItem('access_token')
      if (!token) {
        alert('Your session has expired. Please login again.')
        window.location.href = '/login'
        return
      }

      console.log('Applying improved strategy:', improvedStrategyText)
      console.log('Request params:', {
        strategy_text: improvedStrategyText,
        stock_symbol: params.stock_symbol,
        start_date: params.start_date,
        end_date: params.end_date,
        initial_capital: params.initial_capital,
      })

      const response = await api.runBacktest({
        strategy_text: improvedStrategyText,
        stock_symbol: params.stock_symbol,
        start_date: params.start_date,
        end_date: params.end_date,
        initial_capital: params.initial_capital,
      })

      console.log('Backtest response:', response)

      if (!response || !response.metrics) {
        throw new Error('Invalid response from backtest API')
      }

      // Update results and params with the improved strategy
      const updatedParams = {
        ...params,
        strategy_text: improvedStrategyText,
      }

      setResults(response)
      setParams(updatedParams)

      // Store in session storage
      sessionStorage.setItem('backtest_results', JSON.stringify(response))
      sessionStorage.setItem('backtest_params', JSON.stringify(updatedParams))

      console.log('Dashboard updated with improved strategy results')

      // Reset to overview tab to show new results
      setActiveTab('overview')
    } catch (error) {
      console.error('Failed to run backtest with improved strategy:', error)
      
      // Handle 401 errors
      if (error instanceof Error && error.message.includes('401')) {
        alert('Your session has expired. Please login again.')
        localStorage.removeItem('access_token')
        window.location.href = '/login'
      } else {
        alert(`Failed to run backtest with improved strategy: ${error instanceof Error ? error.message : 'Unknown error'}`)
      }
    } finally {
      setIsRunningBacktest(false)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-primary via-secondary to-primary">
      {/* Header */}
      <header className="border-b border-slate-700 bg-primary/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between mb-4">
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
                  Backtest Dashboard
                </h1>
                <p className="text-slate-400 mt-1">
                  {params.stock_symbol} • {params.start_date} to {params.end_date}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <ProfileCard />
              <button
                onClick={() => setShowImprovementModal(true)}
                className="flex items-center gap-2 px-4 py-2 bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400 rounded-lg border border-yellow-500/30 transition-colors"
              >
                <Lightbulb className="w-4 h-4" />
                Improve Strategy
              </button>
              <button
                onClick={handleDownload}
                className="flex items-center gap-2 px-4 py-2 bg-secondary hover:bg-secondary/80 text-white rounded-lg border border-slate-700 transition-colors"
              >
                <Download className="w-4 h-4" />
                Export
              </button>
              <Link
                href="/"
                className="flex items-center gap-2 px-4 py-2 bg-accent hover:bg-blue-600 text-white rounded-lg transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                New Backtest
              </Link>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-4 border-t border-slate-700 pt-4">
            {(['overview', 'trades', 'analysis'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 font-semibold transition-colors ${
                  activeTab === tab
                    ? 'text-accent border-b-2 border-accent'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-8 animate-fade-in">
            {/* Strategy Info */}
            <div className="p-6 bg-secondary/50 border border-slate-700 rounded-lg">
              <h2 className="text-lg font-semibold text-white mb-3">Strategy</h2>
              <p className="text-slate-300 font-mono text-sm bg-primary/50 p-3 rounded">
                {params.strategy_text}
              </p>
            </div>

            {/* Key Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
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

            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Equity Curve */}
              <div className="lg:col-span-2">
                <EquityChart
                  data={results.equity_curve}
                  initialCapital={params.initial_capital}
                />
              </div>

              {/* Performance Distribution */}
              <PerformanceChart trades={results.trades} />

              {/* Drawdown Chart */}
              <DrawdownChart
                equityCurve={results.equity_curve}
                initialCapital={params.initial_capital}
              />
            </div>

            {/* Summary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
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

            {/* Trade Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
          </div>
        )}

        {/* Trades Tab */}
        {activeTab === 'trades' && (
          <div className="animate-fade-in">
            {results.trades.length > 0 ? (
              <TradesTable trades={results.trades} />
            ) : (
              <div className="p-12 bg-secondary/50 border border-slate-700 rounded-lg text-center">
                <p className="text-slate-400">No trades executed</p>
              </div>
            )}
          </div>
        )}

        {/* Analysis Tab */}
        {activeTab === 'analysis' && (
          <div className="space-y-8 animate-fade-in">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Monthly Returns */}
              <div className="p-6 bg-secondary/50 border border-slate-700 rounded-lg">
                <h3 className="text-lg font-semibold text-white mb-4">
                  Analysis Metrics
                </h3>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-slate-400 mb-2">Return Distribution</p>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 bg-secondary rounded-full overflow-hidden">
                        <div
                          className="h-full bg-green-500"
                          style={{
                            width: `${Math.min(
                              (metrics.winning_trades / metrics.total_trades) * 100,
                              100
                            )}%`,
                          }}
                        />
                      </div>
                      <span className="text-sm text-green-400 font-semibold">
                        {metrics.win_rate.toFixed(1)}%
                      </span>
                    </div>
                  </div>

                  <div>
                    <p className="text-sm text-slate-400 mb-2">Risk/Reward Ratio</p>
                    <div className="text-2xl font-bold text-white">
                      {(metrics.avg_win / Math.abs(metrics.avg_loss)).toFixed(2)}:1
                    </div>
                    <p className="text-xs text-slate-500 mt-1">
                      Average win vs average loss
                    </p>
                  </div>

                  <div>
                    <p className="text-sm text-slate-400 mb-2">Consecutive Wins</p>
                    <div className="text-2xl font-bold text-white">
                      {(() => {
                        let maxConsecutive = 0
                        let current = 0
                        results.trades.forEach((trade) => {
                          if ((trade.pnl ?? 0) > 0) {
                            current++
                            maxConsecutive = Math.max(maxConsecutive, current)
                          } else {
                            current = 0
                          }
                        })
                        return maxConsecutive
                      })()}
                    </div>
                  </div>

                  <div>
                    <p className="text-sm text-slate-400 mb-2">Consecutive Losses</p>
                    <div className="text-2xl font-bold text-red-400">
                      {(() => {
                        let maxConsecutive = 0
                        let current = 0
                        results.trades.forEach((trade) => {
                          if ((trade.pnl ?? 0) < 0) {
                            current++
                            maxConsecutive = Math.max(maxConsecutive, current)
                          } else {
                            current = 0
                          }
                        })
                        return maxConsecutive
                      })()}
                    </div>
                  </div>
                </div>
              </div>

              {/* Trade Analysis */}
              <div className="p-6 bg-secondary/50 border border-slate-700 rounded-lg">
                <h3 className="text-lg font-semibold text-white mb-4">
                  Trade Analysis
                </h3>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-slate-400 mb-2">Best Trade</p>
                    <div className="text-2xl font-bold text-green-400">
                      +${Math.max(...results.trades.map((t) => t.pnl)).toFixed(2)}
                    </div>
                  </div>

                  <div>
                    <p className="text-sm text-slate-400 mb-2">Worst Trade</p>
                    <div className="text-2xl font-bold text-red-400">
                      -${Math.abs(Math.min(...results.trades.map((t) => t.pnl))).toFixed(2)}
                    </div>
                  </div>

                  <div>
                    <p className="text-sm text-slate-400 mb-2">Avg Trade Duration</p>
                    <div className="text-2xl font-bold text-white">
                      {(() => {
                        const durations = results.trades.map((trade) => {
                          const entry = new Date(trade.entry_date).getTime()
                          const exit = new Date(trade.exit_date).getTime()
                          return (exit - entry) / (1000 * 60 * 60 * 24)
                        })
                        const avg = durations.reduce((a, b) => a + b, 0) / durations.length
                        return avg.toFixed(1)
                      })()}{' '}
                      days
                    </div>
                  </div>

                  <div>
                    <p className="text-sm text-slate-400 mb-2">Expectancy</p>
                    <div className="text-2xl font-bold text-white">
                      ${(
                        (metrics.winning_trades * metrics.avg_win -
                          metrics.losing_trades * Math.abs(metrics.avg_loss)) /
                        metrics.total_trades
                      ).toFixed(2)}
                    </div>
                    <p className="text-xs text-slate-500 mt-1">
                      Average profit per trade
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-700 bg-primary/50 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 text-center text-sm text-slate-400">
          <p>© 2024 Trading Strategy Backtester. All rights reserved.</p>
        </div>
      </footer>

      {/* Strategy Improvement Modal */}
      <StrategyImprovementModal
        isOpen={showImprovementModal}
        onClose={() => setShowImprovementModal(false)}
        strategyText={params?.strategy_text || ''}
        metrics={results?.metrics || ({} as BacktestMetrics)}
        tradesCount={results?.trades.length || 0}
        onApplyImprovement={handleApplyImprovement}
      />

      {/* Loading Overlay for Backtest */}
      {isRunningBacktest && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-secondary border border-slate-700 rounded-lg p-8 text-center">
            <Loader2 className="w-12 h-12 text-accent animate-spin mx-auto mb-4" />
            <p className="text-white font-semibold">Running backtest with improved strategy...</p>
            <p className="text-slate-400 text-sm mt-2">This may take a moment</p>
          </div>
        </div>
      )}
    </main>
  )
}
