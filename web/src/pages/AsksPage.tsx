import { useState, useEffect, useMemo } from 'react'
import PortfolioTicker from '../components/PortfolioTicker'

const API = import.meta.env.VITE_API_URL || ''

interface Props {
  token: string
  onLogout: () => void
  onBack: () => void
}

export default function AsksPage({ token, onLogout, onBack }: Props) {
  const [columns, setColumns] = useState<string[]>([])
  const [rows, setRows] = useState<Record<string, string>[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [links, setLinks] = useState<Record<string, string>>({})

  useEffect(() => {
    const fetchAsks = async () => {
      try {
        const res = await fetch(`${API}/api/asks`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (res.status === 401) {
          onLogout()
          return
        }
        const data = await res.json()
        const allCols: string[] = data.columns || []
        const allRows: Record<string, string>[] = data.rows || []

        // Extract links from the "Link" column (if backend hasn't stripped it)
        const linkCol = allCols.find(c => c.toLowerCase() === 'link')
        const compCol = allCols.find(c => c.toLowerCase().includes('company'))
        let extractedLinks: Record<string, string> = data.links || {}
        if (linkCol && compCol) {
          for (const row of allRows) {
            const url = (row[linkCol] || '').trim()
            const name = (row[compCol] || '').trim()
            if (url && name && url.startsWith('http')) {
              extractedLinks[name] = url
            }
          }
        }

        setColumns(allCols.filter(c => c.toLowerCase() !== 'link'))
        setRows(allRows)
        setLinks(extractedLinks)
      } catch {
        setError('Failed to load portfolio asks.')
      } finally {
        setLoading(false)
      }
    }
    fetchAsks()
  }, [token, onLogout])

  // Filter rows
  const filteredRows = useMemo(() => {
    if (!search) return rows
    const q = search.toLowerCase()
    return rows.filter(row =>
      columns.some(col => String(row[col] || '').toLowerCase().includes(q))
    )
  }, [rows, columns, search])

  const companyCol = useMemo(() =>
    columns.find(c => c.toLowerCase().includes('company')) || '',
  [columns])

  const colWidth = (col: string) => {
    const lower = col.toLowerCase()
    if (lower.includes('company')) return '15%'
    if (lower.includes('descri')) return '40%'
    if (lower.includes('ask')) return '45%'
    return '25%'
  }

  const isWrapColumn = (col: string) => {
    const lower = col.toLowerCase()
    return lower.includes('descri') || lower.includes('ask')
  }

  return (
    <div className="h-screen bg-white flex flex-col overflow-hidden">
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
          <span className="font-black uppercase tracking-widest text-sm text-gray-900">Portfolio Asks</span>
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
          <div className="flex-1 min-w-[200px]">
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search portfolio asks..."
              className="w-full border-2 border-gray-200 px-3 py-2 text-sm text-gray-900 placeholder-gray-300 focus:outline-none transition"
              onFocus={e => (e.target.style.borderColor = '#1400FF')}
              onBlur={e => (e.target.style.borderColor = '#e5e7eb')}
            />
          </div>

          {!loading && (
            <span className="text-xs font-bold uppercase tracking-widest text-gray-400">
              {filteredRows.length} compan{filteredRows.length !== 1 ? 'ies' : 'y'}
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
            <p className="text-center text-gray-400 py-12">No portfolio asks available. Check that ASKS_SHEET_ID is configured.</p>
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
                      No results match your search.
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
                          {col === companyCol && links[(row[col] || '').trim()] ? (
                            <a
                              href={links[(row[col] || '').trim()]}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="underline text-gray-900"
                            >
                              {row[col]}
                            </a>
                          ) : (
                            row[col] ?? ''
                          )}
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
