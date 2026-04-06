import { useState, useRef, useEffect, FormEvent } from 'react'
import MessageBubble from '../components/MessageBubble'
import TypingIndicator from '../components/TypingIndicator'
import PortfolioTicker from '../components/PortfolioTicker'
import SuggestionChips from '../components/SuggestionChips'

const API = import.meta.env.VITE_API_URL || ''

interface Message {
  role: 'user' | 'assistant'
  content: string
  queryType?: string
  structuredData?: Record<string, any> | null
  options?: Array<{ label: string; query: string }>
}

interface Props {
  token: string
  onLogout: () => void
  onBack: () => void
}

const WELCOME_SUGGESTIONS = [
  { label: 'Current TVPI', query: 'What is our current TVPI?' },
  { label: 'Top 5 by return', query: 'Top 5 companies by return' },
  { label: 'Fintech companies', query: 'Show fintech companies' },
  { label: 'Fund IRR', query: "What's the fund IRR?" },
  { label: 'Recent investments', query: 'Show our 5 most recent investments' },
]

function getFollowUpSuggestions(queryType: string): Array<{ label: string; query: string }> {
  switch (queryType) {
    case 'fund_metric':
      return [
        { label: 'Show trend over time', query: 'Show me the trend over time' },
        { label: 'Compare with DPI', query: 'Compare TVPI and DPI over time' },
      ]
    case 'portfolio_ranking':
      return [
        { label: 'Bottom performers', query: 'Show worst performing companies' },
        { label: 'By investment size', query: 'Top 5 companies by investment size' },
      ]
    case 'portfolio_list':
      return [
        { label: 'Top by return', query: 'Top 5 companies by return' },
        { label: 'Average check size', query: "What's the average check size?" },
      ]
    case 'time_series':
      return [
        { label: 'Current value', query: 'What is the current value?' },
        { label: 'Compare metrics', query: 'Compare TVPI and DPI over time' },
      ]
    default:
      return []
  }
}

export default function ChatPage({ token, onLogout, onBack }: Props) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "Hi! I'm your RV Fund Assistant. Ask me anything about the portfolio — metrics, rankings, company details, or fund performance.",
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const sendMessage = async (text: string) => {
    const trimmed = text.trim()
    if (!trimmed || loading) return

    setMessages(prev => [...prev, { role: 'user', content: trimmed }])
    setInput('')
    setLoading(true)

    const history = messages.slice(-6).map(m => ({
      role: m.role,
      content: m.content,
    }))

    // Find the last assistant message with structured data (table results)
    const lastAssistantWithData = [...messages].reverse().find(
      m => m.role === 'assistant' && m.structuredData?.rows
    )
    const previousResult = lastAssistantWithData?.structuredData || null

    try {
      const res = await fetch(`${API}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ message: trimmed, conversation_history: history, previous_result: previousResult }),
      })

      if (res.status === 401) {
        onLogout()
        return
      }

      const data = await res.json()
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response,
        queryType: data.query_type,
        structuredData: data.structured_data || null,
        options: data.options || null,
      }])
    } catch {
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: 'Sorry, something went wrong. Please try again.' },
      ])
    } finally {
      setLoading(false)
    }
  }

  const send = (e: FormEvent) => {
    e.preventDefault()
    sendMessage(input)
  }

  const lastMsg = messages[messages.length - 1]
  const showWelcomeChips = messages.length === 1 && !loading
  const followUpSuggestions = !loading && messages.length > 1 && lastMsg.role === 'assistant'
    ? (lastMsg.options || getFollowUpSuggestions(lastMsg.queryType || ''))
    : []

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
          <span className="font-black uppercase tracking-widest text-sm text-gray-900">RV Fund</span>
        </div>
        <button
          onClick={onLogout}
          className="text-xs font-bold uppercase tracking-widest text-gray-400 hover:text-gray-900 transition-colors"
        >
          Sign out
        </button>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4 max-w-3xl w-full mx-auto">
        {messages.map((msg, i) => (
          <MessageBubble
            key={i}
            role={msg.role}
            content={msg.content}
            queryType={msg.queryType}
            structuredData={msg.structuredData}
          />
        ))}
        {loading && <TypingIndicator />}

        {showWelcomeChips && (
          <SuggestionChips
            suggestions={WELCOME_SUGGESTIONS}
            onSelect={sendMessage}
            disabled={loading}
          />
        )}

        {!showWelcomeChips && followUpSuggestions.length > 0 && (
          <SuggestionChips
            suggestions={followUpSuggestions}
            onSelect={sendMessage}
            disabled={loading}
          />
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t-2 border-gray-100 bg-white px-4 py-4">
        <form onSubmit={send} className="max-w-3xl mx-auto flex gap-0">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Ask about the fund or portfolio..."
            disabled={loading}
            className="flex-1 border-2 border-gray-200 border-r-0 px-4 py-3 text-gray-900 placeholder-gray-300 focus:outline-none transition disabled:opacity-50"
            onFocus={e => (e.target.style.borderColor = '#1400FF')}
            onBlur={e => (e.target.style.borderColor = '#e5e7eb')}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="text-white px-5 py-3 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed flex items-center"
            style={{ backgroundColor: '#1400FF' }}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </form>
      </div>

      <PortfolioTicker />
    </div>
  )
}
