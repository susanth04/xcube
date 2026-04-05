import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(220, 13%, 91%)',
        input: 'hsl(220, 13%, 91%)',
        ring: 'hsl(262, 83%, 58%)',
        background: 'hsl(220, 14%, 96%)',
        foreground: 'hsl(220, 9%, 14%)',
        primary: {
          DEFAULT: 'hsl(262, 83%, 58%)',
          foreground: 'hsl(0, 0%, 100%)',
        },
        secondary: {
          DEFAULT: 'hsl(220, 13%, 91%)',
          foreground: 'hsl(220, 9%, 14%)',
        },
        muted: {
          DEFAULT: 'hsl(220, 13%, 91%)',
          foreground: 'hsl(220, 9%, 46%)',
        },
        card: {
          DEFAULT: 'hsl(0, 0%, 100%)',
          foreground: 'hsl(220, 9%, 14%)',
        },
      },
    },
  },
  plugins: [],
};

export default config;
