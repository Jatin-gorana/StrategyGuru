'use client'

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { Trade } from '@/lib/api'

interface PerformanceChartProps {
  trades: Trade[]
}

export default function PerformanceChart({ trades }: PerformanceChartProps) {
  if (!trades || trades.length === 0) {
    return (
      <div className="w-full h-96 flex items-center justify-center bg-secondary/50 border border-slate-700 rounded-lg">
        <p className="text-slate-400">No trades to display</p>
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
        <div className="bg-primary border border-slate-700 rounded-lg p-3 shadow-lg">
          <p className="text-sm text-slate-400">{payload[0].payload.month}</p>
          <p className="text-sm font-semibold text-green-400">
            Wins: {payload[0].payload.wins}
          </p>
          <p className="text-sm font-semibold text-red-400">
            Losses: {payload[0].payload.losses}
          </p>
          <p className="text-sm font-semibold text-accent">
            Profit: ${payload[0].payload.profit.toLocaleString()}
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="w-full bg-secondary/50 border border-slate-700 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Monthly Performance</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis
            dataKey="month"
            stroke="#94a3b8"
            style={{ fontSize: '12px' }}
          />
          <YAxis
            stroke="#94a3b8"
            style={{ fontSize: '12px' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ paddingTop: '20px' }}
            contentStyle={{
              backgroundColor: '#1e293b',
              border: '1px solid #475569',
              borderRadius: '8px',
            }}
            labelStyle={{ color: '#cbd5e1' }}
          />
          <Bar dataKey="wins" stackId="a" fill="#10b981" name="Winning Trades" />
          <Bar dataKey="losses" stackId="a" fill="#ef4444" name="Losing Trades" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
