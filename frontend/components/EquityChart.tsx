'use client'

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
} from 'recharts'
import { EquityCurvePoint } from '@/lib/api'
import { useState, useMemo } from 'react'

interface EquityChartProps {
  data: EquityCurvePoint[]
  initialCapital: number
}

export default function EquityChart({
  data,
  initialCapital,
}: EquityChartProps) {
  const [hoveredDate, setHoveredDate] = useState<string | null>(null)

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

  // Calculate statistics
  const stats = useMemo(() => {
    const equities = chartData.map((d) => d.equity)
    const minEquity = Math.min(...equities)
    const maxEquity = Math.max(...equities)
    const finalEquity = equities[equities.length - 1]
    const totalReturn = ((finalEquity - initialCapital) / initialCapital) * 100

    return { minEquity, maxEquity, finalEquity, totalReturn }
  }, [chartData, initialCapital])

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      const equity = payload[0].value
      const returnPct = ((equity - initialCapital) / initialCapital) * 100

      return (
        <div className="bg-primary border border-slate-700 rounded-lg p-4 shadow-lg">
          <p className="text-sm text-slate-400 font-semibold">{data.fullDate}</p>
          <p className="text-sm font-semibold text-accent mt-1">
            Portfolio: ${equity.toLocaleString('en-US', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </p>
          <p
            className={`text-sm font-semibold mt-1 ${
              returnPct >= 0 ? 'text-green-400' : 'text-red-400'
            }`}
          >
            Return: {returnPct >= 0 ? '+' : ''}{returnPct.toFixed(2)}%
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="w-full bg-secondary/50 border border-slate-700 rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Equity Curve</h3>
        <div className="flex gap-6 text-sm">
          <div>
            <p className="text-slate-400">Min</p>
            <p className="text-white font-semibold">
              ${stats.minEquity.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </p>
          </div>
          <div>
            <p className="text-slate-400">Max</p>
            <p className="text-white font-semibold">
              ${stats.maxEquity.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </p>
          </div>
          <div>
            <p className="text-slate-400">Final</p>
            <p
              className={`font-semibold ${
                stats.totalReturn >= 0 ? 'text-green-400' : 'text-red-400'
              }`}
            >
              ${stats.finalEquity.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </p>
          </div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart
          data={chartData}
          onMouseMove={(state: any) => {
            if (state.isTooltipActive && state.activeTooltipIndex !== undefined) {
              setHoveredDate(chartData[state.activeTooltipIndex]?.date || null)
            }
          }}
          onMouseLeave={() => setHoveredDate(null)}
        >
          <defs>
            <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis
            dataKey="date"
            stroke="#94a3b8"
            style={{ fontSize: '12px' }}
            tick={{ fill: '#cbd5e1' }}
          />
          <YAxis
            stroke="#94a3b8"
            style={{ fontSize: '12px' }}
            tick={{ fill: '#cbd5e1' }}
            tickFormatter={(value) =>
              `$${(value / 1000).toFixed(0)}k`
            }
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
          <ReferenceLine
            y={initialCapital}
            stroke="#64748b"
            strokeDasharray="5 5"
            label={{
              value: 'Initial Capital',
              position: 'right',
              fill: '#94a3b8',
              fontSize: 12,
            }}
          />
          <Line
            type="monotone"
            dataKey="equity"
            stroke="#3b82f6"
            dot={false}
            strokeWidth={2.5}
            isAnimationActive={true}
            name="Portfolio Value"
            fill="url(#colorEquity)"
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Stats Footer */}
      <div className="mt-4 pt-4 border-t border-slate-700 grid grid-cols-3 gap-4">
        <div>
          <p className="text-xs text-slate-400 uppercase">Total Return</p>
          <p
            className={`text-lg font-bold ${
              stats.totalReturn >= 0 ? 'text-green-400' : 'text-red-400'
            }`}
          >
            {stats.totalReturn >= 0 ? '+' : ''}{stats.totalReturn.toFixed(2)}%
          </p>
        </div>
        <div>
          <p className="text-xs text-slate-400 uppercase">Days Traded</p>
          <p className="text-lg font-bold text-white">{chartData.length}</p>
        </div>
        <div>
          <p className="text-xs text-slate-400 uppercase">Volatility</p>
          <p className="text-lg font-bold text-white">
            {(
              (stats.maxEquity - stats.minEquity) /
              initialCapital *
              100
            ).toFixed(2)}%
          </p>
        </div>
      </div>
    </div>
  )
}
