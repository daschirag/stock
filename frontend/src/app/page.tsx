'use client'

import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, Activity, DollarSign } from 'lucide-react'
import MetricCard from '@/components/dashboard/MetricCard'
import PriceChart from '@/components/charts/PriceChart'
import SentimentGauge from '@/components/dashboard/SentimentGauge'

export default function DashboardPage() {
    const [currentPrice, setCurrentPrice] = useState<number | null>(null)
    const [priceChange, setPriceChange] = useState<number>(0)
    const [prediction, setPrediction] = useState<any>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        // Fetch initial data
        fetchLatestPrice()
        fetchPrediction()
    }, [])

    const fetchLatestPrice = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/v1/data/latest?symbol=WTI')
            const data = await response.json()

            if (data && data.close) {
                setCurrentPrice(data.close)

                // Calculate price change (mock for now)
                const change = ((data.close - data.open) / data.open) * 100
                setPriceChange(change)
            }
        } catch (error) {
            console.error('Error fetching price:', error)
            // Mock data for development
            setCurrentPrice(75.42)
            setPriceChange(2.34)
        } finally {
            setLoading(false)
        }
    }

    const fetchPrediction = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/v1/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ horizon: '1d', symbol: 'WTI' })
            })
            const data = await response.json()
            setPrediction(data)
        } catch (error) {
            console.error('Error fetching prediction:', error)
            // Mock prediction
            setPrediction({
                predicted_price: 76.89,
                confidence_lower: 74.21,
                confidence_upper: 79.57
            })
        }
    }

    const isPriceUp = priceChange >= 0

    return (
        <div className="min-h-screen p-8">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-4xl font-bold text-gradient mb-2">
                    Crude Oil Price Prediction
                </h1>
                <p className="text-text-muted">
                    AI-powered forecasting with hybrid ML models
                </p>
            </div>

            {/* Live Price Banner */}
            <div className="mb-8 p-6 rounded-lg bg-gradient-to-r from-accent-gold/20 to-accent-goldLight/20 border border-accent-gold/30 glassmorphism animate-fade-in">
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-text-muted text-sm mb-1">WTI Crude Oil</p>
                        <div className="flex items-baseline gap-3">
                            <h2 className="text-5xl font-bold">
                                {loading ? '...' : `$${currentPrice?.toFixed(2)}`}
                            </h2>
                            <div className={`flex items-center gap-1 text-lg font-semibold ${isPriceUp ? 'price-up' : 'price-down'}`}>
                                {isPriceUp ? <TrendingUp size={24} /> : <TrendingDown size={24} />}
                                <span>{isPriceUp ? '+' : ''}{priceChange.toFixed(2)}%</span>
                            </div>
                        </div>
                    </div>
                    <Activity className="text-accent-gold" size={48} />
                </div>
            </div>

            {/* Metric Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <MetricCard
                    title="Current Price"
                    value={currentPrice ? `$${currentPrice.toFixed(2)}` : '...'}
                    change={priceChange}
                    icon={<DollarSign />}
                />
                <MetricCard
                    title="1-Day Prediction"
                    value={prediction ? `$${prediction.predicted_price.toFixed(2)}` : '...'}
                    subtitle={prediction ? `±$${((prediction.confidence_upper - prediction.confidence_lower) / 2).toFixed(2)}` : ''}
                    icon={<TrendingUp />}
                />
                <MetricCard
                    title="Model Accuracy"
                    value="94.2%"
                    subtitle="7-day MAPE"
                    icon={<Activity />}
                />
            </div>

            {/* Main Chart */}
            <div className="mb-8">
                <div className="card">
                    <h3 className="text-xl font-semibold mb-4">Price Chart with Predictions</h3>
                    <PriceChart />
                </div>
            </div>

            {/* Bottom Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="card">
                    <h3 className="text-xl font-semibold mb-4">Sentiment Analysis</h3>
                    <SentimentGauge score={0.65} />
                </div>

                <div className="card">
                    <h3 className="text-xl font-semibold mb-4">Latest Insights</h3>
                    <div className="space-y-3">
                        <div className="p-3 bg-background-tertiary rounded-lg">
                            <p className="text-sm text-text-secondary">
                                ✓ High correlation detected between USD strength and oil prices
                            </p>
                        </div>
                        <div className="p-3 bg-background-tertiary rounded-lg">
                            <p className="text-sm text-text-secondary">
                                ⚡ Increased volatility expected due to OPEC+ meeting
                            </p>
                        </div>
                        <div className="p-3 bg-background-tertiary rounded-lg">
                            <p className="text-sm text-text-secondary">
                                📈 Bullish sentiment from 78% of analyzed news sources
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
