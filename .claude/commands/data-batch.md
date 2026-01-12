# Data Batch Command

Create multiple datasets from a list with source hints. This command orchestrates parallel discovery and creation of datasets.

## Usage

```
/data-batch
```

Then provide a list of datasets with optional source hints:
- Inline: "Population from NSO, Inflation from MongolBank, Mining from MRPAM"
- Or when prompted, enter each dataset on a new line

## Input Formats

### Format 1: Inline List

```
/data-batch Population from NSO, Inflation from NSO/MongolBank, Mining stats from MRPAM
```

### Format 2: Interactive

```
/data-batch

Enter datasets (one per line, empty line to finish):
> Population trends
> GDP and economic growth
> Exchange rates from MongolBank
>
```

### Format 3: With Source Hints

```
/data-batch

Enter datasets with optional source hints:
> Population by age from NSO table DT_NSO_0300_003V1.px
> Inflation rate from NSO/MongolBank
> Mining production from MRPAM PDF
>
```

## Workflow

### Phase 1: Parse Input

Parse the input into structured entries:

```python
entries = [
    {"topic": "Population", "source_hints": ["nso-1212"], "table_id": None},
    {"topic": "Inflation", "source_hints": ["nso-1212", "mongolbank"], "table_id": None},
    {"topic": "Mining stats", "source_hints": ["mrpam"], "table_id": None}
]
```

**Source hint keywords:**
- `NSO`, `1212` → `nso-1212`
- `MongolBank`, `Bank of Mongolia` → `mongolbank`
- `MRPAM`, `Mining` → `mrpam`

### Phase 2: Parallel Discovery

Spawn discovery workers for each entry:

```
For each entry:
1. Create Task with datamn-discovery-worker agent
2. Include search query and source hints
3. Collect DISCOVERY_RESULT from each
```

**IMPORTANT**: Send all Task calls in a SINGLE message for parallel execution.

Example spawning:

```
Task 1: datamn-discovery-worker
  Search for "Population" in nso-1212
  Return matching tables with metadata

Task 2: datamn-discovery-worker
  Search for "Inflation" in nso-1212, mongolbank
  Return matching tables with metadata

Task 3: datamn-discovery-worker
  Search for "Mining stats" in mrpam
  Return matching tables with metadata
```

### Phase 3: Present Matches

Collect all discovery results and present to user:

```
📊 Discovery Results

1. Population (NSO)
   Found 3 matching tables:
   ├── DT_NSO_0300_003V1.px - Population by age and sex (2024)
   ├── DT_NSO_0300_007V1.px - Population by region (2024)
   └── DT_NSO_0300_001V2.px - Total population (historical)

   Recommended: DT_NSO_0300_003V1.px (most comprehensive)

2. Inflation (NSO + MongolBank)
   Found 2 matching tables:
   ├── [NSO] DT_NSO_2100_001V1.px - Consumer Price Index
   └── [MongolBank] Monthly inflation statistics

   Recommended: NSO table (has historical data)

3. Mining stats (MRPAM)
   Found 1 source:
   └── Monthly Mining Report PDF (November 2025)

Select tables to create datasets from:
[1] All recommended
[2] Custom selection
[3] Skip some
```

### Phase 4: Analyze Selected Tables

For each selected table, spawn an analysis worker:

```
Task: datamn-discovery-worker (analyze mode)
  Analyze structure of DT_NSO_0300_003V1.px
  Return dimensions and recommended splits
```

Present split recommendations:

```
📊 Dataset Splits for Population (DT_NSO_0300_003V1.px)

Dimensions: Year (40 values), Sex (3), Age Group (16)

Recommended datasets:
[x] 1. population-total - Mongolia Total Population (1956-2024)
[x] 2. population-pyramid - Population Pyramid (2024)
[x] 3. population-by-sex - Population by Sex (1956-2024)
[ ] 4. population-by-age - Population by Age Group (2024)

Select datasets to create (comma-separated numbers, or 'all'):
```

### Phase 5: Parallel Dataset Creation

For each confirmed dataset, spawn a creation worker:

```
Batch datasets into groups of 4 (maximum parallel workers)

For each batch:
  Send all Task calls in ONE message:

  Task 1: datamn-dataset-worker
    Create population-total from parent nso-population-by-age-sex

  Task 2: datamn-dataset-worker
    Create population-pyramid from parent nso-population-by-age-sex

  Task 3: datamn-dataset-worker
    Create population-by-sex from parent nso-population-by-age-sex

  Task 4: datamn-dataset-worker
    Create inflation-cpi from nso-cpi-data

Wait for batch to complete before starting next batch.
```

### Phase 6: Validation

After all workers complete:

```bash
cd data/data.mn && python3 ../tools/scripts/validate_vega.py --all
```

**CRITICAL**: Fix any chart validation errors before proceeding.

### Phase 7: Summary

```
=== Batch Creation Complete ===

Created (12 datasets):

From Population (DT_NSO_0300_003V1.px):
  ✓ population-total - 40 rows, area chart
  ✓ population-pyramid - 30 rows, pyramid chart
  ✓ population-by-sex - 80 rows, multi-line chart

From Inflation (DT_NSO_2100_001V1.px):
  ✓ inflation-cpi - 120 rows, area chart
  ✓ inflation-by-category - 480 rows, multi-line chart

From Mining (MRPAM PDF):
  ✓ mining-coal-production - 24 rows, bar chart
  ✓ mining-permits - 12 rows, bar chart

Failed (1):
  ✗ mining-exports - PDF table structure changed
    → Update extraction instructions in source definition

Files generated:
  - 12 CSV files
  - 12 XLSX files
  - 12 chart specs
  - 24 MDX pages (12 EN + 12 MN)

Chart validation: PASSED

Next steps:
  1. Preview: cd data/data.mn && npm run dev
  2. Build: cd data/data.mn && npm run build
  3. Deploy: kamal deploy
```

## Options

- `--dry-run` - Show what would be created without creating
- `--source {id}` - Only search in specific source
- `--no-splits` - Don't recommend splits, create as-is
- `--batch-size {n}` - Override default batch size of 4

## Error Handling

### Discovery Errors

If a source cannot be searched:
- Log the error
- Continue with other sources
- Report in summary

### Creation Errors

Worker failures don't affect other workers:
- Failed datasets reported in summary
- Successful datasets still committed
- Offer retry for failed ones

## Skills Used

- `datamn-source-nso` - NSO data search
- `datamn-source-mongolbank` - Bank of Mongolia (when available)
- `datamn-source-mrpam` - MRPAM (when available)
- `datamn-registry` - Dataset registration
- `datamn-chart-vega` - Chart generation
- `datamn-page-mdx` - Page generation
- `datamn-transform-split` - Data transformation

## Agents Used

- `datamn-discovery-worker` - Search and analyze sources
- `datamn-dataset-worker` - Create individual datasets

## Notes

- Maximum 4 parallel workers at a time
- Always validate charts after creation
- Parent datasets are created automatically when needed
- All datasets get both EN and MN pages
