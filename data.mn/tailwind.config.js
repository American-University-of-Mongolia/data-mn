import defaultTheme from 'tailwindcss/defaultTheme';
import plugin from 'tailwindcss/plugin';
import typographyPlugin from '@tailwindcss/typography';

export default {
  content: ['./src/**/*.{astro,html,js,jsx,json,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        // Core semantic colors from CSS variables
        primary: 'var(--aw-color-primary)',
        'primary-light': 'var(--aw-color-primary-light)',
        'primary-dark': 'var(--aw-color-primary-dark)',
        secondary: 'var(--aw-color-secondary)',
        'secondary-light': 'var(--aw-color-secondary-light)',
        accent: 'var(--aw-color-accent)',
        'accent-alt': 'var(--aw-color-accent-alt)',
        default: 'var(--aw-color-text-default)',
        muted: 'var(--aw-color-text-muted)',
        // Chart/visualization colors
        'chart-1': 'var(--aw-color-chart-1)',
        'chart-2': 'var(--aw-color-chart-2)',
        'chart-3': 'var(--aw-color-chart-3)',
        'chart-4': 'var(--aw-color-chart-4)',
        'chart-5': 'var(--aw-color-chart-5)',
      },
      fontFamily: {
        sans: ['var(--aw-font-sans, ui-sans-serif)', ...defaultTheme.fontFamily.sans],
        serif: ['var(--aw-font-serif, ui-serif)', ...defaultTheme.fontFamily.serif],
        heading: ['var(--aw-font-heading, ui-sans-serif)', ...defaultTheme.fontFamily.sans],
      },

      animation: {
        fade: 'fadeInUp 1s both',
      },

      keyframes: {
        fadeInUp: {
          '0%': { opacity: 0, transform: 'translateY(2rem)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [
    typographyPlugin,
    plugin(({ addVariant }) => {
      addVariant('intersect', '&:not([no-intersect])');
    }),
  ],
  darkMode: 'class',
};
