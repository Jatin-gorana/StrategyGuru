'use client'

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { EquityCurvePoint } from '@/lib/api'

interface DrawdownChartProps {
  equityCurve: EquityCurvePoint[]
  initialCapital: number
}

export default function DrawdownChart({
  equityCurve,
  initialCapital,
}: DrawdownChartProps) {
  if (!equityCurve || equityCurve.length === 0) {
    return (
      <div className="w-full h-96 flex items-center justify-center bg-secondary/50 border border-slate-700 rounded-lg">
        <p className="text-slate-400">No data available</p>
      </div>
    )
  }

  // Calculate drawdown
  const chartData = equityCurve.map((point) => {
    const date = new Date(point.date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    })

    // Find the peak up to this point
    const peakEquity = Math.max(
      ...equityCurve
        .slice(0, equityCurve.indexOf(point) + 1)
        .map((p) => p.equity)
    )

    // Calculate drawdown percentage
    const drawdown = ((point.equity - peakEquity) / peakEquity) * 100

    return {
      date,
      drawdown: Math.round(drawdown * 100) / 100,
      timestamp: new Date(point.date).getTime(),
    }
  })

  // Sample data if too many points
  const sampledData =
    chartData.length > 100
      ? chartData.filter((_, i) => i % Math.ceil(chartData.length / 100) === 0)
      : chartData

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-primary border border-slate-700 rounded-lg p-3 shadow-lg">
          <p className="text-sm text-slate-400">{payload[0].payload.date}</p>
          <p className="text-sm font-semibold text-red-400">
            Drawdown: {payload[0].value.toFixed(2)}%
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="w-full bg-secondary/50 border border-slate-700 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Drawdown Analysis</h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={sampledData}>
          <defs>
            <linearGradient id="colorDrawdown" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#ef4444" stopOpacity={0.1} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis
            dataKey="date"
            stroke="#94a3b8"
            style={{ fontSize: '12px' }}
          />
          <YAxis
            stroke="#94a3b8"
            style={{ fontSize: '12px' }}
            tickFormatter={(value) => `${value}%`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="drawdown"
            stroke="#ef4444"
            fillOpacity={1}
            fill="url(#colorDrawdown)"
            isAnimationActive={true}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
