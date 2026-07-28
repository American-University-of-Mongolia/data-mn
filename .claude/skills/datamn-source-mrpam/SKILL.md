---
name: datamn-source-mrpam
description: Fetch and extract data from MRPAM (Mineral Resources and Petroleum Authority of Mongolia) monthly PDF reports. Use when working with coal production, petroleum, mining permits, commodity prices, or fuel price data from mrpam.gov.mn.
dependencies:
  - python3
  - pdfplumber
  - requests
  - beautifulsoup4
  - pandas
  - openpyxl
---

# MRPAM Data Source Skill

Fetches monthly statistical reports (PDFs) from the Mineral Resources and Petroleum Authority of Mongolia (MRPAM) and extracts tabular data for use in the data.mn pipeline.

Base directory for this skill (repo-relative): `.claude/skills/datamn-source-mrpam`

---

## Source Overview

| Field | Value |
|-------|-------|
| **Source ID** | `mrpam` |
| **Name EN** | Mineral Resources and Petroleum Authority of Mongolia |
| **Name MN** | Ашигт малтмал, газрын тосны газар |
| **Base URL** | https://mrpam.gov.mn |
| **Data Type** | PDF Reports |
| **Update Frequency** | Monthly |
| **Language** | Mongolian only — translation required |

---

## Page IDs by Year

Each year's reports are on a separate page:

| Year | Page ID | URL |
|------|---------|-----|
| 2021 | 169 | https://mrpam.gov.mn/page/169 |
| 2022 | 177 | https://mrpam.gov.mn/page/177 |
| 2023 | 196 | https://mrpam.gov.mn/page/196 |
| 2024 | 202 | https://mrpam.gov.mn/page/202 |
| 2025 | 714 | https://mrpam.gov.mn/page/714 |
| 2026 | 732 | https://mrpam.gov.mn/page/732 |

---

## Helper Scripts

| Script | Purpose |
|--------|---------|
| `fetch_report.py` | Scrape page for PDF links and download reports to cache |
| `extract_tables.py` | Extract specific tables from downloaded PDFs → bilingual CSVs |

---

## Workflow

### Step 1: Download Reports

```bash
cd .claude/skills/datamn-source-mrpam

# List available reports for a year (no download)
conda run -n datamn python3 fetch_report.py --year 2025 --list

# Download all 2025 reports
conda run -n datamn python3 fetch_report.py --year 2025

# Download a specific month
conda run -n datamn python3 fetch_report.py --year 2025 --month 1

# Download all years (2021-2025)
conda run -n datamn python3 fetch_report.py --all-years

# PDFs are cached in: tools/temp/mrpam-pdfs/
```

### Step 2: Extract Tables

```bash
# Extract coal production from all 2025 PDFs
conda run -n datamn python3 extract_tables.py --dataset mrpam-coal-production --year 2025

# Extract all datasets from a specific PDF
conda run -n datamn python3 extract_tables.py --pdf tools/temp/mrpam-pdfs/2025.1.stat.report.mon.pdf --all

# Output goes to: tools/temp/mrpam-extracted/
```

### Step 3: Translate CSVs

```bash
# Translate Mongolian CSV to English
conda run -n datamn python3 tools/scripts/translate_csv.py \
  tools/temp/mrpam-extracted/mrpam-coal-production-mn.csv \
  --from mn --to en \
  -o tools/temp/mrpam-extracted/mrpam-coal-production-en.csv
```

---

## Available Datasets

| Dataset ID | Source Table | Description |
|-----------|-------------|-------------|
| `mrpam-coal-production` | 3.17 | Monthly coal production, sales, export (thousand tons) |
| `mrpam-petroleum-production` | 4.1, 4.2 | Monthly petroleum production and export (barrels) |
| `mrpam-mining-permits` | 1.1 | Mining permit counts and area by province |
| `mrpam-commodity-prices` | 3.8 | World market mineral prices (gold, copper, coal, etc.) |
| `mrpam-fuel-prices` | 4.6 | Retail fuel prices by province |
| `mrpam-petroleum-imports` | 4.3 | Petroleum product imports by type |
| `mrpam-budget-revenue` | 5.1 | State budget revenue from mining sector |

---

## Report Structure

Each monthly PDF (~30 pages) has 5 sections. Find tables by Mongolian heading text, NOT by page number (pages shift between months).

### Section 1: Mining Licenses (Тусгай зөвшөөрөл)
- Table 1.1 — Valid licenses by province (count + area)
- Table 1.8 — License holder origin (Mongolian/Foreign/Joint venture)

### Section 3: Mining (Уул уурхай)
- Table 3.8 — World commodity prices (gold, silver, copper, coal, etc.)
- Table 3.17 — Coal production/sales/export by month

### Section 4: Petroleum (Газрын тос)
- Table 4.1/4.2 — Petroleum production and export (barrels)
- Table 4.3 — Petroleum product imports by type
- Table 4.6 — Retail fuel prices by province
- Table 4.7 — Retail fuel prices monthly trend

### Section 5: Budget Revenue (Улсын төсвийн орлого)
- Table 5.1 — Budget revenue by type (billion MNT)

---

## CSV Output Contract

All output CSVs must follow the bilingual contract:

### Coal Production (`mrpam-coal-production`)
**EN** (`mrpam-coal-production-en.csv`):
```
year,month,production_kt,sales_kt,export_kt
2026,6,13036.0,11221.5,10367.4
```
**MN** (`mrpam-coal-production-mn.csv`):
```
он,сар,олборлолт_мян_тн,борлуулалт_мян_тн,экспорт_мян_тн
2026,6,13036.0,11221.5,10367.4
```

### Petroleum Production (`mrpam-petroleum-production`)
**EN**: `year,month,production_barrels,export_barrels`
**MN**: `он,сар,олборлолт_баррель,экспорт_баррель`

### Mining Permits (`mrpam-mining-permits`)
The PDF reports licensed area in **thousand hectares**, not hectares.

**EN**: `year,month,province,total_count,total_area_kha,extraction_count,extraction_area_kha,exploration_count,exploration_area_kha`
**MN**: `он,сар,аймаг,нийт_тоо,нийт_талбай_мян_га,ашиглалтын_тоо,ашиглалтын_талбай_мян_га,хайгуулын_тоо,хайгуулын_талбай_мян_га`

### Commodity Prices (`mrpam-commodity-prices`)
**EN**: `year,month,commodity,price,unit,source`
**MN**: `он,сар,бараа,үнэ,нэгж,эх_үүсвэр`

### Fuel Prices (`mrpam-fuel-prices`)
**EN**: `year,month,province,ai92_price,ai92_euro5_price,ai95_price,diesel_price,diesel_euro5_price`
**MN**: `он,сар,аймаг,аи92_үнэ,аи92_евро5_үнэ,аи95_үнэ,дизель_үнэ,дизель_евро5_үнэ`

### Petroleum Imports (`mrpam-petroleum-imports`)
**EN**: `year,month,product,volume_t`
**MN**: `он,сар,бүтээгдэхүүн,хэмжээ_тн`

The nine 2026 product positions are Total, AI-92, AI-92 Euro-5, AI-95,
diesel, diesel Euro-5, jet fuel TS-1, LPG, and Other. Empty/`-` cells must
remain empty; never collapse them before assigning product labels.

### Budget Revenue (`mrpam-budget-revenue`)
Table 5.1 reports **million MNT** (`сая төгрөг`), not billion MNT.

**EN**: `year,month,revenue_type,plan_mln_mnt,actual_mln_mnt,pct_of_plan`
**MN**: `он,сар,орлогын_төрөл,төлөвлөгөө_сая_төг,гүйцэтгэл_сая_төг,хувь`

### Rules
- `date` columns: ISO format `YYYY-MM-DD` or separate `year`/`month` columns
- Numbers: no commas, no units in value cells
- EN CSV: English headers + English categorical values
- MN CSV: Mongolian headers + Mongolian categorical values
- Numeric values MUST be identical in both CSVs
- English CSV categorical values (province, commodity, product, unit, and
  revenue type) MUST be translated; Mongolian CSV categories retain the source
  wording

---

## Key Mongolian Terms

| Mongolian | English |
|-----------|---------|
| Тусгай зөвшөөрөл | Special permit / License |
| Хайгуулын | Exploration |
| Ашиглалтын | Extraction / Mining |
| Нүүрс | Coal |
| Газрын тос | Petroleum / Oil |
| Олборлолт | Production |
| Экспорт | Export |
| Дотоодын хэрэглээ | Domestic consumption |
| Баррель | Barrel |
| мян.тн | kt (thousand tons) |
| Улсын төсвийн орлого | State budget revenue |
| Аймаг | Province / Aimag |
| Нийт | Total |
| Төлөвлөгөө | Plan / Target |
| Гүйцэтгэл | Actual / Performance |
| Бензин | Gasoline |
| Дизель | Diesel |

---

## Column Name Translation Reference

| Mongolian | English |
|-----------|---------|
| он | year |
| сар | month |
| огноо | date |
| аймаг | province |
| нийт | total |
| тоо | count |
| талбай | area |
| олборлолт | production |
| экспорт | export |
| дотоод_хэрэглээ | domestic_consumption |
| үнэ | price |
| нэгж | unit |
| төлөвлөгөө | plan |
| гүйцэтгэл | actual |

---

## Troubleshooting

| Problem | Solution |
|---------|---------|
| No tables detected on a page | Try `vertical_strategy="text"` instead of `"lines"` |
| Merged cells return `None` | Forward-fill using the pattern in `extract_tables.py` |
| Section not found | Search for heading keywords, not fixed page numbers |
| Different column count across months | Normalize to common schema, fill missing with `None` |
| Numbers with spaces (1 234,5) | Strip spaces and replace `,` with `.` |

---

## Dependencies

```
requests>=2.31.0
pandas>=2.0.0
beautifulsoup4>=4.12.0
openpyxl>=3.1.0
pdfplumber>=0.10.0
```

All are included in the `datamn` conda environment.
