import ReactMarkdown from 'react-markdown'
import { markdownComponents } from './markdownConfig'

interface Props {
  data: Record<string, any>
  fallbackText: string
}

export default function TimeSeriesTable({ data, fallbackText }: Props) {
  const series = data.time_series
  if (!series || !Array.isArray(series) || series.length === 0) {
    return <ReactMarkdown components={markdownComponents}>{fallbackText}</ReactMarkdown>
  }

  return (
    <div>
      <p className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-2">
        {data.metric || 'Time Series'}
      </p>
      <div className="overflow-x-auto mb-3">
        <table className="w-full text-xs border-collapse">
          <thead>
            <tr>
              <th className="text-left px-3 py-2 font-bold uppercase tracking-wider text-gray-500 border-b-2" style={{ borderBottomColor: '#1400FF' }}>Period</th>
              <th className="text-right px-3 py-2 font-bold uppercase tracking-wider text-gray-500 border-b-2" style={{ borderBottomColor: '#1400FF' }}>Value</th>
              <th className="text-center px-3 py-2 font-bold uppercase tracking-wider text-gray-500 border-b-2" style={{ borderBottomColor: '#1400FF' }}>Trend</th>
            </tr>
          </thead>
          <tbody>
            {series.map((point: any, i: number) => {
              const prev = i > 0 ? parseFloat(series[i - 1].value) : null
              const curr = parseFloat(point.value)
              const trend = prev === null ? '' : curr > prev ? '\u2191' : curr < prev ? '\u2193' : '\u2192'
              const trendColor = trend === '\u2191' ? '#16a34a' : trend === '\u2193' ? '#E8321A' : '#9ca3af'
              return (
                <tr key={i} className="border-b border-gray-100">
                  <td className="px-3 py-2 text-gray-700">{point.period}</td>
                  <td className="px-3 py-2 text-gray-900 font-medium text-right">{point.value}</td>
                  <td className="px-3 py-2 text-center font-bold" style={{ color: trendColor }}>{trend}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      <ReactMarkdown components={markdownComponents}>{fallbackText}</ReactMarkdown>
    </div>
  )
}
