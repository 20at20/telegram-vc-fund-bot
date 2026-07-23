import { useEffect, useState } from 'react'

const API = import.meta.env.VITE_API_URL || ''

interface Props {
  token: string
  onLogout: () => void
}

interface Deal {
  company: string
  industry: string
  round: string
  description: string
  link: string
}

const CARD_SPACING = 240 // px offset for side slots relative to center

export default function DealsCarousel({ token, onLogout }: Props) {
  const [deals, setDeals] = useState<Deal[]>([])
  const [loading, setLoading] = useState(true)
  const [currentIndex, setCurrentIndex] = useState(0)

  useEffect(() => {
    const fetchDeals = async () => {
      try {
        const res = await fetch(`${API}/api/deals`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (res.status === 401) {
          onLogout()
          return
        }
        const data = await res.json()
        const columns: string[] = data.columns || []
        const rows: Record<string, string>[] = data.rows || []
        const links: Record<string, string> = data.links || {}

        const companyCol = columns.find(c => c.toLowerCase().includes('company')) || ''
        const industryCol = columns.find(c => c.toLowerCase().includes('industry')) || ''
        const roundCol = columns.find(c => c.toLowerCase().includes('round') && !c.toLowerCase().includes('size')) || ''
        const descCol = columns.find(c => c.toLowerCase().includes('descri')) || ''

        const parsed: Deal[] = rows
          .map(row => {
            const company = (row[companyCol] || '').trim()
            return {
              company,
              industry: (row[industryCol] || '').trim(),
              round: (row[roundCol] || '').trim(),
              description: (row[descCol] || '').trim(),
              link: links[company] || '',
            }
          })
          .filter(d => d.company)

        setDeals(parsed)
      } catch {
        setDeals([])
      } finally {
        setLoading(false)
      }
    }
    fetchDeals()
  }, [token, onLogout])

  const n = deals.length

  const circularDistance = (idx: number) => {
    let d = idx - currentIndex
    if (d > n / 2) d -= n
    if (d < -n / 2) d += n
    return d
  }

  const goPrev = () => setCurrentIndex(i => (i - 1 + n) % n)
  const goNext = () => setCurrentIndex(i => (i + 1) % n)

  const handleCenterClick = () => {
    const link = deals[currentIndex]?.link
    if (link) window.open(link, '_blank', 'noopener,noreferrer')
  }

  if (loading || n === 0) return null

  // Which deals are visible this render, and at what offset from center (d).
  // n === 2 is special-cased: both side slots show the single "other" deal
  // (there's no well-defined left vs. right for a 2-item circular list).
  type Slot = { idx: number; d: number; key: string }
  const slots: Slot[] = []
  if (n === 1) {
    slots.push({ idx: 0, d: 0, key: 'center' })
  } else if (n === 2) {
    const otherIdx = (currentIndex + 1) % 2
    slots.push({ idx: otherIdx, d: -1, key: 'left' })
    slots.push({ idx: currentIndex, d: 0, key: 'center' })
    slots.push({ idx: otherIdx, d: 1, key: 'right' })
  } else {
    for (let idx = 0; idx < n; idx++) {
      const d = circularDistance(idx)
      if (Math.abs(d) <= 1) {
        slots.push({ idx, d, key: `slot-${idx}` })
      }
    }
  }

  return (
    <div className="relative w-full max-w-2xl mx-auto">
      <div className="relative h-64">
        {slots.map(({ idx, d, key }) => {
          const deal = deals[idx]
          const isCenter = d === 0
          return (
            <div
              key={key}
              onClick={isCenter ? handleCenterClick : () => setCurrentIndex(idx)}
              style={{
                transform: `translate(calc(-50% + ${d * CARD_SPACING}px), -50%) scale(${isCenter ? 1 : 0.85})`,
                opacity: isCenter ? 1 : 0.5,
                zIndex: isCenter ? 20 : 10,
              }}
              className={`
                absolute top-1/2 left-1/2 w-64 border-2 border-gray-200 bg-white p-5
                transition-all duration-500 ease-out
                ${isCenter
                  ? deal.link ? 'cursor-pointer hover:border-[#1400FF]' : 'cursor-default'
                  : 'cursor-pointer'}
              `}
            >
              <div className="flex flex-wrap gap-2 mb-3">
                {deal.industry && (
                  <span className="text-[10px] font-bold uppercase tracking-widest text-[#1400FF]">
                    {deal.industry}
                  </span>
                )}
                {deal.round && (
                  <span className="text-[10px] font-bold uppercase tracking-widest text-gray-400">
                    {deal.round}
                  </span>
                )}
              </div>
              <div
                style={{ fontFamily: "'Space Grotesk', sans-serif" }}
                className="font-black text-lg text-gray-900 mb-2"
              >
                {deal.company}
              </div>
              {deal.description && (
                <p className="text-xs text-gray-500 leading-snug line-clamp-3">
                  {deal.description}
                </p>
              )}
            </div>
          )
        })}
      </div>

      {n > 1 && (
        <div className="flex items-center justify-center gap-8 mt-4">
          <button
            onClick={goPrev}
            aria-label="Previous deal"
            className="text-gray-400 hover:text-[#1400FF] transition-colors"
          >
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <button
            onClick={goNext}
            aria-label="Next deal"
            className="text-gray-400 hover:text-[#1400FF] transition-colors"
          >
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      )}
    </div>
  )
}
