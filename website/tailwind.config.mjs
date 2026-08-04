// Colors/fonts come from the CSS variables in the generated theme.css;
// the -rgb form keeps opacity modifiers (e.g. text-charcoal/70) working.
const themeColor = (name) => `rgb(var(--${name}-rgb) / <alpha-value>)`;

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,ts,tsx,md,mdx}'],
  theme: {
    extend: {
      colors: {
        navy: themeColor('navy'),
        gold: themeColor('gold'),
        charcoal: themeColor('charcoal'),
        warmgray: themeColor('warmgray'),
        lightnavy: themeColor('lightnavy'),
        paper: themeColor('paper'),
      },
      fontFamily: {
        display: 'var(--display)',
        sans: 'var(--text)',
      },
      maxWidth: {
        content: 'var(--max-width)',
      },
      borderRadius: {
        DEFAULT: 'var(--radius)',
      },
    },
  },
  plugins: [],
};
