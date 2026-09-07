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

// Unprefixed demo/template routes that are noindexed (see LandingLayout,
// index-original, src/data/post/*). '/landing' also covers '/landing/*'
// but not '/tag/landing-pages' (matched only on exact or slash boundary).
const DEMO_PATHS = [
  '/landing',
  '/index-original',
  '/astrowind-template-in-depth',
  '/get-started-website-with-astro-tailwind-css',
  '/how-to-customize-astrowind-to-your-brand',
  '/markdown-elements-demo-post',
  '/useful-resources-to-create-websites',
];

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
      // Astrowind demo/template pages are noindexed — don't submit them either.
      filter: (page) => {
        const { pathname } = new URL(page);
        return !DEMO_PATHS.some((p) => pathname === p || pathname.startsWith(`${p}/`));
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
    domains: ['cdn.pixabay.com'],
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
