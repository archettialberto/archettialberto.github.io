// Tailwind theme is driven by the SAME source as the CV: theme/themes/<active>.yaml,
// exported to src/styles/theme.css by `cv build-site`. Switch with
// `python -m src.cli theme use <name>` then `cv build-site`.
//
// Colors/fonts/layout reference the generated CSS *variables* rather than baked
// values, so a theme switch is a pure CSS reload — the dev server picks it up
// without a restart, and utility classes (text-navy, bg-gold/10, …) can never
// drift from the var()-based styles. `<alpha-value>` keeps opacity modifiers
// (e.g. text-charcoal/70) working on top of the variables.
const themeColor = (name) => `rgb(var(--${name}-rgb) / <alpha-value>)`;

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,ts,tsx,md,mdx}'],
  theme: {
    extend: {
      // Semantic color names are theme-stable; only their values change.
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
