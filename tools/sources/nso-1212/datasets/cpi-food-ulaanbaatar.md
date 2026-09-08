# Dataset: Food Price Changes in Ulaanbaatar (2020-2025)

## Identification

- **ID**: `cpi-food-ulaanbaatar`
- **Source**: `nso-1212`
- **Parent**: `nso-cpi-ulaanbaatar-mom`
- **Category**: Economy
- **Tags**: [mongolia, cpi, inflation, food, prices, ulaanbaatar, monthly]

## Source Reference

- **Parent Table ID**: `DT_NSO_0600_003V4.px`
- **Title**: CONSUMER PRICE INDEX IN THE CAPITAL, by groups, compared with previous month
- **URL**: https://data.1212.mn

## Title

- **EN**: Food Price Changes in Ulaanbaatar, % MoM (2020-2025)
- **MN**: Улаанбаатар хотын хүнсний үнийн өөрчлөлт, % сар тутамд (2020-2025)

## Description

Month-over-month food price changes in Ulaanbaatar city.
Улаанбаатар хотын хүнсний үнийн сар бүрийн өөрчлөлт.

## Split Filter

This dataset is created by filtering the parent dataset:

```json
{
  "reference_year": "2020=100",
  "group": " Food and non-alcaholic beverages"
}
```

The group name is stored verbatim as published by the NSO API, including the
leading space and the source spelling `non-alcaholic`. Strip whitespace before
matching. Reference year `2020=100` covers February 2020 to January 2025. The
series is frozen at the source: newer months are published under reference
year `2023=100` (see parent dataset `nso-cpi-ulaanbaatar-mom`).

## Transform

- Keep rows matching the split filter, drop rows with null values.
- Strip whitespace from group names.
- Chart CSV (`month,value` / `сар,утга`): monthly series sorted ascending.
- XLSX: long form, sheet `Data`.

## Chart

Area chart with line and nearest-point hover. See
`data.mn/public/charts/cpi-food-ulaanbaatar-en.json` and `-mn.json`.
