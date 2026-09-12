# Dataset: Inbound Tourists to Mongolia, Annual Total (2006–2025)

## Identification

- **ID**: `tourism-arrivals-monthly`
- **Source**: `nso-1212`
- **Category**: Tourism
- **Tags**: [mongolia, tourism, inbound tourists, travel, visitors]

## Source Reference

- **Table ID**: `DT_NSO_1800_005V2.px`
- **Sector**: `Tourism`
- **Subsector**: `Inbound passengers`
- **Last Updated**: 2025-01-01

## Title

- **EN**: Inbound Tourists to Mongolia, Annual Total (2006–2025)
- **MN**: Монгол Улсад ирсэн гадаадын жуулчдын тоо (2006–2025)

## Description

Annual number of inbound foreign tourists arriving in Mongolia from 2006
to 2025, showing the COVID-19 impact and post-pandemic recovery.

## Variables

### Year (Он)
20 years: 2006-2025 (continuous, no gaps)

### Tourists (Жуулчид)
Number of inbound tourists. Range: 33,100 (2021) to 847,170 (2025).

## Update Instructions

Query the API for table `DT_NSO_1800_005V2.px` and compare `updated` field with registry.

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_1800_005V2.px --output ./output
```

Raw columns EN: `Geographical region, Purpose of visit, Year, value`.
Aggregate to the annual national total, rename to `year, tourists`, and
sort by year ascending.

## Files

- `data.mn/public/datasets/tourism-arrivals-monthly-en.csv`
- `data.mn/public/datasets/tourism-arrivals-monthly-mn.csv`
- `data.mn/public/datasets/tourism-arrivals-monthly.xlsx`
- `data.mn/public/charts/tourism-arrivals-monthly-en.json`
- `data.mn/public/charts/tourism-arrivals-monthly-mn.json`
- `data.mn/src/data/data/en/tourism-arrivals-monthly.mdx`
- `data.mn/src/data/data/mn/tourism-arrivals-monthly.mdx`

## Chart

Single-series area + line chart with nearest-point hover over the annual
tourist total.

## Notes

- 20 rows (2006-2025) per language
- Legacy ID contains "monthly" but the series is ANNUAL totals; do not
  rename without updating all references (CSV, charts, MDX, registry)
- Raw NSO fetch archived at
  `tools/versions/nso-inbound-passengers-by-region-purpose/v1/`; NSO has
  since revised some yearly totals, so a fresh fetch may differ slightly
  from the published series
- Related dataset `inbound-passengers-tourism` (same source table) covers
  tourism-purpose arrivals only (417,935 in 2025)
