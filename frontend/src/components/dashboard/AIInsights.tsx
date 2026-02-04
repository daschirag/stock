'use client'

import { useEffect, useState } from 'react'
import { Sparkles, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { fetchApi } from '@/lib/api'

interface KeyLevels {
  support_1: number
  support_2: number
  resistance_1: number
  resistance_2: number
  pivot: number
}

interface AIInsightsData {
  summary: string
  key_drivers: string[]
  key_levels: KeyLevels
  technical_summary: string
  outlook: string
  confidence_score: number
}

export default function AIInsights() {
  const [data, setData] = useState<AIInsightsData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchApi<AIInsightsData>('/insights?symbol=WTI')
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="card animate-pulse">
        <div className="h-6 bg-background-tertiary rounded w-1/3 mb-4" />
        <div className="space-y-2">
          <div className="h-4 bg-background-tertiary rounded w-full" />
          <div className="h-4 bg-background-tertiary rounded w-4/5" />
        </div>
      </div>
    )
  }

  if (!data) return null

  const OutlookIcon = data.outlook === 'bullish' ? TrendingUp : data.outlook === 'bearish' ? TrendingDown : Minus
  const outlookColor = data.outlook === 'bullish' ? 'text-success' : data.outlook === 'bearish' ? 'text-error' : 'text-warning'

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="text-accent-gold" size={24} />
        <h3 className="text-xl font-semibold">AI Market Insights</h3>
      </div>
      <p className="text-text-secondary text-sm mb-4 leading-relaxed">{data.summary}</p>
      <div className="flex items-center gap-2 mb-3">
        <OutlookIcon className={outlookColor} size={20} />
        <span className={`font-medium capitalize ${outlookColor}`}>{data.outlook} outlook</span>
        <span className="text-text-muted text-sm">({(data.confidence_score * 100).toFixed(0)}% confidence)</span>
      </div>
      <p className="text-text-muted text-xs mb-4">{data.technical_summary}</p>
      <div>
        <p className="text-text-muted text-xs font-medium uppercase tracking-wider mb-2">Key drivers</p>
        <ul className="space-y-1">
          {data.key_drivers.slice(0, 5).map((d, i) => (
            <li key={i} className="text-sm text-text-secondary flex items-center gap-2">
              <span className="text-accent-gold">•</span> {d}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
