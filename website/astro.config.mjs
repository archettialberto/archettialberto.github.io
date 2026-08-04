import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  site: 'https://archettialberto.github.io',
  base: '/',
  output: 'static',
  // global.css owns the @tailwind directives.
  integrations: [tailwind({ applyBaseStyles: false })],
});
