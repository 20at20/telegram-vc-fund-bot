import PortfolioTicker from '../components/PortfolioTicker'
import DealsCarousel from '../components/DealsCarousel'

const sections = [
  {
    title: 'Get to know more about Fund II',
    tools: [
      {
        id: 'fund-docs',
        name: 'Fund II Info Assistant',
        description: 'Ask any questions about Fund II, like strategy and terms.',
        icon: (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        ),
        ready: true,
      },
      {
        id: 'fund-data',
        name: 'Fund Data',
        description: 'Access fund decks and monthly newsletters.',
        icon: (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
        ),
        ready: true,
      },
    ],
  },
  {
    title: 'Extend your network with us',
    tools: [
      {
        id: 'companies',
        name: 'Network',
        description: 'Look for any connections that you need in our network.',
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
        id: 'experts',
        name: 'Experts',
        description: 'Find domain experts in our close network.',
        icon: (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <circle cx="12" cy="8" r="6" strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11" />
          </svg>
        ),
        ready: true,
      },
    ],
  },
  {
    title: 'Find and analyse investment opportunities',
    tools: [
      {
        id: 'deals',
        name: 'Deals on the Table',
        description: 'Check active deals pipeline for potential co-investments.',
        icon: (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M13 2 3 14h9l-1 8 10-12h-9l1-8z" />
          </svg>
        ),
        ready: true,
      },
      {
        id: 'submit-deal',
        name: 'Submit a Deal',
        description: 'Share a deal with us if you want to get feedback.',
        icon: (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
          </svg>
        ),
        ready: true,
      },
    ],
  },
]


interface Props {
  token: string
  onSelect: (agentId: string) => void
  onLogout: () => void
}

export default function AgentSelectPage({ token, onSelect, onLogout }: Props) {
  return (
    <div className="h-screen bg-white flex flex-col overflow-hidden">
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
        <div className="w-96 border-r border-gray-100 flex flex-col p-6 overflow-y-auto flex-shrink-0">
          <h1
            style={{ fontFamily: "'Space Grotesk', sans-serif" }}
            className="text-xl font-extrabold tracking-tight text-gray-900 mb-1"
          >
            Roosh LP Platform
          </h1>

          <div className="flex flex-col gap-6">
            {sections.map(section => (
              <div key={section.title}>
                <p className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-2 px-1">
                  {section.title}
                </p>
                <div className="flex flex-col gap-1.5">
                  {section.tools.map(tool => (
                    <button
                      key={tool.id}
                      onClick={() => tool.ready && onSelect(tool.id)}
                      disabled={!tool.ready}
                      className={`
                        flex items-center gap-3 px-3 py-3 border-2 border-transparent text-left
                        transition-all duration-200
                        ${tool.ready
                          ? 'cursor-pointer hover:scale-[1.02] hover:shadow-md hover:border-[#1400FF]'
                          : 'cursor-not-allowed opacity-40'
                        }
                      `}
                    >
                      <div
                        className="w-8 h-8 flex items-center justify-center flex-shrink-0"
                        style={{ backgroundColor: tool.ready ? '#1400FF' : '#e5e7eb' }}
                      >
                        <span className={tool.ready ? 'text-white' : 'text-gray-400'}>{tool.icon}</span>
                      </div>
                      <div className="min-w-0 flex-1">
                        <div
                          style={{ fontFamily: "'Space Grotesk', sans-serif" }}
                          className="font-bold text-gray-900 text-sm leading-tight"
                        >
                          {tool.name}
                        </div>
                        <div className="text-xs text-gray-400 leading-snug mt-0.5 line-clamp-2">
                          {tool.description}
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right panel — deals carousel (top) + placeholder (bottom) */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="h-1/2 overflow-y-auto bg-gray-50 flex flex-col items-center justify-center p-6">
            <h2 className="font-black uppercase tracking-widest text-sm text-gray-900 self-start mb-4">
              Deals on the Table
            </h2>
            <DealsCarousel token={token} onLogout={onLogout} />
          </div>
          <div className="h-1/2 overflow-y-auto bg-gray-50 border-t border-gray-100" />
        </div>

      </div>

      <PortfolioTicker />
    </div>
  )
}
