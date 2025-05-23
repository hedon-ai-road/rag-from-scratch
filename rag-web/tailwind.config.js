/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
    "./src-tauri/**/*.{html,rs}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}