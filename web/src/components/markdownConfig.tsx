import type { Components } from 'react-markdown'

export const markdownComponents: Components = {
  p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
  strong: ({ children }) => <strong className="font-bold text-gray-900">{children}</strong>,
  code: ({ children }) => (
    <code className="bg-gray-200 px-1.5 py-0.5 text-xs font-mono" style={{ color: '#1400FF' }}>{children}</code>
  ),
  ul: ({ children }) => <ul className="list-disc list-outside pl-5 space-y-0.5 my-1">{children}</ul>,
  ol: ({ children }) => <ol className="list-decimal list-outside pl-5 space-y-0.5 my-1">{children}</ol>,
  li: ({ children }) => {
    // Only suppress li when ALL children are empty/whitespace strings.
    // If any child is a React element (bold, link, etc.) keep the item.
    const allWhitespace = Array.isArray(children)
      ? children.every(c => typeof c === 'string' && !c.trim())
      : typeof children === 'string' && !children.trim()
    if (allWhitespace) return null
    return <li className="text-gray-700">{children}</li>
  },
}
