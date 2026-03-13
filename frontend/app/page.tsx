'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import StrategyInput from '@/components/StrategyInput'
import api, { StrategyExample, BacktestResponse } from '@/lib/api'
import { AlertCircle, CheckCircle } from 'lucide-react'

export default function Home() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [examples, setExamples] = useState<StrategyExample[]>([])
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    loadExamples()
  }, [])

  const loadExamples = async () => {
    try {
      const data = await api.getExamples()
      setExamples(data.examples)
    } catch (err) {
      console.error('Failed to load examples:', err)
    }
  }

  const handleSubmit = async (data: {
    strategy_text: string
    stock_symbol: string
    start_date: string
    end_date: string
    initial_capital: number
  }) => {
    setIsLoading(true)
    setError('')
    setSuccess('')

    try {
      const response = await api.runBacktest(data)
      
      if (response.success) {
        setSuccess('Backtest completed successfully!')
        
        // Store results in sessionStorage for the dashboard page
        sessionStorage.setItem('backtest_results', JSON.stringify(response))
        sessionStorage.setItem('backtest_params', JSON.stringify(data))
        
        // Redirect to dashboard page
        setTimeout(() => {
          router.push('/dashboard')
        }, 500)
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to run backtest'
      setError(errorMessage)
      console.error('Backtest error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-primary via-secondary to-primary">
      {/* Header */}
      <header className="border-b border-slate-700 bg-primary/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">
                Trading Strategy Backtester
              </h1>
              <p className="text-slate-400 mt-1">
                Test your trading strategies with historical data
              </p>
            </div>
            <div className="hidden md:block text-right">
              <p className="text-sm text-slate-400">
                Powered by FastAPI & Next.js
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Success Message */}
        {success && (
          <div className="mb-6 flex items-center gap-3 p-4 bg-green-500/10 border border-green-500/30 rounded-lg animate-fade-in">
            <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
            <p className="text-sm text-green-400">{success}</p>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mb-6 flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg animate-fade-in">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        {/* Main Form */}
        <div className="mb-12 animate-slide-up">
          <div className="bg-secondary/50 border border-slate-700 rounded-lg p-8">
            <StrategyInput
              onSubmit={handleSubmit}
              isLoading={isLoading}
              examples={examples}
            />
          </div>
        </div>

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          <div className="p-6 bg-secondary/50 border border-slate-700 rounded-lg hover:border-accent/50 transition-all">
            <div className="text-accent text-2xl font-bold mb-2">📊</div>
            <h3 className="text-lg font-semibold text-white mb-2">
              Real Market Data
            </h3>
            <p className="text-sm text-slate-400">
              Backtest using actual historical stock prices from Yahoo Finance
            </p>
          </div>

          <div className="p-6 bg-secondary/50 border border-slate-700 rounded-lg hover:border-accent/50 transition-all">
            <div className="text-accent text-2xl font-bold mb-2">🎯</div>
            <h3 className="text-lg font-semibold text-white mb-2">
              Multiple Indicators
            </h3>
            <p className="text-sm text-slate-400">
              Use RSI, Moving Averages, MACD, and more in your strategies
            </p>
          </div>

          <div className="p-6 bg-secondary/50 border border-slate-700 rounded-lg hover:border-accent/50 transition-all">
            <div className="text-accent text-2xl font-bold mb-2">📈</div>
            <h3 className="text-lg font-semibold text-white mb-2">
              Detailed Metrics
            </h3>
            <p className="text-sm text-slate-400">
              Get Sharpe ratio, drawdown, win rate, and more performance metrics
            </p>
          </div>
        </div>

        {/* Features Section */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <h2 className="text-2xl font-bold text-white mb-6">
              Supported Indicators
            </h2>
            <ul className="space-y-3">
              {[
                'RSI (Relative Strength Index)',
                'SMA (Simple Moving Average)',
                'EMA (Exponential Moving Average)',
                'MACD (Moving Average Convergence Divergence)',
                'Bollinger Bands',
                'ATR (Average True Range)',
                'Stochastic Oscillator',
                'ADX (Average Directional Index)',
              ].map((indicator) => (
                <li
                  key={indicator}
                  className="flex items-center gap-3 text-slate-300"
                >
                  <span className="w-2 h-2 bg-accent rounded-full" />
                  {indicator}
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h2 className="text-2xl font-bold text-white mb-6">
              Performance Metrics
            </h2>
            <ul className="space-y-3">
              {[
                'Total Return & Return %',
                'Sharpe Ratio (Risk-Adjusted)',
                'Maximum Drawdown',
                'Win Rate',
                'Profit Factor',
                'Average Win/Loss',
                'Trade Count',
                'Equity Curve',
              ].map((metric) => (
                <li
                  key={metric}
                  className="flex items-center gap-3 text-slate-300"
                >
                  <span className="w-2 h-2 bg-accent rounded-full" />
                  {metric}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Example Strategies */}
        {examples.length > 0 && (
          <div className="mt-16">
            <h2 className="text-2xl font-bold text-white mb-6">
              Example Strategies
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {examples.map((example) => (
                <div
                  key={example.name}
                  className="p-6 bg-secondary/50 border border-slate-700 rounded-lg hover:border-accent/50 transition-all"
                >
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="text-lg font-semibold text-white">
                      {example.name}
                    </h3>
                    <span
                      className={`text-xs font-semibold px-2 py-1 rounded ${
                        example.risk_level === 'Low'
                          ? 'bg-green-500/20 text-green-400'
                          : example.risk_level === 'Medium'
                          ? 'bg-yellow-500/20 text-yellow-400'
                          : 'bg-red-500/20 text-red-400'
                      }`}
                    >
                      {example.risk_level} Risk
                    </span>
                  </div>
                  <p className="text-sm text-slate-400 mb-3">
                    {example.description}
                  </p>
                  <p className="text-sm font-mono text-accent mb-3 bg-primary/50 p-2 rounded">
                    {example.strategy}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {example.indicators.map((indicator) => (
                      <span
                        key={indicator}
                        className="text-xs bg-accent/20 text-accent px-2 py-1 rounded"
                      >
                        {indicator}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-700 bg-primary/50 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            <div>
              <h4 className="text-white font-semibold mb-3">About</h4>
              <p className="text-sm text-slate-400">
                A modern trading strategy backtesting platform built with FastAPI and Next.js
              </p>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-3">Features</h4>
              <ul className="text-sm text-slate-400 space-y-2">
                <li>Real market data</li>
                <li>Multiple indicators</li>
                <li>Detailed metrics</li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-3">Disclaimer</h4>
              <p className="text-sm text-slate-400">
                Past performance does not guarantee future results. Always test thoroughly before trading.
              </p>
            </div>
          </div>
          <div className="border-t border-slate-700 pt-8 text-center text-sm text-slate-400">
            <p>© 2024 Trading Strategy Backtester. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </main>
  )
}
