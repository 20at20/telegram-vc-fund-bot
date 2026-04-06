import type { Components } from 'react-markdown'

export const markdownComponents: Components = {
  p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
  strong: ({ children }) => <strong className="font-bold text-gray-900">{children}</strong>,
  code: ({ children }) => (
    <code className="bg-gray-200 px-1.5 py-0.5 text-xs font-mono" style={{ color: '#1400FF' }}>{children}</code>
  ),
  ul: ({ children }) => <ul className="list-disc list-inside space-y-1 my-2">{children}</ul>,
  ol: ({ children }) => <ol className="list-decimal list-inside space-y-1 my-2">{children}</ol>,
  li: ({ children }) => {
    const text = Array.isArray(children)
      ? children.map(c => (typeof c === 'string' ? c : '')).join('')
      : typeof children === 'string' ? children : ''
    if (!text.trim()) return null
    return <li className="text-gray-700">{children}</li>
  },
}
