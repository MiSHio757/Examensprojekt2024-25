/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html", // Kollar index.html i roten av frontend
    "./src/**/*.{vue,js,ts,jsx,tsx}", // Kollar alla relevanta filer i src-mappen och dess undermappar
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
