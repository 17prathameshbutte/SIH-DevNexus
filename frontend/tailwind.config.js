/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        midnight: '#0a0a0f',
        'dark-surface': '#111827',
        panel: '#1a1f2e',
        'accent-green': '#00ff88',
        'accent-amber': '#ffb800',
        'accent-red': '#ff3366',
        'accent-blue': '#3b82f6',
        'accent-cyan': '#06b6d4',
        'accent-purple': '#a855f7'
      }
    },
  },
  plugins: [],
}
