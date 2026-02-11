interface Suggestion {
  label: string
  query: string
}

interface Props {
  suggestions: Suggestion[]
  onSelect: (query: string) => void
  disabled?: boolean
}

export default function SuggestionChips({ suggestions, onSelect, disabled }: Props) {
  return (
    <div className="flex flex-wrap gap-2 mt-3">
      {suggestions.map((s, i) => (
        <button
          key={i}
          onClick={() => onSelect(s.query)}
          disabled={disabled}
          className="text-xs font-medium px-3 py-1.5 border-2 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          style={{
            color: '#1400FF',
            borderColor: '#1400FF',
            backgroundColor: 'transparent',
          }}
          onMouseEnter={e => (e.currentTarget.style.backgroundColor = 'rgba(20, 0, 255, 0.05)')}
          onMouseLeave={e => (e.currentTarget.style.backgroundColor = 'transparent')}
        >
          {s.label}
        </button>
      ))}
    </div>
  )
}
