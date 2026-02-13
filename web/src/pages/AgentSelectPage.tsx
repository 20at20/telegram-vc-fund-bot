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
    name: 'RV Fund',
    description: 'Portfolio performance, fund metrics (TVPI, IRR, DPI), company details, rankings and sector breakdowns.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
          d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
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
          d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
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
          d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" />
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
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
          d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
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
          d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
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
        <h1 className="text-4xl font-black uppercase tracking-tight text-gray-900 mb-2">Choose an Assistant</h1>
        <p className="text-gray-400 mb-10 text-center text-sm uppercase tracking-widest font-medium">Select a tool</p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-px bg-gray-100 border border-gray-100 w-full max-w-5xl">
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
              <h3 className="font-black uppercase tracking-tight text-gray-900 mb-1">{agent.name}</h3>
              <p className="text-sm text-gray-400 leading-relaxed">{agent.description}</p>
            </button>
          ))}
        </div>
      </div>

      <PortfolioTicker />
    </div>
  )
}
