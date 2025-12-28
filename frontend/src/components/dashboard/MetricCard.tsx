'use client'

import { ReactNode } from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'

interface MetricCardProps {
    title: string
    value: string
    change?: number
    subtitle?: string
    icon?: ReactNode
}

export default function MetricCard({ title, value, change, subtitle, icon }: MetricCardProps) {
    const hasChange = change !== undefined
    const isPriceUp = change && change >= 0

    return (
        <div className="metric-card animate-slide-up">
            <div className="flex items-start justify-between mb-4">
                <div>
                    <p className="text-text-muted text-sm mb-1">{title}</p>
                    <h3 className="text-3xl font-bold">{value}</h3>
                    {subtitle && (
                        <p className="text-text-muted text-sm mt-1">{subtitle}</p>
                    )}
                </div>
                {icon && (
                    <div className="p-3 bg-accent-gold/20 rounded-lg text-accent-gold">
                        {icon}
                    </div>
                )}
            </div>

            {hasChange && (
                <div className={`flex items-center gap-1 text-sm font-semibold ${isPriceUp ? 'price-up' : 'price-down'}`}>
                    {isPriceUp ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                    <span>{isPriceUp ? '+' : ''}{change.toFixed(2)}%</span>
                    <span className="text-text-muted ml-1">vs yesterday</span>
                </div>
            )}
        </div>
    )
}
