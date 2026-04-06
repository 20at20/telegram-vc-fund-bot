import ReactMarkdown from 'react-markdown'
import { markdownComponents } from './markdownConfig'
import TableView from './TableView'
import MetricCard from './MetricCard'
import TimeSeriesTable from './TimeSeriesTable'

interface Props {
  role: 'user' | 'assistant'
  content: string
  queryType?: string
  structuredData?: Record<string, any> | null
}

export default function MessageBubble({ role, content, queryType, structuredData }: Props) {
  const isUser = role === 'user'

  const renderContent = () => {
    if (isUser) {
      return <p className="whitespace-pre-wrap">{content}</p>
    }

    if (structuredData) {
      switch (queryType) {
        case 'portfolio_ranking':
        case 'portfolio_list':
        case 'company_detail':
          if (structuredData.type === 'table') {
            return <TableView data={structuredData} fallbackText={content} />
          }
          break
        case 'fund_metric':
        case 'portfolio_aggregation':
          if (structuredData.type === 'dict') {
            return <MetricCard data={structuredData} fallbackText={content} />
          }
          break
        case 'time_series':
          if (structuredData.type === 'dict' && structuredData.time_series) {
            return <TimeSeriesTable data={structuredData} fallbackText={content} />
          }
          break
      }
    }

    // Strip empty bullet points (lines with only a list marker and whitespace)
    const cleaned = content
      .replace(/^[\-\*\+]\s*$/gm, '')
      .replace(/\n{3,}/g, '\n\n')
      .trim()

    return (
      <ReactMarkdown components={markdownComponents}>
        {cleaned}
      </ReactMarkdown>
    )
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-7 h-7 flex items-center justify-center mr-2 mt-1 flex-shrink-0" style={{ backgroundColor: '#1400FF' }}>
          <svg className="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
      )}

      <div
        className={`max-w-[80%] px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? 'text-white'
            : 'bg-gray-50 text-gray-800 border-l-2'
        }`}
        style={isUser ? { backgroundColor: '#1400FF' } : { borderLeftColor: '#1400FF' }}
      >
        {renderContent()}
      </div>
    </div>
  )
}
