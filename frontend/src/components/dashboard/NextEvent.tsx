'use client'

import { useEffect, useState } from 'react'
import { Calendar, Clock } from 'lucide-react'
import { fetchApi } from '@/lib/api'

interface Event {
  date: string
  title: string
  impact: string
  description?: string
}

export default function NextEvent() {
  const [events, setEvents] = useState<Event[]>([])

  useEffect(() => {
    fetchApi<{ events: Event[] }>('/calendar')
      .then((d) => setEvents(d?.events?.slice(0, 3) ?? []))
      .catch(() => setEvents([]))
  }, [])

  const next = events[0]
  const impactColor = next ? (next.impact === 'high' ? 'text-error' : next.impact === 'medium' ? 'text-warning' : 'text-success') : ''

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-2">
        <Clock className="text-accent-gold" size={18} />
        <h3 className="text-lg font-semibold">Next key event</h3>
      </div>
      {next ? (
        <div className="p-3 rounded-lg bg-accent-gold/10 border border-accent-gold/20">
          <p className="font-medium text-sm">{next.title}</p>
          <div className="flex items-center gap-2 mt-1 text-text-muted text-xs">
            <Calendar size={12} />
            <span>{next.date}</span>
            <span className={impactColor}>· {next.impact} impact</span>
          </div>
          {next.description && (
            <p className="text-text-muted text-xs mt-1">{next.description}</p>
          )}
        </div>
      ) : (
        <p className="text-text-muted text-sm py-2">Loading events…</p>
      )}
    </div>
  )
}
