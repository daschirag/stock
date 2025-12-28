import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
    title: 'Crude Oil Price Prediction',
    description: 'AI-powered crude oil price forecasting with hybrid ML models',
    keywords: ['crude oil', 'price prediction', 'machine learning', 'forecasting'],
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en" className="dark">
            <body className={inter.className}>
                <div className="min-h-screen bg-background-primary">
                    {children}
                </div>
            </body>
        </html>
    )
}
