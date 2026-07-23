import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      animation: {
        'bounce-dot': 'bounce 1s infinite',
        'ticker': 'ticker 60s linear infinite',
        'ticker-vertical': 'ticker-vertical 30s linear infinite',
      },
      keyframes: {
        ticker: {
          '0%': { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(-50%)' },
        },
        'ticker-vertical': {
          '0%': { transform: 'translateY(0)' },
          '100%': { transform: 'translateY(-50%)' },
        },
      },
      colors: {
        brand: {
          blue: '#1400FF',
          red: '#E8321A',
          text: '#111111',
        },
      },
    },
  },
  plugins: [],
} satisfies Config
