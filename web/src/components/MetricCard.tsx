import ReactMarkdown from 'react-markdown'
import { markdownComponents } from './markdownConfig'

interface Props {
  data: Record<string, any>
  fallbackText: string
}

export default function MetricCard({ data, fallbackText }: Props) {
  const metricName = data.metric || data.field || 'Metric'
  const value = data.value
  const subtitle = data.period || (data.aggregation ? `${data.aggregation} of ${data.data_points} companies` : '')

  if (value === undefined || value === null) {
    return <ReactMarkdown components={markdownComponents}>{fallbackText}</ReactMarkdown>
  }

  return (
    <div>
      <div className="border-l-2 pl-4 py-2 mb-3" style={{ borderLeftColor: '#1400FF' }}>
        <p className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-1">{metricName}</p>
        <p className="text-2xl font-black text-gray-900">{String(value)}</p>
        {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
      </div>
    </div>
  )
}
