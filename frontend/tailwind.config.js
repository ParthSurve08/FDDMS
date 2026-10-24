/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        forest: '#234B36',
        cream: '#F5EBD7',
        warmwhite: '#FFFCF5',
        darkgreen: '#183629',
        softsage: '#DCE8D8',
      }
    },
  },
  plugins: [],
}
