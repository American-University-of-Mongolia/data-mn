# Dataset: Average Crop Product Prices in Mongolia (2018-2025)

## Identification

- **ID**: `crop-prices-national`
- **Source**: `nso-1212`
- **Category**: Agriculture
- **Tags**: [mongolia, agriculture, crop prices, wheat, hay, fodder, tuv]

## Source Reference

- **Source Name**: National Statistics Office of Mongolia
- **URL**: https://data.1212.mn
- **Table ID**: `DT_NSO_1002_001V4.px`
- **Sector**: verify sector/subsector on data.1212.mn for table DT_NSO_1002_001V4.px
- **Subsector**: verify sector/subsector on data.1212.mn for table DT_NSO_1002_001V4.px

## Title

- **EN**: Average Crop Product Prices in Mongolia (2018-2025)
- **MN**: Монгол Улсын таримал бүтээгдэхүүний дундаж үнэ (2018-2025)

## Description

Monthly average market prices for crop products in Tuv province,
Mongolia's main agricultural region. Covers wheat (commodity and seed),
hay (baled and loose), green feed, oat, and wheat bran (25kg and 50kg
bags). Prices show seasonal patterns with winter months typically higher
due to increased demand for animal feed.

## Variables

### Product (Бүтээгдэхүүн)
8 products:

| EN | MN |
|----|----|
| Green feed | Ногоон тэжээл |
| Hay | Задгай өвс |
| Hay bale | Боодолтой өвс |
| Oat | Овъёос |
| Wheat | Таваарын буудай |
| Wheat bran, 25kg | Хивэг,25кг |
| Wheat bran, 50kg | Хивэг,50кг |
| Wheat seed | Үрийн буудай |

### Date (Огноо)
82 months: 2018-12 to 2025-12, format `YYYY-MM`.
Coverage is sparse: 541 rows for 8 products x 82 months (not every
product has a price every month).

### Price (Үнэ)
Monthly average market price in MNT (verify unit and per-quantity basis
against the NSO table metadata).

## File Shapes

- EN CSV columns: `product, date, price` — 541 data rows
- MN CSV columns: `бүтээгдэхүүн, огноо, үнэ` — 541 data rows
- XLSX: bilingual workbook (EN + MN sheets)

## Update Instructions

Query the API for table `DT_NSO_1002_001V4.px` and compare `updated`
field with registry.

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_1002_001V4.px --output ./output
```

Filter to the 8 crop products above, rename columns to
`product, date, price` (EN) and `бүтээгдэхүүн, огноо, үнэ` (MN),
and sort by product, date ascending.

## Files

- `data.mn/public/datasets/crop-prices-national-en.csv`
- `data.mn/public/datasets/crop-prices-national-mn.csv`
- `data.mn/public/datasets/crop-prices-national.xlsx`
- `data.mn/public/charts/crop-prices-national-en.json`
- `data.mn/public/charts/crop-prices-national-mn.json`
- `data.mn/src/data/data/en/crop-prices-national.mdx`
- `data.mn/src/data/data/mn/crop-prices-national.mdx`

## Chart

Multi-series line chart: x = date (monthly), y = price (MNT),
color = product.

## Notes

- Published snapshot backfilled at `tools/versions/crop-prices-national/v1/`
- Related dataset `wheat-bran-prices` (same NSO table
  DT_NSO_1002_001V4.px) covers wheat bran prices across all aimags
