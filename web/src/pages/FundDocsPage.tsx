import { useState, useEffect } from 'react'
import PortfolioTicker from '../components/PortfolioTicker'

const API = import.meta.env.VITE_API_URL || ''

interface Props {
  token: string
  onLogout: () => void
  onBack: () => void
}

interface Doc {
  name: string
  url: string
}

function friendlyName(raw: string): string {
  const lower = raw.toLowerCase()
  if (lower.includes('fundraising') || lower.includes('deck')) return 'Fundraising Deck'
  if (lower.includes('memorandum') || lower.includes('offering')) return 'Offering Memorandum'
  if (lower.includes('m&a') || lower.includes('signed') || lower.includes('roosh vc -')) return 'M&A Agreement'
  return raw.replace(/\.[^.]+$/, '')
}

const DOC_ORDER: Record<string, number> = {
  'Fundraising Deck': 0,
  'Offering Memorandum': 1,
  'M&A Agreement': 2,
}

function sortDocs(docs: Doc[]): Doc[] {
  return [...docs].sort((a, b) => {
    const ai = DOC_ORDER[friendlyName(a.name)] ?? 99
    const bi = DOC_ORDER[friendlyName(b.name)] ?? 99
    return ai - bi
  })
}

function docIcon() {
  return (
    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
    </svg>
  )
}

export default function FundDocsPage({ token, onLogout, onBack }: Props) {
  const [docs, setDocs] = useState<Doc[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchDocs = async () => {
      try {
        const res = await fetch(`${API}/api/fund-docs-list`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (res.status === 401) { onLogout(); return }
        const data = await res.json()
        setDocs(data.docs || [])
      } catch {
        setError('Failed to load documents.')
      } finally {
        setLoading(false)
      }
    }
    fetchDocs()
  }, [token, onLogout])

  return (
    <div className="h-screen bg-white flex flex-col overflow-hidden">
      <header className="flex items-center justify-between px-4 py-3 border-b-2 border-gray-100 bg-white flex-shrink-0">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="text-gray-400 hover:text-gray-900 transition-colors"
            title="Back"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <img src="/logo.png" alt="ROOSH" className="h-7" />
          <span className="font-black uppercase tracking-widest text-sm text-gray-900">Fund Data</span>
        </div>
        <button
          onClick={onLogout}
          className="text-xs font-bold uppercase tracking-widest text-gray-400 hover:text-gray-900 transition-colors"
        >
          Sign out
        </button>
      </header>

      <div className="flex-1 overflow-y-auto px-4 py-10">
        <div className="max-w-xl mx-auto">
          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-16 bg-gray-100 animate-pulse" />
              ))}
            </div>
          ) : error ? (
            <p className="text-center text-gray-400 py-12">{error}</p>
          ) : docs.length === 0 ? (
            <p className="text-center text-gray-400 py-12">No documents found.</p>
          ) : (
            <div className="flex flex-col gap-3">
              {sortDocs(docs).map(doc => (
                <a
                  key={doc.url}
                  href={doc.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-4 px-5 py-4 border-2 border-gray-100 hover:border-[#1400FF] transition-all group"
                >
                  <div
                    className="w-10 h-10 flex items-center justify-center flex-shrink-0 text-white"
                    style={{ backgroundColor: '#1400FF' }}
                  >
                    {docIcon()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div
                      style={{ fontFamily: "'Space Grotesk', sans-serif" }}
                      className="font-bold text-gray-900 text-sm"
                    >
                      {friendlyName(doc.name)}
                    </div>
                    <div className="text-xs text-gray-400 mt-0.5">PDF · Opens in Google Drive</div>
                  </div>
                  <svg className="w-4 h-4 text-gray-300 group-hover:text-[#1400FF] transition-colors flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              ))}
            </div>
          )}
        </div>
      </div>

      <PortfolioTicker />
    </div>
  )
}
