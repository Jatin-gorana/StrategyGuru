'use client'

import { useState } from 'react'
import { Trade } from '@/lib/api'
import { ChevronDown, ChevronUp } from 'lucide-react'

interface TradesTableProps {
  trades: Trade[]
}

export default function TradesTable({ trades }: TradesTableProps) {
  const [sortConfig, setSortConfig] = useState<{
    key: keyof Trade
    direction: 'asc' | 'desc'
  }>({ key: 'entry_date', direction: 'asc' })

  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 10

  const sortedTrades = [...trades].sort((a, b) => {
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

  const totalPages = Math.ceil(sortedTrades.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const paginatedTrades = sortedTrades.slice(
    startIndex,
    startIndex + itemsPerPage
  )

  const handleSort = (key: keyof Trade) => {
    setSortConfig({
      key,
      direction:
        sortConfig.key === key && sortConfig.direction === 'asc'
          ? 'desc'
          : 'asc',
    })
    setCurrentPage(1)
  }

  const SortIcon = ({ column }: { column: keyof Trade }) => {
    if (sortConfig.key !== column) {
      return <div className="w-4 h-4" />
    }
    return sortConfig.direction === 'asc' ? (
      <ChevronUp className="w-4 h-4" />
    ) : (
      <ChevronDown className="w-4 h-4" />
    )
  }

  return (
    <div className="w-full bg-[#0B0E14] rounded-lg overflow-hidden">
      <div className="p-1 border-b border-slate-800">
        <h3 className="text-lg font-semibold text-white">
          Trades ({trades.length})
        </h3>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-slate-800 bg-[#0B0E14]">
              <th className="px-6 py-4 text-left">
                <button
                  onClick={() => handleSort('entry_date')}
                  className="flex items-center gap-2 text-[10px] uppercase tracking-widest font-bold text-slate-500 hover:text-white transition-colors"
                >
                  Entry Date
                  <SortIcon column="entry_date" />
                </button>
              </th>
              <th className="px-6 py-4 text-left">
                <button
                  onClick={() => handleSort('entry_price')}
                  className="flex items-center gap-2 text-[10px] uppercase tracking-widest font-bold text-slate-500 hover:text-white transition-colors"
                >
                  Entry Price
                  <SortIcon column="entry_price" />
                </button>
              </th>
              <th className="px-6 py-4 text-left">
                <button
                  onClick={() => handleSort('exit_date')}
                  className="flex items-center gap-2 text-[10px] uppercase tracking-widest font-bold text-slate-500 hover:text-white transition-colors"
                >
                  Exit Date
                  <SortIcon column="exit_date" />
                </button>
              </th>
              <th className="px-6 py-4 text-left">
                <button
                  onClick={() => handleSort('exit_price')}
                  className="flex items-center gap-2 text-[10px] uppercase tracking-widest font-bold text-slate-500 hover:text-white transition-colors"
                >
                  Exit Price
                  <SortIcon column="exit_price" />
                </button>
              </th>
              <th className="px-6 py-4 text-left">
                <button
                  onClick={() => handleSort('quantity')}
                  className="flex items-center gap-2 text-[10px] uppercase tracking-widest font-bold text-slate-500 hover:text-white transition-colors"
                >
                  Qty
                  <SortIcon column="quantity" />
                </button>
              </th>
              <th className="px-6 py-4 text-right">
                <button
                  onClick={() => handleSort('pnl')}
                  className="flex items-center justify-end gap-2 text-[10px] uppercase tracking-widest font-bold text-slate-500 hover:text-white transition-colors w-full"
                >
                  P&L
                  <SortIcon column="pnl" />
                </button>
              </th>
              <th className="px-6 py-4 text-right">
                <button
                  onClick={() => handleSort('pnl_percent')}
                  className="flex items-center justify-end gap-2 text-[10px] uppercase tracking-widest font-bold text-slate-500 hover:text-white transition-colors w-full"
                >
                  Return %
                  <SortIcon column="pnl_percent" />
                </button>
              </th>
            </tr>
          </thead>
          <tbody>
            {paginatedTrades.map((trade, index) => (
              <tr
                key={index}
                className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors"
              >
                <td className="px-6 py-4 text-sm font-mono text-slate-400">
                  {new Date(trade.entry_date).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 text-sm font-mono text-white">
                  ${trade.entry_price.toFixed(2)}
                </td>
                <td className="px-6 py-4 text-sm font-mono text-slate-400">
                  {new Date(trade.exit_date).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 text-sm font-mono text-white">
                  ${trade.exit_price.toFixed(2)}
                </td>
                <td className="px-6 py-4 text-sm font-mono text-slate-300">
                  {trade.quantity}
                </td>
                <td
                  className={`px-6 py-4 text-sm font-mono font-bold text-right ${
                    (trade.pnl ?? 0) >= 0 ? 'text-accent' : 'text-danger'
                  }`}
                >
                  {(trade.pnl ?? 0) >= 0 ? '+' : ''}${(trade.pnl ?? 0).toFixed(2)}
                </td>
                <td
                  className={`px-6 py-4 text-sm font-mono font-bold text-right ${
                    (trade.pnl_percent ?? 0) >= 0 ? 'text-accent bg-accent/10 px-2 rounded inline-block' : 'text-danger bg-danger/10 px-2 rounded inline-block'
                  }`}
                >
                  {(trade.pnl_percent ?? 0) >= 0 ? '+' : ''}
                  {(trade.pnl_percent ?? 0).toFixed(2)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-6 py-4 border-t border-slate-800 bg-[#0B0E14]">
          <p className="text-[10px] uppercase tracking-widest font-bold text-slate-500">
            Page {currentPage} of {totalPages}
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 bg-secondary border border-slate-700 hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed text-slate-300 text-[10px] font-bold uppercase tracking-wider rounded transition-colors"
            >
              Previous
            </button>
            <button
              onClick={() =>
                setCurrentPage(Math.min(totalPages, currentPage + 1))
              }
              disabled={currentPage === totalPages}
              className="px-3 py-1 bg-secondary border border-slate-700 hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed text-slate-300 text-[10px] font-bold uppercase tracking-wider rounded transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
