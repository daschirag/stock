'use client'

import { Target } from 'lucide-react'

interface OpportunityMeterProps {
  score: number  // -1 to 1, positive = favourable
  currentPrice?: number | null
  support?: number
  resistance?: number
}

export default function OpportunityMeter({ score, currentPrice, support = 73, resistance = 78 }: OpportunityMeterProps) {
  const segment = score > 0.2 ? 'favourable' : score < -0.2 ? 'cautious' : 'neutral'
  const percent = Math.round((score + 1) * 50) // 0-100
  const colors = {
    favourable: { bar: 'bg-success', text: 'text-success', label: 'Favourable' },
    neutral: { bar: 'bg-warning', text: 'text-warning', label: 'Neutral' },
    cautious: { bar: 'bg-error', text: 'text-error', label: 'Cautious' },
  }
  const { bar, text, label } = colors[segment]

  const nearSupport = currentPrice != null && support != null && currentPrice <= support * 1.02
  const nearResistance = currentPrice != null && resistance != null && currentPrice >= resistance * 0.98

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-3">
        <Target className="text-accent-gold" size={20} />
        <h3 className="text-lg font-semibold">Opportunity meter</h3>
      </div>
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-text-muted">Bias</span>
          <span className={`font-medium ${text}`}>{label}</span>
        </div>
        <div className="h-2 rounded-full bg-background-tertiary overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${bar}`}
            style={{ width: `${Math.max(5, Math.min(95, percent))}%` }}
          />
        </div>
        {(nearSupport || nearResistance) && currentPrice != null && (
          <p className="text-text-muted text-xs mt-2">
            {nearSupport && `Price near support $${support.toFixed(2)}`}
            {nearResistance && `Price near resistance $${resistance.toFixed(2)}`}
          </p>
        )}
      </div>
    </div>
  )
}
