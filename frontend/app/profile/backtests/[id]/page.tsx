'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import api from '@/lib/api'
import MetricsCard from '@/components/MetricsCard'
import EquityChart from '@/components/EquityChart'
import DrawdownChart from '@/components/DrawdownChart'
import TradesTable from '@/components/TradesTable'

interface BacktestDetail {
  id: string
  stock_symbol: string
  start_date: string
  end_date: string
  initial_capital: number
  total_return: number | null
  return_percent: number | null
  sharpe_ratio: number | null
  max_drawdown: number | null
  max_drawdown_percent: number | null
  win_rate: number | null
  profit_factor: number | null
  total_trades: number | null
  created_at: string
  trades: Array<{
    id: string
    entry_date: string
    exit_date: string
    entry_price: number
    exit_price: number
    profit: number
    profit_percent: number
  }>
  equity_curve: Array<{
    id: string
    date: string
    equity_value: number
  }>
}

export default function BacktestDetailPage() {
  const router = useRouter()
  const params = useParams()
  const backtestId = params.id as string

  const [backtest, setBacktest] = useState<BacktestDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchBacktest = async () => {
      try {
        const data = await api.getBacktestDetail(backtestId)
        setBacktest(data)
      } catch (err: any) {
        setError('Failed to load backtest details')
        if (err.response?.status === 401) {
          router.push('/login')
        } else if (err.response?.status === 404) {
          router.push('/profile/backtests')
        }
      } finally {
        setLoading(false)
      }
    }

    fetchBacktest()
  }, [backtestId, router])

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-slate-400">Loading backtest details...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-red-400">{error}</div>
      </div>
    )
  }

  if (!backtest) {
    return null
  }

  return (
    <div className="min-h-screen bg-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link href="/profile/backtests" className="text-blue-400 hover:text-blue-300 mb-4 inline-block">
            ← Back to Backtests
          </Link>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">
                {backtest.stock_symbol} Backtest
              </h1>
              <p className="text-slate-400">
                {new Date(backtest.start_date).toLocaleDateString()} to{' '}
                {new Date(backtest.end_date).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <MetricsCard
            title="Total Return"
            value={backtest.total_return ? `$${backtest.total_return.toFixed(2)}` : 'N/A'}
            subtitle={backtest.return_percent ? `${backtest.return_percent.toFixed(2)}%` : undefined}
          />
          <MetricsCard
            title="Sharpe Ratio"
            value={backtest.sharpe_ratio ? backtest.sharpe_ratio.toFixed(2) : 'N/A'}
          />
          <MetricsCard
            title="Max Drawdown"
            value={backtest.max_drawdown_percent ? `${backtest.max_drawdown_percent.toFixed(2)}%` : 'N/A'}
          />
          <MetricsCard
            title="Win Rate"
            value={backtest.win_rate ? `${(backtest.win_rate * 100).toFixed(1)}%` : 'N/A'}
          />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
            <h2 className="text-xl font-bold text-white mb-4">Equity Curve</h2>
            <EquityChart data={backtest.equity_curve.map(pt => ({ ...pt, equity: pt.equity_value }))} />
          </div>

          <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
            <h2 className="text-xl font-bold text-white mb-4">Drawdown</h2>
            <DrawdownChart equityCurve={backtest.equity_curve.map(pt => ({ ...pt, equity: pt.equity_value }))} />
          </div>
        </div>

        {/* Trades Table */}
        <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
          <h2 className="text-xl font-bold text-white mb-4">Trades ({backtest.trades.length})</h2>
          <TradesTable trades={backtest.trades.map(t => ({ ...t, pnl: t.profit, pnl_percent: t.profit_percent, quantity: 1 }))} />
        </div>
      </div>
    </div>
  )
}
