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
    id: 'fund-docs',
    name: 'Fund II Info Assistant',
    description: 'Ask questions about Fund II — strategy, team, portfolio, terms, and more.',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
          d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
      </svg>
    ),
    ready: true,
  },
  {
    id: 'deals',
    name: 'Deals on the Table',
    description: 'Active deal pipeline — company, geo, round, industry, and investment thesis.',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M18 8a4 4 0 0 1 0 8" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M18 4a8 8 0 0 1 0 16" />
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
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
    description: 'Search 20K+ people in our network. Filter by industry, country, and stage.',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
          d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M14 2v6h6" />
        <path strokeLinecap="round" strokeWidth={1.5} d="M16 13H8M16 17H8M10 9H8" />
      </svg>
    ),
    ready: true,
  },
  {
    id: 'submit-deal',
    name: 'Submit a Deal',
    description: 'Share a company for ROOSH consideration — attach a deck and your thoughts.',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
          d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
      </svg>
    ),
    ready: true,
  },
]

const fundRows = [
  {
    label: 'INDUSTRY',
    text: (
      <>
        We invest in exceptional founders using AI to transform{' '}
        <strong>traditional industries</strong> like finance, healthcare, and enterprise software,
        where <strong>up to 80% of workflows can be automated</strong>
      </>
    ),
    badge: 'Application AI for Traditional Businesses',
  },
  {
    label: 'GEO',
    text: (
      <>
        The <strong>European opportunity is massive</strong>, with founders building world-class AI
        companies like ElevenLabs, DeepMind, and Mistral AI
      </>
    ),
    badge: '80% Europe+ · 20% US',
  },
  {
    label: 'STAGE',
    text: (
      <>
        We focus on early-stage investments, where{' '}
        <strong>price-to-return potential is highest</strong>, and{' '}
        <strong>most of the application-layer opportunities</strong> are emerging
      </>
    ),
    badge: '50% Seed · 30% Pre-Seed · 20% Follow-ons',
  },
  {
    label: 'TEAM',
    text: (
      <>
        We back founders who <strong>execute quickly and iterate fast</strong>, have{' '}
        <strong>deep insight into their market</strong>, and show the{' '}
        <strong>ambition to build large, global companies</strong>
      </>
    ),
    badge: 'Do-er · Market · Ambition',
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
      <header className="flex items-center justify-between px-6 py-4 border-b-2 border-gray-100 flex-shrink-0">
        <img src="/logo.png" alt="ROOSH" className="h-7" />
        <button
          onClick={onLogout}
          className="text-xs font-bold uppercase tracking-widest text-gray-400 hover:text-gray-900 transition-colors"
        >
          Sign out
        </button>
      </header>

      {/* Split layout */}
      <div className="flex-1 flex overflow-hidden">

        {/* Left panel — tool list */}
        <div className="w-72 border-r border-gray-100 flex flex-col p-6 overflow-y-auto flex-shrink-0">
          <h1
            style={{ fontFamily: "'Space Grotesk', sans-serif" }}
            className="text-xl font-extrabold tracking-tight text-gray-900 mb-1"
          >
            Roosh LP Platform
          </h1>
          <p className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-6">
            Select a workspace
          </p>

          <div className="flex flex-col gap-1.5">
            {agents.map(agent => (
              <button
                key={agent.id}
                onClick={() => agent.ready && onSelect(agent.id)}
                disabled={!agent.ready}
                className={`
                  flex items-center gap-3 px-3 py-3 border-2 border-transparent text-left
                  transition-all duration-200
                  ${agent.ready
                    ? 'cursor-pointer hover:scale-[1.02] hover:shadow-md hover:border-[#1400FF]'
                    : 'cursor-not-allowed opacity-40'
                  }
                `}
              >
                <div
                  className="w-8 h-8 flex items-center justify-center flex-shrink-0"
                  style={{ backgroundColor: agent.ready ? '#1400FF' : '#e5e7eb' }}
                >
                  <span className={agent.ready ? 'text-white' : 'text-gray-400'}>{agent.icon}</span>
                </div>
                <div className="min-w-0 flex-1">
                  <div
                    style={{ fontFamily: "'Space Grotesk', sans-serif" }}
                    className="font-bold text-gray-900 text-sm leading-tight"
                  >
                    {agent.name}
                  </div>
                  <div className="text-xs text-gray-400 leading-snug mt-0.5 line-clamp-2">
                    {agent.description}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Right panel — Fund II overview */}
        <div className="flex-1 overflow-y-auto bg-gray-50 flex items-center justify-center p-10">
          <div className="w-full max-w-2xl flex flex-col gap-0 border border-gray-200 bg-white">

            {/* Fund II title */}
            <div className="px-8 py-6 border-b border-gray-200">
              <div style={{ fontFamily: "'Space Grotesk', sans-serif" }} className="flex items-baseline gap-3">
                <span style={{ color: '#1400FF' }} className="text-4xl font-extrabold leading-none">€50M</span>
                <span className="text-3xl font-extrabold text-gray-900">Fund II</span>
              </div>
            </div>

            {/* Rows */}
            <div className="flex flex-col divide-y divide-gray-200">
              {fundRows.map(row => (
                <div key={row.label} className="flex items-stretch">
                  {/* Vertical label */}
                  <div
                    className="flex items-center justify-center px-3 flex-shrink-0"
                    style={{ backgroundColor: '#1400FF', writingMode: 'vertical-rl', textOrientation: 'mixed' }}
                  >
                    <span
                      className="text-white text-xs font-black tracking-widest uppercase"
                      style={{ transform: 'rotate(180deg)' }}
                    >
                      {row.label}
                    </span>
                  </div>

                  {/* Content */}
                  <div className="flex-1 flex flex-col justify-center px-6 py-5">
                    <p className="text-sm text-gray-700 leading-relaxed">{row.text}</p>
                    <div className="mt-3">
                      <span
                        className="text-xs font-bold uppercase tracking-widest px-2 py-1"
                        style={{ color: '#1400FF', backgroundColor: 'rgba(20,0,255,0.06)' }}
                      >
                        {row.badge}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

          </div>
        </div>

      </div>

      <PortfolioTicker />
    </div>
  )
}
