'use client'

import { Activity } from 'lucide-react'

type Level = 'low' | 'medium' | 'high'

interface VolatilityBadgeProps {
  level: Level
  className?: string
}

const config: Record<Level, { label: string; color: string; bg: string }> = {
  low: { label: 'Low volatility', color: 'text-success', bg: 'bg-success/20' },
  medium: { label: 'Medium volatility', color: 'text-warning', bg: 'bg-warning/20' },
  high: { label: 'High volatility', color: 'text-error', bg: 'bg-error/20' },
}

export default function VolatilityBadge({ level, className = '' }: VolatilityBadgeProps) {
  const { label, color, bg } = config[level]
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${bg} ${color} ${className}`}>
      <Activity size={12} />
      {label}
    </span>
  )
}

export function getVolatilityFromChange(changePercent: number): Level {
  const abs = Math.abs(changePercent)
  if (abs < 1) return 'low'
  if (abs < 3) return 'medium'
  return 'high'
}
