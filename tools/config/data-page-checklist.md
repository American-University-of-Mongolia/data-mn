# Data Page Quality Checklist

This checklist defines all requirements for a complete, valid data page on data.mn.
Used by the checker subagent to validate pages after creation or updates.

**Total Checks: 85**

---

## 1. File Existence (7 checks)

Every dataset requires these 7 files:

| # | Check | Path Pattern | Scripted |
|---|-------|--------------|----------|
| 1.1 | MDX page (EN) | `src/data/data/en/{id}.mdx` | Yes |
| 1.2 | MDX page (MN) | `src/data/data/mn/{id}.mdx` | Yes |
| 1.3 | CSV data (EN) | `public/datasets/{id}-en.csv` | Yes |
| 1.4 | CSV data (MN) | `public/datasets/{id}-mn.csv` | Yes |
| 1.5 | Excel file | `public/datasets/{id}.xlsx` | Yes |
| 1.6 | Chart spec (EN) | `public/charts/{id}-en.json` | Yes |
| 1.7 | Chart spec (MN) | `public/charts/{id}-mn.json` | Yes |

**Validation**: `python validate_dataset.py --all {id}`

---

## 2. MDX Frontmatter (25 checks)

### 2A. Required Fields (13 checks)

| # | Field | Validation | Scripted |
|---|-------|------------|----------|
| 2.1 | `title` | Non-empty, min 5 characters | Yes |
| 2.2 | `publishDate` | Valid YYYY-MM-DD format | Yes |
| 2.3 | `excerpt` | Non-empty, 1-3 sentences | AI |
| 2.4 | `category` | Must be in `config/categories.json` | Yes |
| 2.5 | `tags` | Array of strings, ≥3 items | Yes |
| 2.6 | `keywords` | Array of strings for SEO | Yes |
| 2.7 | `author` | Non-empty (usually "Data.mn") | Yes |
| 2.8 | `dataVersion` | Integer ≥1 | Yes |
| 2.9 | `dataDate` | Valid YYYY-MM-DD format | Yes |
| 2.10 | `dataFiles` | Array with ≥2 entries (CSV + XLSX) | Yes |
| 2.11 | `source.name` | Non-empty, language-appropriate | Yes |
| 2.12 | `source.url` | Valid URL format | Yes |
| 2.13 | `source.tableId` | Present if from NSO (optional otherwise) | AI |

### 2B. Allowed Categories

**Source of truth**: `tools/config/categories.json`

Categories are validated with alias support for backward compatibility.

### 2C. dataFiles Structure (8 checks)

| # | Check | Validation | Scripted |
|---|-------|------------|----------|
| 2.14 | CSV entry exists | Has entry with `format: "csv"` | Yes |
| 2.15 | CSV path correct | Path ends with `-{lang}.csv` matching page language | Yes |
| 2.16 | XLSX entry exists | Has entry with `format: "xlsx"` | Yes |
| 2.17 | XLSX path correct | Path has no language suffix (shared file) | Yes |
| 2.18 | Paths start with `/` | All paths are absolute from public root | Yes |
| 2.19 | Files exist | Referenced files actually exist at paths | Yes |
| 2.20 | Size field present | Each entry has `size` (e.g., "5 KB") | Yes |
| 2.21 | Description present | Each entry has `description` | Yes |

### 2D. Encoding/Format (4 checks)

| # | Check | Validation | Scripted |
|---|-------|------------|----------|
| 2.22 | No BOM | File doesn't start with non-ASCII bytes | Yes |
| 2.23 | UTF-8 encoding | File is valid UTF-8 | Yes |
| 2.24 | Valid YAML | Frontmatter parses without errors | Yes |
| 2.25 | Proper delimiters | Starts and ends with `---` | Yes |

**Validation**: `python validate_dataset.py --mdx path/to/file.mdx`

---

## 3. MDX Body Content (5 checks)

| # | Check | Validation | Scripted |
|---|-------|------------|----------|
| 3.1 | VegaChart import | Contains `import VegaChart from '~/components/ui/VegaChart.astro';` | Yes |
| 3.2 | VegaChart component | Contains `<VegaChart ... />` | Yes |
| 3.3 | Spec path correct | `spec` attribute matches page language (`-en.json` or `-mn.json`) | Yes |
| 3.4 | Title attribute | VegaChart has `title` attribute | AI |
| 3.5 | No placeholder text | No "TODO", "TBD", "PLACEHOLDER", or template remnants | AI |

---

## 4. CSV Data Files (14 checks)

CSVs must be in **long/normalized form** (one observation per row).

### 4A. Structure (6 checks)

| # | Check | Validation | Scripted |
|---|-------|------------|----------|
| 4.1 | Non-empty | File size > 0 bytes | Yes |
| 4.2 | Readable | Parses as valid CSV | Yes |
| 4.3 | Has data rows | At least 1 data row beyond header | Yes |
| 4.4 | No duplicate columns | All column names unique | Yes |
| 4.5 | No empty columns | No columns that are entirely NULL/empty | Yes |
| 4.6 | Long form | One observation per row (not pivoted/wide) | AI |

### 4B. Whitespace - CRITICAL (3 checks)

These cause **silent chart failures** where charts render but show no data:

| # | Check | Validation | Scripted |
|---|-------|------------|----------|
| 4.7 | No leading whitespace | No values like `"   Female"` | Yes |
| 4.8 | No trailing whitespace | No values like `"Male   "` | Yes |
| 4.9 | No whitespace-only | No cells containing only spaces | Yes |

### 4C. Language-Specific Headers (2 checks)

| # | Check | Validation | Scripted |
|---|-------|------------|----------|
| 4.10 | EN CSV has EN headers | Uses `year`, `value`, `category`, `sex`, etc. | Yes |
| 4.11 | MN CSV has MN headers | Uses `он`, `утга`, `ангилал`, `хүйс`, etc. | Yes |

**Header Translation Reference:**

| English | Mongolian |
|---------|-----------|
| `year` | `он` |
| `value` | `утга` |
| `category` | `ангилал` |
| `sex` | `хүйс` |
| `region` | `бүс` |
| `location` | `байршил` |
| `type` | `төрөл` |
| `age` | `нас` |
| `population` | `хүн ам` |
| `rate` | `түвшин` |
| `amount` | `дүн` |
| `total` | `нийт` |

### 4D. Data Consistency - EN vs MN (3 checks)

| # | Check | Validation | Scripted |
|---|-------|------------|----------|
| 4.12 | Same row count | EN and MN CSVs have identical row counts | AI |
| 4.13 | Same column count | EN and MN CSVs have same number of columns | AI |
| 4.14 | Numeric values match | All numeric data identical between EN/MN | AI |

**Validation**: `python validate_dataset.py --csv path/to/file.csv`

---

## 5. XLSX File (6 checks)

Excel files must be in **wide/short form** (suitable for Excel viewing).

| # | Check | Validation | Scripted |
|---|-------|------------|----------|
| 5.1 | Non-empty | File size > 0 bytes | Yes |
| 5.2 | Readable | Opens with openpyxl without errors | Yes |
| 5.3 | Has sheets | At least 1 worksheet | Yes |
| 5.4 | Sheet has data | Active sheet has data rows | Yes |
| 5.5 | Wide format | Data is pivoted (years/categories as columns) | AI |
| 5.6 | No language suffix | Filename is `{id}.xlsx` (not `-en` or `-mn`) | Yes |

**Validation**: `python validate_dataset.py --xlsx path/to/file.xlsx`

---

## 6. Chart Specifications (21 checks)

### 6A. JSON Structure (4 checks)

| # | Check | Validation | Scripted |
|---|-------|------------|----------|
| 6.1 | Valid JSON | Parses without syntax errors | Yes |
| 6.2 | Has $schema | Contains `"$schema": "https://vega.github.io/schema/vega-lite/v5.json"` | Yes |
| 6.3 | Has description | Contains `"description"` field | Yes |
| 6.4 | Has data source | Contains `"data"` with `"url"` or `"values"` | Yes |

### 6B. Responsive Design (2 checks)

| # | Check | Validation | Scripted |
|---|-------|------------|----------|
| 6.5 | No hardcoded width | Does NOT contain top-level `"width"` | Yes |
| 6.6 | No hardcoded height | Does NOT contain top-level `"height"` | Yes |

### 6C. Data URL Language Match (2 checks)

| # | Check | Validation | Scripted |
|---|-------|------------|----------|
| 6.7 | EN chart → EN data | `-en.json` references `-en.csv` in `data.url` | Yes |
| 6.8 | MN chart → MN data | `-mn.json` references `-mn.csv` in `data.url` | Yes |

### 6D. Axis Types (2 checks)

| # | Check | Validation | Scripted |
|---|-------|------------|----------|
| 6.9 | Year not ordinal | Year/time fields use `quantitative` or `temporal`, NOT `ordinal` | Yes |
| 6.10 | Proper axis types | Each encoding has appropriate `type` | Yes |

### 6E. Layered Structure with Hover (8 checks) - REQUIRED for line/area

| # | Check | Validation | Scripted |
|---|-------|------------|----------|
| 6.11 | Has layer array | Line/area charts use `"layer": [...]` structure | Yes |
| 6.12 | Main mark layer | First layer has the primary mark (line/area) | Yes |
| 6.13 | Hover point layer | Has layer with point mark for hover | Yes |
| 6.14 | Hover params | Point layer has `"params"` with hover selection | Yes |
| 6.15 | Nearest selection | Hover uses `"nearest": true` | Yes |
| 6.16 | Pointer events | Uses `"on": "pointerover"` and `"clear": "pointerout"` | Yes |
| 6.17 | Opacity condition | Point opacity = 1 on hover, 0 otherwise | Yes |
| 6.18 | Tooltips defined | Point layer has `"tooltip"` array in encoding | Yes |

**Required Hover Layer Pattern:**
```json
{
  "params": [{
    "name": "hover",
    "select": {
      "type": "point",
      "nearest": true,
      "on": "pointerover",
      "clear": "pointerout"
    }
  }],
  "mark": {"type": "point", "filled": true, "size": 100},
  "encoding": {
    "opacity": {
      "condition": {"param": "hover", "empty": false, "value": 1},
      "value": 0
    },
    "tooltip": [
      {"field": "year", "type": "quantitative", "title": "Year"},
      {"field": "value", "type": "quantitative", "title": "Value", "format": ",.0f"}
    ]
  }
}
```

### 6F. Brand Compliance (3 checks)

| # | Check | Validation | Scripted |
|---|-------|------------|----------|
| 6.19 | Legend orientation | If legend present, `"orient": "top"` | Yes |
| 6.20 | Axis label font size | `config.axis.labelFontSize` = 14 | Yes |
| 6.21 | Axis title font size | `config.axis.titleFontSize` = 16 | Yes |

**Validation**: `python validate_vega.py path/to/chart.json` or `python validate_vega.py --all`

---

## 7. Chart-CSV Consistency (4 checks) - CRITICAL

These catch **silent failures** where charts render but show no data:

| # | Check | Validation | Scripted |
|---|-------|------------|----------|
| 7.1 | Color domain exists | If chart has color encoding with domain, validate it | Yes |
| 7.2 | Domain values in CSV | ALL color domain values exist in CSV data | Yes |
| 7.3 | Exact string match | Domain values match CSV values exactly (case, whitespace) | Yes |
| 7.4 | Language alignment | EN chart domain uses EN terms, MN uses MN terms | Yes |

**Example Silent Failure:**
- Chart domain: `["Male", "Female"]`
- CSV values: `["Эрэгтэй", "Эмэгтэй"]`
- Result: Chart renders but shows **NO DATA**

**Validation**: `python validate_dataset.py --all {id}` (includes cross-validation)

---

## 8. Bilingual Consistency (7 checks)

| # | Check | Validation | Type |
|---|-------|------------|------|
| 8.1 | Both MDX pages exist | EN and MN versions both present | Yes |
| 8.2 | Same category concept | EN "Economy" ↔ MN "Эдийн засаг" | AI |
| 8.3 | Same dataVersion | Both pages have identical `dataVersion` | AI |
| 8.4 | Same dataDate | Both pages have identical `dataDate` | AI |
| 8.5 | Same tag count | Similar number of tags in both | AI |
| 8.6 | Charts same structure | Both charts use same visualization type | AI |
| 8.7 | Data identical | Numeric values match across EN/MN CSVs | AI |

---

## 9. Registry Synchronization (6 checks)

| # | Check | Validation | Scripted |
|---|-------|------------|----------|
| 9.1 | Dataset registered | Entry exists in `datasets` table with matching ID | Yes |
| 9.2 | Source linked | Valid `source_id` foreign key | Yes |
| 9.3 | MDX paths set | `mdx_file_en` and `mdx_file_mn` populated | Yes |
| 9.4 | Chart path set | `chart_spec` field populated | Yes |
| 9.5 | Published flag | `is_published = 1` for live datasets | Yes |
| 9.6 | Version recorded | Entry in `versions` table for current version | Yes |

**Validation**: `python -m registry info {id}`

---

## 10. Content Quality (6 checks)

| # | Check | Validation | Type |
|---|-------|------------|------|
| 10.1 | Title has time range | If time-series, includes years (e.g., "1990-2024") | AI |
| 10.2 | Excerpt tells story | Not just "data about X" but includes actual insight | AI |
| 10.3 | Source properly attributed | Source name and URL are accurate | AI |
| 10.4 | No placeholder text | No TODO, TBD, FIXME, or template remnants | AI |
| 10.5 | Tags are relevant | Tags actually relate to the dataset content | AI |
| 10.6 | Keywords for SEO | Keywords include common search terms | AI |

---

## Summary by Validation Type

| Type | Count | Tool |
|------|-------|------|
| Scripted | ~60 | `validate_dataset.py`, `validate_vega.py`, `registry` |
| AI Judgment | ~25 | Checker subagent |
| **Total** | **85** | |

---

## Running Full Validation

```bash
# From data/ directory
cd data.mn

# 1. Validate all files for a dataset
python ../tools/scripts/validate_dataset.py --all {dataset-id}

# 2. Validate chart specs
python ../tools/scripts/validate_vega.py --all

# 3. Check registry
python -m ../tools/registry info {dataset-id}

# 4. AI checks run by checker subagent (see checker process)
```

---

## Checker Subagent Report Format

The checker subagent should output a structured report:

```
## Data Page Validation Report: {dataset-id}

### Section 1: File Existence
- [x] 1.1 MDX (EN): ✓ exists
- [x] 1.2 MDX (MN): ✓ exists
- [ ] 1.3 CSV (EN): ✗ MISSING
...

### Section 2: MDX Frontmatter
- [x] 2.1 title: ✓ "Mongolia GDP..."
- [ ] 2.4 category: ✗ "Employment" not in allowed list
...

### Summary
- Total checks: 85
- Passed: 78
- Failed: 7
- Warnings: 3

### Issues to Fix
1. [1.3] CSV (EN) file missing at public/datasets/{id}-en.csv
2. [2.4] Category "Employment" → use "Labor Market"
3. [6.15] Hover selection missing nearest: true
...
```

---

## Version History

- **2025-12-15**: Initial checklist created
  - 85 total checks across 10 sections
  - Categories loaded from `config/categories.json`
  - Hover pattern validation added to `validate_vega.py`
