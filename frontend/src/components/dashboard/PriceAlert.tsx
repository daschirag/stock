'use client'

import { useState, useEffect } from 'react'
import { Bell, BellOff } from 'lucide-react'

const STORAGE_KEY = 'crude-oil-price-alerts'

export interface PriceAlertItem {
  id: string
  symbol: string
  targetPrice: number
  direction: 'above' | 'below'
  createdAt: number
}

export default function PriceAlert() {
  const [alerts, setAlerts] = useState<PriceAlertItem[]>([])
  const [showForm, setShowForm] = useState(false)
  const [targetPrice, setTargetPrice] = useState('')
  const [direction, setDirection] = useState<'above' | 'below'>('above')

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (raw) setAlerts(JSON.parse(raw))
    } catch {
      setAlerts([])
    }
  }, [])

  const saveAlerts = (next: PriceAlertItem[]) => {
    setAlerts(next)
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
    } catch {
      //
    }
  }

  const addAlert = () => {
    const p = parseFloat(targetPrice)
    if (Number.isNaN(p) || p <= 0) return
    const newAlert: PriceAlertItem = {
      id: `alert-${Date.now()}`,
      symbol: 'WTI',
      targetPrice: p,
      direction,
      createdAt: Date.now(),
    }
    saveAlerts([...alerts, newAlert])
    setTargetPrice('')
    setShowForm(false)
  }

  const removeAlert = (id: string) => {
    saveAlerts(alerts.filter((a) => a.id !== id))
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Bell className="text-accent-gold" size={20} />
          <h3 className="text-lg font-semibold">Price alerts</h3>
        </div>
        {alerts.length > 0 && (
          <span className="text-text-muted text-xs">{alerts.length} set</span>
        )}
      </div>
      {!showForm ? (
        <button
          type="button"
          onClick={() => setShowForm(true)}
          className="w-full py-2 rounded-lg border border-dashed border-gray-600 text-text-muted text-sm hover:border-accent-gold/50 hover:text-accent-gold transition-colors"
        >
          + Set price alert
        </button>
      ) : (
        <div className="space-y-2">
          <div className="flex gap-2">
            <input
              type="number"
              step="0.01"
              placeholder="Price (e.g. 80)"
              value={targetPrice}
              onChange={(e) => setTargetPrice(e.target.value)}
              className="input-field flex-1 text-sm py-1.5"
            />
            <select
              value={direction}
              onChange={(e) => setDirection(e.target.value as 'above' | 'below')}
              className="input-field text-sm py-1.5 w-24"
            >
              <option value="above">Above</option>
              <option value="below">Below</option>
            </select>
          </div>
          <div className="flex gap-2">
            <button type="button" onClick={addAlert} className="btn-primary text-sm py-1.5 px-3 flex-1">
              Add
            </button>
            <button type="button" onClick={() => setShowForm(false)} className="btn-secondary text-sm py-1.5 px-3">
              Cancel
            </button>
          </div>
        </div>
      )}
      {alerts.length > 0 && (
        <ul className="mt-3 space-y-1">
          {alerts.slice(0, 5).map((a) => (
            <li key={a.id} className="flex items-center justify-between text-sm py-1.5 px-2 rounded bg-background-tertiary/50">
              <span>WTI {a.direction === 'above' ? '≥' : '≤'} ${a.targetPrice.toFixed(2)}</span>
              <button type="button" onClick={() => removeAlert(a.id)} className="p-0.5 text-text-muted hover:text-error">
                <BellOff size={14} />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
