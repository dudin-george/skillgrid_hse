/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#4da6ff',
          DEFAULT: '#0077e6',
          dark: '#004d99',
        },
        secondary: {
          light: '#8c8c8c',
          DEFAULT: '#595959',
          dark: '#333333',
        },
      },
    },
  },
  plugins: [],
} 