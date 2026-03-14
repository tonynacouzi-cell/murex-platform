/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eef4ff',
          100: '#d9e8ff',
          200: '#bcd4fe',
          300: '#8eb8fc',
          400: '#5990f8',
          500: '#3470f2',
          600: '#1E3A5F',
          700: '#1a3356',
          800: '#162c4a',
          900: '#0f1e33',
        },
        accent: {
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
        }
      },
      fontFamily: {
        sans: ['Inter var', 'Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 1px 3px 0 rgba(0,0,0,0.06), 0 1px 2px -1px rgba(0,0,0,0.06)',
        'card-hover': '0 4px 12px 0 rgba(0,0,0,0.08), 0 2px 4px -1px rgba(0,0,0,0.06)',
        'elevated': '0 10px 40px -10px rgba(30,58,95,0.15)',
      }
    },
  },
  plugins: [],
}
