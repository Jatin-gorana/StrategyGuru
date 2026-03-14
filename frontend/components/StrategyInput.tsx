'use client'

import { useState } from 'react'
import { Play, Loader2, AlertCircle } from 'lucide-react'
import { StrategyExample } from '@/lib/api'

interface StrategyInputProps {
  onSubmit: (data: {
    strategy_text: string
    stock_symbol: string
    start_date: string
    end_date: string
    initial_capital: number
  }) => void
  isLoading: boolean
  examples: StrategyExample[]
}

export default function StrategyInput({
  onSubmit,
  isLoading,
  examples,
}: StrategyInputProps) {
  const [strategyText, setStrategyText] = useState('')
  const [symbol, setSymbol] = useState('AAPL')
  const [startDate, setStartDate] = useState('2023-01-01')
  const [endDate, setEndDate] = useState('2024-01-01')
  const [capital, setCapital] = useState(10000)
  const [error, setError] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!strategyText.trim()) {
      setError('Please enter a strategy')
      return
    }

    if (!symbol.trim()) {
      setError('Please enter a stock symbol')
      return
    }

    if (new Date(startDate) >= new Date(endDate)) {
      setError('Start date must be before end date')
      return
    }

    if (capital <= 0) {
      setError('Initial capital must be greater than 0')
      return
    }

    onSubmit({
      strategy_text: strategyText,
      stock_symbol: symbol.toUpperCase(),
      start_date: startDate,
      end_date: endDate,
      initial_capital: capital,
    })
  }

  const loadExample = (example: StrategyExample) => {
    setStrategyText(example.strategy)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const strategy = e.dataTransfer.getData('text/plain')
    if (strategy) {
      setStrategyText((prev) => prev + (prev && prev.endsWith('\n') ? '' : '\n') + strategy)
    }
  }

  const handleDragStart = (e: React.DragEvent, strategy: string) => {
    e.dataTransfer.setData('text/plain', strategy)
  }

  return (
    <div className="w-full max-w-4xl mx-auto">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Strategy Text */}
        <div className="space-y-2">
          <label className="block text-sm font-semibold text-white">
            Trading Strategy
          </label>
          <textarea
            value={strategyText}
            onChange={(e) => setStrategyText(e.target.value)}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            placeholder="e.g., Buy when RSI < 30 and sell when RSI > 70"
            className="w-full h-40 px-4 py-3 bg-[#0B0E14] border border-slate-700 rounded-lg text-accent font-mono placeholder-slate-600 focus:border-accent focus:ring-1 focus:ring-accent outline-none resize-none"
            disabled={isLoading}
          />
          <p className="text-xs text-slate-400">
            Describe your trading strategy in natural language
          </p>
        </div>

        {/* Examples */}
        {examples.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs font-semibold text-slate-400 uppercase">
              Quick Examples
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {examples.slice(0, 4).map((example) => (
                <button
                  key={example.name}
                  type="button"
                  draggable
                  onDragStart={(e) => handleDragStart(e, example.strategy)}
                  onClick={() => loadExample(example)}
                  className="text-left p-3 bg-secondary/50 hover:bg-secondary cursor-grab active:cursor-grabbing border border-slate-700 rounded-lg transition-colors border-dashed hover:border-accent/50"
                  disabled={isLoading}
                >
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-semibold text-accent">
                      {example.name}
                    </p>
                    <span className="text-[10px] text-slate-500 hidden md:block">(Drag me)</span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1 line-clamp-1">
                    {example.strategy}
                  </p>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Stock Symbol */}
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-white">
              Stock Symbol
            </label>
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              placeholder="AAPL"
              className="w-full px-4 py-2 bg-secondary border border-slate-700 rounded-lg text-white placeholder-slate-400 focus:border-accent focus:ring-2 focus:ring-accent/20"
              disabled={isLoading}
            />
          </div>

          {/* Initial Capital */}
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-white">
              Initial Capital ($)
            </label>
            <input
              type="number"
              value={capital}
              onChange={(e) => setCapital(Number(e.target.value))}
              placeholder="10000"
              className="w-full px-4 py-2 bg-secondary border border-slate-700 rounded-lg text-white placeholder-slate-400 focus:border-accent focus:ring-2 focus:ring-accent/20"
              disabled={isLoading}
              min="100"
              step="100"
            />
          </div>

          {/* Start Date */}
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-white">
              Start Date
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-4 py-2 bg-secondary border border-slate-700 rounded-lg text-white focus:border-accent focus:ring-2 focus:ring-accent/20"
              disabled={isLoading}
            />
          </div>

          {/* End Date */}
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-white">
              End Date
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full px-4 py-2 bg-secondary border border-slate-700 rounded-lg text-white focus:border-accent focus:ring-2 focus:ring-accent/20"
              disabled={isLoading}
            />
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-accent hover:bg-[#00e67a] text-[#0B0E14] font-bold tracking-wide uppercase rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Running Backtest...
            </>
          ) : (
            <>
              <Play className="w-5 h-5" />
              Run Backtest
            </>
          )}
        </button>
      </form>
    </div>
  )
}
