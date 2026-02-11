import ReactMarkdown from 'react-markdown'
import { markdownComponents } from './markdownConfig'

interface Props {
  data: Record<string, any>
  fallbackText: string
}

export default function TableView({ data, fallbackText }: Props) {
  const columns: string[] = data.columns
  const rows: Record<string, any>[] = data.rows

  if (!columns || !rows || rows.length === 0) {
    return <ReactMarkdown components={markdownComponents}>{fallbackText}</ReactMarkdown>
  }

  // Single-row result → vertical key-value card
  if (rows.length === 1) {
    const row = rows[0]
    return (
      <div>
        <div className="space-y-2 mb-3">
          {columns.map((col: string) => (
            <div key={col} className="flex justify-between gap-4 py-1 border-b border-gray-100 last:border-0">
              <span className="text-xs font-bold uppercase tracking-wider text-gray-400 flex-shrink-0">{col}</span>
              <span className="text-sm text-gray-900 text-right">{row[col] ?? ''}</span>
            </div>
          ))}
        </div>
        <ReactMarkdown components={markdownComponents}>{fallbackText}</ReactMarkdown>
      </div>
    )
  }

  return (
    <div>
      <div className="overflow-x-auto mb-3">
        <table className="w-full text-xs border-collapse">
          <thead>
            <tr>
              {columns.map((col: string) => (
                <th
                  key={col}
                  className="text-left px-3 py-2 font-bold uppercase tracking-wider text-gray-500 border-b-2"
                  style={{ borderBottomColor: '#1400FF' }}
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row: Record<string, any>, i: number) => (
              <tr key={i} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                {columns.map((col: string) => (
                  <td key={col} className="px-3 py-2 text-gray-700 whitespace-nowrap">
                    {row[col] ?? ''}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <ReactMarkdown components={markdownComponents}>{fallbackText}</ReactMarkdown>
    </div>
  )
}
