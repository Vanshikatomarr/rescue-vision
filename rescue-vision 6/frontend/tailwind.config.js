/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        rescue: {
          700: '#cbd5e1',
          800: '#e2e8f0',
          850: '#f1f5f9',
          900: '#ffffff',
          950: '#f8fafc',
        },
        alert: {
          orange: '#ff6a00',
          cyan: '#0891b2',
          amber: '#f59e0b',
        },
      },
      boxShadow: {
        'glow-orange': '0 0 20px -3px rgba(255, 106, 0, 0.4)',
        'glow-cyan': '0 0 20px -3px rgba(0, 229, 255, 0.4)',
      },
    },
  },
  plugins: [],
}
