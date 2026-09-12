# Dataset: Wheat Bran Prices by Region in Mongolia (2018-2025)

## Identification

- **ID**: `wheat-bran-prices`
- **Source**: `nso-1212`
- **Category**: Agriculture
- **Tags**: [mongolia, agriculture, wheat bran, animal feed, livestock, regional prices]

## Source Reference

- **Source Name**: National Statistics Office of Mongolia
- **URL**: https://data.1212.mn
- **Table ID**: `DT_NSO_1002_001V4.px`
- **Sector**: verify sector/subsector on data.1212.mn for table DT_NSO_1002_001V4.px
- **Subsector**: verify sector/subsector on data.1212.mn for table DT_NSO_1002_001V4.px

## Title

- **EN**: Wheat Bran Prices by Region in Mongolia (2018-2025)
- **MN**: Хивэгний үнэ аймгаар, Монгол улс (2018-2025)

## Description

Monthly wheat bran prices (25kg and 50kg bags) across 22 regions of
Mongolia (21 aimags plus Ulaanbaatar). Wheat bran (хивэг) is a key
animal feed supplement used by livestock farmers throughout Mongolia.
Regional price comparison helps farmers optimize feed sourcing decisions.

Note: the published CSV coverage starts 2020-01 (71 months to 2025-12),
narrower than the 2018 start in the title — verify against the source
table whether 2018-2019 regional data exists.

## Variables

### Date (Огноо)
71 months: 2020-01 to 2025-12, format `YYYY-MM`.

### Product × Region (Бүтээгдэхүүн × Бүс)
44 series = 2 bag sizes × 22 regions, joined as
`"<product> — <region>"`:

- Sizes: `Wheat bran, 25kg` / `Хивэг,25кг`,
  `Wheat bran, 50kg` / `Хивэг,50кг`
- Regions: Arkhangai, Bayan-Ulgii, Bayankhongor, Bulgan, Darkhan-Uul,
  Dornod, Dornogovi, Dundgovi, Govi-Altai, Govisumber, Khentii, Khovd,
  Khuvsgul, Orkhon, Selenge, Sukhbaatar, Tuv, Ulaanbaatar, Umnugovi,
  Uvs, Uvurkhangai, Zavkhan

### Price (Үнэ)
Monthly average market price in MNT per bag (verify unit against the
NSO table metadata).

## File Shapes

- EN CSV columns: `date, product_region, price` — 1820 data rows
- MN CSV columns: `огноо, бүтээгдэхүүн_бүс, үнэ` — 1820 data rows
- XLSX: bilingual workbook (EN + MN sheets)

## Update Instructions

Query the API for table `DT_NSO_1002_001V4.px` and compare `updated`
field with registry.

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_1002_001V4.px --output ./output
```

Filter to wheat bran products by region, build the combined
`product_region` label (`"<product> — <region>"`), rename columns to
`date, product_region, price` (EN) and
`огноо, бүтээгдэхүүн_бүс, үнэ` (MN), and sort by date,
product_region ascending.

## Files

- `data.mn/public/datasets/wheat-bran-prices-en.csv`
- `data.mn/public/datasets/wheat-bran-prices-mn.csv`
- `data.mn/public/datasets/wheat-bran-prices.xlsx`
- `data.mn/public/charts/wheat-bran-prices-en.json`
- `data.mn/public/charts/wheat-bran-prices-mn.json`
- `data.mn/src/data/data/en/wheat-bran-prices.mdx`
- `data.mn/src/data/data/mn/wheat-bran-prices.mdx`

## Chart

Multi-series line chart: x = date (monthly), y = price (MNT),
color = product × region series.

## Notes

- Published snapshot backfilled at `tools/versions/wheat-bran-prices/v1/`
- Related dataset `crop-prices-national` (same NSO table
  DT_NSO_1002_001V4.px) covers Tuv-province crop product prices
