'use client'

import { useState } from 'react'
import { BookOpen, ChevronDown, ChevronUp } from 'lucide-react'

const TERMS = [
  {
    term: 'WTI (West Texas Intermediate)',
    definition: 'US benchmark crude oil. Light, sweet crude delivered at Cushing, Oklahoma. Used as the main reference for North American oil pricing.',
  },
  {
    term: 'Brent Crude',
    definition: 'International benchmark. Blend from North Sea fields. Used to price two-thirds of global crude. More sensitive to global supply shocks.',
  },
  {
    term: 'Support & Resistance',
    definition: 'Support is a price level where buying tends to emerge; resistance is where selling tends to cap rallies. Key levels help plan entries and exits.',
  },
  {
    term: 'OPEC+',
    definition: 'Organization of the Petroleum Exporting Countries plus allies (e.g. Russia). Decisions on production quotas influence global supply and prices.',
  },
  {
    term: 'EIA Inventories',
    definition: 'US Energy Information Administration weekly report on crude oil, gasoline, and distillate stockpiles. Draws often support prices, builds can pressure them.',
  },
  {
    term: 'VMD (Variational Mode Decomposition)',
    definition: 'Signal processing method used in our models to split price series into frequency bands (high/mid/low) for more accurate forecasting.',
  },
]

export default function Glossary() {
  const [openId, setOpenId] = useState<number | null>(0)

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <BookOpen className="text-accent-gold" size={22} />
        <h3 className="text-xl font-semibold">Glossary & Learn</h3>
      </div>
      <p className="text-text-muted text-xs mb-3">Terms every oil trader should know</p>
      <div className="space-y-1">
        {TERMS.map((item, i) => (
          <div
            key={i}
            className="rounded-lg bg-background-tertiary/50 overflow-hidden"
          >
            <button
              type="button"
              onClick={() => setOpenId(openId === i ? null : i)}
              className="w-full flex items-center justify-between p-3 text-left hover:bg-background-tertiary/50 transition-colors"
            >
              <span className="font-medium text-sm">{item.term}</span>
              {openId === i ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
            </button>
            {openId === i && (
              <div className="px-3 pb-3 text-sm text-text-secondary border-t border-gray-700/50 pt-2">
                {item.definition}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
