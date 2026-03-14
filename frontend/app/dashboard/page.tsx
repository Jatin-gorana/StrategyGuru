'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import ProfileCard from '@/components/ProfileCard'
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
  Zap,
  AlertCircle,
  Download,
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
      <div className="min-h-screen bg-primary flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-accent border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-400">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (!results || !params) {
    return (
      <div className="min-h-screen bg-primary flex items-center justify-center">
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
      alert(`Failed to run backtest with improved strategy: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsRunningBacktest(false)
    }
  }

  return (
    <main className="min-h-screen bg-primary pb-20">
      {/* Header */}
      <header className="border-b border-slate-800 bg-primary sticky top-0 z-50">
        <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <div className="flex items-center gap-2 hidden sm:flex">
              <div className="w-6 h-6 bg-accent rounded-sm transform rotate-45 flex items-center justify-center">
                <div className="w-3 h-3 bg-primary transform -rotate-45" />
              </div>
              <h1 className="text-xl font-bold text-white tracking-wide">
                Quant Terminal
              </h1>
            </div>
            <nav className="flex items-center gap-6 h-16">
              <Link href="/" className="text-slate-400 hover:text-white transition-colors h-full flex items-center text-sm font-semibold tracking-wide hidden md:flex">Dashboard</Link>
              <Link href="/dashboard" className="text-accent border-b-2 border-accent h-full flex items-center text-sm font-semibold tracking-wide">Backtests</Link>
              <Link href="/" className="text-slate-400 hover:text-white transition-colors h-full flex items-center text-sm font-semibold tracking-wide hidden lg:flex">Live Terminal</Link>
              <Link href="/" className="text-slate-400 hover:text-white transition-colors h-full flex items-center text-sm font-semibold tracking-wide hidden xl:flex">Nodes</Link>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right hidden sm:block">
              <p className="text-xs font-bold text-white">Quant_User_01</p>
              <p className="text-[10px] text-accent font-bold tracking-wider">PRO TIER</p>
            </div>
            <ProfileCard />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 pt-8">

        {/* Title Area */}
        <div className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-semibold tracking-wider text-slate-500 mb-2">
              <Link href="/" className="hover:text-slate-300 transition-colors">BACKTESTS</Link>
              <span>/</span>
              <span className="text-slate-400">{params.stock_symbol}-AGENT</span>
              <span>/</span>
              <span className="text-accent">BT-{params.stock_symbol}-ALPHA</span>
            </div>
            <div className="flex items-center gap-3 mb-2">
              <span className="bg-green-500/20 text-accent text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider border border-green-500/20">Completed</span>
              <span className="text-xs text-slate-500 font-mono tracking-wider">ID: 0x8a29_ALPHA_V2</span>
            </div>
            <h1 className="text-4xl font-extrabold text-white tracking-tight mb-2">
              BT-{params.stock_symbol}-Alpha Analytics
            </h1>
            <p className="text-slate-400">
              Mean Reversion strategy optimized for {params.stock_symbol} Perpetual.
            </p>
          </div>
          <div className="flex gap-3 mt-4 md:mt-0">
            <button
              onClick={handleDownload}
              className="px-6 py-2 bg-secondary hover:bg-secondary/80 text-white text-sm font-semibold rounded-lg border border-slate-700 transition-colors flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Export Data
            </button>
            <button
              onClick={() => setShowImprovementModal(true)}
              className="px-6 py-2 bg-accent hover:bg-[#00e67a] text-black text-sm font-bold tracking-wide rounded-lg transition-colors flex items-center gap-2"
            >
              <Zap className="w-4 h-4" />
              Improve Strategy
            </button>
          </div>
        </div>

        {/* Top Cards Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-2 p-6 bg-secondary border border-slate-800 rounded-xl hover:border-slate-700 transition-all">
            <h3 className="text-accent text-sm font-bold tracking-wider mb-4 flex items-center gap-2 uppercase">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
              Agentic Logic Summary
            </h3>
            <p className="text-sm text-slate-300 leading-relaxed mb-6">
              This strategy isolates momentum in {params.stock_symbol}. The system includes a proprietary "Noise Filter" to reduce false breakouts during low-volume sessions. <br /><br />
              Original Code logic:<br />
              <span className="font-mono text-xs text-slate-400 bg-[#0B0E14] p-1 rounded inline-block mt-2">{params.strategy_text.substring(0, 100)}{params.strategy_text.length > 100 ? '...' : ''}</span>
            </p>
            <div className="flex flex-wrap gap-2 text-[10px] font-bold tracking-wider">
              <span className="px-3 py-1 bg-[#0B0E14] border border-slate-800 rounded text-slate-400"><span className="text-slate-500 mr-2">TIMEFRAME</span> 1日 / 1h</span>
              <span className="px-3 py-1 bg-[#0B0E14] border border-slate-800 rounded text-slate-400"><span className="text-slate-500 mr-2">LEVERAGE</span> 1.0x</span>
              <span className="px-3 py-1 bg-[#0B0E14] border border-slate-800 rounded text-slate-400"><span className="text-slate-500 mr-2">UNIVERSE</span> {params.stock_symbol}</span>
            </div>
          </div>

          <div className="p-6 bg-secondary border border-slate-800 rounded-xl hover:border-slate-700 transition-all">
            <h3 className="text-accent text-sm font-bold tracking-wider mb-6 flex items-center gap-2 uppercase">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
              Backtest Period
            </h3>
            <div className="space-y-4 text-sm">
              <div className="flex justify-between border-b border-slate-800 pb-2">
                <span className="text-slate-500 font-semibold tracking-wider">START DATE</span>
                <span className="text-white font-mono">{params.start_date}</span>
              </div>
              <div className="flex justify-between border-b border-slate-800 pb-2">
                <span className="text-slate-500 font-semibold tracking-wider">END DATE</span>
                <span className="text-white font-mono">{params.end_date}</span>
              </div>
              <div className="flex justify-between pb-4">
                <span className="text-slate-500 font-semibold tracking-wider">DURATION</span>
                <span className="text-white font-mono">{Math.floor((new Date(params.end_date).getTime() - new Date(params.start_date).getTime()) / (1000 * 3600 * 24))} Days</span>
              </div>
              <div className="flex justify-between items-center pt-2">
                <span className="text-slate-500 font-semibold tracking-wider">DATA SOURCE</span>
                <span className="text-accent font-mono text-xs flex items-center gap-1"><span className="w-1.5 h-1.5 bg-accent rounded-full inline-block"></span> Yahoo Finance Daily</span>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs - keeping for functionality but styling them less prominent */}
        <div className="flex gap-6 border-b border-slate-800 mb-8">
          {(['overview', 'trades', 'analysis'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-3 text-sm font-bold tracking-widest uppercase transition-colors relative ${activeTab === tab
                  ? 'text-accent'
                  : 'text-slate-500 hover:text-slate-300'
                }`}
            >
              {tab}
              {activeTab === tab && (
                <div className="absolute bottom-0 left-0 w-full h-0.5 bg-accent rounded-t-full"></div>
              )}
            </button>
          ))}
        </div>
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6 animate-fade-in">

            {/* Key Metrics Grid - Image 1 style: 4 equal cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">

              {/* Total Return */}
              <div className="p-5 bg-secondary border border-slate-800 rounded-xl hover:border-slate-700 transition-all">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <p className="text-[10px] font-bold text-slate-500 tracking-widest uppercase">Total Return</p>
                    <p className="text-[10px] text-slate-600 mt-0.5">Final ${finalEquity.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
                  </div>
                  <svg className="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
                </div>
                <p className="text-2xl font-bold text-white mb-1">
                  ${metrics.total_return.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  <span className="text-sm font-normal text-slate-400 ml-1">({metrics.total_return_percent >= 0 ? '+' : ''}{metrics.total_return_percent.toFixed(2)}%)</span>
                </p>
                {metrics.total_return >= 0 ? (
                  <p className="text-[11px] text-accent flex items-center gap-1">↗ Positive</p>
                ) : (
                  <p className="text-[11px] text-red-400 flex items-center gap-1">↘ Negative</p>
                )}
              </div>

              {/* Sharpe Ratio */}
              <div className="p-5 bg-secondary border border-slate-800 rounded-xl hover:border-slate-700 transition-all">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <p className="text-[10px] font-bold text-slate-500 tracking-widest uppercase">Sharpe Ratio</p>
                    <p className="text-[10px] text-slate-600 mt-0.5">Risk-adjusted return</p>
                  </div>
                  <svg className="w-5 h-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                </div>
                <p className="text-2xl font-bold text-white mb-1">{metrics.sharpe_ratio.toFixed(4)}</p>
                {metrics.sharpe_ratio >= 1 ? (
                  <p className="text-[11px] text-accent flex items-center gap-1">↗ Positive</p>
                ) : metrics.sharpe_ratio >= 0 ? (
                  <p className="text-[11px] text-yellow-400 flex items-center gap-1">→ Neutral</p>
                ) : (
                  <p className="text-[11px] text-red-400 flex items-center gap-1">↘ Negative</p>
                )}
              </div>

              {/* Max Drawdown */}
              <div className="p-5 bg-secondary border border-slate-800 rounded-xl hover:border-slate-700 transition-all">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <p className="text-[10px] font-bold text-slate-500 tracking-widest uppercase">Max Drawdown</p>
                    <p className="text-[10px] text-slate-600 mt-0.5">Peak to trough decline</p>
                  </div>
                  <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" /></svg>
                </div>
                <p className="text-2xl font-bold text-red-400 mb-1">{metrics.max_drawdown_percent.toFixed(2)}%</p>
                <p className="text-[11px] text-red-400 flex items-center gap-1">↘ Negative</p>
              </div>

              {/* Win Rate */}
              <div className="p-5 bg-secondary border border-slate-800 rounded-xl hover:border-slate-700 transition-all">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <p className="text-[10px] font-bold text-slate-500 tracking-widest uppercase">Win Rate</p>
                    <p className="text-[10px] text-slate-600 mt-0.5">{metrics.winning_trades}/{metrics.total_trades} trades</p>
                  </div>
                  <svg className="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" strokeWidth={2}/><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3" /></svg>
                </div>
                <p className="text-2xl font-bold text-white mb-1">{metrics.win_rate.toFixed(2)}%</p>
                {metrics.win_rate >= 50 ? (
                  <p className="text-[11px] text-accent flex items-center gap-1">↗ Positive</p>
                ) : (
                  <p className="text-[11px] text-red-400 flex items-center gap-1">↘ Negative</p>
                )}
              </div>

            </div>

            {/* Charts Grid */}
            <div className="p-6 bg-secondary border border-slate-800 rounded-xl relative">
              <div className="absolute top-6 right-6 flex items-center gap-2">
                <button className="px-3 py-1 bg-accent text-black font-bold text-[10px] tracking-wider uppercase rounded">LINEAR</button>
                <button className="px-3 py-1 border border-slate-700 text-slate-400 font-bold text-[10px] tracking-wider uppercase rounded hover:text-white transition-colors">LOGARITHMIC</button>
              </div>
              <div className="flex items-center gap-6 mb-8">
                <h2 className="text-sm font-bold tracking-wider text-white uppercase flex items-center gap-2">EQUITY CURVE</h2>
                <div className="flex items-center gap-4 text-xs font-semibold">
                  <span className="flex items-center gap-1 text-slate-300"><span className="w-3 h-0.5 bg-accent inline-block"></span> STRATEGY</span>
                  <span className="flex items-center gap-1 text-slate-500"><span className="w-3 h-0.5 bg-slate-600 border border-slate-600 border-dashed inline-block"></span> BENCHMARK</span>
                </div>
              </div>
              <div className="pt-4">
                <EquityChart
                  data={results.equity_curve}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Drawdown Chart */}
              <div className="p-6 bg-secondary border border-slate-800 rounded-xl">
                <h2 className="text-[10px] font-bold tracking-widest text-white uppercase mb-6">DRAWDOWN DISTRIBUTION</h2>
                <DrawdownChart
                  equityCurve={results.equity_curve}
                />
              </div>
              {/* Monthly Heatmap Placeholder - since we don't have this component, we'll reuse performance distribution but title it appropriately */}
              <div className="p-6 bg-secondary border border-slate-800 rounded-xl">
                <h2 className="text-[10px] font-bold tracking-widest text-white uppercase mb-6">PERFORMANCE DISTRIBUTION</h2>
                <PerformanceChart trades={results.trades} />
              </div>
            </div>

            {/* Performance Summary + Risk Metrics - Image 2 Top Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mt-6">

              {/* Performance Summary */}
              <div className="p-6 bg-secondary border border-slate-800 rounded-xl">
                <h3 className="text-sm font-bold text-white mb-5">Performance Summary</h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center border-b border-slate-800 pb-3">
                    <span className="text-sm text-slate-400">Initial Capital</span>
                    <span className="text-sm font-semibold text-white">${params.initial_capital.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
                  </div>
                  <div className="flex justify-between items-center border-b border-slate-800 pb-3">
                    <span className="text-sm text-slate-400">Final Equity</span>
                    <span className="text-sm font-semibold text-white">${finalEquity.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                  </div>
                  <div className="flex justify-between items-center border-b border-slate-800 pb-3">
                    <span className="text-sm text-slate-400">Total Profit/Loss</span>
                    <span className={`text-sm font-bold ${isPositive ? 'text-accent' : 'text-red-400'}`}>
                      {isPositive ? '+' : '-'}${Math.abs(metrics.total_return).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </span>
                  </div>
                  <div className="flex justify-between items-center pt-1">
                    <span className="text-sm text-slate-400">Return %</span>
                    <span className={`text-sm font-bold ${isPositive ? 'text-accent' : 'text-red-400'}`}>
                      {isPositive ? '+' : ''}{metrics.total_return_percent.toFixed(2)}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Risk Metrics */}
              <div className="p-6 bg-secondary border border-slate-800 rounded-xl">
                <h3 className="text-sm font-bold text-white mb-5">Risk Metrics</h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center border-b border-slate-800 pb-3">
                    <span className="text-sm text-slate-400">Max Drawdown</span>
                    <span className="text-sm font-bold text-red-400">{metrics.max_drawdown_percent.toFixed(2)}%</span>
                  </div>
                  <div className="flex justify-between items-center border-b border-slate-800 pb-3">
                    <span className="text-sm text-slate-400">Sharpe Ratio</span>
                    <span className="text-sm font-semibold text-white">{metrics.sharpe_ratio.toFixed(4)}</span>
                  </div>
                  <div className="flex justify-between items-center border-b border-slate-800 pb-3">
                    <span className="text-sm text-slate-400">Win Rate</span>
                    <span className="text-sm font-semibold text-white">{metrics.win_rate.toFixed(2)}%</span>
                  </div>
                  <div className="flex justify-between items-center pt-1">
                    <span className="text-sm text-slate-400">Profit Factor</span>
                    <span className="text-sm font-semibold text-white">{metrics.profit_factor.toFixed(2)}</span>
                  </div>
                </div>
              </div>

            </div>

            {/* Image 2 Bottom Row: 3 small stat cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-5">

              {/* Total Trades */}
              <div className="p-5 bg-secondary border border-slate-800 rounded-xl hover:border-slate-700 transition-all">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <p className="text-xs text-slate-400">Total Trades</p>
                    <p className="text-[10px] text-slate-600 mt-0.5">
                      {metrics.winning_trades} wins, {metrics.losing_trades} losses
                    </p>
                  </div>
                  <svg className="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
                </div>
                <p className="text-3xl font-bold text-white">{metrics.total_trades}</p>
              </div>

              {/* Profit Factor */}
              <div className="p-5 bg-secondary border border-slate-800 rounded-xl hover:border-slate-700 transition-all">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <p className="text-xs text-slate-400">Profit Factor</p>
                    <p className="text-[10px] text-slate-600 mt-0.5">Gross profit / Gross loss</p>
                  </div>
                </div>
                <p className="text-3xl font-bold text-white mb-1">{metrics.profit_factor.toFixed(2)}</p>
                {metrics.profit_factor < 1 ? (
                  <p className="text-[11px] text-red-400">↘ Negative</p>
                ) : (
                  <p className="text-[11px] text-accent">↗ Positive</p>
                )}
              </div>

              {/* Avg Win/Loss */}
              <div className="p-5 bg-secondary border border-slate-800 rounded-xl hover:border-slate-700 transition-all">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <p className="text-xs text-slate-400">Avg Win/Loss</p>
                    <p className="text-[10px] text-slate-600 mt-0.5">Average per trade</p>
                  </div>
                </div>
                <p className="text-3xl font-bold text-white mb-1">
                  ${metrics.avg_win.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  <span className="text-sm font-normal text-slate-500 ml-1">/ ${Math.abs(metrics.avg_loss).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                </p>
              </div>

            </div>

          </div>
        )}

        {/* Trades Tab */}
        {activeTab === 'trades' && (
          <div className="animate-fade-in p-6 bg-secondary border border-slate-800 rounded-xl">
            <h2 className="text-[10px] font-bold tracking-widest text-white uppercase mb-6 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" /></svg>
                EXECUTION HISTORY
              </div>
              <button className="px-3 py-1 bg-[#0B0E14] border border-slate-700 rounded text-slate-400 hover:text-white transition-colors">FILTER All Trades</button>
            </h2>
            {results.trades.length > 0 ? (
              <TradesTable trades={results.trades} />
            ) : (
              <div className="p-12 text-center text-slate-500">
                <p>No trades executed</p>
              </div>
            )}
          </div>
        )}

        {/* Analysis Tab (kept minimal based on earlier) */}
        {activeTab === 'analysis' && (
          <div className="animate-fade-in p-6 bg-secondary border border-slate-800 rounded-xl">
            <h2 className="text-[10px] font-bold tracking-widest text-white uppercase mb-6">ADVANCED ANALYSIS METRICS</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              <div className="flex flex-col">
                <span className="text-xs text-slate-500 tracking-wider mb-2">Risk/Reward Ratio</span>
                <span className="text-2xl font-bold font-mono text-white">{(metrics.avg_win / Math.abs(metrics.avg_loss)).toFixed(2)}:1</span>
              </div>
              <div className="flex flex-col">
                <span className="text-xs text-slate-500 tracking-wider mb-2">Expectancy</span>
                <span className="text-2xl font-bold font-mono text-white">
                  ${((metrics.winning_trades * metrics.avg_win - metrics.losing_trades * Math.abs(metrics.avg_loss)) / metrics.total_trades).toFixed(2)}
                </span>
              </div>
              <div className="flex flex-col">
                <span className="text-xs text-slate-500 tracking-wider mb-2">Best Trade</span>
                <span className="text-2xl font-bold font-mono text-accent">
                  +${Math.max(...results.trades.map((t) => t.pnl)).toFixed(2)}
                </span>
              </div>
              <div className="flex flex-col">
                <span className="text-xs text-slate-500 tracking-wider mb-2">Worst Trade</span>
                <span className="text-2xl font-bold font-mono text-danger">
                  -${Math.abs(Math.min(...results.trades.map((t) => t.pnl))).toFixed(2)}
                </span>
              </div>
            </div>
          </div>
        )}

      </div>

      {/* Footer / Status bar matches Image 3 */}
      <footer className="fixed bottom-0 left-0 right-0 border-t border-slate-800 bg-[#0B0E14] h-10 flex items-center justify-between px-6 text-[10px] font-mono text-slate-500 tracking-wider z-50">
        <div className="flex items-center gap-6">
          <span className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-accent"></span> SYSTEM LATENCY: 1.4MS</span>
          <span className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-accent"></span> CLUSTER: NODE-ALPHA-WEST</span>
        </div>
        <div>
          © 2024 AGENTIC QUANTUM TERMINAL // ALL PARAMETERS OPTIMIZED
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
