import PortfolioTicker from '../components/PortfolioTicker'

interface Props {
  token: string
  onLogout: () => void
  onBack: () => void
}

const DECKS = [
  {
    id: 'long',
    name: 'Long Deck',
    description: 'Full fund presentation',
    url: 'https://docsend.com/view/u48kk2mdzutvzmgx',
  },
  {
    id: 'short',
    name: 'Short Deck',
    description: 'Summary fund presentation',
    url: 'https://docsend.com/view/v8ykewmt85m7ag2h',
  },
]

const NEWSLETTERS = [
  { id: 'mar-2026', title: 'March 2026', url: 'https://archive.sendpul.se/v/5dkqd/9z0a/' },
  { id: 'feb-2026', title: 'February 2026', url: 'https://archive.sendpul.se/v/5dkqd/98td/' },
  { id: 'jan-2026', title: 'January 2026', url: 'https://archive.sendpul.se/v/5dkqd/8nla/' },
  { id: 'dec-2025', title: 'December 2025', url: 'https://archive.sendpul.se/v/5dkqd/7txx/' },
  { id: 'nov-2025', title: 'November 2025', url: 'https://archive.sendpul.se/v/5dkqd/6zwx/' },
  { id: 'oct-2025', title: 'October 2025', url: 'https://archive.sendpul.se/v/5dkqd/6436/' },
]

function DeckIcon() {
  return (
    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
    </svg>
  )
}

function NewsletterIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>
  )
}

export default function FundDocsPage({ onLogout, onBack }: Props) {
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

      <div className="flex-1 overflow-y-auto px-4 py-8">
        <div className="max-w-xl mx-auto flex flex-col gap-8">

          {/* Decks */}
          <div className="flex flex-col gap-3">
            {DECKS.map(deck => (
              <a
                key={deck.id}
                href={deck.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-4 px-5 py-4 border-2 border-gray-100 hover:border-[#1400FF] transition-all group"
              >
                <div
                  className="w-10 h-10 flex items-center justify-center flex-shrink-0 text-white"
                  style={{ backgroundColor: '#1400FF' }}
                >
                  <DeckIcon />
                </div>
                <div className="flex-1 min-w-0">
                  <div
                    style={{ fontFamily: "'Space Grotesk', sans-serif" }}
                    className="font-bold text-gray-900 text-sm"
                  >
                    {deck.name}
                  </div>
                  <div className="text-xs text-gray-400 mt-0.5">{deck.description} · Opens in DocSend</div>
                </div>
                <svg className="w-4 h-4 text-gray-300 group-hover:text-[#1400FF] transition-colors flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            ))}
          </div>

          {/* Newsletters */}
          <div>
            <p className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-3">Newsletters</p>
            <div className="flex flex-col gap-3">
              {NEWSLETTERS.map(nl => (
                <a
                  key={nl.id}
                  href={nl.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-4 px-5 py-4 border-2 border-gray-100 hover:border-[#1400FF] transition-all group"
                >
                  <div
                    className="w-10 h-10 flex items-center justify-center flex-shrink-0 text-white"
                    style={{ backgroundColor: '#1400FF' }}
                  >
                    <NewsletterIcon />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div
                      style={{ fontFamily: "'Space Grotesk', sans-serif" }}
                      className="font-bold text-gray-900 text-sm"
                    >
                      {nl.title}
                    </div>
                    <div className="text-xs text-gray-400 mt-0.5">Monthly investor update</div>
                  </div>
                  <svg className="w-4 h-4 text-gray-300 group-hover:text-[#1400FF] transition-colors flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              ))}
            </div>
          </div>

        </div>
      </div>

      <PortfolioTicker />
    </div>
  )
}
