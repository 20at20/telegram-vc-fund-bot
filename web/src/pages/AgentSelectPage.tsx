import { useState, useEffect } from 'react'
import PortfolioTicker from '../components/PortfolioTicker'

const API = import.meta.env.VITE_API_URL || ''

interface Metric {
  metric: string
  value: string | number
  period: string
}

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
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
    description: 'Search 20K+ people in my network. Filter by industry, country, and stage.',
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
]

interface Props {
  token: string
  onSelect: (agentId: string) => void
  onLogout: () => void
}

export default function AgentSelectPage({ token, onSelect, onLogout }: Props) {
  const [metrics, setMetrics] = useState<Metric[]>([])
  const [metricsLoading, setMetricsLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(`${API}/api/fund_metrics`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (res.ok) {
          const data = await res.json()
          setMetrics(data.metrics || [])
        }
      } catch { /* ignore */ } finally {
        setMetricsLoading(false)
      }
    }
    load()
  }, [token])

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

        {/* Right panel — fund metrics dashboard */}
        <div className="flex-1 p-8 bg-gray-50 overflow-y-auto">
          <p className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-6">
            Fund Overview
          </p>

          {metricsLoading ? (
            <div className="grid grid-cols-3 gap-4">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="h-28 bg-gray-200 animate-pulse" />
              ))}
            </div>
          ) : metrics.length === 0 ? (
            <p className="text-sm text-gray-400">No metrics available.</p>
          ) : (
            <div className="grid grid-cols-3 gap-4">
              {metrics.map(m => (
                <div key={m.metric} className="bg-white border border-gray-200 p-6">
                  <div className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-2">
                    {m.metric}
                  </div>
                  <div
                    className="text-3xl font-black"
                    style={{ color: '#1400FF' }}
                  >
                    {m.value}
                  </div>
                  <div className="text-xs text-gray-400 mt-1">{m.period}</div>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>

      <PortfolioTicker />
    </div>
  )
}
