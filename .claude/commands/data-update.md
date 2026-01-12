# Data Update Command

Check all registered data sources for updates and process them using parallel worker agents.

## Overview

This command orchestrates dataset updates in two phases:
1. **Discovery Phase**: Check all datasets for available updates (sequential)
2. **Execution Phase**: Update datasets in parallel batches using worker agents

## Critical: Understanding Parent/Split Relationships

Datasets can be:
1. **Standalone**: No parent, no splits (simple datasets)
2. **Parent**: Has `is_parent=1`, contains splits defined in `## Splits` section
3. **Split**: Has `parent_id` pointing to parent, has `split_filter` JSON

**When updating**:
- Only check PARENT datasets (or standalone) for source updates
- When a parent updates, ALL its splits must be regenerated (handled by worker)
- Never check splits directly - they derive from parent data

---

## Phase 1: Discovery (Sequential)

### 1.1 Load Registry

```bash
cd /Users/ritz/Insync/robert@aum.edu.mn/Google\ Drive/data/tools && python -m registry list
```

Get all datasets that are candidates for updates:
- `auto_update=1` (enabled for automatic updates)
- Either standalone (`parent_id IS NULL AND is_parent=0`) OR parent (`is_parent=1`)
- **Skip splits** (`parent_id IS NOT NULL`) - these are updated by their parent

### 1.2 Check Each Dataset for Updates

For each candidate dataset, determine if an update is available.

#### For API Sources (nso-1212)

1. Read the source definition: `tools/sources/nso-1212/source.md`
2. Query the API to get the table's `updated` timestamp:
   ```
   GET https://data.1212.mn/api/v1/en/NSO/{sector}/{subsector}/
   ```
3. Find the table by its ID (e.g., `DT_NSO_0300_003V1.px`)
4. Compare API's `updated` field with dataset's `source_updated_at` in registry
5. If API timestamp is newer → update available

#### Handle Missing Tables

When checking a dataset, if the table ID (e.g., `DT_NSO_0300_003V1.px`) is NOT found in the API response:

1. **Mark as error** in the check results:
   ```python
   {
       "dataset_id": "...",
       "source_id": "nso-1212",
       "has_update": False,
       "error": "table_not_found",
       "source_ref": "DT_NSO_0400_021V1.px",
       "suggestion": None  # Will be populated by search
   }
   ```

2. **Search for similar tables** using the skill cache:
   ```bash
   # Skills are at Drive root (../.claude from data/)
   cd ../.claude/skills/datamn-source-nso
   python3 query_api.py [keywords from dataset name]
   ```

3. **Record suggestions** if similar tables found:
   ```python
   result["suggestion"] = {
       "similar_tables": ["DT_NSO_0400_053V1.px", "DT_NSO_0400_022V1.px"],
       "reason": "Tables with 'salary' or 'wage' in name"
   }
   ```

4. **Report in Phase 1.3** with special formatting:
   ```
   ⚠️ Missing Tables (1):
     - average-salary: Table DT_NSO_0400_021V1.px not found in API
       Possible replacements:
       - DT_NSO_0400_053V1.px: Labour share of GDP (wages)
       - MONTHLY AVERAGE NOMINAL WAGES: Monthly wages by category

       Action needed: Update source_ref in registry or investigate API changes
   ```

5. **Skip these datasets** in Phase 2 execution - they require manual intervention.

#### For PDF/Web Sources (mrpam, mongolbank)

1. Read the source definition: `tools/sources/{source}/source.md`
2. Use Playwright MCP to navigate to the source page
3. Find the latest report/data date on the page
4. Compare with dataset's `last_fetched_at` in registry
5. If source has newer data → update available

#### Record Results

For each dataset, record:
```python
{
    "dataset_id": "nso-population-by-age-sex",
    "source_id": "nso-1212",
    "has_update": True,
    "source_updated_at": "2025-11-15T00:00:00Z",
    "source_definition_path": "tools/sources/nso-1212/source.md",
    "dataset_definition_path": "tools/sources/nso-1212/datasets/population-by-age-sex.md"
}
```

### 1.3 Report Status to User

Display a summary of findings:

```
Checking 8 datasets for updates...

Updates available (4):
  - nso-population-by-age-sex (source updated: 2025-11-15)
  - nso-gdp-quarterly (source updated: 2025-11-10)
  - mrpam-monthly-mining (new report: October 2025)
  - mongolbank-exchange-rates (source updated: 2025-11-28)

Already current (3):
  - nso-trade-balance (checked, no updates)
  - nso-employment (checked, no updates)
  - mongolbank-interest-rates (checked, no updates)

Errors (1):
  - mrpam-licensing: Could not access page (timeout)

Proceed with 4 updates? [Y/n]
```

Wait for user confirmation before proceeding.

---

## Phase 2: Parallel Execution

After user confirms, process updates using parallel worker agents.

### 2.1 Batch Datasets

Group datasets needing updates into batches of **4 workers maximum**.

Example with 7 datasets:
- Batch 1: datasets 1-4 (parallel)
- Batch 2: datasets 5-7 (parallel)

### 2.2 Spawn Worker Agents

For each batch, spawn Task agents in parallel using `subagent_type="datamn-dataset-worker"`.

**The agent file contains complete instructions** - you just need to provide parameters.

#### Worker Task Prompt

For each dataset, spawn a `datamn-dataset-worker` agent:

```
Task tool:
  subagent_type: "datamn-dataset-worker"
  prompt: |
    UPDATE existing dataset with these parameters:

    - DATASET_ID: {dataset_id}
    - SOURCE_ID: {source_id}
    - SOURCE_UPDATED_AT: {source_updated_at}
    - MODE: update (not create)

    Source definition: data/tools/sources/{source_id}/source.md
    Dataset definition: data/tools/sources/{source_id}/datasets/{dataset_id}.md

    Follow your standard workflow:
    1. Read definitions
    2. Fetch latest data
    3. Process splits (if parent)
    4. Generate charts and MDX
    5. Update registry
    6. Report WORKER_RESULT
```

The agent has complete instructions in `.claude/agents/datamn-dataset-worker.md`.

#### Spawning Parallel Tasks

**IMPORTANT**: Send all Task tool calls for a batch in a SINGLE message to ensure parallel execution.

Example for a batch of 4:

```
Use Task tool 4 times in ONE message:

Task 1: subagent_type="general-purpose", description="Update nso-population-by-age-sex"
  [Worker prompt for dataset 1]

Task 2: subagent_type="general-purpose", description="Update nso-gdp-quarterly"
  [Worker prompt for dataset 2]

Task 3: subagent_type="general-purpose", description="Update mrpam-monthly-mining"
  [Worker prompt for dataset 3]

Task 4: subagent_type="general-purpose", description="Update mongolbank-exchange-rates"
  [Worker prompt for dataset 4]
```

### 2.3 Collect Results

Each worker returns a structured WORKER_RESULT. Parse these results:

**Success example:**
```json
{
  "dataset_id": "nso-population-by-age-sex",
  "status": "success",
  "new_version": 3,
  "row_count": 2880,
  "rows_changed": 48,
  "splits_updated": ["population-total", "population-pyramid", "population-by-sex"],
  "files_generated": [...]
}
```

**Error example:**
```json
{
  "dataset_id": "mrpam-monthly-mining",
  "status": "error",
  "failed_at_step": "Step 4: Fetch Data",
  "error_message": "PDF table structure changed",
  "suggestion": "Update extraction instructions in dataset definition"
}
```

### 2.4 Process Next Batch

If more datasets remain, spawn the next batch of up to 4 workers.
Continue until all batches are complete.

---

## Phase 3: Validation & Summary

### 3.1 Validate All Charts

**CRITICAL**: After all workers complete, validate all generated charts:

```bash
cd /Users/ritz/Insync/robert@aum.edu.mn/Google\ Drive/data/data.mn && python3 ../tools/scripts/validate_vega.py --all
```

**Do NOT proceed if the validator reports errors.** Fix all errors before finishing.

### 3.2 Display Final Summary

```
=== Update Complete ===

Successful (3/4):
  nso-population-by-age-sex: v3
    - 2880 rows (48 new)
    - Splits updated: population-total, population-pyramid, population-by-sex
    - 6 MDX pages, 3 charts, 3 CSVs generated

  nso-gdp-quarterly: v5
    - 240 rows (4 new)
    - 2 MDX pages, 1 chart, 1 CSV generated

  mongolbank-exchange-rates: v12
    - 3650 rows (30 new)
    - 2 MDX pages, 1 chart, 1 CSV generated

Failed (1/4):
  mrpam-monthly-mining
    - Error at: Step 4 (Fetch Data)
    - Reason: PDF table structure changed on page 3
    - Suggestion: Update tools/sources/mrpam/datasets/monthly-mining-stats.md

Chart Validation: PASSED (5 charts validated)

Files Generated:
  - 10 MDX pages (5 EN, 5 MN)
  - 5 Vega-Lite chart specs
  - 5 CSV files
  - 5 XLSX files

Next Steps:
  1. Review failed dataset definition
  2. Create changelog entries for updated datasets
  3. Preview changes: cd data.mn && npm run dev
  4. Build site: cd data.mn && npm run build
  5. Deploy: kamal deploy
```

---

## Creating Changelog Entries

**IMPORTANT**: After successfully updating datasets, create changelog entries to document significant changes.

### When to Create Changelog Entries for Updates

Create a changelog entry when:
- **Major data updates**: New data covering multiple months/quarters/years
- **Structural changes**: New variables, changed categories, extended time range
- **Data quality improvements**: Corrections, revisions, or restatements
- **Source changes**: Dataset now uses a different or additional source

**Skip changelog entries for:**
- Minor routine updates (adding 1-2 recent data points)
- Automated monthly/quarterly updates without significant changes
- Technical fixes that don't affect data content

### Changelog Entry Template for Updates

Create two MDX files (one for each language):

**File names:**
- English: `data.mn/src/data/changelog/en/{YYYY-MM-DD}-{dataset-id}.mdx`
- Mongolian: `data.mn/src/data/changelog/mn/{YYYY-MM-DD}-{dataset-id}.mdx`

Use today's date in YYYY-MM-DD format.

**Template content (identical for both EN and MN files):**

```mdx
---
date: {YYYY-MM-DD}
action: updated
dataset_id: {dataset-id}
dataset_name_en: {English dataset title}
dataset_name_mn: {Mongolian dataset title}
description_en: {1-2 sentence English description of what changed, what's new, or what was improved}
description_mn: {1-2 sentence Mongolian description of what changed, what's new, or what was improved}
source: {Source name, e.g., "National Statistics Office"}
version: {new version number}
---
```

### Example Changelog Entry for Update

**File: `data.mn/src/data/changelog/en/2025-12-05-gdp-quarterly.mdx`**
**File: `data.mn/src/data/changelog/mn/2025-12-05-gdp-quarterly.mdx`**

```mdx
---
date: 2025-12-05
action: updated
dataset_id: gdp-quarterly
dataset_name_en: Mongolia Quarterly GDP (2000-2024)
dataset_name_mn: Монгол Улсын улирлын ДНБ (2000-2024)
description_en: Updated with Q3 2024 data from Bank of Mongolia. Added year-over-year growth rate calculations and extended historical coverage back to 2000.
description_mn: Монголбанкнаас авсан 2024 оны 3-р улирлын өгөгдлөөр шинэчлэв. Өмнөх оны мөн үеэс өссөн хурдыг нэмж тооцоолж, түүхэн өгөгдлийг 2000 он хүртэл сунгав.
source: Bank of Mongolia
version: 5
---
```

### Notes

- The frontmatter is identical in both language files
- Version number should match the new version in the registry
- Focus on what's **new or changed**, not a full dataset description
- For split datasets, create ONE changelog entry for the parent dataset
- See `data.mn/CHANGELOG_TEMPLATE.md` for complete documentation

---

## Error Handling

### Worker Failures

- Workers are independent - one failure doesn't affect others
- Failed workers report detailed errors
- Orchestrator collects all results before showing summary
- No registry updates occur for failed datasets (atomic per-dataset)

### Discovery Errors

If a source cannot be checked during discovery:
- Log the error
- Skip that dataset
- Continue checking others
- Report in summary

### Missing Source Tables

If a dataset's source table no longer exists in the API:
- This is NOT an automatic retry situation
- User must investigate: was the table renamed, removed, or restructured?
- Use `datamn-source-nso` skill to search for replacement tables
- Update the dataset's `source_ref` in the registry once resolved
- Consider refreshing the skill cache: `python3 query_api.py --refresh`

### Table Replacement Process

When a source table is renamed or restructured (e.g., `DT_NSO_0400_021V1.px` → `DT_NSO_0400_022V1.px`):

1. **Keep the old version** - The version history preserves all previous data
2. **Find the replacement** using the skill:
   ```bash
   # Skills are at Drive root (../.claude from data/)
   cd ../.claude/skills/datamn-source-nso
   python3 query_api.py [keywords]  # e.g., "salary wages"
   ```
3. **Update the registry** with new source_ref
4. **Log the replacement** in activity_log with message:
   ```
   TABLE REPLACED: Old source X no longer exists. Replaced with Y.
   Note: [any data differences, e.g., time range changes]
   ```
5. **Re-fetch and regenerate** the dataset with new source

**Important**: Document any data loss (e.g., "Lost 1995-2000 data, now starts 2001") in the activity log for audit trail.

### Retry Option

After showing summary, offer:
```
Would you like to retry failed datasets? [y/N]
```

If yes, spawn new workers for failed datasets only.

---

## Command Options

Parse these from user input if provided:

- `--source {source_id}` - Only check/update datasets from this source
- `--dataset {dataset_id}` - Only check/update this specific dataset
- `--dry-run` - Check for updates but don't fetch/process
- `--force` - Re-fetch even if no updates detected
- `--batch-size {n}` - Override default batch size of 4

Examples:
```
/data-update --source nso-1212
/data-update --dataset nso-population-by-age-sex --force
/data-update --dry-run
```

---

## Activity Logging

All operations are logged to the registry's activity_log table:

- Discovery: `action='check'` for each dataset checked
- Updates: Workers log their own `action='update'` entries
- Errors: `action='error'` with details

---

## Notes

- Run from the `data/` directory
- Safe to run multiple times (idempotent)
- Workers have access to all tools (Bash, Read, Write, Playwright MCP, etc.)
- Typical update cycle: 5-15 minutes depending on number of datasets
- Maximum parallel workers: 4 (conservative limit for stability)
- Uses skills: `datamn-registry`, `datamn-source-nso`, `datamn-chart-vega`, `datamn-page-mdx` (translations), `datamn-transform-split` (CSV/XLSX)
- Spawns `datamn-dataset-worker` agents for parallel updates (see `.claude/agents/datamn-dataset-worker.md`)
- **Always validate charts** before completing the update
