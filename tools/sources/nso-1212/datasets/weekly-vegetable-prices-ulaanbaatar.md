# Dataset: Weekly Vegetable Prices in Ulaanbaatar (2021-2025)

## Identification

- **ID**: `weekly-vegetable-prices-ulaanbaatar`
- **Source**: `nso-1212`
- **Category**: Prices & Inflation
- **Tags**: [mongolia, prices, vegetables, produce, ulaanbaatar, weekly]
- **Concept ID**: `weekly-prices`

## Source Reference

- **Table ID**: `DT_NSO_0600_001V4.px`
- **Parent Dataset**: `nso-weekly-prices-ulaanbaatar`
- **Sector**: `Economy, environment`
- **Subsector**: `Consumer Price Index`
- **API Path**: `/en/NSO/Economy, environment/Consumer Price Index/DT_NSO_0600_001V4.px`

## Title

- **EN**: Weekly Vegetable Prices in Ulaanbaatar (2021-2025)
- **MN**: Улаанбаатар дахь хүнсний ногооны долоо хоногийн үнэ (2021-2025)

## Description

Weekly price tracking for vegetables and fruits in Ulaanbaatar, including
potatoes, carrots, cabbage, onions, beets, and apples. Prices show strong
seasonal patterns, with winter prices 2-3x higher than summer.

## Variables

### Product (Бүтээгдэхүүн)
6 products (EN/MN labels paired by identical date+price series in the
published CSVs):

| EN | MN |
|----|----|
| Apple, kg, China | Алим, кг |
| Beet, kg | Хүрэн манжин, кг |
| Cabbage, kg | Байцаа, кг |
| Carrot, kg | Лууван, кг |
| Onion, kg | Сонгино, кг |
| Tomato, kg | Төмс, кг |

### Date (Огноо)
287 weekly dates from 2021-01-06 to 2026-08-31.

### Price (Үнэ)
Price in MNT per kg.

## Update Instructions

Query the API for table `DT_NSO_0600_001V4.px` and compare the `updated`
field with the registry.

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_0600_001V4.px --output ./output
```

Filter the parent table to the 6 vegetable/fruit products above, rename
raw columns to `product, date, price` (EN) /
`бүтээгдэхүүн, огноо, үнэ` (MN), strip whitespace from product names,
and sort by product, date ascending.

## Files

- `data.mn/public/datasets/weekly-vegetable-prices-ulaanbaatar-en.csv` (1722 rows: 6 products x 287 weeks; columns `product, date, price`)
- `data.mn/public/datasets/weekly-vegetable-prices-ulaanbaatar-mn.csv` (1722 rows; columns `бүтээгдэхүүн, огноо, үнэ`)
- `data.mn/public/datasets/weekly-vegetable-prices-ulaanbaatar.xlsx` (wide format)
- `data.mn/public/charts/weekly-vegetable-prices-ulaanbaatar-en.json`
- `data.mn/public/charts/weekly-vegetable-prices-ulaanbaatar-mn.json`
- `data.mn/src/data/data/en/weekly-vegetable-prices-ulaanbaatar.mdx`
- `data.mn/src/data/data/mn/weekly-vegetable-prices-ulaanbaatar.mdx`

## Chart

Multi-line time series. X is `date` (temporal), Y is `price` in MNT
(quantitative), color is `product` (6 series, legend on top).

## Notes

- Split dataset derived from parent `nso-weekly-prices-ulaanbaatar`
  (table DT_NSO_0600_001V4.px, 31 products)
- Related splits: `weekly-grocery-prices-ulaanbaatar`,
  `weekly-meat-prices-ulaanbaatar`, `weekly-fuel-prices-ulaanbaatar`
- Verify label mismatch: the EN series `Tomato, kg` and the MN series
  `Төмс, кг` (potato) contain identical date+price values (287/287
  match). The parent table lists product 24 as `Tomato, kg` /
  `Улаан лооль, кг` with no potato item, so one published label is
  likely wrong. Published files were left untouched.
