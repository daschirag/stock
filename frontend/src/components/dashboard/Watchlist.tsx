'use client'

import { useState, useEffect } from 'react'
import { Star, TrendingUp } from 'lucide-react'
import { fetchApi } from '@/lib/api'

const SYMBOLS = [
  { id: 'WTI', name: 'WTI Crude', ticker: 'CL' },
  { id: 'BRENT', name: 'Brent Crude', ticker: 'BZ' },
]

interface LatestPrice {
  symbol?: string
  close?: number
  open?: number
}

export default function Watchlist() {
  const [activeSymbol, setActiveSymbol] = useState('WTI')
  const [prices, setPrices] = useState<Record<string, LatestPrice>>({})

  useEffect(() => {
    SYMBOLS.forEach(({ id }) => {
      fetchApi<LatestPrice>(`/data/latest?symbol=${id}`)
        .then((data) => setPrices((p) => ({ ...p, [id]: data })))
        .catch(() => setPrices((p) => ({ ...p, [id]: {} })))
    })
  }, [])

  const changePct = (sym: string) => {
    const d = prices[sym]
    if (!d?.close || !d?.open) return null
    return ((d.close - d.open) / d.open) * 100
  }

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <Star className="text-accent-gold" size={22} />
        <h3 className="text-xl font-semibold">Watchlist</h3>
      </div>
      <div className="flex flex-col gap-2">
        {SYMBOLS.map(({ id, name, ticker }) => {
          const close = prices[id]?.close
          const ch = changePct(id)
          const isActive = activeSymbol === id
          return (
            <button
              key={id}
              type="button"
              onClick={() => setActiveSymbol(id)}
              className={`flex items-center justify-between p-3 rounded-lg text-left transition-colors ${
                isActive ? 'bg-accent-gold/20 border border-accent-gold/40' : 'bg-background-tertiary/50 hover:bg-background-tertiary'
              }`}
            >
              <div>
                <p className="font-medium">{name}</p>
                <p className="text-text-muted text-xs">{ticker}</p>
              </div>
              <div className="text-right">
                <p className="font-mono font-semibold">{close != null ? `$${close.toFixed(2)}` : '—'}</p>
                {ch != null && (
                  <p className={`text-xs flex items-center justify-end gap-0.5 ${ch >= 0 ? 'text-success' : 'text-error'}`}>
                    <TrendingUp size={12} className={ch < 0 ? 'rotate-180' : ''} />
                    {ch >= 0 ? '+' : ''}{ch.toFixed(2)}%
                  </p>
                )}
              </div>
            </button>
          )
        })}
      </div>
      <p className="text-text-muted text-xs mt-2">Click to switch symbol for charts</p>
    </div>
  )
}
