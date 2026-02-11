import { useState, useEffect, useMemo } from 'react'
import PortfolioTicker from '../components/PortfolioTicker'

const API = import.meta.env.VITE_API_URL || ''

interface Props {
  token: string
  onLogout: () => void
  onBack: () => void
}

export default function DealsPage({ token, onLogout, onBack }: Props) {
  const [columns, setColumns] = useState<string[]>([])
  const [rows, setRows] = useState<Record<string, string>[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [industryFilter, setIndustryFilter] = useState('')
  const [roundFilter, setRoundFilter] = useState('')
  const [geoFilter, setGeoFilter] = useState('')

  useEffect(() => {
    const fetchDeals = async () => {
      try {
        const res = await fetch(`${API}/api/deals`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (res.status === 401) {
          onLogout()
          return
        }
        const data = await res.json()
        setColumns(data.columns || [])
        setRows(data.rows || [])
      } catch {
        setError('Failed to load deals data.')
      } finally {
        setLoading(false)
      }
    }
    fetchDeals()
  }, [token, onLogout])

  // Extract unique values for filter dropdowns
  const industries = useMemo(() => {
    const col = columns.find(c => c.toLowerCase().includes('industry'))
    if (!col) return []
    const values = new Set(rows.map(r => r[col]).filter(Boolean))
    return Array.from(values).sort()
  }, [columns, rows])

  const rounds = useMemo(() => {
    const col = columns.find(c => c.toLowerCase().includes('round') && !c.toLowerCase().includes('size'))
    if (!col) return []
    const values = new Set(rows.map(r => r[col]).filter(Boolean))
    return Array.from(values).sort()
  }, [columns, rows])

  const geos = useMemo(() => {
    const col = columns.find(c => c.toLowerCase().includes('geo'))
    if (!col) return []
    const values = new Set(rows.map(r => r[col]).filter(Boolean))
    return Array.from(values).sort()
  }, [columns, rows])

  // Filter rows
  const filteredRows = useMemo(() => {
    return rows.filter(row => {
      // Search filter — match across all columns
      if (search) {
        const q = search.toLowerCase()
        const matches = columns.some(col =>
          String(row[col] || '').toLowerCase().includes(q)
        )
        if (!matches) return false
      }

      // Industry filter
      if (industryFilter) {
        const col = columns.find(c => c.toLowerCase().includes('industry'))
        if (col && row[col] !== industryFilter) return false
      }

      // Round filter
      if (roundFilter) {
        const col = columns.find(c => c.toLowerCase().includes('round') && !c.toLowerCase().includes('size'))
        if (col && row[col] !== roundFilter) return false
      }

      // Geo filter
      if (geoFilter) {
        const col = columns.find(c => c.toLowerCase().includes('geo'))
        if (col && row[col] !== geoFilter) return false
      }

      return true
    })
  }, [rows, columns, search, industryFilter, roundFilter, geoFilter])

  // Identify text-heavy columns that should wrap instead of expanding
  const isWrapColumn = (col: string) => {
    const lower = col.toLowerCase()
    return lower.includes('descri') || lower.includes('why') || lower.includes('interesting')
  }

  // Fixed column widths so table-layout: fixed distributes space correctly
  const colWidth = (col: string) => {
    const lower = col.toLowerCase()
    if (lower.includes('why') || lower.includes('interesting')) return '30%'
    if (lower.includes('descri')) return '24%'
    if (lower.includes('company')) return '10%'
    if (lower.includes('industry')) return '9%'
    if (lower.includes('round') && lower.includes('size')) return '7%'
    if (lower.includes('round')) return '7%'
    if (lower.includes('geo')) return '5%'
    return '8%'
  }

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 border-b-2 border-gray-100 bg-white">
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
          <span className="font-black uppercase tracking-widest text-sm text-gray-900">Deals on the Table</span>
        </div>
        <button
          onClick={onLogout}
          className="text-xs font-bold uppercase tracking-widest text-gray-400 hover:text-gray-900 transition-colors"
        >
          Sign out
        </button>
      </header>

      {/* Filters */}
      <div className="px-4 py-4 border-b border-gray-100 bg-white">
        <div className="max-w-6xl mx-auto flex flex-wrap items-center gap-3">
          {/* Search */}
          <div className="flex-1 min-w-[200px]">
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search deals..."
              className="w-full border-2 border-gray-200 px-3 py-2 text-sm text-gray-900 placeholder-gray-300 focus:outline-none transition"
              onFocus={e => (e.target.style.borderColor = '#1400FF')}
              onBlur={e => (e.target.style.borderColor = '#e5e7eb')}
            />
          </div>

          {/* Industry filter */}
          {industries.length > 0 && (
            <select
              value={industryFilter}
              onChange={e => setIndustryFilter(e.target.value)}
              className="border-2 border-gray-200 px-3 py-2 text-sm text-gray-700 bg-white focus:outline-none transition"
              onFocus={e => (e.target.style.borderColor = '#1400FF')}
              onBlur={e => (e.target.style.borderColor = '#e5e7eb')}
            >
              <option value="">All Industries</option>
              {industries.map(ind => (
                <option key={ind} value={ind}>{ind}</option>
              ))}
            </select>
          )}

          {/* Round filter */}
          {rounds.length > 0 && (
            <select
              value={roundFilter}
              onChange={e => setRoundFilter(e.target.value)}
              className="border-2 border-gray-200 px-3 py-2 text-sm text-gray-700 bg-white focus:outline-none transition"
              onFocus={e => (e.target.style.borderColor = '#1400FF')}
              onBlur={e => (e.target.style.borderColor = '#e5e7eb')}
            >
              <option value="">All Rounds</option>
              {rounds.map(r => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          )}

          {/* Geo filter */}
          {geos.length > 0 && (
            <select
              value={geoFilter}
              onChange={e => setGeoFilter(e.target.value)}
              className="border-2 border-gray-200 px-3 py-2 text-sm text-gray-700 bg-white focus:outline-none transition"
              onFocus={e => (e.target.style.borderColor = '#1400FF')}
              onBlur={e => (e.target.style.borderColor = '#e5e7eb')}
            >
              <option value="">All Geos</option>
              {geos.map(g => (
                <option key={g} value={g}>{g}</option>
              ))}
            </select>
          )}

          {/* Result count */}
          {!loading && (
            <span className="text-xs font-bold uppercase tracking-widest text-gray-400">
              {filteredRows.length} deal{filteredRows.length !== 1 ? 's' : ''}
            </span>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto px-4 py-4">
        <div className="max-w-6xl mx-auto">
          {loading ? (
            <div className="space-y-3">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="h-10 bg-gray-100 animate-pulse" />
              ))}
            </div>
          ) : error ? (
            <p className="text-center text-gray-400 py-12">{error}</p>
          ) : rows.length === 0 ? (
            <p className="text-center text-gray-400 py-12">No deals data available. Check that DEALS_SHEET_ID is configured.</p>
          ) : (
            <table className="w-full text-sm border-collapse" style={{ tableLayout: 'fixed' }}>
              <colgroup>
                {columns.map(col => (
                  <col key={col} style={{ width: colWidth(col) }} />
                ))}
              </colgroup>
              <thead>
                <tr>
                  {columns.map(col => (
                    <th
                      key={col}
                      className="text-left px-3 py-2 font-bold uppercase tracking-wider text-xs text-gray-500 border-b-2 whitespace-nowrap overflow-hidden text-ellipsis"
                      style={{ borderBottomColor: '#1400FF' }}
                    >
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filteredRows.length === 0 ? (
                  <tr>
                    <td colSpan={columns.length} className="text-center text-gray-400 py-8">
                      No deals match your filters.
                    </td>
                  </tr>
                ) : (
                  filteredRows.map((row, i) => (
                    <tr key={i} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                      {columns.map(col => (
                        <td
                          key={col}
                          className="px-3 py-2 text-gray-700"
                          style={isWrapColumn(col)
                            ? { overflowWrap: 'break-word', wordBreak: 'break-word' }
                            : { whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }
                          }
                        >
                          {row[col] ?? ''}
                        </td>
                      ))}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          )}
        </div>
      </div>

      <PortfolioTicker />
    </div>
  )
}
