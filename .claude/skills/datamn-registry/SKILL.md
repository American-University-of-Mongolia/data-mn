---
name: datamn-registry
description: "Query and manage the data.mn dataset registry. Use when checking dataset status, listing sources, viewing dataset details, registering new datasets, or tracking data versions."
---


# Data.mn Registry Skill

Query and manage the central registry database for data.mn datasets.

## Quick Reference

```bash
cd data/tools && python -m registry status           # Overall status
cd data/tools && python -m registry sources          # List all sources
cd data/tools && python -m registry list             # List all datasets
cd data/tools && python -m registry info DATASET_ID  # Dataset details
cd data/tools && python -m registry published        # List published URLs
cd data/tools && python -m registry redirects        # List URL redirects
```

## Commands

### View Overall Status

```bash
cd data/tools && python -m registry status
```

Shows:
- Total sources (enabled/disabled)
- Datasets by status (pending, active, outdated, error)
- Datasets by category
- Datasets needing updates
- Recent activity log

### List Data Sources

```bash
cd data/tools && python -m registry sources
```

Shows all registered data sources with:
- Source ID and name
- Type (api, pdf, scrape)
- Update frequency
- Definition file path

### List Datasets

```bash
cd data/tools && python -m registry list [--source SOURCE_ID] [--status STATUS]
```

Options:
- `--source nso-1212` - Filter by source
- `--status active` - Filter by status (pending, active, outdated, error, disabled)

Shows:
- Dataset ID and name
- Source, category
- Current status and version
- Last fetched date

### Get Dataset Details

```bash
cd data/tools && python -m registry info DATASET_ID
```

Shows comprehensive info:
- Names (EN/MN)
- Source and category
- Status and version
- Definition file path
- Output files (CSV, MDX, chart)
- Timing (data date, last check, last fetch)
- Version history

## URL Stability Commands

**CRITICAL**: URLs must be permanent once published. See `data/docs/principles/url-stability.md`.

### Publish a Dataset

```bash
cd data/tools && python -m registry publish DATASET_ID [--slug CUSTOM_SLUG]
```

Assigns a permanent URL. Must run after creating MDX pages. The `canonical_slug` cannot be changed after this without creating a redirect.

### Rename a URL (with redirect)

```bash
cd data/tools && python -m registry rename DATASET_ID NEW_SLUG --reason "Explanation"
```

Changes the URL but creates a 301 redirect from the old URL. Both URLs work forever.

### Deprecate a Dataset

```bash
cd data/tools && python -m registry deprecate DATASET_ID --reason "Explanation" [--successor NEW_ID]
```

Marks data as obsolete. URL keeps working but shows deprecation notice.

### Add Manual Redirect

```bash
cd data/tools && python -m registry add-redirect OLD_SLUG --target DATASET_ID --reason "Explanation"
```

Creates a redirect for URLs not from renames (typo fixes, consolidations).

### List Published Datasets

```bash
cd data/tools && python -m registry published
```

Shows all datasets with permanent URLs and their publication dates.

### List Redirects

```bash
cd data/tools && python -m registry redirects
```

Shows all URL redirects with hit counts.

### Export Redirects for Astro

```bash
cd data/tools && python -m registry export-redirects -o ../data.mn/src/redirects.json
```

Generates redirect config for Astro. Run before building site if redirects changed.

Or use the dedicated script:
```bash
python3 data/tools/scripts/generate_astro_redirects.py
```

## Database Location

The registry database is at: `data/tools/registry/data.db`

## Schema

The registry tracks:

1. **Sources** - Data providers (1212.mn, MRPAM, etc.)
2. **Datasets** - Individual datasets we track
3. **Versions** - Full version history for each dataset
4. **Activity Log** - All operations performed

## Key Concepts

### Parent/Split Datasets

Multi-dimensional source data is split into user-friendly datasets:

```
Parent (raw data)              Splits (user-friendly)
─────────────────              ─────────────────────
nso-population-by-age-sex  ──► population-total
                           ──► population-pyramid
                           ──► population-by-sex
```

- **Parent**: Stores complete raw data, `is_parent=1`, `parent_id=NULL`
- **Splits**: Filtered views, `is_parent=0`, have `parent_id` and `split_filter`
- When parent updates, all splits are regenerated automatically

### Dataset Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Registered but not yet fetched |
| `active` | Up to date and published |
| `outdated` | Source has newer data available |
| `error` | Last update failed |
| `disabled` | Temporarily disabled from updates |

## Python API

For programmatic access:

```python
from registry import Registry, Source, Dataset

reg = Registry()

# Get status
status = reg.get_status()

# List datasets
datasets = reg.list_datasets(source_id='nso-1212', status='active')

# Get specific dataset
dataset = reg.get_dataset('nso-population-total')

# Get versions
versions = reg.get_versions('nso-population-total', limit=5)

# Log activity
reg.log_activity(
    action='check',
    status='success',
    dataset_id='nso-population-total',
    message='No updates available'
)

# Register a new dataset (BILINGUAL categories required)
reg.add_dataset(
    dataset_id='my-new-dataset',
    name_en='My Dataset',
    name_mn='Миний өгөгдөл',
    source_id='nso-1212',
    category_en='Demographics',      # English category
    category_mn='Хүн ам зүй',        # Mongolian category
    is_parent=False,
    parent_id='parent-dataset-id',
    split_filter='{"sex": "Total"}'
)

# Update dataset status
reg.update_dataset(
    dataset_id='my-new-dataset',
    status='active',
    current_version=1
)

# Register a dataset with coverage metadata (for overlapping datasets)
reg.add_dataset(
    dataset_id='weekly-prices-ulaanbaatar',
    name_en='Weekly Prices (Ulaanbaatar)',
    name_mn='Долоо хоногийн үнэ (Улаанбаатар)',
    source_id='nso-1212',
    category_en='Economy',
    category_mn='Эдийн засаг',
    is_parent=True,
    # Coverage metadata
    coverage_geography='["Ulaanbaatar"]',
    coverage_granularity=None,  # No sub-breakdown within UB
    coverage_time_start='2020-01',
    coverage_frequency='weekly',
    concept_id='weekly-prices',
    related_datasets='["weekly-prices-aimags"]',
    coverage_notes='UB/national prices only. For provincial data see weekly-prices-aimags.'
)

# Find datasets by concept
datasets = reg.list_datasets_by_concept('weekly-prices')
for ds in datasets:
    print(f"{ds.id}: {ds.coverage_geography}")
```

## Adding Data

To add new sources or datasets:

1. Use the `/data-add` command for interactive workflow
2. Or manually:
   - Create definition files in `data/tools/sources/{source}/`
   - Use Python API to add to registry

## Registry Fields

### Sources Table

| Field | Description |
|-------|-------------|
| `source_id` | Unique identifier (e.g., `nso-1212`) |
| `name_en` | English name |
| `name_mn` | Mongolian name |
| `type` | api, pdf, scrape |
| `base_url` | Source URL |
| `update_frequency` | daily, weekly, monthly, quarterly, annual |
| `enabled` | Whether to check for updates |

### Datasets Table

| Field | Description |
|-------|-------------|
| `dataset_id` | Unique identifier |
| `name_en` | English name |
| `name_mn` | Mongolian name |
| `source_id` | Parent source |
| `category_en` | English category (Demographics, Economy, etc.) |
| `category_mn` | Mongolian category (Хүн ам зүй, Эдийн засаг, etc.) |
| `status` | pending, active, outdated, error, disabled |
| `is_parent` | 1 if this is a parent dataset |
| `parent_id` | ID of parent dataset (for splits) |
| `split_filter` | JSON filter criteria (for splits) |
| `current_version` | Latest version number |
| `auto_update` | Whether to check for updates automatically |
| `canonical_slug` | Permanent URL slug (set by `publish` command) |
| `first_published_at` | When URL first went live |
| `is_published` | Whether dataset has a permanent URL |
| `deprecated_at` | When marked deprecated (NULL if active) |
| `deprecation_reason` | Why deprecated |
| `successor_id` | Replacement dataset ID if deprecated |

### Coverage Fields (for handling overlapping datasets)

| Field | Description |
|-------|-------------|
| `coverage_geography` | JSON array of regions: `["Ulaanbaatar"]`, `["all_aimags"]`, `["national"]` |
| `coverage_granularity` | Geographic detail: `national`, `regional`, `aimag`, `soum`, `bag` |
| `coverage_time_start` | When data begins: `"2020-01"`, `"1990"` |
| `coverage_time_end` | When data ends (NULL for ongoing) |
| `coverage_frequency` | Update frequency: `weekly`, `monthly`, `quarterly`, `annual` |
| `coverage_dimensions` | JSON of available breakdowns: `{"sex": true, "age": true}` |
| `concept_id` | Groups related datasets: `"weekly-prices"`, `"gdp-per-capita"` |
| `related_datasets` | JSON array of related dataset IDs |
| `coverage_notes` | Text explaining limitations or alternatives |

### Concepts Table

Groups related datasets measuring the same indicator at different granularities.

| Field | Description |
|-------|-------------|
| `id` | Unique concept ID (e.g., `weekly-prices`) |
| `name_en` | English name |
| `name_mn` | Mongolian name |
| `description_en` | What this concept measures |
| `category_en` | Category for grouping |
| `primary_dataset_id` | "Best" dataset for this concept |

### Bilingual Categories

**IMPORTANT:** Always provide both English and Mongolian categories when registering datasets.

| English | Mongolian |
|---------|-----------|
| Demographics | Хүн ам зүй |
| Economy | Эдийн засаг |
| Employment | Хөдөлмөр эрхлэлт |
| Housing | Орон сууц |
| Mining | Уул уурхай |
| Finance | Санхүү |
| Agriculture | Хөдөө аж ахуй |
| Education | Боловсрол |
| Health | Эрүүл мэнд |
| Trade | Худалдаа |
| Energy | Эрчим хүч |
| Tourism | Аялал жуулчлал |

## Notes

- All times are stored in UTC
- Dataset IDs follow pattern: `{source}-{topic}` (e.g., `nso-population-total`)
- Version numbers are monotonically increasing integers
- Run commands from the `data/` directory
- **URL Stability**: Always run `registry publish` after creating MDX pages
- See `data/docs/principles/url-stability.md` for complete URL stability rules
