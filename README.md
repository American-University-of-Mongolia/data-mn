# Data.mn

Mongolia's open data platform - making Mongolian statistics accessible, understandable, and usable.

## Overview

Data.mn aggregates data from multiple Mongolian government sources (National Statistics Office, Bank of Mongolia, MRPAM, etc.) and presents them in a clean, bilingual (English/Mongolian) format with interactive visualizations.

## Features

- **Bilingual**: All datasets available in both English and Mongolian
- **Interactive Charts**: Vega-Lite powered visualizations
- **Multiple Formats**: Download data as CSV or XLSX
- **API Access**: Programmatic access to all datasets
- **Version History**: Track changes to datasets over time

## Project Structure

```
data/
├── data.mn/          # Astro website (main application)
├── tools/            # Data management tools and registry
├── docs/             # Documentation
├── projects/         # Standalone data projects
└── .claude/          # Claude Code skills and commands
```

## Quick Start

```bash
# Install dependencies
cd data.mn && npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## Data Sources

| Source | Type | Coverage |
|--------|------|----------|
| National Statistics Office (1212.mn) | REST API | Demographics, Economy, Social |
| Bank of Mongolia | Mixed | Monetary, Financial |
| MRPAM | PDF Reports | Mining, Resources |

## Development

This project uses Claude Code with custom skills for data management. See `CLAUDE.md` for details on available commands:

- `/data-status` - View registry status
- `/data-add` - Add new datasets
- `/data-update` - Update existing datasets
- `/data-batch` - Batch dataset creation

## Tech Stack

- **Website**: Astro, MDX, Tailwind CSS
- **Charts**: Vega-Lite
- **Data Processing**: Python, pandas
- **Database**: SQLite (registry)

## License

MIT
