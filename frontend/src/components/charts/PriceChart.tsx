'use client'

import { useEffect, useRef, useState } from 'react'
import { createChart, IChartApi, ISeriesApi, CandlestickData, Time } from 'lightweight-charts'

export default function PriceChart() {
    const chartContainerRef = useRef<HTMLDivElement>(null)
    const chartRef = useRef<IChartApi | null>(null)
    const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null)

    useEffect(() => {
        if (!chartContainerRef.current) return

        // Create chart
        const chart = createChart(chartContainerRef.current, {
            layout: {
                background: { color: '#1e293b' },
                textColor: '#cbd5e1',
            },
            grid: {
                vertLines: { color: '#334155' },
                horzLines: { color: '#334155' },
            },
            width: chartContainerRef.current.clientWidth,
            height: 400,
            timeScale: {
                timeVisible: true,
                secondsVisible: false,
            },
        })

        chartRef.current = chart

        // Create candlestick series
        const candlestickSeries = chart.addCandlestickSeries({
            upColor: '#10b981',
            downColor: '#ef4444',
            borderVisible: false,
            wickUpColor: '#10b981',
            wickDownColor: '#ef4444',
        })

        candlestickSeriesRef.current = candlestickSeries

        // Generate mock data
        const generateMockData = (): CandlestickData[] => {
            const data: CandlestickData[] = []
            const now = new Date()
            let basePrice = 75

            for (let i = 60; i >= 0; i--) {
                const date = new Date(now)
                date.setDate(date.getDate() - i)

                const change = (Math.random() - 0.5) * 2
                const open = basePrice
                const close = basePrice + change
                const high = Math.max(open, close) + Math.random()
                const low = Math.min(open, close) - Math.random()

                data.push({
                    time: (date.getTime() / 1000) as Time,
                    open,
                    high,
                    low,
                    close,
                })

                basePrice = close
            }

            return data
        }

        const mockData = generateMockData()
        candlestickSeries.setData(mockData)

        // Handle resize
        const handleResize = () => {
            if (chartContainerRef.current && chartRef.current) {
                chartRef.current.applyOptions({
                    width: chartContainerRef.current.clientWidth,
                })
            }
        }

        window.addEventListener('resize', handleResize)

        return () => {
            window.removeEventListener('resize', handleResize)
            chart.remove()
        }
    }, [])

    return (
        <div className="relative">
            <div ref={chartContainerRef} className="rounded-lg overflow-hidden" />

            {/* Time range selector */}
            <div className="flex items-center justify-center gap-2 mt-4">
                {['1D', '1W', '1M', '3M', '1Y', 'ALL'].map((range) => (
                    <button
                        key={range}
                        className="px-3 py-1 rounded bg-background-tertiary hover:bg-accent-gold/20 text-sm transition-colors"
                    >
                        {range}
                    </button>
                ))}
            </div>
        </div>
    )
}
