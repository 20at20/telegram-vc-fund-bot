import { useEffect, useState } from 'react'

const API = import.meta.env.VITE_API_URL || ''

interface Props {
  token: string
  onLogout: () => void
}

interface NewsItem {
  category: string
  company: string
  description: string
  link: string
}

const CATEGORY_COLORS: Record<string, string> = {
  'Big Round': 'text-[#1400FF]',
  'M&A': 'text-[#E8321A]',
}

function categoryColor(category: string): string {
  return CATEGORY_COLORS[category] || 'text-gray-500'
}

function isSafeUrl(url: string): boolean {
  try {
    return ['http:', 'https:'].includes(new URL(url).protocol)
  } catch {
    return false
  }
}

export default function MarketNewsTicker({ token, onLogout }: Props) {
  const [items, setItems] = useState<NewsItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const res = await fetch(`${API}/api/market-news`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (res.status === 401) {
          onLogout()
          return
        }
        const data = await res.json()
        setItems(data.items || [])
      } catch {
        setItems([])
      } finally {
        setLoading(false)
      }
    }
    fetchNews()
  }, [token, onLogout])

  if (loading || items.length === 0) return null

  const renderItem = (item: NewsItem, key: string) => {
    const content = (
      <>
        <div className={`text-[10px] font-bold uppercase tracking-widest ${categoryColor(item.category)}`}>
          {item.category}
        </div>
        <div className="font-black text-sm text-gray-900 mt-0.5">{item.company}</div>
        <p className="text-xs text-gray-500 leading-snug line-clamp-2 mt-0.5">{item.description}</p>
      </>
    )
    return item.link && isSafeUrl(item.link) ? (
      <a
        key={key}
        href={item.link}
        target="_blank"
        rel="noopener noreferrer"
        className="block py-3 border-b border-gray-100 hover:bg-gray-50 transition-colors"
      >
        {content}
      </a>
    ) : (
      <div key={key} className="py-3 border-b border-gray-100">
        {content}
      </div>
    )
  }

  return (
    <div className="relative w-full h-full overflow-hidden">
      <div className="animate-ticker-vertical hover:[animation-play-state:paused]">
        {items.map((item, i) => renderItem(item, `a-${i}`))}
        {items.map((item, i) => renderItem(item, `b-${i}`))}
      </div>
    </div>
  )
}
