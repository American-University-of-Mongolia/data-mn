# Dataset: Weekly Meat Prices in Ulaanbaatar (2021-2025)

## Identification

- **ID**: `weekly-meat-prices-ulaanbaatar`
- **Source**: `nso-1212`
- **Category**: Prices & Inflation
- **Tags**: [mongolia, prices, meat, ulaanbaatar, weekly]
- **Concept ID**: `weekly-prices`

## Source Reference

- **Table ID**: `DT_NSO_0600_001V4.px`
- **Parent Dataset**: `nso-weekly-prices-ulaanbaatar`
- **Sector**: `Economy, environment`
- **Subsector**: `Consumer Price Index`
- **API Path**: `/en/NSO/Economy, environment/Consumer Price Index/DT_NSO_0600_001V4.px`

## Title

- **EN**: Weekly Meat Prices in Ulaanbaatar (2021-2025)
- **MN**: Улаанбаатар дахь махны долоо хоногийн үнэ (2021-2025)

## Description

Weekly price tracking for mutton, beef, horse meat, and goat meat in
Ulaanbaatar, Mongolia's capital. As of December 2025, mutton averages
around 17,000 MNT/kg and beef around 16,500 MNT/kg.

## Variables

### Product (Бүтээгдэхүүн)
5 products (EN/MN labels paired by identical date+price series in the
published CSVs):

| EN | MN |
|----|----|
| Beef, kg | Үхрийн мах, ястай, кг |
| Beef, without bones, kg | Үхрийн мах, цул, кг |
| Goat meat, kg | Ямааны мах, ястай, кг |
| Horse meat, kg | Адууны мах, ястай, кг |
| Mutton, kg | Хонины мах, ястай, кг |

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

Filter the parent table to the 5 meat products above, rename raw
columns to `product, date, price` (EN) / `бүтээгдэхүүн, огноо, үнэ` (MN),
strip whitespace from product names, and sort by product, date ascending.

## Files

- `data.mn/public/datasets/weekly-meat-prices-ulaanbaatar-en.csv` (1435 rows: 5 products x 287 weeks; columns `product, date, price`)
- `data.mn/public/datasets/weekly-meat-prices-ulaanbaatar-mn.csv` (1435 rows; columns `бүтээгдэхүүн, огноо, үнэ`)
- `data.mn/public/datasets/weekly-meat-prices-ulaanbaatar.xlsx` (wide format)
- `data.mn/public/charts/weekly-meat-prices-ulaanbaatar-en.json`
- `data.mn/public/charts/weekly-meat-prices-ulaanbaatar-mn.json`
- `data.mn/src/data/data/en/weekly-meat-prices-ulaanbaatar.mdx`
- `data.mn/src/data/data/mn/weekly-meat-prices-ulaanbaatar.mdx`

## Chart

Multi-line time series. X is `date` (temporal), Y is `price` in MNT
(quantitative), color is `product` (5 series, legend on top).

## Notes

- Split dataset derived from parent `nso-weekly-prices-ulaanbaatar`
  (table DT_NSO_0600_001V4.px, 31 products)
- Related splits: `weekly-grocery-prices-ulaanbaatar`,
  `weekly-vegetable-prices-ulaanbaatar`, `weekly-fuel-prices-ulaanbaatar`
