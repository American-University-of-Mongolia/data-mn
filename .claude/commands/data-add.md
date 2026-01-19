# Data Add Command

Interactively add a new dataset to track in the registry.

---

## ⚠️ MANDATORY: Agents & Skills Usage

**This command REQUIRES using specific agents and skills. Do NOT skip these.**

### Required Agents (use Task tool)

| Agent | When to Use | Subagent Type |
|-------|-------------|---------------|
| **datamn-discovery-worker** | Searching for data, checking what's available | `datamn-discovery-worker` |
| **datamn-dataset-worker** | Creating EACH dataset (parent + every split) | `datamn-dataset-worker` |
| **datamn-checker-worker** | After creation, validating all files | `datamn-checker-worker` |

### Required Skills (use Skill tool)

| Skill | When to Invoke | Purpose |
|-------|----------------|---------|
| `datamn-source-nso` | Before searching NSO data | API query instructions |
| `datamn-registry` | Before registry operations | CLI/Python commands |
| `datamn-chart-vega` | Before creating charts | Templates & brand colors |
| `datamn-page-mdx` | Before creating MDX | Translation tables & templates |
| `datamn-transform-split` | Before splitting data | Filter logic & export patterns |

### Workflow Pattern

```
1. User requests data → ASK: which source?
2. INVOKE SKILL: datamn-source-nso (if NSO)
3. SPAWN AGENT: datamn-discovery-worker → search & recommend splits
4. User approves splits
5. FOR EACH dataset (parent + splits):
   └─ SPAWN AGENT: datamn-dataset-worker → creates all files
6. SPAWN AGENT: datamn-checker-worker → validates everything
7. Fix any issues → Re-run checker until green
8. Show user next steps (preview, publish, deploy)
```

**CRITICAL**: You MUST spawn `datamn-dataset-worker` for EACH dataset. Do NOT try to create dataset files manually in the main conversation.

---

## 🛑 MANDATORY: Post-Creation Validation Checklist

**STOP! Before showing "Next Steps" to the user, you MUST complete ALL of these:**

### Validation Checklist (ALL REQUIRED)

- [ ] **Run `validate_dataset.py --all {dataset_id}` for EACH dataset created**
  ```bash
  # From the data/ project root directory:
  python3 tools/scripts/validate_dataset.py --all {dataset_id} --base-dir data.mn
  ```

- [ ] **All datasets must show "Valid: 11, Invalid: 0"**
  - If any show Invalid > 0, FIX THE ISSUES before proceeding

- [ ] **Run `validate_vega.py` on all new charts**
  ```bash
  python3 tools/scripts/validate_vega.py data.mn/public/charts/{dataset_id}-en.json
  ```

- [ ] **Charts must show "✓ Chart is valid" (warnings are OK, errors are NOT)**

### Why Worker Self-Validation Is NOT Enough

The `datamn-dataset-worker` agents report their own validation, but this is NOT sufficient because:
1. Workers may use different validation logic than the official validators
2. Workers may miss cross-file consistency issues
3. Workers may report success even when files are in wrong locations
4. Independent validation catches issues workers don't check

**⚠️ DO NOT skip this step. DO NOT rely solely on worker-reported validation.**

### If Validation Fails

1. Read the error messages carefully
2. Fix each specific issue (missing files, wrong paths, invalid chart specs)
3. Re-run validation
4. Repeat until ALL checks pass

Only after ALL validation passes should you proceed to show the user "Next Steps".

---

## Philosophy: Statista-style Data

**IMPORTANT**: Data from sources like 1212.mn is often highly compressed with multiple dimensions (sex, age, region, year, etc.). This makes it confusing for users.

Our goal is to be like **Statista** - make data user-friendly by splitting complex, multi-dimensional datasets into **simple, single-topic datasets**. For example:

- ❌ "Population by age, sex, and year (1956-2024)" - Too many dimensions
- ✅ "Mongolia Total Population (1956-2024)" - Simple trend
- ✅ "Mongolia Population Pyramid (2024)" - Clear snapshot
- ✅ "Mongolia Population by Sex (1956-2024)" - Single comparison

Each dataset should answer **ONE clear question** that users might ask.

## Critical: Dataset Splitting

**YOU MUST ALWAYS CONSIDER SPLITTING** when adding datasets from 1212.mn or other multi-dimensional sources.

### How Splitting Works

1. **Parent Dataset**: The raw multi-dimensional data from the source (e.g., `nso-population-by-age-sex`)
   - Registered with `is_parent=1`
   - Stores the complete raw data in `tools/versions/`
   - Has a `## Splits` section in its definition file

2. **Split Datasets**: User-friendly filtered views (e.g., `population-total`, `population-pyramid`)
   - Registered with `parent_id` pointing to parent
   - Has `split_filter` JSON defining the filter criteria
   - Gets its own MDX pages, CSV/XLSX, and chart spec

### When to Split

Split a dataset when it has **2+ dimensions** beyond the time dimension. Ask yourself:
- Does this data have multiple categories (sex, region, age group)?
- Would users want to see just one slice of this data?
- Can we create simpler charts by filtering?

### Registry Fields for Splits

```sql
-- Parent dataset
is_parent = 1
parent_id = NULL

-- Split dataset
is_parent = 0
parent_id = 'nso-population-by-age-sex'
split_filter = '{"sex": "Total", "age_group": "Total"}'
```

## File Locations

**CRITICAL**: All output files must go to the correct locations:

| File Type | Location |
|-----------|----------|
| MDX Pages (EN) | `data.mn/src/data/data/en/{id}.mdx` |
| MDX Pages (MN) | `data.mn/src/data/data/mn/{id}.mdx` |
| CSV Downloads | `data.mn/public/datasets/{id}-{lang}.csv` |
| XLSX Downloads | `data.mn/public/datasets/{id}.xlsx` |
| Chart Specs | `data.mn/public/charts/{id}-{lang}.json` |
| Dataset Definitions | `tools/sources/{source}/datasets/{id}.md` |
| Raw Data Backup | `tools/versions/{id}/` |

**WARNING**: Do NOT use `src/content/data/` - this project uses `src/data/data/` for content collections.

## Coverage Check (MANDATORY)

**CRITICAL**: Before creating any new dataset, you MUST check for overlapping tables that cover the same indicator at different granularities.

### Why Coverage Detection Matters

NSO and other sources often publish the same indicator in multiple tables:
- Weekly prices **for Ulaanbaatar only** vs **for all aimags (no UB)**
- GDP per capita **national** vs **by aimag**
- Unemployment **by sex/age** vs **by region**

Without checking, you risk:
- Creating confusing duplicates
- Missing better coverage options
- Inconsistent naming

### Coverage Detection Steps

**Step 1: Search for Related Tables**

When the user requests a topic (e.g., "weekly prices"), search broadly:

```bash
cd ../.claude/skills/datamn-source-nso
python3 query_api.py "weekly prices"
python3 query_api.py "price aimag"
python3 query_api.py "price capital"
```

**Step 2: Identify Coverage Patterns**

Look for tables with similar names but different geographic/temporal coverage:

| Pattern | Meaning |
|---------|---------|
| "by aimags" | Provincial data, often excludes UB |
| "aimags and the Capital" | Complete coverage including UB |
| "by soum" / "by bag" | Lower geographic levels |
| "national" | Single country value |
| "weekly" vs "monthly" | Different update frequency |

**Step 3: Check Existing Registry**

```bash
cd data/tools
python -m registry list | grep -i "price"
python -m registry info existing-dataset-id
```

**Step 4: Present Coverage Analysis to User**

```
📊 Coverage Analysis

Found 3 tables for "weekly prices":

| Table | Geographic | Products | Time Range |
|-------|-----------|----------|------------|
| 0600_001V4 | UB only | 31 | 2020-present |
| 0300_010V5 | 21 aimags (no UB) | 11 | 2024-present |
| 0600_019V1 | All (monthly) | many | 2015-present |

Existing in registry:
- weekly-prices-aimags (from 0300_010V5)

Recommendation: Add 0600_001V4 as "weekly-prices-ulaanbaatar" to complement existing data.
```

**Step 5: Name Datasets to Show Coverage**

When coverage varies, encode it in the dataset ID:

| Scope | Dataset ID Pattern |
|-------|-------------------|
| UB only | `{topic}-ulaanbaatar` |
| Aimags (no UB) | `{topic}-aimags` |
| All regions | `{topic}` (no qualifier) |
| National only | `{topic}-national` |

**Step 6: Document Coverage in Registry**

Set coverage fields when registering:
- `coverage_geography`: JSON array of regions covered
- `coverage_granularity`: national, regional, aimag, soum, bag
- `coverage_time_start`: When data begins
- `coverage_frequency`: weekly, monthly, quarterly, annual
- `concept_id`: Groups related datasets
- `related_datasets`: Links to alternatives

See `data/docs/principles/coverage-detection.md` for complete documentation.

---

## Workflow

### 1. Ask Source Type

Ask the user which source they want to add data from:

1. **nso-1212** - National Statistics Office (1212.mn)
2. **mrpam** - Mining and Petroleum Authority (PDF reports)
3. **mongolbank** - Bank of Mongolia
4. **new** - Create a new source

### 2. For NSO 1212 Source

If user selects `nso-1212`:

#### Step 2.1: Invoke NSO Skill (REQUIRED)
```
INVOKE SKILL: datamn-source-nso
```
This gives you the API query commands and table catalog.

#### Step 2.2: Search Using Discovery Agent (REQUIRED)
```
SPAWN AGENT: datamn-discovery-worker
Prompt: |
  MODE: Search for Datasets
  SOURCE_ID: nso-1212
  SEARCH_QUERY: {user's search terms}

  Search 1212.mn for matching tables. Return:
  - Table IDs and titles
  - Dimensions/variables
  - Recommended splits for user-friendly datasets
```

#### Step 2.3: Present Results & Get Approval
Show the discovery results to the user:
- Available tables matching their query
- Recommended dataset splits
- Ask them to approve/modify the split plan

#### Step 2.4: Create Each Dataset Using Worker Agents (REQUIRED)

**⚠️ CRITICAL: You MUST spawn `datamn-dataset-worker` for EACH dataset. Do NOT create files manually.**

For the parent dataset AND each approved split:
```
SPAWN AGENT: datamn-dataset-worker
Prompt: |
  Create dataset with these parameters:
  - DATASET_ID: {dataset_id}
  - SOURCE_ID: nso-1212
  - PARENT_ID: {parent_id or null}
  - SPLIT_FILTER: {filter JSON or null}
  - TITLE_EN: {english title}
  - TITLE_MN: {mongolian title}
  - CATEGORY_EN: {category}
  - CATEGORY_MN: {mongolian category}
  - CHART_TYPE: {area|line|bar|population-pyramid}
  - TABLE_ID: {NSO table ID}
```

You can spawn multiple workers in parallel (up to 4 at a time) for independent splits.

#### Step 2.5: Validate with Checker Agent (REQUIRED)
```
SPAWN AGENT: datamn-checker-worker
Prompt: |
  Validate dataset: {dataset_id}
  base_dir: data.mn
```

Run checker for each dataset created. Parse the report and fix any issues.

#### Step 2.6: Fix Loop
If checker reports failures:
1. Fix the specific issues identified
2. Re-spawn checker
3. Repeat until all 85 checks pass

#### Step 2.7: Finalize
Once all datasets pass validation:
- Show user the created files
- Provide next steps (preview, publish, deploy)

### 3. For MRPAM Source

If user selects `mrpam`:

1. **Read source definition**: `tools/sources/mrpam/source.md`

2. **Ask what data to track**:
   - Mining permits statistics
   - Coal production
   - Petroleum statistics
   - All (combined monthly report)

3. **Navigate to MRPAM** using web-navigator skill:
   - Go to https://mrpam.gov.mn/page/714
   - Identify the latest report
   - Download the PDF

4. **Create dataset definition** with extraction instructions

5. **Extract initial data** from PDF (Mongolian only)

6. **Translate to create bilingual CSVs**:
   - Identify categorical columns requiring translation
   - Generate translations using standard mappings + AI
   - Create both `-en.csv` and `-mn.csv` versions
   - Validate that both files have matching structure

7. **Generate content** using bilingual CSVs

### 4. For Mongolbank Source

Similar workflow, following `tools/sources/mongolbank/source.md`

**Note**: Check if the specific dataset is bilingual or single-language. If single-language, follow the translation workflow (see step 6 in MRPAM section above).

### 5. For New Source

1. **Ask for source details**:
   - Name (EN and MN)
   - URL
   - Type (api, pdf, scrape)
   - Update frequency

2. **Navigate to source** to understand structure

3. **Create source.md** definition file

4. **Register source** in database

5. Then proceed to add a dataset from this new source

## Language and Translation Workflow

**CRITICAL**: All datasets MUST have bilingual CSVs (`-en.csv` and `-mn.csv`).

### For NSO 1212.mn
NSO provides bilingual data via API. Use `fetch_data.py` to fetch both languages automatically.

### For Single-Language Sources (MRPAM, MongolBank PDFs, etc.)

When a source provides data in only ONE language, follow this translation workflow:

#### Step 1: Detect Source Language
After extracting/fetching data, determine the language:
- Column names in Cyrillic → Mongolian
- Column names in Latin alphabet → English

#### Step 2: Identify Translation Needs
```python
import pandas as pd

df_source = pd.read_csv('raw-data.csv')

# Find categorical columns (non-numeric)
string_cols = df_source.select_dtypes(include=['object']).columns
date_cols = [col for col in string_cols if 'date' in col.lower() or 'он' in col.lower()]
categorical_cols = [col for col in string_cols if col not in date_cols]

print(f"Columns requiring translation: {categorical_cols}")
```

#### Step 3: Apply Translation
Use standard translation mappings from the source template skill:
- Column name translations
- Common value translations (gender, urban/rural, sectors, etc.)
- Source-specific translations

```python
# Load standard translations
from datamn_translations import STANDARD_COLUMN_TRANSLATIONS, STANDARD_VALUE_TRANSLATIONS

# Apply translations to create the target language version
if source_language == 'mn':
    df_en = translate_mongolian_to_english(df_source)
    df_mn = df_source
else:
    df_mn = translate_english_to_mongolian(df_source)
    df_en = df_source
```

#### Step 4: Validate Bilingual Output
- Both CSVs have identical row counts
- Numeric columns have identical values
- Only categorical/string columns differ
- Column counts match (no added/removed columns)

#### Step 5: Save Both Versions
```python
df_en.to_csv(f'{dataset_id}-en.csv', index=False)
df_mn.to_csv(f'{dataset_id}-mn.csv', index=False)
```

**See** `.claude/skills/datamn-source-template/SKILL.md` section "Handling Single-Language Sources" for complete translation workflow and standard mappings.

## Data Analysis and Splitting

**This is a critical step.** After fetching raw data from any source and ensuring bilingual CSVs exist:

### 1. Analyze Data Structure

```python
import pandas as pd

df = pd.read_csv("raw_data.csv")

# Identify dimensions (columns with categorical values)
dimensions = []
for col in df.columns:
    if df[col].dtype == 'object' or df[col].nunique() < 20:
        dimensions.append({
            "column": col,
            "unique_values": df[col].nunique(),
            "values": df[col].unique().tolist()[:10]  # First 10 values
        })

# Identify value columns (numeric)
value_columns = df.select_dtypes(include=['number']).columns.tolist()
```

### 2. Present Analysis to User

Show the user what you found:

```
📊 Data Analysis

Dimensions found:
- Sex: 3 values (Total, Male, Female)
- Age Group: 16 values (Total, 0-4, 5-9, ...)
- Year: 40 values (1956-2024)

Value column: population

Total rows: 1,920
```

### 3. Recommend Splits

Based on the dimensions, recommend user-friendly datasets:

```
🎯 Recommended Datasets

Based on this data structure, I recommend creating these user-friendly datasets:

1. **population-total** - Total population over time (1956-2024)
   - Filter: Sex=Total, Age=Total
   - Chart: Line chart showing trend
   - Question it answers: "How has Mongolia's population grown?"

2. **population-pyramid** - Population by age and sex for latest year
   - Filter: Year=2024, Age≠Total, Sex≠Total
   - Chart: Population pyramid (horizontal bars)
   - Question it answers: "What is the age distribution?"

3. **population-by-sex** - Male vs Female population over time
   - Filter: Age=Total, Sex≠Total
   - Chart: Multi-line chart
   - Question it answers: "How do male/female populations compare?"

Would you like me to create all 3 datasets, or would you like to modify this list?
```

### 4. User Confirmation

Ask the user to:
- Accept all recommendations
- Remove some datasets
- Add custom splits
- Modify chart types or titles

### 5. Process Each Dataset

For each approved dataset:
1. Filter the raw data according to the split criteria
2. Save as both CSV and XLSX in `public/datasets/`
3. Create Vega-Lite chart spec in `public/charts/`
4. Create EN and MN MDX pages using templates
5. Register in the database

### Split Criteria Examples

| Data Type | Common Splits |
|-----------|---------------|
| Time series with categories | One dataset per category, one "total" |
| Regional data | National overview + regional breakdown |
| Multi-year snapshots | Latest year detail + historical trend |
| Complex hierarchies | Top-level overview + drill-down by dimension |

## Dataset Definition Template

Create file at `tools/sources/{source}/datasets/{dataset-id}.md`:

```markdown
# Dataset: {Dataset Name}

## Identification
- **ID**: {source}-{topic}
- **Category**: {Demographics | Economy | Mining | etc.}
- **Tags**: [tag1, tag2, ...]

## Source Reference
- **Table ID**: {for 1212: table ID}
- **URL**: {for web sources}

## Variables

Document all dimensions in the source data:

### {Dimension Name} ({Original Name})
- `code`: value_label
- `code`: value_label
...

## Update Instructions

### Check for Updates
[Steps to check if source has new data]

### Fetch Data
[Steps to fetch the actual data]

### Validation
[Rules to validate the data]

## Splits

**IMPORTANT**: This section defines how to split multi-dimensional data into user-friendly datasets.

### 1. {split-id}

- **ID**: `{split-id}` (will be registered as separate dataset)
- **Title EN**: {English title - answers ONE question}
- **Title MN**: {Mongolian title}
- **Filter**:
  - {dimension}: {value} (e.g., Sex: Total)
  - {dimension}: {value}
- **Chart Type**: line | bar | area | population-pyramid
- **Chart Config**:
  - X-axis: {column}
  - Y-axis: {column}
  - Color: {column or fixed color}
- **Description EN**: {One sentence describing what this shows}
- **Description MN**: {Mongolian description}

### 2. {another-split-id}
...

## Content Generation

**CRITICAL: Data pages must be MINIMAL**

When generating MDX pages for splits, follow these rules strictly:

1. **NO prose sections** - Do not create "Overview", "Key Findings", "Analysis", or "Trend" sections
2. **Only include:**
   - Frontmatter with metadata
   - Import statements
   - One excerpt sentence (factual, with key numbers)
   - VegaChart component
3. **The chart IS the content** - Let the visualization tell the story

See `data.mn/src/data/data/mn/gdp-per-capita.mdx` as the ideal example structure.

### CRITICAL: Bilingual Tags

**Tags in Mongolian pages MUST be in Mongolian.** Do NOT use English tags in MN pages.

**→ See the `datamn-page-mdx` skill for the complete tag translation table.**

### Key Findings Template
{What metrics to auto-extract and highlight IN THE EXCERPT SENTENCE ONLY}

### Common Tags
{Tags that apply to all splits - remember to translate for MN pages}
```

### Split Definition Examples

**Time Series (Total)**:
```markdown
### 1. population-total
- **ID**: `population-total`
- **Title EN**: Mongolia Total Population (1956-2024)
- **Title MN**: Монгол Улсын нийт хүн ам (1956-2024)
- **Filter**:
  - Sex: Total
  - Age Group: Total
- **Chart Type**: line
- **Chart Config**:
  - X-axis: year
  - Y-axis: population
  - Color: #3b82f6 (blue)
```

**Population Pyramid**:
```markdown
### 2. population-pyramid
- **ID**: `population-pyramid`
- **Title EN**: Mongolia Population Pyramid (2024)
- **Title MN**: Монгол Улсын хүн амын пирамид (2024)
- **Filter**:
  - Year: latest
  - Sex: NOT Total
  - Age Group: NOT Total
- **Chart Type**: population-pyramid
- **Chart Config**:
  - Y-axis: age_group
  - X-axis: population (signed by sex)
  - Color: sex (Male=#3b82f6, Female=#ec4899)
```

**Multi-line Comparison**:
```markdown
### 3. population-by-sex
- **ID**: `population-by-sex`
- **Title EN**: Mongolia Population by Sex (1956-2024)
- **Title MN**: Монгол Улсын хүн ам хүйсээр (1956-2024)
- **Filter**:
  - Age Group: Total
  - Sex: NOT Total
- **Chart Type**: multi-line
- **Chart Config**:
  - X-axis: year
  - Y-axis: population
  - Color: sex
```

## After Adding

Once added, **verify all files are in correct locations**:

```bash
# Verify MDX pages exist in correct location (NOT src/content/)
ls data.mn/src/data/data/en/{dataset-id}.mdx
ls data.mn/src/data/data/mn/{dataset-id}.mdx

# Verify CSV/XLSX files exist
ls data.mn/public/datasets/{dataset-id}*.csv
ls data.mn/public/datasets/{dataset-id}.xlsx

# Verify chart specs exist
ls data.mn/public/charts/{dataset-id}*.json
```

Then show the user:
1. Created files and their locations (with full paths)
2. Fetched data summary (rows, columns)
3. Registry status
4. Next steps for the user (see below)

### Next Steps (Show to User)

Tell the user they need to complete these steps:

1. **Preview locally**: `cd data.mn && npm run build && npm run dev`
2. **Visually verify** the charts look correct in the browser
3. **Publish datasets** (only after visual verification):
   ```bash
   cd tools && python -m registry publish {dataset-id}
   ```
   Run this for each split dataset. This assigns permanent URLs.
4. **Deploy**: `kamal deploy`

**IMPORTANT**: Do NOT run `registry publish` automatically. The user must visually verify the data and charts before publishing, because:
- Published URLs become **permanent** and cannot be changed without creating redirects
- Once published, the dataset is committed to the URL stability policy
- Visual verification catches chart rendering issues, incorrect data, or labeling errors

## Creating Changelog Entries

**IMPORTANT**: After successfully adding a dataset, create a changelog entry to document the addition.

### Changelog Entry Template

Create two MDX files (one for each language):

**File names:**
- English: `data.mn/src/data/changelog/en/{YYYY-MM-DD}-{dataset-id}.mdx`
- Mongolian: `data.mn/src/data/changelog/mn/{YYYY-MM-DD}-{dataset-id}.mdx`

Use today's date in YYYY-MM-DD format.

**Template content (identical for both EN and MN files):**

```mdx
---
date: {YYYY-MM-DD}
action: added
dataset_id: {dataset-id}
dataset_name_en: {English dataset title}
dataset_name_mn: {Mongolian dataset title}
description_en: {1-2 sentence English description of what was added, including source and time range}
description_mn: {1-2 sentence Mongolian description of what was added, including source and time range}
source: {Source name, e.g., "National Statistics Office"}
version: 1
---
```

### Example Changelog Entry

**File: `data.mn/src/data/changelog/en/2025-12-05-population-total.mdx`**
**File: `data.mn/src/data/changelog/mn/2025-12-05-population-total.mdx`**

```mdx
---
date: 2025-12-05
action: added
dataset_id: population-total
dataset_name_en: Mongolia Total Population (1956-2024)
dataset_name_mn: Монгол Улсын нийт хүн ам (1956-2024)
description_en: Initial release of historical population data from NSO 1212.mn covering 1956 to 2024. Includes annual population totals with interactive time series visualization.
description_mn: ҮСХ 1212.mn-ээс авсан 1956-2024 оны түүхэн хүн амын өгөгдлийн анхны хувилбар. Жилийн нийт хүн амын тоо, интерактив цаг хугацааны дүрслэл орсон.
source: National Statistics Office
version: 1
---
```

**Note**: The frontmatter is identical in both language files. Both contain both the English and Mongolian descriptions.

### When to Create Changelog Entries

- **Always** create a changelog entry after successfully adding a new dataset
- For split datasets, create ONE changelog entry for the parent dataset (not individual splits)
- Create the changelog entry **before** deploying to production
- See `data.mn/CHANGELOG_TEMPLATE.md` for complete documentation

## CRITICAL: Validate Charts

**After creating any Vega-Lite chart, you MUST validate it:**

```bash
cd tools && python3 scripts/validate_vega.py /path/to/chart.json --data /path/to/data.csv
```

Or validate all charts at once:
```bash
cd data.mn && python3 ../tools/scripts/validate_vega.py --all
```

**Do NOT proceed if the validator reports errors.** Fix all errors before finishing.

Common issues the validator catches:
- Using `ordinal` for year/date fields (should be `quantitative` or `temporal`)
- Setting width/height (breaks responsive design)
- Not starting at zero for absolute values
- Missing data fields

## Skills Used

This command uses the following skills:
- `datamn-source-nso` - Search and fetch NSO 1212.mn data
- `datamn-source-mongolbank` - Bank of Mongolia data (when available)
- `datamn-source-mrpam` - MRPAM data (when available)
- `datamn-registry` - Dataset registration and status
- `datamn-chart-vega` - Vega-Lite chart generation
- `datamn-page-mdx` - Bilingual MDX page generation, **ALL translation tables**
- `datamn-transform-split` - Data filtering, CSV/XLSX export logic

## Spawning Workers (MANDATORY)

**⚠️ CRITICAL: Always use agents. Never create dataset files manually in the main conversation.**

### Why Agents Are Required

1. **Consistency**: Workers follow the exact same validation steps every time
2. **Completeness**: Workers know ALL 7 required files and won't forget any
3. **Quality**: Workers automatically run validation and use correct templates
4. **Skills**: Workers invoke the right skills at the right time

### Agent Spawn Commands

**Discovery (search/check for updates):**
```
Task tool:
  subagent_type: "datamn-discovery-worker"
  prompt: |
    MODE: Search for Datasets
    SOURCE_ID: {source_id}
    SEARCH_QUERY: {user's query}
```

**Dataset Creation (SPAWN FOR EACH DATASET):**
```
Task tool:
  subagent_type: "datamn-dataset-worker"
  prompt: |
    Create dataset with these parameters:
    - DATASET_ID: {dataset_id}
    - SOURCE_ID: {source_id}
    - PARENT_ID: {parent_id or null}
    - SPLIT_FILTER: {filter JSON or null}
    - TITLE_EN: {english title}
    - TITLE_MN: {mongolian title}
    - CATEGORY_EN: {category}
    - CATEGORY_MN: {mongolian category}
    - CHART_TYPE: {area|line|bar|population-pyramid}
    - TABLE_ID: {source table ID}

    The worker has complete instructions for: fetch → transform → chart → MDX → registry.
```

**Validation (run after each dataset):**
```
Task tool:
  subagent_type: "datamn-checker-worker"
  prompt: |
    Validate dataset: {dataset_id}
    base_dir: data.mn
```

### When NOT to Use Agents (exceptions)

Only skip the worker agent if:
- You're just answering questions about the registry (use Skill: datamn-registry instead)
- You're fixing a single field in an existing file (use Edit tool directly)
- The user explicitly requests manual control

For ANY new dataset creation → ALWAYS use datamn-dataset-worker.

## Regional Data: Preferred Aimags

When creating datasets with regional breakdowns (e.g., prices, employment by aimag), **use these preferred aimags** if available in the source data:

| Aimag | Region | Reason |
|-------|--------|--------|
| **Ulaanbaatar** | Capital | ~50% of population, economic center |
| **Darkhan-Uul** | North | Industrial city, good data coverage |
| **Orkhon** | North-Central | Erdenet mining center, best data completeness |
| **Umnugovi** | South (Gobi) | Mining region (Oyu Tolgoi), strategic importance |
| **Khovd** | West | Western Mongolia representation |

**Note:** Some NSO tables (like weekly prices) exclude Ulaanbaatar. In those cases, use the 4 aimags without UB.

### Why These Aimags?

1. **Geographic diversity** - North, South, West, and Central covered
2. **Economic diversity** - Capital, industrial, mining, and rural areas
3. **Data completeness** - These aimags typically have the most complete data
4. **User relevance** - Major population and economic centers

**Do NOT arbitrarily pick aimags.** Always prefer this list unless the user specifies otherwise or the data suggests better alternatives.

## Notes

- Dataset IDs follow pattern: `{source}-{topic}` (e.g., `nso-population-total`)
- All definitions are markdown files that can be manually edited
- The agent interprets these definitions when updating
- Use Playwright MCP tools for web navigation when needed
