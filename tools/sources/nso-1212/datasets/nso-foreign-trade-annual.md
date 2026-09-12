# Dataset: Mongolia Foreign Trade, Million USD (1924–2025)

## Identification

- **ID**: `nso-foreign-trade-annual`
- **Source**: `nso-1212`
- **Category**: Trade
- **Tags**: [mongolia, foreign trade, exports, imports, trade balance, annual]

## Source Reference

- **Source Name**: National Statistics Office of Mongolia
- **URL**: https://www.1212.mn
- **Table ID**: `DT_NSO_1400_001V1_year.px`
- **Sector**: `Foreign Trade`
- **Subsector**: `Foreign trade`

## Title

- **EN**: Mongolia Foreign Trade, Million USD (1924–2025)
- **MN**: Монгол Улсын гадаад худалдаа, сая ам.дол (1924–2025)

## Description

Annual foreign trade statistics for Mongolia from 1924 to 2025, covering
total turnover, exports, imports, and trade balance in million USD.
Mongolia's foreign trade grew from near-zero pre-transition volumes to
over $20 billion in annual turnover by the 2010s, driven by mineral
exports — primarily coal and copper. The trade balance turned positive
in the 2000s as commodity export revenues surged. Data covers the full
historical series from 1924, though systematic recording became
consistent from 1990 onward.

## Variables

### Indicator (Үзүүлэлт)
4 indicators, 102 years each:

| EN | MN |
|----|----|
| Total turnover | Нийт эргэлт |
| Exports | Экспорт |
| Imports | Импорт |
| Balance | Тэнцэл |

### Year (Он)
102 years: 1924-2025 (continuous, no gaps)

### Value (Үнэ)
Trade value in million USD. Balance may be negative; turnover, exports
and imports should be positive.

## File Shapes

- EN CSV columns: `indicator, year, value_usd_mn` — 408 data rows
- MN CSV columns: `үзүүлэлт, он, үнэ_сая_ам_доллар` — 408 data rows
- XLSX: bilingual workbook (EN + MN sheets)

## Update Instructions

Query the API for table `DT_NSO_1400_001V1_year.px` and compare `updated`
field with registry.

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_1400_001V1_year.px --output ./output
```

Keep all four indicators, rename columns to
`indicator, year, value_usd_mn` (EN) and
`үзүүлэлт, он, үнэ_сая_ам_доллар` (MN), strip whitespace from string
columns, and sort by indicator, year ascending.

Validate: total turnover should equal Exports + Imports per year;
Balance should equal Exports − Imports per year; EN/MN row counts and
totals must match.

## Files

- `data.mn/public/datasets/nso-foreign-trade-annual-en.csv`
- `data.mn/public/datasets/nso-foreign-trade-annual-mn.csv`
- `data.mn/public/datasets/nso-foreign-trade-annual.xlsx`
- `data.mn/public/charts/nso-foreign-trade-annual-en.json`
- `data.mn/public/charts/nso-foreign-trade-annual-mn.json`
- `data.mn/src/data/data/en/nso-foreign-trade-annual.mdx`
- `data.mn/src/data/data/mn/nso-foreign-trade-annual.mdx`

## Chart

Multi-series line chart: x = year, y = value in million USD,
color = indicator (Total turnover, Exports, Imports, Balance).

## Notes

- Published snapshot backfilled at `tools/versions/nso-foreign-trade-annual/v1/`
- Values are in million USD, FOB basis
- Related dataset `nso-foreign-trade-monthly` (table
  DT_NSO_1400_003V1.px) covers monthly trade from 1997
