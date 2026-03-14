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
}

export default function DrawdownChart({
  equityCurve,
}: DrawdownChartProps) {
  if (!equityCurve || equityCurve.length === 0) {
    return (
      <div className="w-full h-[300px] flex items-center justify-center">
        <p className="text-slate-500 font-mono text-xs uppercase tracking-wider">No data available</p>
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
        <div className="bg-[#0B0E14] border border-slate-800 rounded p-3 shadow-lg">
          <p className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">{payload[0].payload.date}</p>
          <p className="text-xs font-mono font-bold text-danger mt-1">
            DRAWDOWN: {payload[0].value.toFixed(2)}%
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="w-full h-[300px]">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={sampledData}>
          <defs>
            <linearGradient id="colorDrawdown" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#ef4444" stopOpacity={0.1} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
          <XAxis
            dataKey="date"
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
            tickFormatter={(value) => `${value}%`}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#334155', strokeWidth: 1, strokeDasharray: '3 3' }} />
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
