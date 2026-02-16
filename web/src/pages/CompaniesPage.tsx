import { useState, useEffect, useCallback, useRef } from 'react'
import PortfolioTicker from '../components/PortfolioTicker'

const API = import.meta.env.VITE_API_URL || ''

interface Props {
  token: string
  onLogout: () => void
  onBack: () => void
}

interface Filters {
  industries: string[]
  countries: string[]
  stages: string[]
}

export default function CompaniesPage({ token, onLogout, onBack }: Props) {
  const [columns, setColumns] = useState<string[]>([])
  const [rows, setRows] = useState<Record<string, string>[]>([])
  const [links, setLinks] = useState<Record<string, string>>({})
  const [linkedin, setLinkedin] = useState<Record<string, string>>({})
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [industryFilter, setIndustryFilter] = useState('')
  const [countryFilter, setCountryFilter] = useState('')
  const [stageFilter, setStageFilter] = useState('')
  const [filters, setFilters] = useState<Filters>({ industries: [], countries: [], stages: [] })
  const [hasSearched, setHasSearched] = useState(false)
  const [page, setPage] = useState(0)
  const pageSize = 50
  const debounceRef = useRef<ReturnType<typeof setTimeout>>()

  const fetchCompanies = useCallback(async (q: string, industry: string, country: string, stage: string, offset: number) => {
    setLoading(true)
    setError('')
    try {
      const params = new URLSearchParams()
      if (q) params.set('q', q)
      if (industry) params.set('industry', industry)
      if (country) params.set('country', country)
      if (stage) params.set('stage', stage)
      params.set('limit', String(pageSize))
      if (offset) params.set('offset', String(offset))

      const res = await fetch(`${API}/api/companies?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.status === 401) {
        onLogout()
        return
      }
      const data = await res.json()
      setColumns(data.columns || [])
      setRows(data.rows || [])
      setLinks(data.links || {})
      setLinkedin(data.linkedin || {})
      setTotal(data.total || 0)
      if (data.filters) setFilters(data.filters)
      setHasSearched(true)
    } catch {
      setError('Failed to search companies.')
    } finally {
      setLoading(false)
    }
  }, [token, onLogout])

  // Reset to first page when filters change
  useEffect(() => {
    setPage(0)
  }, [search, industryFilter, countryFilter, stageFilter])

  // Debounced search
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current)

    // Don't auto-search on empty query with no filters
    if (!search && !industryFilter && !countryFilter && !stageFilter) {
      if (!hasSearched) return
    }

    debounceRef.current = setTimeout(() => {
      fetchCompanies(search, industryFilter, countryFilter, stageFilter, page * pageSize)
    }, 300)

    return () => { if (debounceRef.current) clearTimeout(debounceRef.current) }
  }, [search, industryFilter, countryFilter, stageFilter, page, fetchCompanies, hasSearched])

  // Load filters on mount (empty search to get filter values)
  useEffect(() => {
    const loadFilters = async () => {
      try {
        const res = await fetch(`${API}/api/companies?limit=0`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (res.ok) {
          const data = await res.json()
          if (data.filters) setFilters(data.filters)
        }
      } catch { /* ignore */ }
    }
    loadFilters()
  }, [token])

  const nameCol = columns.find(c => c.toLowerCase() === 'name') || ''

  const colWidths: Record<string, string> = {
    'Name': '180px',
    'Description': '400px',
    'Industry': '200px',
    'Location (Country)': '150px',
    'Investment Stage': '150px',
    'Year Founded': '100px',
    'Number of Employees': '140px',
    'Investors': '350px',
    'Last Funding Amount (USD)': '160px',
    'Last Funding Date': '120px',
    'Total Funding Amount (USD)': '160px',
    'People': '350px',
    'Last Contact': '120px',
  }
  const colWidth = (col: string) => colWidths[col] || '100px'
  const tableWidth = columns.reduce((sum, col) => {
    return sum + parseInt(colWidth(col))
  }, 0)

  const isWrapColumn = (col: string) => {
    const lower = col.toLowerCase()
    return lower.includes('descri') || lower.includes('investors') || lower.includes('people')
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
          <span className="font-black uppercase tracking-widest text-sm text-gray-900">Companies</span>
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
        <div className="max-w-[1400px] mx-auto flex flex-wrap items-center gap-3">
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

          {filters.industries.length > 0 && (
            <select
              value={industryFilter}
              onChange={e => setIndustryFilter(e.target.value)}
              className="border-2 border-gray-200 px-3 py-2 text-sm text-gray-700 bg-white focus:outline-none transition"
              onFocus={e => (e.target.style.borderColor = '#1400FF')}
              onBlur={e => (e.target.style.borderColor = '#e5e7eb')}
            >
              <option value="">All Industries</option>
              {filters.industries.map(v => (
                <option key={v} value={v}>{v}</option>
              ))}
            </select>
          )}

          {filters.countries.length > 0 && (
            <select
              value={countryFilter}
              onChange={e => setCountryFilter(e.target.value)}
              className="border-2 border-gray-200 px-3 py-2 text-sm text-gray-700 bg-white focus:outline-none transition"
              onFocus={e => (e.target.style.borderColor = '#1400FF')}
              onBlur={e => (e.target.style.borderColor = '#e5e7eb')}
            >
              <option value="">All Countries</option>
              {filters.countries.map(v => (
                <option key={v} value={v}>{v}</option>
              ))}
            </select>
          )}

          {filters.stages.length > 0 && (
            <select
              value={stageFilter}
              onChange={e => setStageFilter(e.target.value)}
              className="border-2 border-gray-200 px-3 py-2 text-sm text-gray-700 bg-white focus:outline-none transition"
              onFocus={e => (e.target.style.borderColor = '#1400FF')}
              onBlur={e => (e.target.style.borderColor = '#e5e7eb')}
            >
              <option value="">All Stages</option>
              {filters.stages.map(v => (
                <option key={v} value={v}>{v}</option>
              ))}
            </select>
          )}

          {hasSearched && !loading && (
            <span className="text-xs font-bold uppercase tracking-widest text-gray-400">
              {page * pageSize + 1}–{Math.min((page + 1) * pageSize, total)} of {total}
            </span>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto px-4 py-4">
        <div className="overflow-x-auto">
          {loading ? (
            <div className="space-y-3">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="h-10 bg-gray-100 animate-pulse" />
              ))}
            </div>
          ) : error ? (
            <p className="text-center text-gray-400 py-12">{error}</p>
          ) : !hasSearched ? (
            <p className="text-center text-gray-400 py-12">Search for companies or select a filter to get started.</p>
          ) : rows.length === 0 ? (
            <p className="text-center text-gray-400 py-12">No companies match your search.</p>
          ) : (
            <table className="text-sm border-collapse" style={{ tableLayout: 'fixed', width: `${tableWidth}px` }}>
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
                      className="text-left px-3 py-2 font-bold uppercase tracking-wider text-xs text-gray-500 border-b-2"
                      style={{ borderBottomColor: '#1400FF' }}
                    >
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((row, i) => (
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
                        {col === nameCol ? (
                          <span className="flex items-center gap-1.5">
                            {links[(row[col] || '').trim()] ? (
                              <a
                                href={links[(row[col] || '').trim()]}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="underline text-gray-900"
                              >
                                {row[col]}
                              </a>
                            ) : (
                              row[col]
                            )}
                            {linkedin[(row[col] || '').trim()] && (
                              <a
                                href={linkedin[(row[col] || '').trim()]}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex-shrink-0 text-gray-400 hover:text-gray-700"
                                title="LinkedIn"
                              >
                                <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
                                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
                                </svg>
                              </a>
                            )}
                          </span>
                        ) : (
                          row[col] ?? ''
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Pagination */}
        {hasSearched && total > pageSize && (
          <div className="flex items-center justify-center gap-4 py-4">
            <button
              onClick={() => setPage(p => p - 1)}
              disabled={page === 0}
              className="px-4 py-2 text-xs font-bold uppercase tracking-widest border-2 border-gray-200 text-gray-600 disabled:opacity-30 disabled:cursor-not-allowed hover:border-[#1400FF] hover:text-[#1400FF] transition"
            >
              Previous
            </button>
            <span className="text-xs font-bold uppercase tracking-widest text-gray-400">
              Page {page + 1} of {Math.ceil(total / pageSize)}
            </span>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={(page + 1) * pageSize >= total}
              className="px-4 py-2 text-xs font-bold uppercase tracking-widest border-2 border-gray-200 text-gray-600 disabled:opacity-30 disabled:cursor-not-allowed hover:border-[#1400FF] hover:text-[#1400FF] transition"
            >
              Next
            </button>
          </div>
        )}
      </div>

      <PortfolioTicker />
    </div>
  )
}
