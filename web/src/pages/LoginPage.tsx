import { useState, FormEvent } from 'react'
import PortfolioTicker from '../components/PortfolioTicker'

const API = import.meta.env.VITE_API_URL || ''

interface Props {
  onLogin: (token: string, username: string) => void
}

export default function LoginPage({ onLogin }: Props) {
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await fetch(`${API}/api/auth`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password }),
      })
      if (!res.ok) {
        setError('Wrong password. Try again.')
        return
      }
      const { token, username } = await res.json()
      onLogin(token, username)
    } catch {
      setError('Cannot reach the server. Check your connection.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-white flex flex-col">
      <div className="flex-1 flex">
        {/* Left blue panel */}
        <div className="hidden md:flex w-80 flex-shrink-0 flex-col justify-between p-10" style={{ backgroundColor: '#1400FF' }}>
          <img src="/logo-transperent.png" alt="ROOSH" className="h-8" />
          <p className="text-white/60 text-sm">Internal AI platform</p>
        </div>

        {/* Right form */}
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="w-full max-w-sm">
            {/* Mobile logo */}
            <div className="md:hidden mb-8">
              <img src="/logo.png" alt="ROOSH" className="h-8" />
            </div>

            <h1 className="text-3xl font-black uppercase tracking-tight text-gray-900 mb-1">Sign in</h1>
            <p className="text-gray-500 text-sm mb-8">Enter your access password to continue</p>

            <form onSubmit={submit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-widest text-gray-500 mb-2">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full border-2 border-gray-200 rounded-none px-4 py-3 text-gray-900 placeholder-gray-300 focus:outline-none transition"
                  onFocus={e => (e.target.style.borderColor = '#1400FF')}
                  onBlur={e => (e.target.style.borderColor = '#e5e7eb')}
                />
              </div>

              {error && <p className="text-sm" style={{ color: '#E8321A' }}>{error}</p>}

              <button
                type="submit"
                disabled={loading}
                className="w-full text-white font-black uppercase tracking-widest py-3 transition-opacity disabled:opacity-60"
                style={{ backgroundColor: '#1400FF' }}
              >
                {loading ? 'Signing in...' : 'Sign in →'}
              </button>
            </form>
          </div>
        </div>
      </div>

      <PortfolioTicker />
    </div>
  )
}
