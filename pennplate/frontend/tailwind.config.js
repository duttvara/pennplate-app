/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#121212",
        oat: "#F1ECE3",
        card: "#FFFFFF",
        cranberry: "#8A1538",
        leaf: "#287A53",
        mint: "#E6F1EA",
        gold: "#E5E1DA",
        neutral: "#E5E1DA"
      },
      boxShadow: {
        soft: "0 1px 2px rgba(18, 18, 18, 0.08)"
      }
    }
  },
  plugins: []
};
