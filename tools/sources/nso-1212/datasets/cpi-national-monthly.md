# Dataset: Mongolia National Consumer Price Index, Monthly (2010–2026)

## Identification

- **ID**: `cpi-national-monthly`
- **Source**: `nso-1212`
- **Category EN**: Prices & Inflation
- **Category MN**: Үнэ ба инфляци
- **Tags**: [mongolia, cpi, inflation, prices, national, monthly]

## Source Reference

- **Table ID**: `DT_NSO_0600_001V3.px`
- **Title**: NATIONAL BASE CONSUMER PRICE INDEX, by group and month
- **URL**: https://data.1212.mn

## Variables

### Reference year (Суурь он)

Base year for the index calculation. This dataset uses `2020=100`:

- `2015=100`: Historical data (2006-01 to 2022-07)
- `2020=100`: Current series (2010-01 to present)
- `2023=100`: Latest base (2010-01 to present)

### Group (Бүлэг)

This dataset uses `Overall index` (headline national CPI, all items).
EN `Overall index` = MN `Ерөнхий индекс`.

### Month (Сар)

Monthly time dimension: 2010-01 to present.

## Update Instructions

### Check for Updates

1. Query the NSO catalog cache for table `DT_NSO_0600_001V3.px`
2. Compare its `last_updated` timestamp against the registry `source_updated_at`
3. If newer data is available, proceed to fetch

### Fetch Data

```bash
.venv/bin/python .claude/skills/datamn-source-nso/fetch_data.py \
  --table "DT_NSO_0600_001V3.px" --lang both --output /tmp/cpi-fetch
```

Raw columns EN: `Reference year, Group, Month, value`.
Raw columns MN: `Суурь он, Бүлэг, Сар, value`.

### Transform

- Strip and collapse whitespace in all string columns (source pads group
  names, e.g. `Overall  index`).
- Keep rows with `Reference year == 2020=100` and Group `Overall index`
  (MN: `Ерөнхий индекс`), drop rows with null values, sort by month ascending.
- Chart/download CSV EN (`date,cpi_index`); MN (`огноо,хэрэглээний_үнийн_индекс`).
- XLSX: same two columns; sheet `CPI National Monthly` (EN) /
  `Үндэсний ХҮИ сараар` (MN).

## Splits

None. This is a standalone dataset.

## Files

- `data.mn/public/datasets/cpi-national-monthly-en.csv`
- `data.mn/public/datasets/cpi-national-monthly-mn.csv`
- `data.mn/public/datasets/cpi-national-monthly-en.xlsx`
- `data.mn/public/datasets/cpi-national-monthly-mn.xlsx`
- `data.mn/public/charts/cpi-national-monthly-en.json`
- `data.mn/public/charts/cpi-national-monthly-mn.json`
- `data.mn/src/data/data/en/cpi-national-monthly.mdx`
- `data.mn/src/data/data/mn/cpi-national-monthly.mdx`

## Chart

Single-series line chart with nearest-point hover over the headline index.
See `data.mn/public/charts/cpi-national-monthly-en.json` and `-mn.json`.

## Related Datasets

- `cpi-national-by-category-monthly`: same source table, breakdown by 13
  spending categories.
