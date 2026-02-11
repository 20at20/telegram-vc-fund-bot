import { useState } from 'react'
import PortfolioTicker from '../components/PortfolioTicker'

interface Newsletter {
  id: string
  title: string
  date: string
  url: string
}

const newsletters: Newsletter[] = [
  { id: 'dec-2025', title: 'December 2025', date: 'Dec 2025', url: 'https://archive.sendpul.se/v/5dkqd/7txx/' },
  { id: 'nov-2025', title: 'November 2025', date: 'Nov 2025', url: 'https://archive.sendpul.se/v/5dkqd/6zwx/' },
  { id: 'oct-2025', title: 'October 2025', date: 'Oct 2025', url: 'https://archive.sendpul.se/v/5dkqd/6436/' },
]

interface Props {
  onLogout: () => void
  onBack: () => void
}

export default function NewslettersPage({ onLogout, onBack }: Props) {
  const [selected, setSelected] = useState<Newsletter | null>(null)

  // Iframe viewer
  if (selected) {
    return (
      <div className="min-h-screen bg-white flex flex-col">
        {/* Header bar */}
        <header className="flex items-center justify-between px-4 py-3 border-b-2 border-gray-100 bg-white flex-shrink-0">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSelected(null)}
              className="text-gray-400 hover:text-gray-900 transition-colors"
              title="Back to newsletters"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <img src="/logo.png" alt="ROOSH" className="h-7" />
            <span className="font-black uppercase tracking-widest text-sm text-gray-900">{selected.title}</span>
          </div>
          <button
            onClick={onLogout}
            className="text-xs font-bold uppercase tracking-widest text-gray-400 hover:text-gray-900 transition-colors"
          >
            Sign out
          </button>
        </header>

        {/* Iframe */}
        <iframe
          src={selected.url}
          className="flex-1 w-full border-none"
          title={selected.title}
        />
      </div>
    )
  }

  // Newsletter list
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
          <span className="font-black uppercase tracking-widest text-sm text-gray-900">Newsletters</span>
        </div>
        <button
          onClick={onLogout}
          className="text-xs font-bold uppercase tracking-widest text-gray-400 hover:text-gray-900 transition-colors"
        >
          Sign out
        </button>
      </header>

      {/* Newsletter cards */}
      <div className="flex-1 px-4 py-8">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-3xl font-black uppercase tracking-tight text-gray-900 mb-2">Newsletters</h1>
          <p className="text-gray-400 text-sm uppercase tracking-widest font-medium mb-8">Monthly investor updates</p>

          <div className="space-y-px bg-gray-100 border border-gray-100">
            {newsletters.map(nl => (
              <button
                key={nl.id}
                onClick={() => setSelected(nl)}
                className="w-full text-left p-6 bg-white hover:bg-gray-50 transition-all duration-150 flex items-center justify-between gap-4"
                onMouseEnter={e => (e.currentTarget.style.outline = '2px solid #1400FF')}
                onMouseLeave={e => (e.currentTarget.style.outline = 'none')}
              >
                <div className="flex items-center gap-4">
                  <div
                    className="w-10 h-10 flex items-center justify-center flex-shrink-0"
                    style={{ backgroundColor: '#1400FF' }}
                  >
                    <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                        d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-black uppercase tracking-tight text-gray-900">{nl.title}</h3>
                    <p className="text-xs text-gray-400 uppercase tracking-widest font-medium mt-0.5">{nl.date}</p>
                  </div>
                </div>
                <svg className="w-5 h-5 text-gray-300 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            ))}
          </div>
        </div>
      </div>

      <PortfolioTicker />
    </div>
  )
}
