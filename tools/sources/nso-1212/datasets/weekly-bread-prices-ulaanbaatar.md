# Dataset: Weekly Bread & Grain Prices in Ulaanbaatar (2021-2025)

## Identification

- **ID**: `weekly-bread-prices-ulaanbaatar`
- **Source**: `nso-1212`
- **Category**: Prices & Inflation
- **Tags**: [mongolia, prices, bread, flour, grain, ulaanbaatar, weekly]

## Source Reference

- **Source Name**: National Statistics Office of Mongolia
- **URL**: https://data.1212.mn
- **Table ID**: `DT_NSO_0600_001V4.px`
- **Sector**: `Economy, environment`
- **Subsector**: `Consumer Price Index`
- **API Path**: `/en/NSO/Economy, environment/Consumer Price Index/DT_NSO_0600_001V4.px`

## Title

- **EN**: Weekly Bread & Grain Prices in Ulaanbaatar (2021-2025)
- **MN**: Улаанбаатар дахь талх, гурилын бүтээгдэхүүний долоо хоногийн үнэ (2021-2025)

## Description

Weekly price tracking for bread, flour, and rice in Ulaanbaatar. Grade 1
flour prices have increased from around 1,800 MNT/kg in 2021 to 2,500
MNT/kg in 2025. This dataset is a category split of the parent
`nso-weekly-prices-ulaanbaatar` table (31 products); only the splits are
published to data.mn.

## Variables

### Product (Бүтээгдэхүүн)
5 products, 287 weeks each:

| EN | MN |
|----|----|
| Flour, grade 1, prepacked, kg | Гурил, I зэрэг, савласан, кг |
| Bread, piece | Талх, 600 гр |
| Sliced bread, 600 gr, piece | Талх, зүссэн, 600 гр |
| Bread, rye, piece | Хар талх, 300 гр |
| Rice, prepacked, kg | Цагаан будаа, кг |

Note: EN/MN pairing verified by joining published CSVs on
(date, price); the MN labels carry package sizes (600 гр, 300 гр) that
the EN labels omit — verify canonical product names against the source
table.

### Date (Огноо)
287 weeks: 2021-01-06 to 2026-08-31, format `YYYY-MM-DD`.

### Price (Үнэ)
Weekly price in MNT per unit (kg or piece as named).

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

Filter to the 5 bread/grain products above, rename columns to
`product, date, price` (EN) and `бүтээгдэхүүн, огноо, үнэ` (MN),
and sort by product, date ascending.

Validate: all price values positive; dates valid weekly dates; EN/MN
row counts and totals must match.

## Files

- `data.mn/public/datasets/weekly-bread-prices-ulaanbaatar-en.csv`
- `data.mn/public/datasets/weekly-bread-prices-ulaanbaatar-mn.csv`
- `data.mn/public/datasets/weekly-bread-prices-ulaanbaatar.xlsx`
- `data.mn/public/charts/weekly-bread-prices-ulaanbaatar-en.json`
- `data.mn/public/charts/weekly-bread-prices-ulaanbaatar-mn.json`
- `data.mn/src/data/data/en/weekly-bread-prices-ulaanbaatar.mdx`
- `data.mn/src/data/data/mn/weekly-bread-prices-ulaanbaatar.mdx`

## Chart

Multi-series line chart: x = date (weekly), y = price (MNT/unit),
color = product type.

## Notes

- Published snapshot backfilled at
  `tools/versions/weekly-bread-prices-ulaanbaatar/v1/`
- Parent definition: `tools/sources/nso-1212/datasets/weekly-prices-ulaanbaatar.md`
- Sibling splits: `weekly-dairy-prices-ulaanbaatar`,
  `weekly-fuel-prices-ulaanbaatar`, `weekly-meat-prices-ulaanbaatar`,
  `weekly-grocery-prices-ulaanbaatar`, `weekly-vegetable-prices-ulaanbaatar`
