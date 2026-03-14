'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import StrategyInput from '@/components/StrategyInput'
import ProfileCard from '@/components/ProfileCard'
import api, { StrategyExample } from '@/lib/api'
import { AlertCircle, CheckCircle } from 'lucide-react'

export default function Home() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [examples, setExamples] = useState<StrategyExample[]>([])
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    loadExamples()
  }, [])

  const loadExamples = async () => {
    try {
      const data = await api.getExamples()
      setExamples(data.examples)
    } catch (err) {
      console.error('Failed to load examples:', err)
    }
  }

  const handleSubmit = async (data: {
    strategy_text: string
    stock_symbol: string
    start_date: string
    end_date: string
    initial_capital: number
  }) => {
    setIsLoading(true)
    setError('')
    setSuccess('')

    try {
      const response = await api.runBacktest(data)
      
      if (response.success) {
        setSuccess('Backtest completed successfully!')
        
        // Store results in sessionStorage for the dashboard page
        sessionStorage.setItem('backtest_results', JSON.stringify(response))
        sessionStorage.setItem('backtest_params', JSON.stringify(data))
        
        // Redirect to dashboard page
        setTimeout(() => {
          router.push('/dashboard')
        }, 500)
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to run backtest'
      setError(errorMessage)
      console.error('Backtest error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-primary">
      {/* Header */}
      <header className="border-b border-slate-800 bg-primary sticky top-0 z-50">
        <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <div className="flex items-center gap-2 hidden sm:flex">
              <div className="w-6 h-6 bg-accent rounded-sm transform rotate-45 flex items-center justify-center">
                 <div className="w-3 h-3 bg-primary transform -rotate-45" />
              </div>
              <h1 className="text-xl font-bold text-white tracking-wide">
                Agentic Quant
              </h1>
            </div>
            <nav className="flex items-center gap-6 h-16">
              <Link href="/" className="text-accent border-b-2 border-accent h-full flex items-center text-sm font-semibold tracking-wide">Terminal</Link>
              <Link href="/dashboard" className="text-slate-400 hover:text-white transition-colors h-full flex items-center text-sm font-semibold tracking-wide">Backtests</Link>
              <Link href="/dashboard" className="text-slate-400 hover:text-white transition-colors h-full flex items-center text-sm font-semibold tracking-wide hidden md:flex">Portfolio</Link>
            </nav>
          </div>
          <div className="flex items-center gap-6">
            <div className="hidden md:flex items-center gap-2 bg-green-500/10 px-3 py-1.5 rounded-full border border-green-500/20">
              <div className="w-2 h-2 rounded-full bg-accent animate-pulse-glow"></div>
              <span className="text-[10px] font-bold text-accent tracking-widest uppercase">Live Feed</span>
            </div>
            <ProfileCard />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-[1600px] mx-auto w-full flex flex-col lg:flex-row h-[calc(100vh-64px)] overflow-hidden">
        
        {/* Left Sidebar */}
        {/* The AI Quant Assistant Sidebar has been extracted to a global dynamic component */}

        {/* Center Editor */}
        <div className="flex-1 flex flex-col bg-[#0B0E14] relative h-full overflow-hidden">
          
          {/* Editor Header */}
          <div className="h-14 border-b border-slate-800 flex items-center px-6 justify-between shrink-0 bg-[#0B0E14]">
             <div className="flex items-center gap-4">
               <div className="flex items-center gap-2 border-r border-slate-800 pr-4">
                 <span className="text-sm text-slate-400 font-mono">strategy_v2_final.py</span>
                 <span className="w-2 h-2 rounded-full bg-warning flex-shrink-0"></span>
                 <span className="text-[10px] text-slate-500 tracking-wider font-semibold">DRAFT</span>
               </div>
             </div>
          </div>

          <div className="flex-1 overflow-y-auto px-6 py-8 relative custom-scrollbar">
            {/* Success Message */}
            {success && (
              <div className="mb-6 flex items-center gap-3 p-4 bg-green-500/10 border border-green-500/30 rounded-lg animate-fade-in max-w-4xl mx-auto">
                <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                <p className="text-sm text-green-400">{success}</p>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="mb-6 flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg animate-fade-in max-w-4xl mx-auto">
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                <p className="text-sm text-red-400">{error}</p>
              </div>
            )}
            
            <StrategyInput
              onSubmit={handleSubmit}
              isLoading={isLoading}
              examples={examples}
            />
            
          </div>
          
          {/* Status Bar */}
          <div className="h-10 border-t border-slate-800 bg-[#0B0E14] px-6 flex items-center justify-between shrink-0 text-[10px] text-slate-500 tracking-wider font-mono">
            <div className="flex items-center gap-3">
              <span className="font-semibold">BACKTEST:</span>
              <div className="w-40 h-1 bg-secondary rounded-full overflow-hidden hidden sm:block">
                <div className="h-full bg-accent w-[75%]"></div>
              </div>
              <span className="text-accent font-semibold">75% Complete</span>
            </div>
            <div className="flex items-center gap-6 hidden md:flex">
              <span>CPU: 14%</span>
              <span>MEM: 1.2GB</span>
              <span>LATENCY: 42ms</span>
            </div>
          </div>
          
        </div>

      </div>
    </main>
  )
}
