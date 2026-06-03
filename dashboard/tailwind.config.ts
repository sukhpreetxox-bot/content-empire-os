import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#0a0e17",
        panel: "#121826",
        edge: "#1e2636",
        accent: "#d4af37",
      },
    },
  },
  plugins: [],
};
export default config;
