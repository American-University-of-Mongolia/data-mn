---
name: datamn-source-nso
description: "Search and browse the full 1212.mn API catalog (1135+ statistical tables). Use this skill to: list all available NSO data, find specific datasets by keyword, check what tables exist for a topic, get table metadata/structure, or download data to CSV. Covers population, GDP, inflation, unemployment, wages, trade, livestock, education, health, crime, housing prices, and all other official Mongolian government statistics."
dependencies:
  - python3
  - python3-requests
  - sqlite3
---

# NSO 1212.mn Data Source Skill

This skill enables querying Mongolia's National Statistical Office (NSO) API v1 at data.1212.mn. It provides access to comprehensive statistical data about Mongolia.

When saving data never put it inside the skills/datamn-source-nso folder. Ask the user where to save the data if not specified.

## Metadata Cache

This skill maintains a **local SQLite database** with the complete 1212.mn API catalog cached for fast searching.

**Location**: `.claude/skills/datamn-source-nso/metadata/tables.db`

**Contents**:
- 1135+ statistical tables
- 8 sectors, ~90 subsectors
- Full-text search index
- Last updated timestamps for each table

### Cache Status

To check cache status:
```bash
cd .claude/skills/datamn-source-nso
sqlite3 metadata/tables.db "SELECT COUNT(*) as tables FROM tables"
sqlite3 metadata/tables.db "SELECT MAX(updated_at) as last_refresh FROM tables"
```

### Refreshing the Cache

**When to refresh:**
- First time using the skill
- If searches return no results for data you know exists
- Monthly (to catch newly added tables)
- After API structure changes

**How to refresh:**
```bash
cd .claude/skills/datamn-source-nso
python3 query_api.py --refresh        # Update existing cache
python3 query_api.py --force-refresh  # Complete rebuild
```

This downloads the full catalog from 1212.mn (~1-2 minutes).

### Automatic Schema Management

The skill includes automatic schema detection and recovery:
- **Schema versioning**: Automatic version detection and upgrade
- **Automatic rebuild**: When schema mismatches are detected, the database is automatically rebuilt
- **Force refresh option**: Use `--force-refresh` to manually trigger a complete rebuild

## Commands

### Search for data
```bash
python3 query_api.py [search terms]
```
Searches the metadata for tables matching the query terms.

### Get detailed data (with variable structure)
```bash
python3 query_api.py --detailed [search terms]
```
Fetches the actual table structure from the API showing available variables and their values.

### List all sectors
```bash
python3 query_api.py --sectors
```
Shows all 8 main sectors (Education/health, Regional development, Society/development, etc.)

### List all available tables
```bash
python3 query_api.py --list
```
Shows all tables in the database with their IDs, sectors, and descriptions.

### Filter tables by sector
```bash
python3 query_api.py --list --sector "Population, household"
```
Shows only tables within a specific sector.

### Get JSON output
```bash
python3 query_api.py --json [search terms]
```
Returns results in JSON format for programmatic processing.

### Refresh metadata
```bash
python3 query_api.py --refresh
```
Updates the local metadata cache from the API.

### Force rebuild database
```bash
python3 query_api.py --force-refresh
```
Deletes the existing database and rebuilds it completely.

### Use Mongolian language
```bash
python3 query_api.py --lang mn [search terms]
```
Query using Mongolian language API.

## Downloading Actual Data to CSV

The `fetch_data.py` script downloads actual statistical data from specific tables and saves them as CSV files. It uses **direct HTTP requests** to the 1212.mn API (no external packages required beyond `requests` and `pandas`).

**Key Feature:** The script supports **bilingual output** - it fetches data in both English and Mongolian, saving separate CSV files for each language.

### Prerequisites

```bash
pip install requests pandas
```

### Usage

```bash
# Fetch a specific table in both languages
python3 fetch_data.py --table DT_NSO_0500_001V1.px --output ./output

# Fetch only English
python3 fetch_data.py --table DT_NSO_0500_001V1.px --lang en --output ./output

# Fetch only Mongolian
python3 fetch_data.py --table DT_NSO_0500_001V1.px --lang mn --output ./output
```

### Finding Table IDs

1. Use `query_api.py` to search for tables:
   ```bash
   python3 query_api.py GDP
   python3 query_api.py --detailed DT_NSO_0500_001V1
   ```
2. Note the table ID from the results (e.g., `DT_NSO_0500_001V1.px`)
3. Use it with `fetch_data.py`

### Output Files

The script generates CSV files with the naming pattern:
- `nso-{table-number}-{lang}.csv`

Example for `DT_NSO_0500_001V1.px`:
- `nso-0500-001v1-en.csv` (English version)
- `nso-0500-001v1-mn.csv` (Mongolian version)

## Smart Query Matching

The system uses intelligent keyword matching with English-Mongolian synonyms:
- "apartment" matches "орон сууц" (housing)
- "price" matches "үнэ" (cost)
- "population" matches "хүн ам"
- "district" matches "дүүрэг"
- "employment" matches "ажил эрхлэлт", "хөдөлмөр"

## Data Categories (Sectors)

The 1212.mn API includes 8 main sectors:

1. **Education, health** (Боловсрол, эрүүл мэнд)
2. **Regional development** (Бүсчилсэн хөгжил)
3. **Society, development** (Нийгэм, хөгжил)
4. **Historical data** (Түүхэн Статистик)
5. **Industry, service** (Үйлдвэрлэл, үйлчилгээ)
6. **Labour, business** (Хөдөлмөр, бизнес)
7. **Population, household** (Хүн ам, өрх)
8. **Economy, environment** (Эдийн засаг, байгаль орчин)

## API Details

**Base URL**: `https://data.1212.mn/api/v1/{lang}/NSO/`

**Endpoints**:
- `GET /{lang}/NSO/` - List sectors
- `GET /{lang}/NSO/{sector}/` - List subsectors
- `GET /{lang}/NSO/{sector}/{subsector}/` - List tables
- `GET /{lang}/NSO/{sector}/{subsector}/{table}.px` - Get table data

**Languages**: `en` (English), `mn` (Mongolian)

## Checking for Updates

To check if a table has been updated:

1. Query the API for the table's metadata
2. Check the `updated` field in the response
3. Compare with the `source_updated_at` in the registry

```python
# Example: Get table update timestamp
import requests
response = requests.get(f"https://data.1212.mn/api/v1/en/NSO/{sector}/{subsector}/")
tables = response.json()
for t in tables:
    if t['id'] == table_id:
        print(f"Last updated: {t['updated']}")
```

## Error Handling

Common errors and solutions:

1. **"Metadata not initialized"**: Run `python3 query_api.py --refresh`
2. **Schema mismatch**: Run `python3 query_api.py --force-refresh`
3. **"No relevant tables found"**: Try different keywords or list all tables
4. **API connection errors**: Check internet connection

## Tips for Effective Use

1. **Understand Mongolian names**: Common terms:
   - Хүн ам = Population
   - Орон сууц = Apartment/Housing
   - Үнэ = Price
   - Дүүрэг = District
   - Аймаг = Province
   - Дундаж = Average
   - Нийслэл = Capital

2. **Use multiple keywords**: Combine location, subject, and metric
3. **Check the variables**: Use `--detailed` to understand table structure
4. **Consider geographic levels**: Data may be by country, province, district, or sub-district

## Coverage Detection (Finding Related Tables)

NSO often publishes the same indicator in multiple tables with different coverage. Before adding a new dataset, search for related tables.

### Common Coverage Patterns

| Table Name Pattern | Geographic Coverage | Notes |
|--------------------|--------------------| ------|
| "by aimags" | 21 provinces only | Usually excludes Ulaanbaatar |
| "by aimags and the Capital" | 21 provinces + UB | Complete coverage |
| "by soum" / "by bag" | Lowest levels | ~330 soums or ~1500 bags |
| "national" / no region | Single value | Country aggregate |
| "by region" | 4-6 regional aggregates | Central, Eastern, Western, Khangai |

### How to Detect Coverage

**Step 1: Search broadly for your topic**

```bash
python3 query_api.py "weekly prices"
python3 query_api.py "price aimag"
python3 query_api.py "price capital"
```

**Step 2: Compare table dimensions**

```bash
python3 query_api.py --detailed "WEEKLY PRICES"
```

Look for:
- **Region dimension**: How many values? Does it include "Ulaanbaatar" or "Capital"?
- **Time dimension**: How many values? (more = longer history)
- **Other dimensions**: Products, sectors, etc.

**Step 3: Document the coverage**

| Table ID | Geographic | Granularity | Time Range | Products |
|----------|-----------|-------------|------------|----------|
| 0600_001V4 | UB only | - | 251 weeks (~5yr) | 31 |
| 0300_010V5 | 21 aimags + regions | aimag | 98 weeks (~2yr) | 11 |

### Coverage Decision Matrix

| Situation | Action |
|-----------|--------|
| Table covers area not in registry | Add with geographic qualifier in name |
| Table has longer history | Consider adding as alternative |
| Table has more dimensions | May be useful for detailed splits |
| Table is subset of existing | Link as related, may skip adding |
| Table has complete coverage | Prefer over partial coverage |

### Naming Convention for Related Tables

When related tables exist, use geographic qualifiers:

```
weekly-prices-ulaanbaatar  → UB/national data
weekly-prices-aimags       → Provincial data (no UB)
weekly-prices              → Complete coverage (if exists)
```

### Registry Integration

When adding a dataset with known overlaps:

```python
reg.add_dataset(
    dataset_id='weekly-prices-ulaanbaatar',
    # ... other fields ...
    coverage_geography='["Ulaanbaatar"]',
    coverage_granularity=None,  # No sub-breakdown within UB
    coverage_time_start='2020-01',
    coverage_frequency='weekly',
    concept_id='weekly-prices',
    related_datasets='["weekly-prices-aimags"]'
)
```

See `data/docs/principles/coverage-detection.md` for complete documentation.
