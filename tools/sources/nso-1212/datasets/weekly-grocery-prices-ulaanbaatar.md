# Dataset: Weekly Grocery Prices in Ulaanbaatar (2021-2025)

## Identification

- **ID**: `weekly-grocery-prices-ulaanbaatar`
- **Source**: `nso-1212`
- **Category**: Prices & Inflation
- **Tags**: [mongolia, prices, groceries, food, ulaanbaatar, weekly]
- **Concept ID**: `weekly-prices`

## Source Reference

- **Table ID**: `DT_NSO_0600_001V4.px`
- **Parent Dataset**: `nso-weekly-prices-ulaanbaatar`
- **Sector**: `Economy, environment`
- **Subsector**: `Consumer Price Index`
- **API Path**: `/en/NSO/Economy, environment/Consumer Price Index/DT_NSO_0600_001V4.px`

## Title

- **EN**: Weekly Grocery Prices in Ulaanbaatar (2021-2025)
- **MN**: Улаанбаатар дахь хүнсний бүтээгдэхүүний долоо хоногийн үнэ (2021-2025)

## Description

Weekly price tracking for common grocery items in Ulaanbaatar, including
vegetable oil, sugar, green tea, and eggs. Egg prices show significant
seasonal variation, ranging from 400-700 MNT/piece.

## Variables

### Product (Бүтээгдэхүүн)
4 products (EN/MN labels paired by identical date+price series in the
published CSVs):

| EN | MN |
|----|----|
| Egg, piece, domestic | Өндөг, ш |
| Green tea, prepacked, 90 g | Ногоон цай, савласан, 90 г |
| Sugar, prepacked, kg, imported | Элсэн чихэр, кг |
| Vegetable oil, l, imported | Ургамлын тос, л |

### Date (Огноо)
287 weekly dates from 2021-01-06 to 2026-08-31.

### Price (Үнэ)
Price in MNT per listed unit (piece, 90 g pack, kg, liter).

## Update Instructions

Query the API for table `DT_NSO_0600_001V4.px` and compare the `updated`
field with the registry.

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_0600_001V4.px --output ./output
```

Filter the parent table to the 4 grocery products above, rename raw
columns to `product, date, price` (EN) / `бүтээгдэхүүн, огноо, үнэ` (MN),
strip whitespace from product names, and sort by product, date ascending.

## Files

- `data.mn/public/datasets/weekly-grocery-prices-ulaanbaatar-en.csv` (1148 rows: 4 products x 287 weeks; columns `product, date, price`)
- `data.mn/public/datasets/weekly-grocery-prices-ulaanbaatar-mn.csv` (1148 rows; columns `бүтээгдэхүүн, огноо, үнэ`)
- `data.mn/public/datasets/weekly-grocery-prices-ulaanbaatar.xlsx` (wide format)
- `data.mn/public/charts/weekly-grocery-prices-ulaanbaatar-en.json`
- `data.mn/public/charts/weekly-grocery-prices-ulaanbaatar-mn.json`
- `data.mn/src/data/data/en/weekly-grocery-prices-ulaanbaatar.mdx`
- `data.mn/src/data/data/mn/weekly-grocery-prices-ulaanbaatar.mdx`

## Chart

Multi-line time series. X is `date` (temporal), Y is `price` in MNT
(quantitative), color is `product` (4 series, legend on top).

## Notes

- Split dataset derived from parent `nso-weekly-prices-ulaanbaatar`
  (table DT_NSO_0600_001V4.px, 31 products)
- Related splits: `weekly-meat-prices-ulaanbaatar`,
  `weekly-vegetable-prices-ulaanbaatar`, `weekly-fuel-prices-ulaanbaatar`
