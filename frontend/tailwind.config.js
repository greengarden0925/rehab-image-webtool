/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,js}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["\"Noto Sans TC\"", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
