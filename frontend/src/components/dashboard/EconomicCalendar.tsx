'use client'

import { useEffect, useState } from 'react'
import { Calendar } from 'lucide-react'
import { fetchApi } from '@/lib/api'

interface Event {
  date: string
  title: string
  impact: string
  description?: string
}

interface CalendarData {
  events: Event[]
}

export default function EconomicCalendar() {
  const [data, setData] = useState<CalendarData | null>(null)

  useEffect(() => {
    fetchApi<CalendarData>('/calendar')
      .then(setData)
      .catch(() => setData(null))
  }, [])

  const events = data?.events ?? []

  const impactColor = (impact: string) => {
    if (impact === 'high') return 'bg-error/20 text-error'
    if (impact === 'medium') return 'bg-warning/20 text-warning'
    return 'bg-success/20 text-success'
  }

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <Calendar className="text-accent-gold" size={22} />
        <h3 className="text-xl font-semibold">Economic Calendar</h3>
      </div>
      <p className="text-text-muted text-xs mb-3">Events that typically move oil markets</p>
      <ul className="space-y-2">
        {events.map((e, i) => (
          <li key={i} className="flex items-start gap-2 p-2 rounded bg-background-tertiary/50">
            <span className="text-accent-gold text-xs font-mono shrink-0">{e.date}</span>
            <div className="min-w-0">
              <p className="text-sm font-medium text-text-primary">{e.title}</p>
              {e.description && (
                <p className="text-xs text-text-muted">{e.description}</p>
              )}
            </div>
            <span className={`shrink-0 text-xs px-1.5 py-0.5 rounded ${impactColor(e.impact)}`}>
              {e.impact}
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}
