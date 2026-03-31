import { useState, useRef } from 'react'
import PortfolioTicker from '../components/PortfolioTicker'

const API = import.meta.env.VITE_API_URL || ''

interface Props {
  token: string
  onLogout: () => void
  onBack: () => void
}

export default function SubmitDealPage({ token, onLogout, onBack }: Props) {
  const [companyName, setCompanyName] = useState('')
  const [availableInfo, setAvailableInfo] = useState('')
  const [thoughts, setThoughts] = useState('')
  const [deckFile, setDeckFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')
  const fileRef = useRef<HTMLInputElement>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!companyName.trim()) return

    setLoading(true)
    setError('')
    try {
      const formData = new FormData()
      formData.append('company_name', companyName.trim())
      formData.append('available_info', availableInfo.trim())
      formData.append('thoughts', thoughts.trim())
      if (deckFile) formData.append('deck', deckFile)

      const res = await fetch(`${API}/api/submit_deal`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      })

      if (res.status === 401) { onLogout(); return }
      if (!res.ok) throw new Error('Request failed')

      setSuccess(true)
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const inputClass = `
    w-full border-2 border-gray-200 px-3 py-2 text-sm text-gray-900
    placeholder-gray-300 focus:outline-none transition
  `
  const focusStyle = {
    onFocus: (e: React.FocusEvent<HTMLElement>) => ((e.target as HTMLElement).style.borderColor = '#1400FF'),
    onBlur: (e: React.FocusEvent<HTMLElement>) => ((e.target as HTMLElement).style.borderColor = '#e5e7eb'),
  }

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 border-b-2 border-gray-100 bg-white">
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
          <span className="font-black uppercase tracking-widest text-sm text-gray-900">Submit a Deal</span>
        </div>
        <button
          onClick={onLogout}
          className="text-xs font-bold uppercase tracking-widest text-gray-400 hover:text-gray-900 transition-colors"
        >
          Sign out
        </button>
      </header>

      {/* Content */}
      <div className="flex-1 flex items-start justify-center px-4 py-10 overflow-auto">
        <div className="w-full max-w-xl">
          {success ? (
            <div className="text-center py-16">
              <div
                className="w-12 h-12 flex items-center justify-center mx-auto mb-4"
                style={{ backgroundColor: '#1400FF' }}
              >
                <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2
                style={{ fontFamily: "'Space Grotesk', sans-serif" }}
                className="text-2xl font-extrabold text-gray-900 mb-2"
              >
                Deal submitted!
              </h2>
              <p className="text-sm text-gray-400 mb-8">We'll review it shortly.</p>
              <button
                onClick={() => {
                  setSuccess(false)
                  setCompanyName('')
                  setAvailableInfo('')
                  setThoughts('')
                  setDeckFile(null)
                }}
                className="text-xs font-bold uppercase tracking-widest border-2 border-gray-200 px-5 py-2 text-gray-600 hover:border-[#1400FF] hover:text-[#1400FF] transition"
              >
                Submit another
              </button>
            </div>
          ) : (
            <>
              <h1
                style={{ fontFamily: "'Space Grotesk', sans-serif" }}
                className="text-2xl font-extrabold text-gray-900 mb-1"
              >
                Share a company
              </h1>
              <p className="text-sm text-gray-400 mb-8 uppercase tracking-widest font-bold">
                For ROOSH consideration
              </p>

              <form onSubmit={handleSubmit} className="flex flex-col gap-5">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-widest text-gray-500 mb-1.5">
                    Company name <span style={{ color: '#1400FF' }}>*</span>
                  </label>
                  <input
                    value={companyName}
                    onChange={e => setCompanyName(e.target.value)}
                    placeholder="e.g. Acme Corp"
                    required
                    className={inputClass}
                    {...focusStyle}
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-widest text-gray-500 mb-1.5">
                    Available information
                  </label>
                  <textarea
                    value={availableInfo}
                    onChange={e => setAvailableInfo(e.target.value)}
                    placeholder="Website, Crunchbase link, LinkedIn, funding round details..."
                    rows={3}
                    className={inputClass + ' resize-none'}
                    {...focusStyle}
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-widest text-gray-500 mb-1.5">
                    Attach deck
                  </label>
                  <input
                    ref={fileRef}
                    type="file"
                    accept=".pdf,.ppt,.pptx,.key"
                    className="hidden"
                    onChange={e => setDeckFile(e.target.files?.[0] ?? null)}
                  />
                  <button
                    type="button"
                    onClick={() => fileRef.current?.click()}
                    className="flex items-center gap-2 border-2 border-dashed border-gray-200 px-4 py-3 w-full text-left text-sm text-gray-400 hover:border-[#1400FF] hover:text-[#1400FF] transition"
                  >
                    <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                        d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                    </svg>
                    {deckFile ? (
                      <span className="text-gray-700 font-medium truncate">{deckFile.name}</span>
                    ) : (
                      'Click to attach PDF, PPT, or Keynote'
                    )}
                  </button>
                  {deckFile && (
                    <button
                      type="button"
                      onClick={() => { setDeckFile(null); if (fileRef.current) fileRef.current.value = '' }}
                      className="mt-1 text-xs text-gray-400 hover:text-gray-700 transition"
                    >
                      Remove file
                    </button>
                  )}
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-widest text-gray-500 mb-1.5">
                    Your thoughts
                  </label>
                  <textarea
                    value={thoughts}
                    onChange={e => setThoughts(e.target.value)}
                    placeholder="Why is this company interesting? What excites you about it?"
                    rows={4}
                    className={inputClass + ' resize-none'}
                    {...focusStyle}
                  />
                </div>

                {error && (
                  <p className="text-sm font-medium" style={{ color: '#E8321A' }}>{error}</p>
                )}

                <button
                  type="submit"
                  disabled={loading || !companyName.trim()}
                  className="py-3 text-sm font-black uppercase tracking-widest text-white transition disabled:opacity-40 disabled:cursor-not-allowed"
                  style={{ backgroundColor: '#1400FF' }}
                >
                  {loading ? 'Sending…' : 'Send for review'}
                </button>
              </form>
            </>
          )}
        </div>
      </div>

      <PortfolioTicker />
    </div>
  )
}
