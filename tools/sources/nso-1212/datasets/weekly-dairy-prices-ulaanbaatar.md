# Dataset: Weekly Dairy Prices in Ulaanbaatar (2021-2025)

## Identification

- **ID**: `weekly-dairy-prices-ulaanbaatar`
- **Source**: `nso-1212`
- **Category**: Prices & Inflation
- **Tags**: [mongolia, prices, dairy, milk, ulaanbaatar, weekly]

## Source Reference

- **Source Name**: National Statistics Office of Mongolia
- **URL**: https://data.1212.mn
- **Table ID**: `DT_NSO_0600_001V4.px`
- **Sector**: `Economy, environment`
- **Subsector**: `Consumer Price Index`
- **API Path**: `/en/NSO/Economy, environment/Consumer Price Index/DT_NSO_0600_001V4.px`

## Title

- **EN**: Weekly Dairy Prices in Ulaanbaatar (2021-2025)
- **MN**: Улаанбаатар дахь сүү, сүүн бүтээгдэхүүний долоо хоногийн үнэ (2021-2025)

## Description

Weekly price tracking for dairy products in Ulaanbaatar, including fresh
milk, pasteurized milk, yoghurt, and butter cream. Fresh milk prices have
remained relatively stable around 3,500-4,000 MNT/liter. This dataset is
a category split of the parent `nso-weekly-prices-ulaanbaatar` table (31
products); only the splits are published to data.mn.

## Variables

### Product (Бүтээгдэхүүн)
5 products, 287 weeks each:

| EN | MN |
|----|----|
| Milk, fresh, not pasteurised, l | Сүү, задгай, л |
| Milk, pasteurised, 500 g | Сүү, ууттай, 0.5 л |
| Milk, pasteurised, l | Сүү, савтай, л |
| Yoghurt, Tsutsgiitei, plain, 900 g | Тараг, савласан, 900 гр |
| Butter cream, Sain zuuhii, 450 g | Цөцгийн тос, 200 гр |

Note: EN/MN pairing verified by joining published CSVs on
(date, price); package sizes differ between languages (e.g. 450 g vs
200 гр for butter cream) — verify canonical product names against the
source table.

### Date (Огноо)
287 weeks: 2021-01-06 to 2026-08-31, format `YYYY-MM-DD`.

### Price (Үнэ)
Weekly price in MNT per unit (liter or package as named).

## File Shapes

- EN CSV columns: `product, date, price` — 1435 data rows
- MN CSV columns: `бүтээгдэхүүн, огноо, үнэ` — 1435 data rows
- XLSX: bilingual workbook (EN + MN sheets)

## Update Instructions

Query the table listing endpoint and compare the `updated` field for
`DT_NSO_0600_001V4.px` with registry:

```
GET https://data.1212.mn/api/v1/en/NSO/Economy, environment/Consumer Price Index/
```

Fetch with the `datamn-source-nso` skill:

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_0600_001V4.px --output ./output
```

Filter to the 5 dairy products above, rename columns to
`product, date, price` (EN) and `бүтээгдэхүүн, огноо, үнэ` (MN),
and sort by product, date ascending.

Validate: all price values positive; dates valid weekly dates; EN/MN
row counts and totals must match.

## Files

- `data.mn/public/datasets/weekly-dairy-prices-ulaanbaatar-en.csv`
- `data.mn/public/datasets/weekly-dairy-prices-ulaanbaatar-mn.csv`
- `data.mn/public/datasets/weekly-dairy-prices-ulaanbaatar.xlsx`
- `data.mn/public/charts/weekly-dairy-prices-ulaanbaatar-en.json`
- `data.mn/public/charts/weekly-dairy-prices-ulaanbaatar-mn.json`
- `data.mn/src/data/data/en/weekly-dairy-prices-ulaanbaatar.mdx`
- `data.mn/src/data/data/mn/weekly-dairy-prices-ulaanbaatar.mdx`

## Chart

Multi-series line chart: x = date (weekly), y = price (MNT/unit),
color = product type.

## Notes

- Published snapshot backfilled at
  `tools/versions/weekly-dairy-prices-ulaanbaatar/v1/`
- Parent definition: `tools/sources/nso-1212/datasets/weekly-prices-ulaanbaatar.md`
- Sibling splits: `weekly-bread-prices-ulaanbaatar`,
  `weekly-fuel-prices-ulaanbaatar`, `weekly-meat-prices-ulaanbaatar`,
  `weekly-grocery-prices-ulaanbaatar`, `weekly-vegetable-prices-ulaanbaatar`
