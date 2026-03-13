'use client'

import { useState, useMemo } from 'react'
import { Trade } from '@/lib/api'
import { ChevronDown, ChevronUp, Search } from 'lucide-react'

interface TradesTableEnhancedProps {
  trades: Trade[]
}

type SortKey = 'entry_date' | 'exit_date' | 'entry_price' | 'exit_price' | 'pnl' | 'pnl_percent'
type SortDirection = 'asc' | 'desc'

export default function TradesTableEnhanced({ trades }: TradesTableEnhancedProps) {
  const [sortConfig, setSortConfig] = useState<{
    key: SortKey
    direction: SortDirection
  }>({ key: 'entry_date', direction: 'asc' })

  const [currentPage, setCurrentPage] = useState(1)
  const [searchTerm, setSearchTerm] = useState('')
  const itemsPerPage = 15

  // Filter trades based on search
  const filteredTrades = useMemo(() => {
    if (!searchTerm) return trades

    const term = searchTerm.toLowerCase()
    return trades.filter((trade) => {
      const entryDate = new Date(trade.entry_date).toLocaleDateString().toLowerCase()
      const exitDate = new Date(trade.exit_date).toLocaleDateString().toLowerCase()
      const entryPrice = trade.entry_price.toString()
      const exitPrice = trade.exit_price.toString()
      const pnl = trade.pnl.toString()

      return (
        entryDate.includes(term) ||
        exitDate.includes(term) ||
        entryPrice.includes(term) ||
        exitPrice.includes(term) ||
        pnl.includes(term)
      )
    })
  }, [trades, searchTerm])

  // Sort trades
  const sortedTrades = useMemo(() => {
    const sorted = [...filteredTrades].sort((a, b) => {
      const aValue = a[sortConfig.key]
      const bValue = b[sortConfig.key]

      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortConfig.direction === 'asc'
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue)
      }

      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortConfig.direction === 'asc' ? aValue - bValue : bValue - aValue
      }

      return 0
    })

    return sorted
  }, [filteredTrades, sortConfig])

  // Paginate trades
  const totalPages = Math.ceil(sortedTrades.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const paginatedTrades = sortedTrades.slice(startIndex, startIndex + itemsPerPage)

  const handleSort = (key: SortKey) => {
    setSortConfig({
      key,
      direction:
        sortConfig.key === key && sortConfig.direction === 'asc' ? 'desc' : 'asc',
    })
    setCurrentPage(1)
  }

  const SortIcon = ({ column }: { column: SortKey }) => {
    if (sortConfig.key !== column) {
      return <div className="w-4 h-4 opacity-0 group-hover:opacity-50" />
    }
    return sortConfig.direction === 'asc' ? (
      <ChevronUp className="w-4 h-4 text-accent" />
    ) : (
      <ChevronDown className="w-4 h-4 text-accent" />
    )
  }

  // Calculate statistics
  const stats = useMemo(() => {
    const totalPnL = sortedTrades.reduce((sum, trade) => sum + trade.pnl, 0)
    const avgPnL = sortedTrades.length > 0 ? totalPnL / sortedTrades.length : 0
    const winningTrades = sortedTrades.filter((t) => t.pnl > 0).length
    const losingTrades = sortedTrades.filter((t) => t.pnl < 0).length

    return { totalPnL, avgPnL, winningTrades, losingTrades }
  }, [sortedTrades])

  if (!trades || trades.length === 0) {
    return (
      <div className="w-full bg-secondary/50 border border-slate-700 rounded-lg p-8 text-center">
        <p className="text-slate-400">No trades to display</p>
      </div>
    )
  }

  return (
    <div className="w-full bg-secondary/50 border border-slate-700 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b border-slate-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">
            Trades ({sortedTrades.length})
          </h3>
          <div className="text-sm text-slate-400">
            Page {currentPage} of {totalPages || 1}
          </div>
        </div>

        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search trades..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value)
              setCurrentPage(1)
            }}
            className="w-full pl-10 pr-4 py-2 bg-primary border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:border-accent focus:ring-2 focus:ring-accent/20"
          />
        </div>
      </div>

      {/* Statistics Bar */}
      {sortedTrades.length > 0 && (
        <div className="px-6 py-4 bg-primary/50 border-b border-slate-700 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-xs text-slate-400 uppercase">Total P&L</p>
            <p
              className={`text-lg font-bold ${
                stats.totalPnL >= 0 ? 'text-green-400' : 'text-red-400'
              }`}
            >
              ${stats.totalPnL.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-400 uppercase">Avg P&L</p>
            <p
              className={`text-lg font-bold ${
                stats.avgPnL >= 0 ? 'text-green-400' : 'text-red-400'
              }`}
            >
              ${stats.avgPnL.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-400 uppercase">Wins</p>
            <p className="text-lg font-bold text-green-400">{stats.winningTrades}</p>
          </div>
          <div>
            <p className="text-xs text-slate-400 uppercase">Losses</p>
            <p className="text-lg font-bold text-red-400">{stats.losingTrades}</p>
          </div>
        </div>
      )}

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-700 bg-primary/50">
              <th className="px-6 py-3 text-left">
                <button
                  onClick={() => handleSort('entry_date')}
                  className="group flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
                >
                  Entry Date
                  <SortIcon column="entry_date" />
                </button>
              </th>
              <th className="px-6 py-3 text-left">
                <button
                  onClick={() => handleSort('exit_date')}
                  className="group flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
                >
                  Exit Date
                  <SortIcon column="exit_date" />
                </button>
              </th>
              <th className="px-6 py-3 text-right">
                <button
                  onClick={() => handleSort('entry_price')}
                  className="group flex items-center justify-end gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors w-full"
                >
                  Entry Price
                  <SortIcon column="entry_price" />
                </button>
              </th>
              <th className="px-6 py-3 text-right">
                <button
                  onClick={() => handleSort('exit_price')}
                  className="group flex items-center justify-end gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors w-full"
                >
                  Exit Price
                  <SortIcon column="exit_price" />
                </button>
              </th>
              <th className="px-6 py-3 text-right">
                <button
                  onClick={() => handleSort('pnl')}
                  className="group flex items-center justify-end gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors w-full"
                >
                  P&L
                  <SortIcon column="pnl" />
                </button>
              </th>
              <th className="px-6 py-3 text-right">
                <button
                  onClick={() => handleSort('pnl_percent')}
                  className="group flex items-center justify-end gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors w-full"
                >
                  Return %
                  <SortIcon column="pnl_percent" />
                </button>
              </th>
            </tr>
          </thead>
          <tbody>
            {paginatedTrades.map((trade, index) => {
              const duration = Math.round(
                (new Date(trade.exit_date).getTime() -
                  new Date(trade.entry_date).getTime()) /
                  (1000 * 60 * 60 * 24)
              )

              return (
                <tr
                  key={index}
                  className="border-b border-slate-700 hover:bg-primary/30 transition-colors"
                >
                  <td className="px-6 py-4 text-sm text-slate-300">
                    <div>
                      {new Date(trade.entry_date).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: '2-digit',
                      })}
                    </div>
                    <div className="text-xs text-slate-500 mt-1">
                      {new Date(trade.entry_date).toLocaleTimeString('en-US', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-300">
                    <div>
                      {new Date(trade.exit_date).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: '2-digit',
                      })}
                    </div>
                    <div className="text-xs text-slate-500 mt-1">
                      {duration} day{duration !== 1 ? 's' : ''}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-300 text-right font-mono">
                    ${trade.entry_price.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-300 text-right font-mono">
                    ${trade.exit_price.toFixed(2)}
                  </td>
                  <td
                    className={`px-6 py-4 text-sm font-semibold text-right font-mono ${
                      trade.pnl >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}
                  >
                    {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                  </td>
                  <td
                    className={`px-6 py-4 text-sm font-semibold text-right ${
                      trade.pnl_percent >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}
                  >
                    {trade.pnl_percent >= 0 ? '+' : ''}
                    {trade.pnl_percent.toFixed(2)}%
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-6 py-4 border-t border-slate-700 bg-primary/50">
          <div className="text-sm text-slate-400">
            Showing {startIndex + 1} to {Math.min(startIndex + itemsPerPage, sortedTrades.length)} of{' '}
            {sortedTrades.length} trades
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="px-4 py-2 bg-secondary hover:bg-secondary/80 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm rounded transition-colors"
            >
              Previous
            </button>
            <div className="flex items-center gap-2">
              {Array.from({ length: Math.min(5, totalPages) }).map((_, i) => {
                const pageNum = i + 1
                return (
                  <button
                    key={pageNum}
                    onClick={() => setCurrentPage(pageNum)}
                    className={`px-3 py-2 text-sm rounded transition-colors ${
                      currentPage === pageNum
                        ? 'bg-accent text-white'
                        : 'bg-secondary hover:bg-secondary/80 text-slate-300'
                    }`}
                  >
                    {pageNum}
                  </button>
                )
              })}
              {totalPages > 5 && (
                <>
                  <span className="text-slate-400">...</span>
                  <button
                    onClick={() => setCurrentPage(totalPages)}
                    className={`px-3 py-2 text-sm rounded transition-colors ${
                      currentPage === totalPages
                        ? 'bg-accent text-white'
                        : 'bg-secondary hover:bg-secondary/80 text-slate-300'
                    }`}
                  >
                    {totalPages}
                  </button>
                </>
              )}
            </div>
            <button
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              className="px-4 py-2 bg-secondary hover:bg-secondary/80 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm rounded transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
