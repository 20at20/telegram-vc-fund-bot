import { useState, useEffect, useMemo } from 'react'
import PortfolioTicker from '../components/PortfolioTicker'

const API = import.meta.env.VITE_API_URL || ''

interface NewsItem {
  title: string
  link: string
  published: string
  snippet: string
}

interface CompanyWithNews {
  name: string
  news: NewsItem[]
}

interface Props {
  token: string
  onLogout: () => void
  onBack: () => void
}

function timeAgo(isoString: string): string {
  if (!isoString) return ''
  const diffMs = Date.now() - new Date(isoString).getTime()
  const hours = Math.floor(diffMs / 3_600_000)
  if (hours < 1) return 'just now'
  if (hours === 1) return '1 hour ago'
  if (hours < 24) return `${hours} hours ago`
  const days = Math.floor(hours / 24)
  return days === 1 ? '1 day ago' : `${days} days ago`
}

export default function NewsPage({ token, onLogout, onBack }: Props) {
  const [companies, setCompanies] = useState<CompanyWithNews[]>([])
  const [total, setTotal] = useState(0)
  const [lastRefreshed, setLastRefreshed] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const res = await fetch(`${API}/api/news`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (res.status === 401) {
          onLogout()
          return
        }
        if (!res.ok) throw new Error('Server error')
        const data = await res.json()
        setCompanies(data.companies || [])
        setTotal(data.total || 0)
        setLastRefreshed(data.last_refreshed || '')
      } catch {
        setError('Failed to load news. Please try again.')
      } finally {
        setLoading(false)
      }
    }
    fetchNews()
  }, [token, onLogout])

  const filtered = useMemo(
    () =>
      companies.filter(c =>
        c.name.toLowerCase().includes(search.toLowerCase())
      ),
    [companies, search]
  )

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 border-b-2 border-gray-100 bg-white flex-shrink-0">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="text-gray-400 hover:text-gray-900 transition-colors"
            title="Back to agents"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <img src="/logo.png" alt="ROOSH" className="h-7" />
          <span className="font-black uppercase tracking-widest text-sm text-gray-900">Portfolio News</span>
        </div>
        <button
          onClick={onLogout}
          className="text-xs font-bold uppercase tracking-widest text-gray-400 hover:text-gray-900 transition-colors"
        >
          Sign out
        </button>
      </header>

      {/* Filters bar */}
      <div className="px-4 py-3 border-b border-gray-100 bg-white flex-shrink-0">
        <div className="max-w-6xl mx-auto flex flex-wrap items-center gap-3">
          <div className="flex-1 min-w-[200px]">
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search companies..."
              className="w-full border-2 border-gray-200 px-3 py-2 text-sm text-gray-900 placeholder-gray-300 focus:outline-none transition"
              onFocus={e => (e.target.style.borderColor = '#1400FF')}
              onBlur={e => (e.target.style.borderColor = '#e5e7eb')}
            />
          </div>
          {!loading && !error && (
            <span className="text-xs text-gray-400 whitespace-nowrap">
              {total > 0
                ? `${total} ${total === 1 ? 'company' : 'companies'} with news`
                : 'No recent news found'}
              {lastRefreshed && ` · Updated ${timeAgo(lastRefreshed)}`}
            </span>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        <div className="max-w-6xl mx-auto px-4 py-6">

          {/* Loading skeleton */}
          {loading && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="border border-gray-100 p-4 space-y-3 animate-pulse">
                  <div className="h-4 bg-gray-200 w-1/3" />
                  <div className="h-3 bg-gray-100 w-full" />
                  <div className="h-3 bg-gray-100 w-5/6" />
                </div>
              ))}
            </div>
          )}

          {/* Error */}
          {!loading && error && (
            <p className="text-sm text-red-500">{error}</p>
          )}

          {/* Cold-start: server still fetching */}
          {!loading && !error && total === 0 && !lastRefreshed && (
            <p className="text-sm text-gray-400">
              News is loading on the server — check back in a moment.
            </p>
          )}

          {/* Empty: no news in last 7 days */}
          {!loading && !error && total === 0 && lastRefreshed && (
            <p className="text-sm text-gray-400">
              No news found for portfolio companies in the last 7 days.
            </p>
          )}

          {/* No search match */}
          {!loading && !error && total > 0 && filtered.length === 0 && (
            <p className="text-sm text-gray-400">No companies match "{search}".</p>
          )}

          {/* Company cards */}
          {!loading && !error && filtered.length > 0 && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {filtered.map(company => (
                <div
                  key={company.name}
                  className="border border-gray-100 flex flex-col"
                >
                  {/* Company name header */}
                  <div
                    className="px-4 py-3 border-b-2"
                    style={{ borderColor: '#1400FF' }}
                  >
                    <span className="font-black uppercase tracking-widest text-xs text-gray-900">
                      {company.name}
                    </span>
                  </div>

                  {/* News items */}
                  <div className="flex flex-col divide-y divide-gray-50">
                    {company.news.map((item, idx) => (
                      <div key={idx} className="px-4 py-3 hover:bg-gray-50 transition-colors">
                        <a
                          href={item.link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm font-semibold text-gray-900 underline underline-offset-2 hover:text-[#1400FF] transition-colors leading-snug block mb-1"
                        >
                          {item.title}
                        </a>
                        {item.snippet && (
                          <p className="text-xs text-gray-500 leading-relaxed mb-1 line-clamp-2">
                            {item.snippet}
                          </p>
                        )}
                        <span className="text-xs text-gray-300">{item.published}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <PortfolioTicker />
    </div>
  )
}
