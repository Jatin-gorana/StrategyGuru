'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import api from '@/lib/api'

interface Backtest {
  id: string
  stock_symbol: string
  return_percent: number | null
  sharpe_ratio: number | null
  win_rate: number | null
  total_trades: number | null
  created_at: string
}

export default function BacktestsPage() {
  const router = useRouter()
  const [backtests, setBacktests] = useState<Backtest[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [sortBy, setSortBy] = useState<'date' | 'return' | 'sharpe'>('date')

  useEffect(() => {
    const fetchBacktests = async () => {
      try {
        const data = await api.getBacktests()
        setBacktests(data.backtests)
      } catch (err: any) {
        setError('Failed to load backtests')
        if (err.response?.status === 401) {
          router.push('/login')
        }
      } finally {
        setLoading(false)
      }
    }

    fetchBacktests()
  }, [router])

  const sortedBacktests = [...backtests].sort((a, b) => {
    if (sortBy === 'date') {
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    } else if (sortBy === 'return') {
      return (b.return_percent || 0) - (a.return_percent || 0)
    } else if (sortBy === 'sharpe') {
      return (b.sharpe_ratio || 0) - (a.sharpe_ratio || 0)
    }
    return 0
  })

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-slate-400">Loading backtests...</div>
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

  return (
    <div className="min-h-screen bg-slate-900 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link href="/profile" className="text-blue-400 hover:text-blue-300 mb-4 inline-block">
            ← Back to Profile
          </Link>
          <h1 className="text-4xl font-bold text-white mb-2">Backtest History</h1>
          <p className="text-slate-400">All your backtest results</p>
        </div>

        {/* Sort Controls */}
        <div className="mb-6 flex gap-2">
          <button
            onClick={() => setSortBy('date')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              sortBy === 'date'
                ? 'bg-blue-600 text-white'
                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
            }`}
          >
            Latest
          </button>
          <button
            onClick={() => setSortBy('return')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              sortBy === 'return'
                ? 'bg-blue-600 text-white'
                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
            }`}
          >
            Best Return
          </button>
          <button
            onClick={() => setSortBy('sharpe')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              sortBy === 'sharpe'
                ? 'bg-blue-600 text-white'
                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
            }`}
          >
            Best Sharpe
          </button>
        </div>

        {backtests.length === 0 ? (
          <div className="bg-slate-800 rounded-lg border border-slate-700 p-8 text-center">
            <p className="text-slate-400 mb-4">No backtests yet</p>
            <Link href="/dashboard" className="text-blue-400 hover:text-blue-300">
              Run your first backtest
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left px-4 py-3 text-slate-400 font-semibold">Stock</th>
                  <th className="text-left px-4 py-3 text-slate-400 font-semibold">Return</th>
                  <th className="text-left px-4 py-3 text-slate-400 font-semibold">Sharpe Ratio</th>
                  <th className="text-left px-4 py-3 text-slate-400 font-semibold">Win Rate</th>
                  <th className="text-left px-4 py-3 text-slate-400 font-semibold">Trades</th>
                  <th className="text-left px-4 py-3 text-slate-400 font-semibold">Date</th>
                  <th className="text-left px-4 py-3 text-slate-400 font-semibold">Action</th>
                </tr>
              </thead>
              <tbody>
                {sortedBacktests.map((backtest) => (
                  <tr key={backtest.id} className="border-b border-slate-700 hover:bg-slate-800/50">
                    <td className="px-4 py-3 text-white font-semibold">{backtest.stock_symbol}</td>
                    <td className={`px-4 py-3 font-semibold ${backtest.return_percent && backtest.return_percent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {backtest.return_percent ? `${backtest.return_percent.toFixed(2)}%` : 'N/A'}
                    </td>
                    <td className="px-4 py-3 text-white">
                      {backtest.sharpe_ratio ? backtest.sharpe_ratio.toFixed(2) : 'N/A'}
                    </td>
                    <td className="px-4 py-3 text-white">
                      {backtest.win_rate ? `${(backtest.win_rate * 100).toFixed(1)}%` : 'N/A'}
                    </td>
                    <td className="px-4 py-3 text-white">{backtest.total_trades || 0}</td>
                    <td className="px-4 py-3 text-slate-400">
                      {new Date(backtest.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      <Link
                        href={`/profile/backtests/${backtest.id}`}
                        className="text-blue-400 hover:text-blue-300 transition-colors"
                      >
                        View
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
