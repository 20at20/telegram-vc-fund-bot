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

  if (loading || n === 0) return null

  // Temporary plain render — replaced with the real 3-slot carousel in Task 2.
  return (
    <div>
      <p>{deals[currentIndex]?.company}</p>
    </div>
  )
}
