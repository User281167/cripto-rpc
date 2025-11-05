import { heroui } from "@heroui/theme";

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/layouts/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./node_modules/@heroui/theme/dist/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Paleta personalizada para el sistema
        cryptoBlue: {
          DEFAULT: "#4F6BFF", // Azul intenso
          dark: "#3b53cc", // Azul oscuro para modo dark
        },
        dollarGold: {
          DEFAULT: "#FEA000", // Dorado para dólar
          dark: "#cc8000", // Dorado oscuro
        },
        euroSilver: {
          DEFAULT: "#A5BDEC", // Plateado para euro
          dark: "#7f9ac2", // Plateado oscuro
        },
        bitcoinGreen: {
          DEFAULT: "#01C89F", // Verde para bitcoin
          dark: "#019a7a", // Verde oscuro
        },
        oilRed: {
          DEFAULT: "#FE4D68", // Rojo petróleo
          dark: "#cc3e54", // Rojo oscuro
        },
      },
    },
  },
  darkMode: "class",
  plugins: [heroui()],
};
