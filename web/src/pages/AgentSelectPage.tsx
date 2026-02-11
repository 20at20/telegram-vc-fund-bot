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
    id: 'deal-flow',
    name: 'Deal Flow',
    description: 'Pipeline tracking, deal stages, founder communications and investment memos.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
          d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
      </svg>
    ),
    ready: false,
  },
  {
    id: 'lp-relations',
    name: 'LP Relations',
    description: 'Investor updates, capital calls, distributions and LP reporting.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
          d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    ),
    ready: false,
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
        <p className="text-gray-400 mb-10 text-center text-sm uppercase tracking-widest font-medium">Select an AI agent to start a conversation</p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-px bg-gray-100 border border-gray-100 w-full max-w-3xl">
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
