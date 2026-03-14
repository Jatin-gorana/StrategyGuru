'use client'

import { useEffect, useState, useMemo } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import api from '@/lib/api'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

interface Trade {
  id: string
  entry_date: string
  exit_date: string
  entry_price: number
  exit_price: number
  profit: number
  profit_percent: number
}

interface EquityPoint {
  date: string
  equity_value: number
}

interface BacktestDetail {
  id: string
  stock_symbol: string
  start_date: string
  end_date: string
  initial_capital: number
  total_return: number
  return_percent: number
  sharpe_ratio: number
  max_drawdown: number
  max_drawdown_percent: number
  win_rate: number
  profit_factor: number
  total_trades: number
  created_at: string
  trades: Trade[]
  equity_curve: EquityPoint[]
}

const COLORS = ['#00FF88', '#3b82f6', '#f43f5e', '#a855f7', '#facc15', '#06b6d4']

export default function CompareBacktestsPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const idsParam = searchParams.get('ids')
  
  const [backtests, setBacktests] = useState<BacktestDetail[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!idsParam) {
      setError('No backtests selected for comparison')
      setLoading(false)
      return
    }

    const ids = idsParam.split(',')
    if (ids.length < 2) {
      setError('Select at least two backtests to compare')
      setLoading(false)
      return
    }

    const fetchAllBacktests = async () => {
      try {
        const results = await Promise.all(
          ids.map(id => api.getBacktestDetail(id))
        )
        setBacktests(results)
      } catch (err: any) {
        setError('Failed to load backtest details')
        if (err.response?.status === 401) {
          router.push('/login')
        }
      } finally {
        setLoading(false)
      }
    }

    fetchAllBacktests()
  }, [idsParam, router])

  // Process data for the combined chart
  const combinedChartData = useMemo(() => {
    if (backtests.length === 0) return []

    // 1. Collect all unique dates across all equity curves
    const allDates = new Set<string>()
    backtests.forEach(bt => {
      bt.equity_curve.forEach(pt => {
        allDates.add(pt.date.split('T')[0])
      })
    })

    // 2. Sort dates chronologically
    const sortedDates = Array.from(allDates).sort()

    // 3. Keep track of last known equity value for each strategy to handle missing days
    const lastValidEquities: Record<string, number> = {}
    backtests.forEach(bt => {
      lastValidEquities[bt.id] = bt.initial_capital
    })

    // 4. Build chart data with one data point per date
    const data = sortedDates.map(date => {
      const dataPoint: any = { 
        rawDate: date,
        displayDate: new Date(date).toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric'
        })
      }
      
      backtests.forEach((bt, idx) => {
        const pointOnDate = bt.equity_curve.find(pt => pt.date.startsWith(date))
        if (pointOnDate) {
          dataPoint[`bt_${idx}`] = Math.round(pointOnDate.equity_value * 100) / 100
          lastValidEquities[bt.id] = pointOnDate.equity_value
        } else {
          // Carry forward previous day's equity
          dataPoint[`bt_${idx}`] = Math.round(lastValidEquities[bt.id] * 100) / 100
        }
      })
      
      return dataPoint
    })

    // Sub-sample if dataset is too large to maintain performance
    if (data.length > 200) {
      const rate = Math.ceil(data.length / 200)
      return data.filter((_, i) => i % rate === 0 || i === data.length - 1)
    }

    return data
  }, [backtests])

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-slate-400">Loading comparison...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center">
        <div className="text-red-400 mb-4">{error}</div>
        <Link href="/profile/backtests" className="text-blue-400 hover:underline">
          Go back to History
        </Link>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link href="/profile/backtests" className="text-blue-400 hover:text-blue-300 mb-4 inline-block">
            ← Back to History
          </Link>
          <h1 className="text-4xl font-bold text-white mb-2">Compare Backtests</h1>
          <p className="text-slate-400">Comparing {backtests.length} selected strategies.</p>
        </div>

        {/* Combined Chart */}
        <div className="bg-slate-800 rounded-xl p-6 mb-8 border border-slate-700 shadow-xl">
          <h2 className="text-xl font-bold text-white mb-6">Equity Growth Comparison</h2>
          <div className="w-full h-[500px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={combinedChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis 
                  dataKey="displayDate" 
                  stroke="#475569"
                  style={{ fontSize: '12px' }}
                  tick={{ fill: '#64748b' }}
                  minTickGap={20}
                />
                <YAxis
                  stroke="#475569"
                  style={{ fontSize: '12px' }}
                  tick={{ fill: '#64748b' }}
                  tickFormatter={(val) => `$${(val / 1000).toFixed(0)}k`}
                  domain={['auto', 'auto']}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem' }}
                  itemStyle={{ fontSize: '14px', fontWeight: 'bold' }}
                />
                <Legend iconType="circle" />
                {backtests.map((bt, idx) => (
                  <Line
                    key={bt.id}
                    type="stepAfter"
                    dataKey={`bt_${idx}`}
                    name={`${bt.stock_symbol} - ${new Date(bt.created_at).toLocaleDateString('en-US', {month: 'short', day: 'numeric'})}`}
                    stroke={COLORS[idx % COLORS.length]}
                    strokeWidth={2}
                    dot={false}
                    isAnimationActive={true}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Metrics Comparison Table */}
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-xl overflow-x-auto">
          <h2 className="text-xl font-bold text-white mb-6">Key Metrics</h2>
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-slate-700 text-slate-400">
                <th className="py-3 px-4 font-semibold">Metric</th>
                {backtests.map((bt, idx) => (
                  <th key={`hdr-${bt.id}`} className="py-3 px-4 font-semibold" style={{ color: COLORS[idx % COLORS.length] }}>
                    Strategy {idx + 1}
                    <div className="text-sm font-normal text-slate-500 mt-1">{bt.stock_symbol}</div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="text-white">
              <tr className="border-b border-slate-700/50 hover:bg-slate-800/50">
                <td className="py-3 px-4 font-medium text-slate-300">Total Return</td>
                {backtests.map(bt => (
                  <td key={`ret-${bt.id}`} className={`py-3 px-4 font-bold ${bt.return_percent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {bt.return_percent ? `${bt.return_percent.toFixed(2)}%` : '0.00%'}
                  </td>
                ))}
              </tr>
              <tr className="border-b border-slate-700/50 hover:bg-slate-800/50">
                <td className="py-3 px-4 font-medium text-slate-300">Sharpe Ratio</td>
                {backtests.map(bt => (
                  <td key={`sharpe-${bt.id}`} className="py-3 px-4">
                    {bt.sharpe_ratio ? bt.sharpe_ratio.toFixed(2) : 'N/A'}
                  </td>
                ))}
              </tr>
              <tr className="border-b border-slate-700/50 hover:bg-slate-800/50">
                <td className="py-3 px-4 font-medium text-slate-300">Win Rate</td>
                {backtests.map(bt => (
                  <td key={`win-${bt.id}`} className="py-3 px-4">
                    {bt.win_rate ? `${(bt.win_rate * 100).toFixed(1)}%` : '0.0%'}
                  </td>
                ))}
              </tr>
              <tr className="border-b border-slate-700/50 hover:bg-slate-800/50">
                <td className="py-3 px-4 font-medium text-slate-300">Max Drawdown</td>
                {backtests.map(bt => (
                  <td key={`dd-${bt.id}`} className="py-3 px-4 text-red-400">
                    {bt.max_drawdown_percent ? `${bt.max_drawdown_percent.toFixed(2)}%` : '0.00%'}
                  </td>
                ))}
              </tr>
              <tr className="border-b border-slate-700/50 hover:bg-slate-800/50">
                <td className="py-3 px-4 font-medium text-slate-300">Total Trades</td>
                {backtests.map(bt => (
                  <td key={`trades-${bt.id}`} className="py-3 px-4">
                    {bt.total_trades || 0}
                  </td>
                ))}
              </tr>
              <tr className="border-b border-slate-700/50 hover:bg-slate-800/50">
                <td className="py-3 px-4 font-medium text-slate-300">Initial Capital</td>
                {backtests.map(bt => (
                  <td key={`cap-${bt.id}`} className="py-3 px-4">
                    ${bt.initial_capital?.toLocaleString() || '10,000'}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-3 px-4 font-medium text-slate-300">Date Range</td>
                {backtests.map(bt => (
                  <td key={`dates-${bt.id}`} className="py-3 px-4 text-sm text-slate-400">
                    {bt.start_date} to {bt.end_date}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
