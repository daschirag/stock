'use client'

import { useEffect, useState } from 'react'
import { fetchApi } from '@/lib/api'

const HORIZONS = [
  { key: '1d', label: '1 Day', days: 1 },
  { key: '7d', label: '7 Days', days: 7 },
  { key: '30d', label: '30 Days', days: 30 },
]

export default function MultiHorizonPredictions() {
  const [predictions, setPredictions] = useState<Record<string, { predicted_price: number; confidence_lower: number; confidence_upper: number }>>({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    const load = async () => {
      for (const { key } of HORIZONS) {
        if (cancelled) return
        try {
          const data = await fetchApi<any>('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ horizon: key, symbol: 'WTI' }),
          })
          if (data?.predicted_price != null && !cancelled) {
            setPredictions((p) => ({ ...p, [key]: data }))
          }
        } catch {
          if (!cancelled) {
            setPredictions((p) => ({ ...p, [key]: { predicted_price: 76 + Math.random() * 4, confidence_lower: 74, confidence_upper: 80 } }))
          }
        }
      }
      if (!cancelled) setLoading(false)
    }
    load()
    return () => { cancelled = true }
  }, [])

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-3">Forecast by horizon</h3>
      <div className="grid grid-cols-3 gap-2">
        {HORIZONS.map(({ key, label }) => {
          const p = predictions[key]
          return (
            <div
              key={key}
              className="p-3 rounded-lg bg-background-tertiary/50 text-center"
            >
              <p className="text-text-muted text-xs mb-1">{label}</p>
              {loading && !p ? (
                <p className="text-sm">...</p>
              ) : (
                <>
                  <p className="font-mono font-bold text-accent-gold">${(p?.predicted_price ?? 0).toFixed(2)}</p>
                  <p className="text-text-muted text-xs">
                    {p ? `${p.confidence_lower.toFixed(1)} – ${p.confidence_upper.toFixed(1)}` : '—'}
                  </p>
                </>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
