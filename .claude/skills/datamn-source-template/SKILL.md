---
name: datamn-source-template
description: Template for creating new data source skills. Use when adding a new government agency, ministry, or data provider to the data.mn system.
---

# Data Source Template

This is a template for creating new data source skills for data.mn. Copy this template and customize it for each new data source.

## Creating a New Source Skill

### 1. Create the Skill Directory

```bash
mkdir -p .claude/skills/datamn-source-{source-name}
```

### 2. Create SKILL.md

Copy the template below and fill in the details:

```markdown
---
name: datamn-source-{source-name}
description: {What data this source provides}. Use when {specific triggers}.
dependencies:
  - python3
  - {other dependencies}
---

# {Source Name} Data Source Skill

{Brief description of the data source and what data it provides.}

## Overview

| Field | Value |
|-------|-------|
| Source ID | `{source-id}` |
| Organization | {Full organization name} |
| Website | {URL} |
| Data Type | {api / pdf / scrape / mixed} |
| Update Frequency | {daily / weekly / monthly / quarterly / annual} |
| Language | {en / mn / both} |

## Authentication

{Describe any authentication required - API keys, login, etc.}

```bash
# Example API key usage
export {SOURCE}_API_KEY="your-key-here"
```

## Available Data

{List the main categories of data available from this source}

### Category 1
- Dataset A
- Dataset B

### Category 2
- Dataset C
- Dataset D

## Data Fetching

### For API Sources

```python
import requests

BASE_URL = "{base-url}"

def fetch_data(endpoint, params=None):
    response = requests.get(f"{BASE_URL}/{endpoint}", params=params)
    return response.json()
```

### For PDF Sources

Use the Playwright MCP tools to navigate and download PDFs:

1. Navigate to {url}
2. Find the latest report link
3. Download the PDF
4. Extract tables using pdfplumber

### For Web Scraping

Use the Playwright MCP tools:

1. Navigate to {url}
2. Capture page snapshot
3. Extract data from specific elements
4. Handle pagination if needed

## Update Detection

{Describe how to check if new data is available}

### For APIs
```python
def check_for_updates(dataset_id, last_updated):
    # Query API for latest timestamp
    response = fetch_data(f"metadata/{dataset_id}")
    source_updated = response.get("updated_at")
    return source_updated > last_updated
```

### For Web/PDF Sources
```python
def check_for_updates():
    # Use Playwright to check page for new content
    # Look for report dates, version numbers, etc.
    pass
```

## Output Format

{Describe the expected output format}

### CSV Structure
```csv
column1,column2,column3,value
...
```

### Data Types
| Column | Type | Description |
|--------|------|-------------|
| column1 | string | {description} |
| column2 | integer | {description} |
| value | float | {description} |

## Common Issues

{List common problems and solutions}

1. **Issue**: {description}
   **Solution**: {how to fix}

2. **Issue**: {description}
   **Solution**: {how to fix}

## Notes

- {Any additional notes}
- {Limitations}
- {Special considerations}
```

## Required Sections

Every source skill MUST include:

1. **SKILL.md frontmatter** with name and description
2. **Overview table** with source metadata
3. **Authentication** section (even if "No authentication required")
4. **Available Data** section listing what's available
5. **Data Fetching** section with code examples
6. **Update Detection** section explaining how to check for new data
7. **Output Format** section describing expected data structure

## Naming Convention

| Type | Pattern | Example |
|------|---------|---------|
| Skill directory | `datamn-source-{id}` | `datamn-source-mongolbank` |
| Source ID | `{short-name}` | `mongolbank` |
| Dataset IDs | `{source}-{topic}` | `mongolbank-exchange-rates` |

## Data Source Types

### API Sources
- Have programmatic access
- Usually return JSON
- Can check timestamps for updates
- Examples: 1212.mn, Bank of Mongolia API

### PDF Sources
- Require downloading documents
- Need PDF parsing (pdfplumber)
- Check page for new report links
- Examples: MRPAM monthly reports

### Web Scraping Sources
- No API, must scrape HTML
- Use Playwright MCP for navigation
- Handle dynamic content
- Check for page changes

### Mixed Sources
- Combination of above
- May have API for some data, PDF for others
- Document which method for each dataset

## Source Registration

After creating the skill, register the source in the registry:

```python
from registry import Registry

reg = Registry()
reg.add_source(
    source_id="{source-id}",
    name_en="{English Name}",
    name_mn="{Mongolian Name}",
    type="{api|pdf|scrape|mixed}",
    base_url="{url}",
    update_frequency="{frequency}",
    enabled=True
)
```

## Handling Single-Language Sources

### Overview

While NSO 1212.mn provides data in both English and Mongolian via API, many other sources only provide data in ONE language:

- **MRPAM**: PDFs in Mongolian only
- **MongolBank**: Some data in Mongolian only
- **Government PDFs**: Often Mongolian only
- **International sources**: Usually English only

**CRITICAL**: The data.mn platform requires ALL datasets to have bilingual CSVs (`-en.csv` and `-mn.csv`) to support the bilingual architecture where charts use language-matched CSVs.

### Translation Strategy

When a source provides single-language data, **AI translation** is used to create the missing language version:

| Source Language | Process |
|----------------|---------|
| English only | AI translates to create Mongolian CSV |
| Mongolian only | AI translates to create English CSV |

### What Gets Translated

#### Column Names (Always)
Both the data values AND column names must be translated:

```python
# English columns
year, sector, region, value

# Mongolian columns
он, салбар, бүс, утга
```

#### Categorical/String Values
Non-numeric values in columns must be translated:
- Gender values: Male→Эрэгтэй, Female→Эмэгтэй
- Location values: Urban→Хот, Rural→Хөдөө
- Administrative divisions: Province names, district names
- Economic sectors: Mining→Уул уурхай, Education→Боловсрол
- Time periods: Q1→1-р улирал, January→1 сар

#### What NOT to Translate
- Numeric values (stay the same in both languages)
- ISO codes (MN, USD, etc.)
- Date values in ISO format (2024-01-01)
- Variable/column names in the source data structure (only output columns)

### Translation Workflow

#### Step 1: Load Source Data
```python
import pandas as pd

# Example: MRPAM PDF in Mongolian
df_mn = pd.read_csv('mrpam-coal-production-raw.csv')
# Columns: огноо, нүүрс_олборлолт, экспорт, дотоод_хэрэглээ
```

#### Step 2: Identify String Columns
```python
# Find all non-numeric columns (categorical data)
string_cols = df_mn.select_dtypes(include=['object']).columns

# For datetime/period columns, handle specially
date_cols = [col for col in df_mn.columns if 'date' in col.lower() or 'он' in col.lower()]
```

#### Step 3: Extract Unique Values
```python
# For each string column, get unique values
translations_needed = {}
for col in string_cols:
    if col not in date_cols:  # Skip date columns
        unique_vals = df_mn[col].dropna().unique().tolist()
        translations_needed[col] = unique_vals
```

#### Step 4: Create Translation Mappings
Use AI to translate each unique value:

```python
# AI generates these translations
column_translations = {
    'огноо': 'date',
    'нүүрс_олборлолт': 'coal_production',
    'экспорт': 'export',
    'дотоод_хэрэглээ': 'domestic_consumption'
}

value_translations = {
    'салбар': {  # sector column
        'Уул уурхай': 'Mining',
        'Боловсрол': 'Education',
        'Эрүүл мэнд': 'Health',
    },
    'бүс': {  # region column
        'Улаанбаатар': 'Ulaanbaatar',
        'Хөдөө': 'Rural',
        'Хот': 'Urban',
    }
}
```

#### Step 5: Create English Version
```python
# Start with copy of Mongolian data
df_en = df_mn.copy()

# Translate column names
df_en = df_en.rename(columns=column_translations)

# Translate categorical values
for col_mn, col_en in column_translations.items():
    if col_mn in value_translations:
        # Map Mongolian values to English
        df_en[col_en] = df_en[col_en].map(value_translations[col_mn])
```

#### Step 6: Save Both Versions
```python
# Save with language suffixes
df_en.to_csv('dataset-id-en.csv', index=False)
df_mn.to_csv('dataset-id-mn.csv', index=False)
```

### Standard Translations Reference

#### Common Column Names
```python
STANDARD_COLUMN_TRANSLATIONS = {
    # Time
    'он': 'year',
    'сар': 'month',
    'улирал': 'quarter',
    'огноо': 'date',

    # Geography
    'аймаг': 'province',
    'дүүрэг': 'district',
    'сум': 'soum',
    'бүс': 'region',
    'хот': 'city',

    # Demographics
    'хүйс': 'sex',
    'нас': 'age',
    'насны_бүлэг': 'age_group',
    'хүн_ам': 'population',

    # Economics
    'салбар': 'sector',
    'үнэ': 'price',
    'утга': 'value',
    'дүн': 'amount',
    'хувь': 'percentage',
    'өсөлт': 'growth',
}
```

#### Common Value Translations
```python
STANDARD_VALUE_TRANSLATIONS = {
    # Gender
    'Эрэгтэй': 'Male',
    'Эмэгтэй': 'Female',
    'Нийт': 'Total',

    # Urban/Rural
    'Хот': 'Urban',
    'Хөдөө': 'Rural',

    # Administrative
    'Улаанбаатар': 'Ulaanbaatar',
    'Хан-Уул': 'Khan-Uul',
    'Баянзүрх': 'Bayanzurkh',
    'Сүхбаатар': 'Sukhbaatar',
    'Чингэлтэй': 'Chingeltei',
    'Баянгол': 'Bayangol',
    'Сонгинохайрхан': 'Songinokhairkhan',

    # Economic Sectors (ISIC-based)
    'Уул уурхай': 'Mining',
    'Боловсрол': 'Education',
    'Эрүүл мэнд': 'Health',
    'Барилга': 'Construction',
    'Үйлдвэрлэл': 'Manufacturing',
    'Худалдаа': 'Trade',
    'Тээвэр': 'Transportation',
    'Санхүү': 'Finance',
    'Хөдөө аж ахуй': 'Agriculture',
}
```

### Implementation in Source Skills

When creating a new source skill for a single-language source, include this section:

```markdown
## Language Support

**Source Language**: [Mongolian / English]
**Translation Required**: Yes

This source provides data in [source language] only. The skill automatically generates the [target language] version through AI translation.

### Translation Process

1. Fetch/extract raw data from source
2. Identify categorical columns requiring translation
3. Generate translations using standard mappings + AI
4. Create bilingual CSVs with language suffixes
5. Both versions are saved to `public/datasets/`

### Translation Mapping

The following translations are applied:

**Column Names**:
- [source_col] → [target_col]
- [source_col] → [target_col]

**Values**:
- [sector/region/category names as relevant to this source]
```

### Complete Example: MRPAM Coal Production

```python
# Step 1: Extract from Mongolian PDF
df_mn = extract_coal_table_from_pdf('2025.10.stat.report.mon.pdf')
# Result: огноо, олборлолт_мян_тн, экспорт_мян_тн, дотоод_мян_тн

# Step 2: Column translations
column_map = {
    'огноо': 'date',
    'олборлолт_мян_тн': 'production_kt',
    'экспорт_мян_тн': 'export_kt',
    'дотоод_мян_тн': 'domestic_kt'
}

# Step 3: Create English version
df_en = df_mn.rename(columns=column_map)

# Step 4: If there are categorical values, translate them
# (In this case, dates and numbers don't need translation)

# Step 5: Save both
df_mn.to_csv('mrpam-coal-production-mn.csv', index=False)
df_en.to_csv('mrpam-coal-production-en.csv', index=False)
```

### Translation Best Practices

1. **Consistency**: Use the same translations across all datasets
2. **Standard mappings first**: Check `STANDARD_COLUMN_TRANSLATIONS` and `STANDARD_VALUE_TRANSLATIONS`
3. **Document custom translations**: Add source-specific translations to source.md
4. **Human review recommended**: Especially for specialized terminology (medical, legal, technical)
5. **Preserve meaning**: Ensure translations maintain statistical accuracy
6. **Handle missing translations**: Use original value if translation unavailable

### Validation

After creating bilingual CSVs, verify:
- Both files have identical structure (same number of rows)
- Numeric columns have identical values
- Only string/categorical columns differ
- Column counts match (translated columns, not added/removed)
- No untranslated values remain (except codes/identifiers)

### Error Handling

If translation fails or is incomplete:
1. Save the single-language CSV with appropriate suffix
2. Log the issue in the dataset definition
3. Mark dataset as `status='pending-translation'` in registry
4. Create a task for manual translation review

## Checklist for New Sources

- [ ] Created skill directory
- [ ] Created SKILL.md with all required sections
- [ ] Documented source language(s) available
- [ ] Specified translation requirements (if single-language)
- [ ] Created translation mapping for common values
- [ ] Tested data fetching
- [ ] Tested translation workflow (if applicable)
- [ ] Validated bilingual CSV output
- [ ] Tested update detection
- [ ] Registered source in registry
- [ ] Created at least one dataset definition
- [ ] Updated CLAUDE.md with new skill reference
