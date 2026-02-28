---
name: datamn-page-mdx
description: "Generate bilingual MDX data pages for data.mn. Use when creating dataset pages with frontmatter, VegaChart components, and DataDownload links. Creates both EN and MN versions in a single pass for consistency."
---


# MDX Page Generation Skill

Generate bilingual (EN/MN) MDX data pages for the data.mn website.

## Overview

This skill creates both English and Mongolian versions of dataset pages in a single pass to ensure consistency. Each page includes:
- Frontmatter with metadata
- Excerpt/description
- VegaChart component
- DataDownload component

## Output Locations

| Language | Path |
|----------|------|
| English | `data/data.mn/src/data/data/en/{dataset-id}.mdx` |
| Mongolian | `data/data.mn/src/data/data/mn/{dataset-id}.mdx` |

## Template Structure

**CRITICAL: Data pages must be MINIMAL - NO prose sections!**

The page layout already handles:
- Title display
- Source attribution
- Data downloads
- Metadata display

**Your MDX file should ONLY contain:**
1. Frontmatter with metadata
2. Import statement(s)
3. One excerpt sentence (that repeats/expands the frontmatter excerpt)
4. The VegaChart component

**ABSOLUTELY DO NOT ADD:**
- "Overview" sections
- "Key Findings" sections
- "Analysis" sections
- "Trend" or "Comparison" headings
- "Download Data" sections (handled by layout)
- "About the Data" paragraphs
- Footer notes or source citations

**The chart IS the content.** Let the visualization speak for itself.

### English Template

```mdx
---
title: "{TITLE_EN}"
publishDate: {PUBLISH_DATE}
excerpt: "{EXCERPT_EN}"
category: "{CATEGORY_EN}"
tags: {TAGS_JSON}
keywords: {KEYWORDS_JSON}
dataFiles:
  - path: "/datasets/{DATASET_ID}-all-en.csv"
    format: "csv"
    size: "{CSV_SIZE}"
    description: "Download as CSV (all data)"
  - path: "/datasets/{DATASET_ID}.xlsx"
    format: "xlsx"
    size: "{XLSX_SIZE}"
    description: "Open in Excel"
source:
  name: "{SOURCE_NAME_EN}"
  url: "{SOURCE_URL}"
  tableId: "{TABLE_ID}"
---

import VegaChart from '~/components/ui/VegaChart.astro';

{EXCERPT_EN}

<VegaChart
  spec="/charts/{DATASET_ID}-en.json"
  title="{CHART_TITLE_EN}"
/>
```

### Mongolian Template

```mdx
---
title: "{TITLE_MN}"
publishDate: {PUBLISH_DATE}
excerpt: "{EXCERPT_MN}"
category: "{CATEGORY_MN}"
tags: {TAGS_JSON}
keywords: {KEYWORDS_JSON}
dataFiles:
  - path: "/datasets/{DATASET_ID}-all-mn.csv"
    format: "csv"
    size: "{CSV_SIZE}"
    description: "CSV татах (бүх өгөгдөл)"
  - path: "/datasets/{DATASET_ID}.xlsx"
    format: "xlsx"
    size: "{XLSX_SIZE}"
    description: "Excel татах"
source:
  name: "{SOURCE_NAME_MN}"
  url: "{SOURCE_URL}"
  tableId: "{TABLE_ID}"
---

import VegaChart from '~/components/ui/VegaChart.astro';

{EXCERPT_MN}

<VegaChart
  spec="/charts/{DATASET_ID}-mn.json"
  title="{CHART_TITLE_MN}"
/>
```

**IMPORTANT NOTES:**
1. **Chart CSV vs Download CSV**: The chart references `{DATASET_ID}-{lang}.csv` (subset for readability), but the dataFiles reference `{DATASET_ID}-all-{lang}.csv` (complete data for download).
2. **Language-specific chart specs**: The English MDX uses `{DATASET_ID}-en.json` and the Mongolian MDX uses `{DATASET_ID}-mn.json`. This ensures axis labels and tooltips are in the correct language.
3. **Excel file**: One Excel file per dataset (wide format with all data), shared between languages.

### When Dataset Has Many Categories (Regions, Products, etc.)

For datasets with many categorical values (e.g., 25 regions), the file structure is:

| File | Content | Used By |
|------|---------|---------|
| `{id}-en.csv` | Subset (4-6 categories) | Chart visualization |
| `{id}-all-en.csv` | ALL data (25 categories) | Download link |
| `{id}.xlsx` | ALL data (wide format) | Download link |

The chart shows a readable subset; the downloads contain everything.

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{TITLE_EN}` | English title | "Mongolia Total Population (1956-2024)" |
| `{TITLE_MN}` | Mongolian title | "Монгол Улсын нийт хүн ам (1956-2024)" |
| `{EXCERPT_EN}` | English description (1-2 sentences) | "Mongolia's population grew 4.2x..." |
| `{EXCERPT_MN}` | Mongolian description | "Монгол Улсын хүн ам 4.2 дахин өслөө..." |
| `{PUBLISH_DATE}` | ISO date | 2025-11-27 |
| `{CATEGORY_EN}` | English category name | "Demographics" |
| `{CATEGORY_MN}` | Mongolian category name | "Хүн ам зүй" |
| `{TAGS_JSON}` | JSON array of tags | ["mongolia", "population"] |
| `{KEYWORDS_JSON}` | JSON array of keywords | ["mongolia population", "demographics"] |
| `{DATASET_ID}` | Dataset identifier | "population-total" |
| `{CSV_SIZE}` | File size | "1 KB" |
| `{XLSX_SIZE}` | File size | "6 KB" |
| `{CHART_SPEC}` | Chart filename | "population-total.json" |
| `{CHART_TITLE_EN}` | English chart title | "Mongolia Total Population" |
| `{CHART_TITLE_MN}` | Mongolian chart title | "Монгол Улсын нийт хүн ам" |
| `{SOURCE_NAME_EN}` | English source name | "National Statistics Office of Mongolia" |
| `{SOURCE_NAME_MN}` | Mongolian source name | "Үндэсний Статистикийн Хороо" |
| `{SOURCE_URL}` | Source URL | "https://data.1212.mn" |
| `{TABLE_ID}` | Source table identifier | "DT_NSO_0300_003V1.px" |

## Categories

**IMPORTANT:** Use the correct language for each page. English pages use English categories, Mongolian pages use Mongolian categories.

| English (EN) | Mongolian (MN) | Description |
|--------------|----------------|-------------|
| Demographics | Хүн ам зүй | Population, vital statistics |
| Economy | Эдийн засаг | GDP, trade, inflation |
| Employment | Хөдөлмөр эрхлэлт | Labor force, unemployment |
| Housing | Орон сууц | Prices, construction |
| Mining | Уул уурхай | Production, exports |
| Finance | Санхүү | Banking, exchange rates |
| Agriculture | Хөдөө аж ахуй | Livestock, crops |
| Education | Боловсрол | Schools, enrollment |
| Health | Эрүүл мэнд | Healthcare, diseases |
| Trade | Худалдаа | Foreign trade, imports/exports |
| Energy | Эрчим хүч | Electricity, fuel |
| Tourism | Аялал жуулчлал | Tourism statistics |

## Workflow

### 1. Gather Required Information

Before generating pages, collect:
- Dataset ID
- Titles (EN and MN)
- Excerpts (EN and MN)
- Category
- Tags and keywords
- Source information
- Chart specification path
- Data file paths and sizes

### 2. Generate Both Pages Together

Always create EN and MN pages in the same operation to ensure:
- Matching metadata (dates, versions, file paths)
- Consistent tags and categories
- Same chart references

**CRITICAL: Bilingual Consistency Requirements**

These fields MUST be identical between EN and MN pages:
- `dataVersion` - same integer value
- `dataDate` - same YYYY-MM-DD date

These should be similar:
- Tag count - difference should be ≤ 2 between EN and MN

### 3. Calculate File Sizes

```python
import os

csv_path = f"data/data.mn/public/datasets/{dataset_id}.csv"
xlsx_path = f"data/data.mn/public/datasets/{dataset_id}.xlsx"

csv_size = os.path.getsize(csv_path)
xlsx_size = os.path.getsize(xlsx_path)

def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes // 1024} KB"
    else:
        return f"{size_bytes // (1024 * 1024)} MB"
```

### 4. Writing the Excerpt

The excerpt should be **factual and descriptive** (what, where, when). It should NOT contain analysis or judgments.

**REQUIREMENTS:**
- Minimum 50 characters
- NEVER start with: "data about", "this dataset contains", "statistics on", "information about"
- Describe the data: topic, geography, time range

**Good excerpts (factual, descriptive):**
- "Monthly CPI data for 5 major spending categories in Ulaanbaatar from January 2020 to December 2025."
- "Annual population figures for Mongolia from 1956 to 2024, broken down by sex."
- "Weekly beef prices across 21 aimags from January 2024 to present."

**Bad excerpts:**
- "Data about Mongolia's GDP." ← Too generic
- "Track inflation trends across categories. Food shows the highest volatility." ← Contains analysis/judgment
- "This dataset contains population statistics." ← Generic pattern

**The body content is literally just this one sentence again.**

### 5. Writing Keywords

Keywords are used for SEO. They should help users find the data via search engines.

**REQUIREMENTS:**
- Minimum 2 keywords
- Must include **multi-word phrases** (e.g., "mongolia gdp growth")
- NOT all generic terms like "data", "statistics", "mongolia"

**Good keywords:**
```yaml
keywords: ["mongolia population growth", "population by sex", "census data mongolia"]
```

**Bad keywords:**
```yaml
keywords: ["data", "statistics"]  # Too generic, fails validation
keywords: ["mongolia", "population"]  # No multi-word phrases
```

## Common Source Names

| Source ID | English | Mongolian | URL |
|-----------|---------|-----------|-----|
| nso-1212 | National Statistics Office of Mongolia | Үндэсний Статистикийн Хороо | https://data.1212.mn |
| mongolbank | Bank of Mongolia | Монгол банк | https://www.mongolbank.mn |
| mrpam | Mineral Resources and Petroleum Authority | Ашигт малтмал, газрын тосны газар | https://mrpam.gov.mn |

---

## Bilingual Translation Reference (SINGLE SOURCE OF TRUTH)

**This section is the canonical reference for all English↔Mongolian translations used across data.mn.**

### Tag Translations

**CRITICAL**: Tags in Mongolian pages MUST be in Mongolian.

| English Tag | Mongolian Tag |
|-------------|---------------|
| mongolia | монгол |
| economy | эдийн засаг |
| population | хүн ам |
| demographics | хүн ам зүй |
| trade | худалдаа |
| exports | экспорт |
| imports | импорт |
| gdp | днб |
| inflation | инфляци |
| unemployment | ажилгүйдэл |
| employment | ажил эрхлэлт |
| salary | цалин |
| income | орлого |
| balance-of-payments | төлбөрийн тэнцэл |
| current-account | урсгал данс |
| fdi | шууд хөрөнгө оруулалт |
| mining | уул уурхай |
| agriculture | хөдөө аж ахуй |
| livestock | мал аж ахуй |
| tourism | аялал жуулчлал |
| education | боловсрол |
| health | эрүүл мэнд |
| housing | орон сууц |
| finance | санхүү |
| reserves | нөөц хөрөнгө |
| remittances | гуйвуулга |
| prices | үнэ |
| cpi | хэрэглээний үнийн индекс |

### Chart Axis/Legend Translations

| English | Mongolian |
|---------|-----------|
| Year | Он |
| Value | Утга |
| Rate (%) | Түвшин (%) |
| Population | Хүн ам |
| Count | Тоо |
| Category | Ангилал |
| Sex | Хүйс |
| Region | Бүс |
| Age | Нас |
| Total | Нийт |
| GDP | ДНБ |
| Amount | Дүн |
| Percent | Хувь |
| Price | Үнэ |
| Date | Огноо |

### Category Value Translations (for chart color domains)

| English | Mongolian |
|---------|-----------|
| Male | Эрэгтэй |
| Female | Эмэгтэй |
| Urban | Хот |
| Rural | Хөдөө |
| Total | Нийт |
| Western | Баруун |
| Khangai | Хангай |
| Central | Төв |
| Eastern | Зүүн |
| Ulaanbaatar | Улаанбаатар |

### Download Button Text

| English | Mongolian |
|---------|-----------|
| Download as CSV (all data) | CSV татах (бүх өгөгдөл) |
| Open in Excel | Excel татах |

---

## Validation

After generating pages, verify:

1. **File exists**: Both EN and MN files created
2. **Frontmatter valid**: YAML parses correctly
3. **Imports present**: VegaChart and DataDownload imported
4. **Chart exists**: Referenced chart spec file exists
5. **Data files exist**: CSV and XLSX files exist

## Example Usage

```python
# Generate pages for a population dataset
dataset_info = {
    "dataset_id": "population-total",
    "title_en": "Mongolia Total Population (1956-2024)",
    "title_mn": "Монгол Улсын нийт хүн ам (1956-2024)",
    "excerpt_en": "Mongolia's population grew 4.2x from 845,000 in 1956 to 3.5 million in 2024.",
    "excerpt_mn": "Монгол Улсын хүн ам 1956 оны 845,000-аас 2024 онд 3.5 сая болж 4.2 дахин өсөв.",
    "category_en": "Demographics",      # English category for EN page
    "category_mn": "Хүн ам зүй",        # Mongolian category for MN page
    "tags": ["mongolia", "population", "demographics", "census"],
    "keywords": ["mongolia population", "population growth"],
    "source_id": "nso-1212",
    "chart_spec": "population-total.json"
}

# Generate EN page (uses category_en)
generate_page(dataset_info, "en")

# Generate MN page (uses category_mn)
generate_page(dataset_info, "mn")
```

## Notes

- Templates are in `data/tools/templates/`
- Always use ISO dates (YYYY-MM-DD)
- Tags should be lowercase, single words
- Keywords can be multi-word phrases
- Category must match one of the standard categories
