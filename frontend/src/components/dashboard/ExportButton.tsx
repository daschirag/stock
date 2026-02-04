'use client'

import { Download } from 'lucide-react'

interface Props {
  data?: { timestamp?: string; symbol?: string; open?: number; high?: number; low?: number; close?: number; volume?: number }[]
  filename?: string
  label?: string
}

export default function ExportButton({ data, filename = 'oil-prices', label = 'Export CSV' }: Props) {
  const exportCsv = () => {
    const rows = data && data.length > 0
      ? data
      : [
          { timestamp: new Date().toISOString(), symbol: 'WTI', open: 74.5, high: 76, low: 74, close: 75.42, volume: 250000 },
        ]
    const headers = ['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume']
    const csv = [
      headers.join(','),
      ...rows.map((r) => headers.map((h) => (r as Record<string, unknown>)[h] ?? '').join(',')),
    ].join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${filename}-${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <button
      type="button"
      onClick={exportCsv}
      className="btn-secondary flex items-center gap-2"
    >
      <Download size={18} />
      {label}
    </button>
  )
}
