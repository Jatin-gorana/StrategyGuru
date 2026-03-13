'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import api from '@/lib/api'

interface Strategy {
  id: string
  strategy_text: string
  created_at: string
}

interface Backtest {
  id: string
  strategy_id: string
  stock_symbol: string
  return_percent: number | null
  sharpe_ratio: number | null
  total_trades: number | null
  created_at: string
}

export default function StrategiesPage() {
  const router = useRouter()
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [backtests, setBacktests] = useState<Backtest[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [strategiesData, backtestsData] = await Promise.all([
          api.getStrategies(),
          api.getBacktests(),
        ])
        setStrategies(strategiesData.strategies)
        setBacktests(backtestsData.backtests)
      } catch (err: any) {
        setError('Failed to load strategies')
        if (err.response?.status === 401) {
          router.push('/login')
        }
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [router])

  const getStrategyBacktests = (strategyId: string) => {
    return backtests.filter((b) => b.strategy_id === strategyId)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-slate-400">Loading strategies...</div>
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
          <h1 className="text-4xl font-bold text-white mb-2">My Strategies</h1>
          <p className="text-slate-400">All trading strategies you've created</p>
        </div>

        {strategies.length === 0 ? (
          <div className="bg-slate-800 rounded-lg border border-slate-700 p-8 text-center">
            <p className="text-slate-400 mb-4">No strategies yet</p>
            <Link href="/dashboard" className="text-blue-400 hover:text-blue-300">
              Create your first strategy
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6">
            {strategies.map((strategy) => {
              const strategyBacktests = getStrategyBacktests(strategy.id)
              const latestBacktest = strategyBacktests[0]

              return (
                <div key={strategy.id} className="bg-slate-800 rounded-lg border border-slate-700 p-6">
                  <div className="mb-4">
                    <p className="text-slate-400 text-sm mb-2">Strategy</p>
                    <p className="text-white text-lg mb-2">{strategy.strategy_text}</p>
                    <p className="text-slate-500 text-sm">
                      Created {new Date(strategy.created_at).toLocaleDateString()}
                    </p>
                  </div>

                  {latestBacktest && (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4 pt-4 border-t border-slate-700">
                      <div>
                        <p className="text-slate-400 text-sm mb-1">Stock</p>
                        <p className="text-white font-semibold">{latestBacktest.stock_symbol}</p>
                      </div>
                      <div>
                        <p className="text-slate-400 text-sm mb-1">Return</p>
                        <p className={`font-semibold ${latestBacktest.return_percent && latestBacktest.return_percent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {latestBacktest.return_percent ? `${latestBacktest.return_percent.toFixed(2)}%` : 'N/A'}
                        </p>
                      </div>
                      <div>
                        <p className="text-slate-400 text-sm mb-1">Sharpe Ratio</p>
                        <p className="text-white font-semibold">
                          {latestBacktest.sharpe_ratio ? latestBacktest.sharpe_ratio.toFixed(2) : 'N/A'}
                        </p>
                      </div>
                      <div>
                        <p className="text-slate-400 text-sm mb-1">Trades</p>
                        <p className="text-white font-semibold">{latestBacktest.total_trades || 0}</p>
                      </div>
                    </div>
                  )}

                  {strategyBacktests.length > 0 && (
                    <Link
                      href={`/profile/backtests/${latestBacktest.id}`}
                      className="inline-block bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
                    >
                      View Latest Backtest
                    </Link>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
