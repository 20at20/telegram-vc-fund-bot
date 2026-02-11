import ReactMarkdown from 'react-markdown'

interface Props {
  role: 'user' | 'assistant'
  content: string
}

export default function MessageBubble({ role, content }: Props) {
  const isUser = role === 'user'

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
        {isUser ? (
          <p className="whitespace-pre-wrap">{content}</p>
        ) : (
          <ReactMarkdown
            components={{
              p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
              strong: ({ children }) => <strong className="font-bold text-gray-900">{children}</strong>,
              code: ({ children }) => (
                <code className="bg-gray-200 px-1.5 py-0.5 text-xs font-mono" style={{ color: '#1400FF' }}>{children}</code>
              ),
              ul: ({ children }) => <ul className="list-disc list-inside space-y-1 my-2">{children}</ul>,
              ol: ({ children }) => <ol className="list-decimal list-inside space-y-1 my-2">{children}</ol>,
              li: ({ children }) => <li className="text-gray-700">{children}</li>,
            }}
          >
            {content}
          </ReactMarkdown>
        )}
      </div>
    </div>
  )
}
