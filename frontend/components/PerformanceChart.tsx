'use client'

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { Trade } from '@/lib/api'

interface PerformanceChartProps {
  trades: Trade[]
}

export default function PerformanceChart({ trades }: PerformanceChartProps) {
  if (!trades || trades.length === 0) {
    return (
      <div className="w-full h-[300px] flex items-center justify-center">
        <p className="text-slate-500 font-mono text-xs uppercase tracking-wider">No trades to display</p>
      </div>
    )
  }

  // Group trades by month
  const monthlyData: { [key: string]: { wins: number; losses: number; profit: number } } = {}

  trades.forEach((trade) => {
    const date = new Date(trade.entry_date)
    const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`

    if (!monthlyData[monthKey]) {
      monthlyData[monthKey] = { wins: 0, losses: 0, profit: 0 }
    }

    const pnl = trade.pnl ?? 0
    if (pnl > 0) {
      monthlyData[monthKey].wins++
    } else {
      monthlyData[monthKey].losses++
    }
    monthlyData[monthKey].profit += pnl
  })

  const chartData = Object.entries(monthlyData)
    .sort()
    .map(([month, data]) => ({
      month,
      wins: data.wins,
      losses: data.losses,
      profit: Math.round(data.profit),
    }))

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-[#0B0E14] border border-slate-800 rounded p-3 shadow-lg">
          <p className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">{payload[0].payload.month}</p>
          <p className="text-xs font-mono font-bold text-accent mt-1">
            WINS: {payload[0].payload.wins}
          </p>
          <p className="text-xs font-mono font-bold text-danger">
            LOSSES: {payload[0].payload.losses}
          </p>
          <p className="text-xs font-mono font-bold text-white mt-1">
            PROFIT: ${payload[0].payload.profit.toLocaleString()}
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="w-full h-[300px]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
          <XAxis
            dataKey="month"
            stroke="#475569"
            style={{ fontSize: '10px', fontFamily: 'monospace' }}
            tick={{ fill: '#64748b' }}
            tickMargin={10}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            stroke="#475569"
            style={{ fontSize: '10px', fontFamily: 'monospace' }}
            tick={{ fill: '#64748b' }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: '#1e293b' }} />
          <Bar dataKey="wins" stackId="a" fill="#00FF88" name="Winning Trades" />
          <Bar dataKey="losses" stackId="a" fill="#ef4444" name="Losing Trades" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
