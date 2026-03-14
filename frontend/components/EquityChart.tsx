'use client'

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { EquityCurvePoint } from '@/lib/api'
import { useMemo } from 'react'

interface EquityChartProps {
  data: EquityCurvePoint[]
}

export default function EquityChart({
  data,
}: EquityChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="w-full h-96 flex items-center justify-center bg-secondary/50 border border-slate-700 rounded-lg">
        <p className="text-slate-400">No data available</p>
      </div>
    )
  }

  // Process and sample data
  const chartData = useMemo(() => {
    const processed = data.map((point) => {
      const date = new Date(point.date)
      return {
        date: date.toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
        }),
        fullDate: date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
        }),
        equity: Math.round(point.equity * 100) / 100,
        timestamp: date.getTime(),
      }
    })

    // Sample every nth point to avoid overcrowding
    if (processed.length > 100) {
      const sampleRate = Math.ceil(processed.length / 100)
      return processed.filter((_, i) => i % sampleRate === 0 || i === processed.length - 1)
    }
    return processed
  }, [data])

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      const equity = payload[0].value

      return (
        <div className="bg-primary border border-slate-700 rounded-lg p-4 shadow-lg">
          <p className="text-sm text-slate-400 font-semibold">{data.fullDate}</p>
          <p className="text-sm font-semibold text-accent mt-1">
            Portfolio: ${equity.toLocaleString('en-US', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="w-full h-[400px]">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
        >
          <defs>
            <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#00FF88" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#00FF88" stopOpacity={0} />
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
            tickFormatter={(value) =>
              `$${(value / 1000).toFixed(0)}k`
            }
            orientation="right"
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#334155', strokeWidth: 1, strokeDasharray: '3 3' }} />
          <Line
            type="monotone"
            dataKey="equity"
            stroke="#00FF88"
            dot={false}
            strokeWidth={2}
            isAnimationActive={true}
            name="Strategy"
            fill="url(#colorEquity)"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
