'use client'

import { useMemo } from 'react'

interface SparklineProps {
  data: number[]
  width?: number
  height?: number
  strokeColor?: string
  fillColor?: string
  className?: string
  trend?: 'up' | 'down' | 'flat'
}

export default function Sparkline({
  data,
  width = 80,
  height = 24,
  strokeColor,
  fillColor,
  className = '',
  trend,
}: SparklineProps) {
  const { path, areaPath } = useMemo(() => {
    if (!data.length) return { path: '', areaPath: '' }
    const min = Math.min(...data)
    const max = Math.max(...data)
    const range = max - min || 1
    const padding = 2
    const w = width - padding * 2
    const h = height - padding * 2
    const step = data.length > 1 ? w / (data.length - 1) : 0
    const points = data.map((v, i) => {
      const x = padding + i * step
      const y = padding + h - ((v - min) / range) * h
      return `${x},${y}`
    })
    const path = `M ${points.join(' L ')}`
    const areaPath = `${path} L ${padding + w},${padding + h} L ${padding},${padding + h} Z`
    return { path, areaPath }
  }, [data, width, height])

  const stroke = strokeColor ?? (trend === 'up' ? '#10b981' : trend === 'down' ? '#ef4444' : '#f59e0b')
  const fill = fillColor ?? (trend === 'up' ? 'rgba(16,185,129,0.2)' : trend === 'down' ? 'rgba(239,68,68,0.2)' : 'rgba(245,158,11,0.2)')

  if (!data.length) return null

  return (
    <svg width={width} height={height} className={className} viewBox={`0 0 ${width} ${height}`}>
      <path d={areaPath} fill={fill} />
      <path d={path} fill="none" stroke={stroke} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}
