# Dataset: Monthly Inflation in Ulaanbaatar (2020-2025)

## Identification

- **ID**: `cpi-monthly-ulaanbaatar`
- **Source**: `nso-1212`
- **Parent**: `nso-cpi-ulaanbaatar-mom`
- **Category**: Economy
- **Tags**: [mongolia, cpi, inflation, prices, ulaanbaatar, monthly]

## Source Reference

- **Parent Table ID**: `DT_NSO_0600_003V4.px`
- **Title**: CONSUMER PRICE INDEX IN THE CAPITAL, by groups, compared with previous month
- **URL**: https://data.1212.mn

## Title

- **EN**: Monthly Inflation in Ulaanbaatar, % (2020-2025)
- **MN**: Улаанбаатар хотын сарын инфляци, % (2020-2025)

## Description

Month-over-month consumer price index change in Ulaanbaatar city.
Улаанбаатар хотын хэрэглээний үнийн индексийн сар бүрийн өөрчлөлт.

## Split Filter

This dataset is created by filtering the parent dataset:

```json
{
  "reference_year": "2020=100",
  "group": "Overall index"
}
```

Reference year `2020=100` covers February 2020 to January 2025. The series is
frozen at the source: newer months are published under reference year `2023=100`
(see parent dataset `nso-cpi-ulaanbaatar-mom`).

## Transform

- Keep rows matching the split filter, drop rows with null values.
- Strip whitespace from group names.
- Chart CSV (`month,value` / `сар,утга`): monthly series sorted ascending.
- Download CSV (`-all-en` / `-all-mn`): same monthly series.
- XLSX: long form, sheet `Data`.

## Chart

Area chart with line and nearest-point hover. See
`data.mn/public/charts/cpi-monthly-ulaanbaatar-en.json` and `-mn.json`.
