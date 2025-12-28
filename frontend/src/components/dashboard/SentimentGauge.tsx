'use client'

interface SentimentGaugeProps {
    score: number // -1 to 1
}

export default function SentimentGauge({ score }: SentimentGaugeProps) {
    // Normalize score to 0-100 for display
    const normalizedScore = ((score + 1) / 2) * 100

    // Determine color based on score
    const getColor = () => {
        if (score > 0.3) return 'text-success'
        if (score < -0.3) return 'text-error'
        return 'text-warning'
    }

    const getLabel = () => {
        if (score > 0.3) return 'Bullish'
        if (score < -0.3) return 'Bearish'
        return 'Neutral'
    }

    return (
        <div className="flex flex-col items-center justify-center py-8">
            {/* Circular Gauge */}
            <div className="relative w-48 h-48 mb-4">
                <svg className="transform -rotate-90 w-48 h-48">
                    {/* Background circle */}
                    <circle
                        cx="96"
                        cy="96"
                        r="80"
                        stroke="currentColor"
                        strokeWidth="12"
                        fill="none"
                        className="text-background-tertiary"
                    />
                    {/* Progress circle */}
                    <circle
                        cx="96"
                        cy="96"
                        r="80"
                        stroke="currentColor"
                        strokeWidth="12"
                        fill="none"
                        strokeDasharray={`${2 * Math.PI * 80}`}
                        strokeDashoffset={`${2 * Math.PI * 80 * (1 - normalizedScore / 100)}`}
                        className={`${getColor()} transition-all duration-1000 ease-out`}
                        strokeLinecap="round"
                    />
                </svg>

                {/* Center text */}
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-4xl font-bold">{normalizedScore.toFixed(0)}%</span>
                    <span className={`text-sm ${getColor()}`}>{getLabel()}</span>
                </div>
            </div>

            {/* Legend */}
            <div className="flex items-center gap-6 text-sm">
                <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-error"></div>
                    <span className="text-text-muted">Bearish</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-warning"></div>
                    <span className="text-text-muted">Neutral</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-success"></div>
                    <span className="text-text-muted">Bullish</span>
                </div>
            </div>
        </div>
    )
}
