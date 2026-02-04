'use client'

interface QuickStatsProps {
  currentPrice?: number | null
  high52w?: number
  low52w?: number
  sessionHigh?: number
  sessionLow?: number
}

export default function QuickStats({
  currentPrice = 75.42,
  high52w = 95.0,
  low52w = 67.0,
  sessionHigh = 76.2,
  sessionLow = 74.8,
}: QuickStatsProps) {
  const range52 = high52w - low52w
  const pctFromLow = range52 ? (((currentPrice ?? 0) - low52w) / range52) * 100 : 0

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-3">Quick stats</h3>
      <div className="grid grid-cols-2 gap-3 text-sm">
        <div>
          <p className="text-text-muted text-xs">52W High</p>
          <p className="font-mono font-semibold text-success">${high52w.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-text-muted text-xs">52W Low</p>
          <p className="font-mono font-semibold text-error">${low52w.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-text-muted text-xs">Session range</p>
          <p className="font-mono">
            ${sessionLow.toFixed(2)} – ${sessionHigh.toFixed(2)}
          </p>
        </div>
        <div>
          <p className="text-text-muted text-xs">Position in 52W range</p>
          <p className="font-mono font-medium">{pctFromLow.toFixed(0)}% from low</p>
        </div>
      </div>
      <div className="mt-2 h-1.5 rounded-full bg-background-tertiary overflow-hidden">
        <div
          className="h-full bg-accent-gold rounded-full transition-all duration-300"
          style={{ width: `${Math.max(0, Math.min(100, pctFromLow))}%` }}
        />
      </div>
    </div>
  )
}
