'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import api from '@/lib/api'

interface User {
  id: string
  name: string
  email: string
}

export default function ProfileCard() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [isOpen, setIsOpen] = useState(false)
  const [loading, setLoading] = useState(true)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const token = localStorage.getItem('access_token')
        if (!token) {
          setLoading(false)
          return
        }
        
        const profile = await api.getProfile()
        setUser(profile.user)
      } catch (err) {
        // User not logged in or token invalid
        localStorage.removeItem('access_token')
      } finally {
        setLoading(false)
      }
    }

    fetchUser()
  }, [])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  if (loading) {
    return null
  }

  if (!user) {
    return (
      <div className="flex gap-2">
        <Link
          href="/login"
          className="px-4 py-2 text-slate-300 hover:text-white transition-colors"
        >
          Sign In
        </Link>
        <Link
          href="/register"
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
        >
          Sign Up
        </Link>
      </div>
    )
  }

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-slate-700 transition-colors"
      >
        <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
          {user.name.charAt(0).toUpperCase()}
        </div>
        <span className="text-white hidden sm:inline">{user.name}</span>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-slate-800 rounded-lg border border-slate-700 shadow-lg z-50">
          <div className="px-4 py-3 border-b border-slate-700">
            <p className="text-white font-semibold">{user.name}</p>
            <p className="text-slate-400 text-sm">{user.email}</p>
          </div>

          <Link
            href="/profile"
            className="block px-4 py-2 text-slate-300 hover:bg-slate-700 transition-colors"
            onClick={() => setIsOpen(false)}
          >
            Profile
          </Link>

          <Link
            href="/profile/strategies"
            className="block px-4 py-2 text-slate-300 hover:bg-slate-700 transition-colors"
            onClick={() => setIsOpen(false)}
          >
            My Strategies
          </Link>

          <Link
            href="/profile/backtests"
            className="block px-4 py-2 text-slate-300 hover:bg-slate-700 transition-colors"
            onClick={() => setIsOpen(false)}
          >
            Backtests
          </Link>

          <button
            onClick={() => {
              api.logout()
              setIsOpen(false)
              setUser(null)
              router.push('/')
            }}
            className="w-full text-left px-4 py-2 text-red-400 hover:bg-slate-700 transition-colors border-t border-slate-700"
          >
            Logout
          </button>
        </div>
      )}
    </div>
  )
}
