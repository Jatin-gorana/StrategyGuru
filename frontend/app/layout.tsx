import type { Metadata } from 'next'
import './globals.css'
import GlobalAIAssistant from '@/components/GlobalAIAssistant'

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
      <body className="bg-primary text-white font-sans antialiased">
        <div className="min-h-screen">
          {children}
        </div>
        <GlobalAIAssistant />
      </body>
    </html>
  )
}
