/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: 'selector',
  theme: {
    extend: {
      colors: {
        'dark-blue': {
          50: '#f0f4ff',
          100: '#e0e9ff',
          200: '#c7d9ff',
          300: '#a4c0ff',
          400: '#7a9eff',
          500: '#5b7cff',
          600: '#3f5aff',
          700: '#2d3eff',
          800: '#1e27d4',
          900: '#0f1694',
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'gradient-dark': 'linear-gradient(135deg, #0f1694 0%, #1e27d4 25%, #2d3eff 50%, #5b7cff 75%, #a78bfa 100%)',
        'gradient-dark-light': 'linear-gradient(135deg, #1e1b4b 0%, #312e81 25%, #3730a3 50%, #6366f1 75%, #c4b5fd 100%)',
      },
      backdropBlur: {
        'xs': '2px',
      },
    },
  },
  plugins: [],
}
