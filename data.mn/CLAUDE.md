# CLAUDE.md - Data.mn Project Guide

This file provides guidance to Claude Code when working with the Data.mn codebase.

## Project Overview

Data.mn is a Statista-like bilingual website (English/Mongolian) that hosts data pages, reports, and insights blog posts. Built with Astro 5 and Tailwind CSS.

### Current Status

**Phase 1 - Core Site (Complete):**
- Three content types configured (Data, Reports, Insights)
- Vega-Lite visualization support with VegaChart component
- Data download functionality with DataDownload component
- Client-side search with smart keyword matching (drops keywords to avoid 0 results)
- Grid card layout for data and reports listings
- Statista-style homepage with hero, search, trending data, stats, topics, and featured sections
- 24 sample content pieces (13 data pages, 6 reports, 6 insights)
- E-Mongolia style Open Data dashboard with stat cards and sparklines
- Dark mode support throughout
- Responsive design for mobile/tablet/desktop
- SEO optimization

**Phase 2 - Multi-language Support (Complete):**
- Bilingual support (English/Mongolian)
- URL structure: `/en/...` and `/mn/...`
- Content organized by language in folders (`en/` and `mn/`)
- Language switcher in header
- hreflang SEO tags for language alternates
- Translation system via `src/i18n/` module
- Language-aware navigation and footer
- Category filter on listing pages (data, reports, insights)

**Deployment (Complete):**
- Kamal deployment configured
- Server: 78.46.40.253
- Domain: data.mn (via Cloudflare proxy)
- SSL enabled

### Known Issues / TODO

**High Priority:**
1. **Category translations** - Categories in Mongolian data/reports/insights are still in English. Need to translate category names or create a category translation map.

**Medium Priority:**
2. **Legal pages needed:**
   - Terms of Use page (`/[lang]/terms`)
   - Privacy Policy page (`/[lang]/privacy`)
3. **Contact page** - Current contact page needs improvement
4. **About page** - Needs better content for both languages

**Future Enhancements:**
- Pagination for data/reports/insights listings
- Category and tag archive pages
- Related content suggestions
- Newsletter subscription
- Analytics integration

## Technology Stack

- **Framework**: Astro 5.0 (static site generation)
- **Styling**: Tailwind CSS with dark mode support
- **Visualizations**: Vega-Lite for interactive charts (see below)
- **Content**: MDX for content with embedded components
- **Deployment**: Kamal 2.8.2 (Docker) on self-hosted server
- **CDN/SSL**: Cloudflare (proxy mode, Full SSL)

### Vega-Lite Chart Libraries

Charts use dynamically-loaded CDN libraries. **Version compatibility is critical** - mismatches cause runtime errors.

| Library | Version | Purpose |
|---------|---------|---------|
| Vega | 5.30.0 | Core visualization grammar |
| Vega-Lite | 5.21.0 | High-level chart specification |
| Vega-Embed | 6.26.0 | Embedding and interactivity |

These are loaded sequentially in `src/components/ui/VegaChart.astro`. Do not change versions without testing thoroughly.

See `/.claude/skills/vega-charts/SKILL.md` for chart creation guidelines.

### Chart Thumbnail Generation

The build process includes automatic thumbnail generation for all Vega-Lite charts. Thumbnails are WebP images used for social sharing, search results, and listing pages.

**How it works:**
- Script: `scripts/export-chart-thumbnails.js`
- Input: Vega-Lite JSON specs from `public/charts/*.json`
- Output: WebP thumbnails in `public/thumbnails/*.webp`
- Size: 800x450px, 85% quality
- Runs automatically during: `npm run build`

**Manual generation:**
```bash
npm run thumbnails
# or
node scripts/export-chart-thumbnails.js
```

**Dependencies:**
- `vega` - Core visualization library
- `vega-lite` - High-level chart specifications
- `canvas` - Node.js canvas implementation (native module)
- `sharp` - Image processing (resize, convert to WebP)

**Important:**
- The script uses `renderer: 'none'` for Vega views (required for server-side)
- `view.toCanvas()` automatically uses node-canvas in Node.js environment
- Chart specs reference data files via relative URLs (e.g., `/datasets/data.csv`)
- The loader's baseURL is set to `public/` to resolve these references

**Troubleshooting:**

If you see "CanvasRenderer is missing a valid canvas or context":
- Check that `canvas` package is installed: `npm install canvas`
- Rebuild native module: `npm rebuild canvas`
- Verify script uses `renderer: 'none'` (not `'canvas'`)

If canvas installation fails:
- Install system dependencies (macOS: Xcode Command Line Tools)
- See: https://github.com/Automattic/node-canvas#installation

## Content Structure

### Multi-language Content Organization
```
src/data/
├── data/
│   ├── en/           # English data pages
│   └── mn/           # Mongolian data pages
├── reports/
│   ├── en/           # English reports
│   └── mn/           # Mongolian reports
├── insights/
│   ├── en/           # English insights
│   └── mn/           # Mongolian insights
└── datasets/         # Source data files (not public)
```

### Public Assets
```
public/
├── datasets/       # Downloadable data files
├── charts/         # Vega-Lite chart specifications
└── images/         # Site images
```

## i18n System

### Translation Files
Location: `src/i18n/index.ts`

Contains translations for:
- Navigation labels
- UI elements
- Search interface
- Footer content
- Type labels (data, reports, insights)

### Using Translations
```astro
---
import { useTranslations, type Language } from '~/i18n';

const { lang } = Astro.params;
const currentLang = (lang as Language) || 'mn';
const t = useTranslations(currentLang);
---

<h1>{t('nav.data')}</h1>
```

### Adding New Translations
Edit `src/i18n/index.ts` and add entries to both `en` and `mn` objects.

## Key Components

### Language-Aware Components

**LanguageSwitcher** (`src/components/common/LanguageSwitcher.astro`)
- Dropdown for switching between EN/MN
- Preserves current path when switching

**HrefLangTags** (`src/components/common/HrefLangTags.astro`)
- Adds SEO hreflang tags for language alternates

**CategoryFilter** (`src/components/ui/CategoryFilter.astro`)
- Client-side filtering for listing pages
- Works with View Transitions

### Data Components

**VegaChart** (`src/components/ui/VegaChart.astro`)
- Embeds Vega-Lite visualizations

**DataDownload** (`src/components/ui/DataDownload.astro`)
- Displays downloadable data files

**GridCards** (`src/components/blog/GridCards.astro`)
- Grid layout for content listings
- Supports category filtering via data-category attribute

**OpenDataStats** (`src/components/widgets/OpenDataStats.astro`)
- E-Mongolia style stats dashboard
- **TODO**: Make language-aware

**LatestInsights** (`src/components/widgets/LatestInsights.astro`)
- Language-aware latest insights widget

## URL Structure

### Routes
- Homepage: `/` (redirects to `/mn`)
- English home: `/en`
- Mongolian home: `/mn`
- Data listing: `/[lang]/data`
- Individual data: `/[lang]/data/[slug]`
- Reports listing: `/[lang]/reports`
- Individual report: `/[lang]/reports/[slug]`
- Insights listing: `/[lang]/insights`
- Individual insight: `/[lang]/insights/[slug]`
- Search: `/[lang]/search?q=query`
- About: `/[lang]/about`

## Search Functionality

Location: `src/pages/[lang]/search.astro`

**Features:**
- Client-side JavaScript search
- Searches title, excerpt, keywords, tags, and categories
- **Smart keyword dropping**: If a search returns 0 results, progressively drops keywords until results are found
- Shows notice when keywords were dropped
- Works with View Transitions (astro:page-load event)
- Language-specific search index

## Development Workflow

### Running Development Server
```bash
npm run dev        # Start dev server at localhost:4321
npm run build      # Build for production
npm run preview    # Preview production build
```

### Creating New Content

1. Create MDX file in appropriate language folder:
   - English: `src/data/{type}/en/my-content.mdx`
   - Mongolian: `src/data/{type}/mn/my-content.mdx`
2. Add frontmatter with title, keywords, category, etc.
3. For data pages: create chart spec in `public/charts/`
4. Content will automatically appear in correct language version

### Deployment
```bash
kamal deploy       # Deploy to production
kamal setup        # First-time setup
```

## Configuration Files

- `src/config.yaml` - Site metadata, SEO settings
- `src/navigation.ts` - Navigation links (language-aware via PageLayout)
- `src/i18n/index.ts` - Translation strings
- `config/deploy.yml` - Kamal deployment config
- `.kamal/secrets` - Registry credentials (gitignored)
- `astro.config.ts` - Astro configuration

## Best Practices

1. **Content**: Always create both EN and MN versions of content
2. **Translations**: Add UI strings to i18n/index.ts, don't hardcode
3. **Categories**: Use consistent category names (translation mapping needed)
4. **Images**: Use descriptive alt text in both languages
5. **SEO**: Include keywords array for search functionality
6. **Testing**: Test both language versions after changes

## Notes

- Default language is Mongolian (`mn`)
- Root `/` redirects to `/mn`
- Trailing slashes set to 'ignore' in astro.config.ts
- View Transitions enabled - use `astro:page-load` event for JS initialization
- Original AstroWind homepage preserved at `/index-original` for reference
