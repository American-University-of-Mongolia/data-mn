import path from 'path';
import { fileURLToPath } from 'url';

import { defineConfig } from 'astro/config';

// URL stability redirects (auto-generated from registry database)
// See docs/principles/url-stability.md for documentation
import { generatedRedirects } from './src/redirects.generated';

import sitemap from '@astrojs/sitemap';
import tailwind from '@astrojs/tailwind';
import mdx from '@astrojs/mdx';
import partytown from '@astrojs/partytown';
import icon from 'astro-icon';
import compress from 'astro-compress';
import type { AstroIntegration } from 'astro';

import astrowind from './vendor/integration';

import { readingTimeRemarkPlugin, responsiveTablesRehypePlugin, lazyImagesRehypePlugin } from './src/utils/frontmatter';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Only the bilingual /en and /mn routes belong in the sitemap. Anything
// unprefixed (the / redirect, 404, legacy redirect stubs) is left out.
const isLocalizedPath = (pathname: string) => /^\/(en|mn)(\/|$)/.test(pathname);

const hasExternalScripts = false;
const whenExternalScripts = (items: (() => AstroIntegration) | (() => AstroIntegration)[] = []) =>
  hasExternalScripts ? (Array.isArray(items) ? items.map((item) => item()) : [items()]) : [];

export default defineConfig({
  site: 'https://data.mn',
  output: 'static',
  trailingSlash: 'ignore',

  // URL stability redirects
  // Generated from: python tools/scripts/generate_astro_redirects.py
  redirects: {
    ...generatedRedirects,
    // Manual redirects can be added here
  },

  i18n: {
    defaultLocale: 'mn',
    locales: ['mn', 'en'],
    routing: {
      prefixDefaultLocale: true, // Both /mn/... and /en/... URLs
    },
  },

  integrations: [
    tailwind({
      applyBaseStyles: false,
    }),
    sitemap({
      filter: (page) => isLocalizedPath(new URL(page).pathname),
      // Emits <xhtml:link rel="alternate" hreflang> for each /en <-> /mn pair.
      i18n: {
        defaultLocale: 'mn',
        locales: { mn: 'mn', en: 'en' },
      },
    }),
    mdx(),
    icon({
      include: {
        tabler: ['*'],
        'flat-color-icons': [
          'template',
          'gallery',
          'approval',
          'document',
          'advertising',
          'currency-exchange',
          'voice-presentation',
          'business-contact',
          'database',
        ],
      },
    }),

    ...whenExternalScripts(() =>
      partytown({
        config: { forward: ['dataLayer.push'] },
      })
    ),

    compress({
      CSS: true,
      HTML: {
        'html-minifier-terser': {
          removeAttributeQuotes: false,
        },
      },
      Image: false,
      JavaScript: true,
      SVG: false,
      Logger: 1,
    }),

    astrowind({
      config: './src/config.yaml',
    }),
  ],

  image: {
    domains: ['cdn.pixabay.com', 'images.unsplash.com', 'plus.unsplash.com'],
  },

  markdown: {
    remarkPlugins: [readingTimeRemarkPlugin],
    rehypePlugins: [responsiveTablesRehypePlugin, lazyImagesRehypePlugin],
  },

  vite: {
    resolve: {
      alias: {
        '~': path.resolve(__dirname, './src'),
      },
    },
  },
});
