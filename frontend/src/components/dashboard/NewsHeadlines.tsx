'use client'

import { useEffect, useState } from 'react'
import { Newspaper } from 'lucide-react'
import { fetchApi } from '@/lib/api'

interface SentimentData {
  top_headlines: string[]
  aggregated_score: number
  source_count: number
}

const FALLBACK_HEADLINES = [
  'Oil prices hold gains on OPEC+ supply discipline',
  'EIA reports draw in US crude inventories',
  'Geopolitical tensions support Brent above $80',
  'Fed rate path remains key for commodity prices',
  'IEA raises 2025 oil demand growth forecast',
]

export default function NewsHeadlines() {
  const [data, setData] = useState<SentimentData | null>(null)

  useEffect(() => {
    fetchApi<SentimentData>('/sentiment?days=7')
      .then(setData)
      .catch(() => setData(null))
  }, [])

  const headlines = (data?.top_headlines?.length ? data.top_headlines : FALLBACK_HEADLINES).slice(0, 5)

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Newspaper className="text-accent-gold" size={22} />
          <h3 className="text-xl font-semibold">News & Headlines</h3>
        </div>
        {data?.source_count != null && data.source_count > 0 && (
          <span className="text-text-muted text-xs">{data.source_count} sources</span>
        )}
      </div>
      <ul className="space-y-2">
        {headlines.map((h, i) => (
          <li key={i} className="text-sm text-text-secondary border-l-2 border-accent-gold/50 pl-3 py-1">
            {h}
          </li>
        ))}
      </ul>
    </div>
  )
}
