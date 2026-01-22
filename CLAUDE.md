# CLAUDE.md - Data Directory

This directory contains the data.mn project and data management tools.

## Directory Structure

```
data/
├── .claude/
│   ├── agents/             # Subagent workers
│   │   ├── datamn-dataset-worker.md   # Create/update single dataset
│   │   └── datamn-discovery-worker.md # Search and check sources
│   └── commands/           # Slash commands
│       ├── data-status.md      # View registry status
│       ├── data-add.md         # Add new datasets
│       ├── data-add-worker.md  # Worker instructions for /data-add
│       ├── data-batch.md       # Batch dataset creation
│       ├── data-update.md      # Update all datasets (orchestrator)
│       └── data-update-worker.md  # Worker instructions for /data-update
├── data.mn/                # Astro website (see data.mn/CLAUDE.md)
├── docs/                   # Project documentation
│   ├── README.md               # Documentation index
│   ├── vision.md               # Mission, principles, roadmap
│   ├── datamn-architecture.md  # Technical architecture
│   ├── validation-postmortem-2024-12.md  # Lessons learned
│   └── principles/             # Guiding principles
│       ├── url-stability.md        # URL stability rules (IMPORTANT)
│       ├── categories.md           # Category system
│       └── coverage-detection.md   # Geographic coverage detection
├── projects/               # Standalone data projects (see below)
│   ├── social_protection/      # Mongolia Social Protection Data Brief
│   └── cars/                   # Car price prediction model
├── tools/
│   ├── registry/           # SQLite database and Python module
│   ├── sources/            # Declarative source definitions
│   ├── scripts/            # Utility scripts
│   │   ├── translate_csv.py            # Bilingual CSV translation
│   │   ├── validate_vega.py            # Chart validation
│   │   ├── validate_mdx_datafiles.py   # MDX dataFiles validation
│   │   └── generate_astro_redirects.py # URL redirect generation
│   ├── templates/          # MDX generation templates
│   ├── versions/           # Dataset version history
│   ├── data-registry.xlsx  # Master registry (open in Excel to browse)
│   └── TRANSLATION_GUIDE.md        # Single-language source translation guide
├── CLAUDE.md               # This file
├── requirements.txt        # Python dependencies
└── environment.yml         # Conda environment config
```

**Note on Skills**: The `datamn-*` skills are defined in `.claude/skills/` within this repository. They are automatically available when working in this directory.

---

## Slash Commands

### `/data-status`
View the current status of all data sources and datasets.

```
/data-status
```

Shows:
- Number of sources configured
- Datasets by status (active, pending, outdated, error)
- Recent activity log

### `/data-add`
Interactively add a new dataset to track.

```
/data-add
```

Workflow:
1. Select source type (nso-1212, mrpam, mongolbank, or new)
2. Search/browse available data
3. Analyze data structure and recommend splits
4. Create dataset definition and fetch initial data
5. Generate MDX pages and charts

**Key concept**: Multi-dimensional datasets are split into simple, user-friendly datasets (Statista-style).

### `/data-batch`
Create multiple datasets from a list with source hints.

```
/data-batch
```

Then provide a list like:
- "Population from NSO"
- "Inflation from NSO/MongolBank"
- "Mining stats from MRPAM"

Uses parallel discovery and creation workers for efficiency.

### `/data-update`
Check all sources for updates and process them using parallel workers.

```
/data-update
/data-update --source nso-1212
/data-update --dataset nso-population-by-age-sex --force
/data-update --dry-run
```

Options:
- `--source {id}` - Only update datasets from this source
- `--dataset {id}` - Only update this specific dataset
- `--dry-run` - Check for updates without fetching
- `--force` - Re-fetch even if no updates detected

**Architecture**: Uses parallel worker agents (batches of 4) for efficient updates.

---

## Skills

### Naming Convention

All data.mn skills use the `datamn-{category}-{name}` pattern:

| Category | Purpose | Examples |
|----------|---------|----------|
| `datamn-source-*` | Data source access | `datamn-source-nso` |
| `datamn-registry` | Registry management | `datamn-registry` |
| `datamn-chart-*` | Visualization | `datamn-chart-vega` |
| `datamn-page-*` | Content generation | `datamn-page-mdx` |
| `datamn-transform-*` | Data transformation | `datamn-transform-split` |
| `datamn-extract-*` | Data extraction | `datamn-extract-pdf` |

### `datamn-source-nso`
Query Mongolia's National Statistical Office (1212.mn) API.

**Location**: `.claude/skills/datamn-source-nso/`

**Setup** (required before first use):
```bash
cd .claude/skills/datamn-source-nso && python3 query_api.py --refresh
```

**Usage**:
```bash
# Search for data
python3 query_api.py population Mongolia

# Get detailed table structure
python3 query_api.py --detailed apartment price

# List all sectors
python3 query_api.py --sectors

# Fetch actual data to CSV
python3 fetch_data.py  # Edit DATASETS list first
```

**Reference Data**: The full catalog of 1,135 NSO tables is in the "NSO Catalog" sheet of `tools/data-registry.xlsx`.

### `datamn-registry`
Query and manage the dataset registry database.

```bash
cd tools && python -m registry status    # Overall status
cd tools && python -m registry sources   # List all sources
cd tools && python -m registry list      # List all datasets
cd tools && python -m registry info ID   # Dataset details
cd tools && python -m registry published # List published datasets with URLs
cd tools && python -m registry redirects # List all URL redirects
```

**URL Stability Commands** (see `docs/principles/url-stability.md`):
```bash
cd tools
python -m registry publish <id>              # Publish dataset (assign permanent URL)
python -m registry rename <id> <new> --reason "..."  # Rename URL (creates redirect)
python -m registry deprecate <id> --reason "..." [--successor <id>]  # Mark deprecated
python -m registry add-redirect <old> --target <id> --reason "..."   # Manual redirect
python -m registry export-redirects          # Export redirects for Astro
```

### `datamn-chart-vega`
Guidelines for creating Vega-Lite chart specifications.

**Key rules**:
- Do NOT set width/height (component handles responsive sizing)
- Use `quantitative` or `temporal` for time axes (NOT `ordinal`)
- Always validate charts after creation

**Validation** (required after creating charts):
```bash
cd data.mn && python3 ../tools/scripts/validate_vega.py --all
```

### `datamn-page-mdx`
Generate bilingual MDX pages (EN + MN) for datasets.

### `datamn-transform-split`
Transform and filter multi-dimensional data into user-friendly splits.

### `datamn-extract-pdf`
Extract tabular data from PDF documents using pdfplumber.

### `datamn-source-template`
Template for creating new data source skills.

---

## Subagent Workers

### `datamn-dataset-worker`
Specialized agent for creating or updating a single dataset. Handles:
- Data fetching/loading
- Transformation and filtering
- Chart generation
- MDX page creation
- Registry updates

### `datamn-discovery-worker`
Read-only agent for searching and checking sources:
- Check if updates are available
- Search for datasets matching queries
- Analyze table structure

---

## Data Sources

| Source | ID | Type | Definition |
|--------|-----|------|------------|
| National Statistics Office | `nso-1212` | REST API | `tools/sources/nso-1212/source.md` |
| Mining & Petroleum Authority | `mrpam` | PDF Reports | `tools/sources/mrpam/source.md` |
| Bank of Mongolia | `mongolbank` | Mixed | `tools/sources/mongolbank/source.md` |

To add a new source, use the `datamn-source-template` skill.

---

## Utility Scripts

### `tools/scripts/validate_vega.py`
Validate Vega-Lite chart specifications.

```bash
# Validate a single chart
python3 tools/scripts/validate_vega.py path/to/chart.json

# Validate with data file
python3 tools/scripts/validate_vega.py chart.json --data data.csv

# Validate all charts in data.mn
cd data.mn && python3 ../tools/scripts/validate_vega.py --all
```

### `tools/scripts/validate_mdx_datafiles.py`
Validate MDX frontmatter `dataFiles` paths point to existing files.

```bash
# Validate all MDX files
python3 tools/scripts/validate_mdx_datafiles.py

# Validate a single file
python3 tools/scripts/validate_mdx_datafiles.py path/to/file.mdx
```

This catches:
- Missing CSV/XLSX files in dataFiles frontmatter
- Wrong language suffixes (e.g., `-en.csv` in an MN page)

### `tools/scripts/validate_dataset.py`
Comprehensive validation for individual dataset files.

```bash
# Validate MDX file
python3 tools/scripts/validate_dataset.py --mdx path/to/file.mdx

# Validate CSV file
python3 tools/scripts/validate_dataset.py --csv path/to/file.csv

# Validate all files for a dataset
python3 tools/scripts/validate_dataset.py --all DATASET_ID
```

Used by worker agents for parallel validation when a full build isn't possible.

### `tools/scripts/translate_csv.py`
Translate CSV data between English and Mongolian for single-language sources.

```bash
# Auto-detect language and translate
python3 tools/scripts/translate_csv.py input.csv --auto -o output.csv

# Explicit translation direction
python3 tools/scripts/translate_csv.py mongolian.csv --from mn --to en -o english.csv
python3 tools/scripts/translate_csv.py english.csv --from en --to mn -o mongolian.csv
```

**When to use**: Any data source that only provides data in one language (MRPAM PDFs, MongolBank bulletins, etc.)

See `tools/TRANSLATION_GUIDE.md` for complete translation workflow.

### `tools/scripts/generate_astro_redirects.py`
Generate URL redirects for Astro from the registry database.

```bash
python3 tools/scripts/generate_astro_redirects.py
```

This reads `url_redirects` table and generates `data.mn/src/redirects.generated.ts`.
Run this after adding redirects and before building the site.

See `docs/principles/url-stability.md` for the full URL stability system.

---

## Key Concepts

### Bilingual Architecture

**CRITICAL**: All datasets MUST have bilingual CSVs (`-en.csv` and `-mn.csv`).

The data.mn platform is fully bilingual:
- Charts reference language-specific CSVs (EN charts use `-en.csv`, MN charts use `-mn.csv`)
- MDX pages exist in both `/en/` and `/mn/` directories
- Each language page uses its matching CSV file

#### Bilingual vs Single-Language Sources

| Source Type | How to Handle |
|------------|---------------|
| **NSO 1212.mn** | Provides bilingual data via API - fetch both languages |
| **MRPAM PDFs** | Mongolian only - translate to create English CSV |
| **MongolBank** | Mixed - some bilingual, some single-language |
| **International** | English only - translate to create Mongolian CSV |

#### Translation Workflow

For single-language sources:

1. **Extract/fetch source data** in its original language
2. **Save as** `dataset-id-{lang}.csv` (e.g., `mrpam-coal-mn.csv`)
3. **Translate** using `tools/scripts/translate_csv.py`:
   ```bash
   python3 tools/scripts/translate_csv.py dataset-mn.csv --from mn --to en -o dataset-en.csv
   ```
4. **Validate** both CSVs have matching structure and identical numeric data
5. **Save both** to `public/datasets/`

**Complete guide**: `tools/TRANSLATION_GUIDE.md`

### Parent/Split Datasets

Multi-dimensional source data is split into user-friendly datasets:

```
Parent (raw data)              Splits (user-friendly)
─────────────────              ─────────────────────
nso-population-by-age-sex  ──► population-total
                           ──► population-pyramid
                           ──► population-by-sex
```

- **Parent**: Stores complete raw data, `is_parent=1`
- **Splits**: Filtered views, have `parent_id` and `split_filter`
- When parent updates, all splits are regenerated automatically

### Declarative Source Definitions

Instead of hardcoded collectors, each source has markdown files describing how to access data. This allows agents to adapt when sources change.

```
tools/sources/nso-1212/
├── source.md           # How to use the 1212.mn API
└── datasets/
    └── population-by-age-sex.md  # Specific dataset instructions
```

### URL Stability

**CRITICAL**: URLs are permanent and must never break once published.

> "Cool URIs don't change" — Tim Berners-Lee

Data.mn URLs will be cited in academic papers, government reports, and linked from external systems. Breaking these links damages trust and invalidates citations.

**Key Rules**:
1. **Never delete a published dataset** — deprecate it instead
2. **Never change a URL** — use `registry rename` which creates a redirect
3. **Always run `registry publish`** before first deployment

**Full Documentation**: `docs/principles/url-stability.md`

**Quick Reference**:
```bash
cd tools
python -m registry publish <id>              # First-time publish
python -m registry rename <id> <new> --reason "..."  # Rename with redirect
python -m registry deprecate <id> --reason "..." --successor <new-id>  # Deprecate
python3 scripts/generate_astro_redirects.py  # Update Astro config
```

---

## Development Workflow

### Adding a New Dataset

1. Run `/data-add` or `/data-batch`
2. Select source and search for data
3. Review recommended splits
4. System creates definition files, fetches data, generates content
5. Validate charts: `python3 tools/scripts/validate_vega.py --all`
6. Preview: `cd data.mn && npm run dev`

### Updating Datasets

1. Run `/data-update`
2. Review which datasets have updates available
3. Confirm to process updates (runs parallel workers)
4. Charts are validated automatically
5. Build: `cd data.mn && npm run build`

### Registry Operations

```bash
cd tools

# View status
python -m registry status

# List datasets with filters
python -m registry list --source nso-1212
python -m registry list --status active

# Get detailed info
python -m registry info population-total
```

---

## Output Locations

| Content Type | Location |
|-------------|----------|
| MDX pages (EN) | `data.mn/src/data/data/en/` |
| MDX pages (MN) | `data.mn/src/data/data/mn/` |
| CSV downloads | `data.mn/public/datasets/` |
| XLSX downloads | `data.mn/public/datasets/` |
| Chart specs | `data.mn/public/charts/` |
| Version history | `tools/versions/{dataset-id}/` |

---

## Python Environment

All Python scripts require the `datamn` conda environment.

### Setup (first time)

```bash
# Create environment
conda env create -f environment.yml

# Or manually:
conda create -n datamn python=3.12
conda activate datamn
pip install -r requirements.txt
```

### Activation

```bash
conda activate datamn
```

### Dependencies

| Package | Purpose |
|---------|---------|
| `requests` | HTTP client for API calls |
| `pandas` | Data manipulation and CSV handling |
| `openpyxl` | Excel file support (.xlsx) |
| `pdfplumber` | PDF table extraction |

---

## Standalone Projects

The `projects/` folder contains standalone data analysis projects that are separate from the main data.mn pipeline. These are typically one-off analyses, reports, or experiments.

### `projects/social_protection/`

Mongolia Social Protection Data Brief - a comprehensive analysis of social protection statistics from NSO 1212.mn.

**Contents**:
- `Mongolia Social Protection Data Brief.pdf` - Final report
- `Mongolia Social Protection Data Brief.md` - Source markdown
- `explore_datasets.py` - API exploration scripts
- `data/` - Downloaded datasets
- `images/` - Generated visualizations

### `projects/cars/`

Car price prediction model using Unegui.mn scraped data.

**Contents**:
- `CLAUDE.md` - Project-specific instructions
- `PLAN.md` - Implementation plan
- `src/` - Model training code
- `data/` - Training datasets (CSV)
- `models/` - Saved model artifacts

**Note**: Each project may have its own CLAUDE.md with specific instructions.

---

## Reference Data Files

| File | Location | Description |
|------|----------|-------------|
| `data-registry.xlsx` | `tools/` | **Master registry** - open in Excel to browse all data |
| `data.db` | `tools/registry/` | SQLite registry database (programmatic access) |

### data-registry.xlsx Sheets

| Sheet | Contents |
|-------|----------|
| Dashboard | Summary stats and category breakdown |
| NSO Catalog | All 1,135 NSO 1212.mn tables with status |
| Datasets | All data.mn datasets with metadata |
| Sources | Data sources (NSO, MRPAM, MongolBank) |
| Versions | Dataset version history |
| Activity Log | Recent operations |

**Tip**: The Excel file is a snapshot for browsing. For programmatic access, use the registry Python module or SQLite database.

---

## Notes

- **IMPORTANT**: Always activate the `datamn` conda environment before running scripts
- Run commands from the `data/` directory
- Registry database: `tools/registry/data.db`
- See `docs/vision.md` for mission, principles, and roadmap
- See `data.mn/CLAUDE.md` for website-specific instructions
- See `docs/principles/url-stability.md` for URL stability rules (**CRITICAL**)
- Use Playwright MCP tools for web navigation when needed

---

## For Contributors

New to the project? See **[CONTRIBUTING.md](CONTRIBUTING.md)** for:

- Complete setup instructions (Git, Node.js, Conda, gh CLI, Claude Code)
- Git workflow for beginners (branches, commits, pull requests)
- How to use Claude Code and the `/data-*` commands
- Code standards and validation requirements

Quick start:
```bash
gh repo fork data-dot-mn/data-tools --clone   # Fork and clone
cd data
conda env create -f environment.yml && conda activate datamn
cd data.mn && npm install && cd ..
claude                              # Start Claude Code
```
