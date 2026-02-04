'use client'

import { Activity, BarChart3 } from 'lucide-react'

const MOCK_INDICATORS = [
  { name: 'RSI (14)', value: 58, status: 'neutral', desc: 'No overbought/oversold' },
  { name: 'MACD', value: 0.42, status: 'bullish', desc: 'Positive momentum' },
  { name: 'Bollinger', value: 'Mid', status: 'neutral', desc: 'Price near middle band' },
  { name: 'Trend', value: 'Short-term up', status: 'bullish', desc: 'Above 20-day MA' },
]

export default function TechnicalSummary() {
  const statusColor = (s: string) =>
    s === 'bullish' ? 'text-success' : s === 'bearish' ? 'text-error' : 'text-warning'

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <BarChart3 className="text-accent-gold" size={22} />
        <h3 className="text-xl font-semibold">Technical Summary</h3>
      </div>
      <ul className="space-y-3">
        {MOCK_INDICATORS.map((ind, i) => (
          <li key={i} className="flex items-center justify-between p-2 rounded bg-background-tertiary/50">
            <div className="flex items-center gap-2">
              <Activity size={16} className="text-text-muted" />
              <span className="text-sm font-medium">{ind.name}</span>
            </div>
            <div className="text-right">
              <span className={`text-sm font-semibold ${statusColor(ind.status)}`}>{ind.value}</span>
              <p className="text-xs text-text-muted">{ind.desc}</p>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
