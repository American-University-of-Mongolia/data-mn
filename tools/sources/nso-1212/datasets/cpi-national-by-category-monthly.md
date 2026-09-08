# Dataset: Mongolia National CPI by Category, Monthly (2010–2026)

## Identification

- **ID**: `cpi-national-by-category-monthly`
- **Source**: `nso-1212`
- **Category EN**: Prices & Inflation
- **Category MN**: Үнэ ба инфляци
- **Tags**: [mongolia, cpi, inflation, prices, national, monthly, category, food, housing, transport, energy]

## Source Reference

- **Table ID**: `DT_NSO_0600_001V3.px`
- **Title**: NATIONAL BASE CONSUMER PRICE INDEX, by group and month
- **URL**: https://data.1212.mn

## Variables

### Reference year (Суурь он)

Base year for the index calculation. This dataset uses `2020=100`.

### Group (Бүлэг)

13 CPI expenditure categories (all groups except `Overall index`):

- Food and non-alcoholic beverages / Хүнсний бараа, ундаа, ус
- Alcoholic beverages, tobacco / Согтууруулах ундаа, тамхи
- Clothing, footwear and cloth / Хувцас, бөс бараа, гутал
- Housing, water, electricity and fuels / Орон сууц, ус, цахилгаан, түлш
- Furnishings, household equipment / Гэр ахуйн тавилга, гэр ахуйн бараа
- Health / Эм тариа, эмнэлгийн үйлчилгээ
- Transport / Тээвэр
- Communication / Холбооны хэрэгсэл, шуудангийн үйлчилгээ
- Recreation and culture / Амралт, чөлөөт цаг, соёлын бараа, үйлчилгээ
- Education / Боловсролын үйлчилгээ
- Restaurants and hotels / Зочид буудал, зоогийн газар, дотуур байр
- Insurance and financial services / Даатгал, санхүүгийн үйлчилгээ
  (partial series, starts 2020-01)
- Miscellaneous goods and services / Бусад бараа, үйлчилгээ

### Month (Сар)

Monthly time dimension: 2010-01 to present.

## Update Instructions

### Check for Updates

1. Query the NSO catalog cache for table `DT_NSO_0600_001V3.px`
2. Compare its `last_updated` timestamp against the registry `source_updated_at`
3. If newer data is available, proceed to fetch

### Fetch Data

Shared with `cpi-national-monthly` (same source table, fetch once):

```bash
.venv/bin/python .claude/skills/datamn-source-nso/fetch_data.py \
  --table "DT_NSO_0600_001V3.px" --lang both --output /tmp/cpi-fetch
```

### Transform

- Strip and collapse whitespace in all string columns (source pads group
  names with double spaces).
- Keep rows with `Reference year == 2020=100`, exclude `Overall index`
  (MN: `Ерөнхий индекс`), drop rows with null values, sort by month ascending
  (stable within-month order).
- Chart/download CSV EN (`date,category,cpi_index`);
  MN (`огноо,ангилал,хэрэглээний_үнийн_индекс`).
- XLSX: same three columns; sheet `CPI by Category` (EN) /
  `ХҮИ ангиллаар` (MN).

## Splits

None. This is a standalone dataset.

## Files

- `data.mn/public/datasets/cpi-national-by-category-monthly-en.csv`
- `data.mn/public/datasets/cpi-national-by-category-monthly-mn.csv`
- `data.mn/public/datasets/cpi-national-by-category-monthly-en.xlsx`
- `data.mn/public/datasets/cpi-national-by-category-monthly-mn.xlsx`
- `data.mn/public/charts/cpi-national-by-category-monthly-en.json`
- `data.mn/public/charts/cpi-national-by-category-monthly-mn.json`
- `data.mn/src/data/data/en/cpi-national-by-category-monthly.mdx`
- `data.mn/src/data/data/mn/cpi-national-by-category-monthly.mdx`

## Chart

Multi-series line chart (13 categories) with nearest-point hover.
See `data.mn/public/charts/cpi-national-by-category-monthly-en.json`
and `-mn.json`.

## Related Datasets

- `cpi-national-monthly`: same source table, headline overall index.
