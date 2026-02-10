import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      animation: {
        'bounce-dot': 'bounce 1s infinite',
      },
    },
  },
  plugins: [],
} satisfies Config
