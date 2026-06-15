import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

// Static site. `site`/`base` target GitHub Pages at
// https://archettialberto.github.io/archettialberto — if you deploy at the
// domain root (e.g. a user page or custom domain), set base to '/'.
export default defineConfig({
  site: 'https://archettialberto.github.io',
  base: '/archettialberto',
  output: 'static',
  // applyBaseStyles:false — our global.css owns the @tailwind directives.
  integrations: [tailwind({ applyBaseStyles: false })],
});
