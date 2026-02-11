import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      animation: {
        'bounce-dot': 'bounce 1s infinite',
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
