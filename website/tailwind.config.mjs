// Colors/fonts come from the CSS variables in the generated theme.css;
// the -rgb form keeps opacity modifiers (e.g. text-ink/70) working.
const themeColor = (name) => `rgb(var(--${name}-rgb) / <alpha-value>)`;

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,ts,tsx,md,mdx}'],
  theme: {
    extend: {
      colors: {
        ink: themeColor('ink'),
        mist: themeColor('mist'),
        blue: themeColor('blue'),
        pink: themeColor('pink'),
        haze: themeColor('haze'),
        page: themeColor('page'),
      },
      fontFamily: {
        display: 'var(--display)',
        sans: 'var(--text)',
      },
      maxWidth: {
        content: 'var(--max-width)',
      },
    },
  },
  plugins: [],
};
