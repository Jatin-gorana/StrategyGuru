'use client'

import { ReactNode } from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'

interface MetricsCardProps {
  title: string
  value: string | number
  unit?: string
  icon?: ReactNode
  trend?: 'up' | 'down' | 'neutral'
  subtitle?: string
  className?: string
}

export default function MetricsCard({
  title,
  value,
  unit,
  icon,
  trend,
  subtitle,
  className = '',
}: MetricsCardProps) {
  const getTrendColor = () => {
    if (trend === 'up') return 'text-green-400'
    if (trend === 'down') return 'text-red-400'
    return 'text-slate-400'
  }

  const getTrendIcon = () => {
    if (trend === 'up') return <TrendingUp className="w-4 h-4" />
    if (trend === 'down') return <TrendingDown className="w-4 h-4" />
    return null
  }

  return (
    <div
      className={`p-6 bg-secondary border border-slate-800 rounded-xl hover:border-accent/50 transition-all flex flex-col justify-between ${className}`}
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-sm font-medium text-slate-400">{title}</p>
          {subtitle && (
            <p className="text-xs text-slate-500 mt-1">{subtitle}</p>
          )}
        </div>
        {icon && <div className="text-accent">{icon}</div>}
      </div>

      <div className="flex items-baseline gap-2">
        <span className="text-2xl font-bold text-white">
          {typeof value === 'number' ? value.toLocaleString() : value}
        </span>
        {unit && <span className="text-sm text-slate-400">{unit}</span>}
      </div>

      {trend && (
        <div className={`flex items-center gap-1 mt-3 ${getTrendColor()}`}>
          {getTrendIcon()}
          <span className="text-xs font-semibold">
            {trend === 'up' ? 'Positive' : trend === 'down' ? 'Negative' : 'Neutral'}
          </span>
        </div>
      )}
    </div>
  )
}
