'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import api from '@/lib/api'

interface UserProfile {
  user: {
    id: string
    name: string
    email: string
    created_at: string
  }
  total_strategies: number
  total_backtests: number
  average_return: number | null
  best_sharpe_ratio: number | null
}

export default function ProfilePage() {
  const router = useRouter()
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem('access_token')
        if (!token) {
          router.push('/login')
          return
        }

        const data = await api.getProfile()
        setProfile(data)
      } catch (err: any) {
        console.error('Error fetching profile:', err)
        if (err.response?.status === 401) {
          localStorage.removeItem('access_token')
          router.push('/login')
        } else {
          setError('Failed to load profile')
        }
      } finally {
        setLoading(false)
      }
    }

    fetchProfile()
  }, [router])

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-slate-400">Loading profile...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-red-400">{error}</div>
      </div>
    )
  }

  if (!profile) {
    return null
  }

  return (
    <div className="min-h-screen bg-slate-900 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Profile</h1>
          <p className="text-slate-400">Manage your trading strategies and backtests</p>
        </div>

        {/* Profile Card */}
        <div className="bg-slate-800 rounded-lg border border-slate-700 p-8 mb-8">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">{profile.user.name}</h2>
              <p className="text-slate-400">{profile.user.email}</p>
              <p className="text-slate-500 text-sm mt-2">
                Member since {new Date(profile.user.created_at).toLocaleDateString()}
              </p>
            </div>
            <button
              onClick={() => {
                api.logout()
                router.push('/')
              }}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Logout
            </button>
          </div>
        </div>

        {/* Statistics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
            <p className="text-slate-400 text-sm mb-2">Total Strategies</p>
            <p className="text-3xl font-bold text-white">{profile.total_strategies}</p>
          </div>

          <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
            <p className="text-slate-400 text-sm mb-2">Total Backtests</p>
            <p className="text-3xl font-bold text-white">{profile.total_backtests}</p>
          </div>

          <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
            <p className="text-slate-400 text-sm mb-2">Average Return</p>
            <p className={`text-3xl font-bold ${profile.average_return && profile.average_return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {profile.average_return ? `${profile.average_return.toFixed(2)}%` : 'N/A'}
            </p>
          </div>

          <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
            <p className="text-slate-400 text-sm mb-2">Best Sharpe Ratio</p>
            <p className="text-3xl font-bold text-white">
              {profile.best_sharpe_ratio ? profile.best_sharpe_ratio.toFixed(2) : 'N/A'}
            </p>
          </div>
        </div>

        {/* Navigation Links */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link
            href="/profile/strategies"
            className="bg-slate-800 hover:bg-slate-700 rounded-lg border border-slate-700 p-6 transition-colors"
          >
            <h3 className="text-xl font-bold text-white mb-2">My Strategies</h3>
            <p className="text-slate-400">View all your trading strategies</p>
          </Link>

          <Link
            href="/profile/backtests"
            className="bg-slate-800 hover:bg-slate-700 rounded-lg border border-slate-700 p-6 transition-colors"
          >
            <h3 className="text-xl font-bold text-white mb-2">Backtest History</h3>
            <p className="text-slate-400">View all your backtest results</p>
          </Link>
        </div>
      </div>
    </div>
  )
}
