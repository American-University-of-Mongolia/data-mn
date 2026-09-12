# Dataset: Weekly Fuel Prices in Ulaanbaatar (2021-2025)

## Identification

- **ID**: `weekly-fuel-prices-ulaanbaatar`
- **Source**: `nso-1212`
- **Category**: Prices & Inflation
- **Tags**: [mongolia, prices, fuel, gasoline, diesel, ulaanbaatar, weekly]

## Source Reference

- **Source Name**: National Statistics Office of Mongolia
- **URL**: https://data.1212.mn
- **Table ID**: `DT_NSO_0600_001V4.px`
- **Sector**: `Economy, environment`
- **Subsector**: `Consumer Price Index`
- **API Path**: `/en/NSO/Economy, environment/Consumer Price Index/DT_NSO_0600_001V4.px`

## Title

- **EN**: Weekly Fuel Prices in Ulaanbaatar (2021-2025)
- **MN**: Улаанбаатар дахь шатахууны долоо хоногийн үнэ (2021-2025)

## Description

Weekly price tracking for fuel in Ulaanbaatar, including petrol (A-80,
A-92) and diesel. A-92 petrol prices have risen from around 2,000 MNT/l
in 2021 to approximately 2,500 MNT/l in 2025. This dataset is a category
split of the parent `nso-weekly-prices-ulaanbaatar` table (31 products);
only the splits are published to data.mn.

## Variables

### Product (Бүтээгдэхүүн)
3 products:

| EN | MN | Weeks |
|----|----|-------|
| Petrol, A-80, l | Аи-80 автобензин, л | 266 of 287 |
| Petrol, A-92, l | Аи-92 автобензин, л | 287 |
| Diesel fuel, l | Дизелийн түлш, л | 287 |

Note: A-80 petrol has gaps (21 missing weeks) as it is being phased out.

### Date (Огноо)
287 weeks: 2021-01-06 to 2026-08-31, format `YYYY-MM-DD`.

### Price (Үнэ)
Weekly price in MNT per liter.

## File Shapes

- EN CSV columns: `product, date, price` — 840 data rows
- MN CSV columns: `бүтээгдэхүүн, огноо, үнэ` — 840 data rows
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

Filter to the 3 fuel products above, rename columns to
`product, date, price` (EN) and `бүтээгдэхүүн, огноо, үнэ` (MN),
and sort by product, date ascending.

Validate: all price values positive; dates valid weekly dates; EN/MN
row counts and totals must match.

## Files

- `data.mn/public/datasets/weekly-fuel-prices-ulaanbaatar-en.csv`
- `data.mn/public/datasets/weekly-fuel-prices-ulaanbaatar-mn.csv`
- `data.mn/public/datasets/weekly-fuel-prices-ulaanbaatar.xlsx`
- `data.mn/public/charts/weekly-fuel-prices-ulaanbaatar-en.json`
- `data.mn/public/charts/weekly-fuel-prices-ulaanbaatar-mn.json`
- `data.mn/src/data/data/en/weekly-fuel-prices-ulaanbaatar.mdx`
- `data.mn/src/data/data/mn/weekly-fuel-prices-ulaanbaatar.mdx`

## Chart

Multi-series line chart: x = date (weekly), y = price (MNT/l),
color = fuel type.

## Notes

- Published snapshot backfilled at
  `tools/versions/weekly-fuel-prices-ulaanbaatar/v1/`
- Parent definition: `tools/sources/nso-1212/datasets/weekly-prices-ulaanbaatar.md`
- Sibling splits: `weekly-bread-prices-ulaanbaatar`,
  `weekly-dairy-prices-ulaanbaatar`, `weekly-meat-prices-ulaanbaatar`,
  `weekly-grocery-prices-ulaanbaatar`, `weekly-vegetable-prices-ulaanbaatar`
