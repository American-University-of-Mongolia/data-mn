# Repository Guidelines

## Scope

Data.mn Astro application with bilingual data/report/insight content and Vega-Lite charts.

## Key Commands

```bash
npm install
npm run dev
npm run build
npm run thumbnails
```

## Key Paths

- `src/data/` - bilingual content collections
- `src/components/ui/VegaChart.astro` - chart renderer
- `public/charts/` - Vega-Lite specs
- `public/datasets/` - downloadable datasets
- `scripts/export-chart-thumbnails.js` - chart thumbnail generation

## Rules

- Preserve bilingual URL/content structure (`/en/*`, `/mn/*`).
- Keep Vega/Vega-Lite/Vega-Embed versions compatible.
- Validate charts and MDX dataFiles when editing dataset pages.
- Keep category labels, translation behavior, and search UX language-aware.
