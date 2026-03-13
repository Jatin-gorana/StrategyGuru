import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Trading Strategy Backtester',
  description: 'Backtest trading strategies with historical stock data',
  icons: {
    icon: '/favicon.ico',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gradient-to-br from-primary via-secondary to-primary">
        <div className="min-h-screen">
          {children}
        </div>
      </body>
    </html>
  )
}
