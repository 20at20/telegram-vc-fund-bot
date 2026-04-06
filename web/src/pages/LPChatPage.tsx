import { useState, useRef, useEffect, FormEvent } from 'react'
import MessageBubble from '../components/MessageBubble'
import TypingIndicator from '../components/TypingIndicator'
import PortfolioTicker from '../components/PortfolioTicker'
import SuggestionChips from '../components/SuggestionChips'

const API = import.meta.env.VITE_API_URL || ''

interface Message {
  role: 'user' | 'assistant'
  content: string
}

interface Props {
  token: string
  onLogout: () => void
  onBack: () => void
}

const WELCOME_SUGGESTIONS = [
  { label: 'Fund strategy', query: 'What is the fund strategy?' },
  { label: 'Team', query: 'Tell me about the team' },
  { label: 'Fund terms', query: 'What are the fund terms?' },
  { label: 'Portfolio companies', query: 'What companies are in the portfolio?' },
  { label: 'Focus sectors', query: 'What sectors does the fund focus on?' },
]

export default function LPChatPage({ token, onLogout, onBack }: Props) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content:
        "Hi! I'm the Fund II Info Assistant. Ask me anything about the fund — strategy, team, portfolio companies, or terms.",
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [streaming, setStreaming] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const sendMessage = async (text: string) => {
    const trimmed = text.trim()
    if (!trimmed || loading || streaming) return

    setMessages(prev => [...prev, { role: 'user', content: trimmed }])
    setInput('')
    setLoading(true)

    const history = messages.slice(-6).map(m => ({
      role: m.role,
      content: m.content,
    }))

    try {
      const res = await fetch(`${API}/api/lp-chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ message: trimmed, conversation_history: history }),
      })

      if (res.status === 401) {
        onLogout()
        return
      }

      if (!res.body) throw new Error('No response body')

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      // Add empty assistant message — will be filled token by token
      setMessages(prev => [...prev, { role: 'assistant', content: '' }])
      setLoading(false)
      setStreaming(true)

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const payload = line.slice(6)
          if (payload === '[DONE]') break
          try {
            const { c } = JSON.parse(payload)
            if (c) {
              setMessages(prev => {
                const last = prev[prev.length - 1]
                return [...prev.slice(0, -1), { ...last, content: last.content + c }]
              })
            }
          } catch {}
        }
      }
    } catch {
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: 'Sorry, something went wrong. Please try again.' },
      ])
    } finally {
      setLoading(false)
      setStreaming(false)
      inputRef.current?.focus()
    }
  }

  const send = (e: FormEvent) => {
    e.preventDefault()
    sendMessage(input)
  }

  const showWelcomeChips = messages.length === 1 && !loading

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 border-b-2 border-gray-100 bg-white">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="text-gray-400 hover:text-gray-900 transition-colors"
            title="Back to tools"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <img src="/logo.png" alt="ROOSH" className="h-7" />
          <span className="font-black uppercase tracking-widest text-sm text-gray-900">Fund II Info Assistant</span>
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
        {messages.map((msg, i) => {
          const isThinking = streaming && i === messages.length - 1 && msg.role === 'assistant' && msg.content === ''
          if (isThinking) {
            return (
              <div key={i} className="flex justify-start">
                <div className="w-7 h-7 flex items-center justify-center mr-2 mt-1 flex-shrink-0" style={{ backgroundColor: '#1400FF' }}>
                  <svg className="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <div className="max-w-[80%] px-4 py-3 text-sm bg-gray-50 border-l-2" style={{ borderLeftColor: '#1400FF' }}>
                  <em className="text-gray-400 animate-pulse">Thinking...</em>
                </div>
              </div>
            )
          }
          return <MessageBubble key={i} role={msg.role} content={msg.content} />
        })}
        {loading && !streaming && <TypingIndicator />}

        {showWelcomeChips && (
          <SuggestionChips
            suggestions={WELCOME_SUGGESTIONS}
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
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Ask about Fund II..."
            disabled={loading || streaming}
            className="flex-1 border-2 border-r-0 px-4 py-3 text-gray-900 placeholder-gray-300 focus:outline-none transition disabled:opacity-50"
            style={{ borderColor: '#1400FF' }}
          />
          <button
            type="submit"
            disabled={loading || streaming || !input.trim()}
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
