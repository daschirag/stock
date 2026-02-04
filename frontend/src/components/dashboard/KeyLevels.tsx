'use client'

import { useEffect, useState } from 'react'
import { Target, ArrowUp, ArrowDown } from 'lucide-react'
import { fetchApi } from '@/lib/api'

interface KeyLevelsData {
  support_1: number
  support_2: number
  resistance_1: number
  resistance_2: number
  pivot: number
}

interface Props {
  currentPrice?: number | null
}

export default function KeyLevels({ currentPrice }: Props) {
  const [levels, setLevels] = useState<KeyLevelsData | null>(null)

  useEffect(() => {
    fetchApi<KeyLevelsData>('/insights/key-levels?symbol=WTI')
      .then(setLevels)
      .catch(() => setLevels(null))
  }, [])

  if (!levels) return null

  const price = currentPrice ?? levels.pivot
  const distSupport = ((price - levels.support_1) / price * 100).toFixed(1)
  const distResistance = ((levels.resistance_1 - price) / price * 100).toFixed(1)

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <Target className="text-accent-gold" size={22} />
        <h3 className="text-xl font-semibold">Key Levels</h3>
      </div>
      <div className="space-y-3">
        <div className="flex justify-between items-center p-2 rounded bg-success/10">
          <span className="text-text-muted text-sm flex items-center gap-1">
            <ArrowUp size={14} /> Resistance 2
          </span>
          <span className="font-mono font-semibold">${levels.resistance_2.toFixed(2)}</span>
        </div>
        <div className="flex justify-between items-center p-2 rounded bg-success/5">
          <span className="text-text-muted text-sm flex items-center gap-1">
            <ArrowUp size={14} /> Resistance 1
          </span>
          <span className="font-mono font-semibold">${levels.resistance_1.toFixed(2)}</span>
        </div>
        <div className="flex justify-between items-center p-2 rounded bg-accent-gold/10 border border-accent-gold/30">
          <span className="text-accent-gold text-sm font-medium">Pivot</span>
          <span className="font-mono font-bold">${levels.pivot.toFixed(2)}</span>
        </div>
        <div className="flex justify-between items-center p-2 rounded bg-error/5">
          <span className="text-text-muted text-sm flex items-center gap-1">
            <ArrowDown size={14} /> Support 1
          </span>
          <span className="font-mono font-semibold">${levels.support_1.toFixed(2)}</span>
        </div>
        <div className="flex justify-between items-center p-2 rounded bg-error/10">
          <span className="text-text-muted text-sm flex items-center gap-1">
            <ArrowDown size={14} /> Support 2
          </span>
          <span className="font-mono font-semibold">${levels.support_2.toFixed(2)}</span>
        </div>
      </div>
      <p className="text-text-muted text-xs mt-3">
        Price {currentPrice != null ? `$${currentPrice.toFixed(2)}` : '—'} is {Number(distSupport) >= 0 ? `${distSupport}%` : `${distResistance}%`} from nearest key level.
      </p>
    </div>
  )
}
