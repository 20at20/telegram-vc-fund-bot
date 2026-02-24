import PortfolioTicker from '../components/PortfolioTicker'

interface Agent {
  id: string
  name: string
  description: string
  icon: JSX.Element
  ready: boolean
}

const agents: Agent[] = [
  {
    id: 'rv-fund',
    name: 'RV Fund Data AI Assistant',
    description: 'Portfolio performance, fund metrics (TVPI, IRR, DPI), company details, rankings and sector breakdowns.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
          d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.937A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.582a.5.5 0 0 1 0 .962L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 3v4M22 5h-4M4 17v2M5 18H3" />
      </svg>
    ),
    ready: true,
  },
  {
    id: 'deals',
    name: 'Deals on the Table',
    description: 'Active deal pipeline — company, geo, round, industry, and investment thesis.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
          d="M13 2 3 14h9l-1 8 10-12h-9l1-8z" />
      </svg>
    ),
    ready: true,
  },
  {
    id: 'asks',
    name: 'Portfolio Asks',
    description: 'What our portfolio companies need — intros, partnerships, hiring, and more.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
          d="M18 8a4 4 0 0 1 0 8" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
          d="M18 4a8 8 0 0 1 0 16" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
          d="M6 8.999h2.764c2.56 0 5.272-.65 7.236-2v8c-1.964-1.35-4.676-2-7.236-2H6a2 2 0 0 1-2-2v-2a2 2 0 0 1 2-2z" />
      </svg>
    ),
    ready: true,
  },
  {
    id: 'experts',
    name: 'Experts',
    description: 'Find domain experts by area of expertise, nationality, or company for warm intros.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <circle cx="12" cy="8" r="6" strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
          d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11" />
      </svg>
    ),
    ready: true,
  },
  {
    id: 'companies',
    name: 'Network',
    description: 'Search 20K+ people in my network. Filter by industry, country, and stage.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <circle cx="18" cy="5" r="3" strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} />
        <circle cx="6" cy="12" r="3" strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} />
        <circle cx="18" cy="19" r="3" strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
          d="m8.59 13.51 6.83 3.98M15.41 6.51l-6.82 3.98" />
      </svg>
    ),
    ready: true,
  },
  {
    id: 'newsletters',
    name: 'Newsletters',
    description: 'Monthly investor updates, market insights, and portfolio highlights.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
          d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M14 2v6h6" />
        <path strokeLinecap="round" strokeWidth={1.5} d="M16 13H8M16 17H8M10 9H8" />
      </svg>
    ),
    ready: true,
  },
]

interface Props {
  onSelect: (agentId: string) => void
  onLogout: () => void
}

export default function AgentSelectPage({ onSelect, onLogout }: Props) {
  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b-2 border-gray-100">
        <img src="/logo.png" alt="ROOSH" className="h-7" />
        <button
          onClick={onLogout}
          className="text-xs font-bold uppercase tracking-widest text-gray-400 hover:text-gray-900 transition-colors"
        >
          Sign out
        </button>
      </header>

      {/* Content */}
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-12">
        <h1 style={{ fontFamily: "'Space Grotesk', sans-serif" }} className="text-4xl font-extrabold tracking-tight text-gray-900 mb-2">Roosh LP Platform</h1>
        <p className="text-gray-400 mb-10 text-center text-sm uppercase tracking-widest font-medium">Select a workspace</p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-px bg-gray-100 border border-gray-100 w-full max-w-5xl">
          {agents.map(agent => (
            <button
              key={agent.id}
              onClick={() => agent.ready && onSelect(agent.id)}
              disabled={!agent.ready}
              className={`
                relative text-left p-8 bg-white transition-all duration-150
                ${agent.ready ? 'cursor-pointer hover:bg-gray-50' : 'cursor-not-allowed opacity-40'}
              `}
              onMouseEnter={agent.ready ? e => (e.currentTarget.style.outline = '2px solid #1400FF') : undefined}
              onMouseLeave={agent.ready ? e => (e.currentTarget.style.outline = 'none') : undefined}
            >
              {!agent.ready && (
                <span className="absolute top-4 right-4 text-xs font-bold uppercase tracking-widest text-gray-300">
                  Soon
                </span>
              )}
              <div
                className="w-10 h-10 flex items-center justify-center mb-5"
                style={{ backgroundColor: agent.ready ? '#1400FF' : '#e5e7eb' }}
              >
                <span className={agent.ready ? 'text-white' : 'text-gray-400'}>{agent.icon}</span>
              </div>
              <h3 style={{ fontFamily: "'Space Grotesk', sans-serif" }} className="font-bold tracking-tight text-gray-900 mb-1">{agent.name}</h3>
              <p className="text-sm text-gray-400 leading-relaxed">{agent.description}</p>
            </button>
          ))}
        </div>
      </div>

      <PortfolioTicker />
    </div>
  )
}
