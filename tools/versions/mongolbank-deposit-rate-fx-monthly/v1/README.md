# Version 1 - Initial Creation

## Metadata

- **Created**: 2026-03-04
- **Data Coverage**: 2008-12 to 2026-01 (190 months)
- **Source**: stat.mongolbank.mn — Report 142 (Deposits interest rate), Indicator 84992
- **Series**: FX deposit weighted average rate (outstanding)

## Source Details

- **API**: `POST https://stat.mongolbank.mn/api/indicator/data?lang=en`
- **Report ID**: 142 (parentId: 140, "Deposits interest rate")
- **Indicator ID**: 84992 ("DEPOSIT WEIGHTED AVERAGE RATES (outstanding) (foreign currency)")
- **MN Name**: "Нийт хадгаламжийн үлдэгдэлд жигнэж тооцсон хүү (валют)"
- **Latest value**: 2026-01 → 4.22%

## FX Series Availability Decision

**Decision**: FX split IS available and reliable.

The stat.mongolbank.mn API (report 142, indicator 84992) provides a dedicated monthly series for weighted average FX deposit rates on outstanding balances, starting December 2008. Data is continuous with no gaps from 2012 onward. Early months (2009-01 through 2009-09) show zero values and were excluded.

No fallback needed.

## Files Backed Up

| File | Description |
|------|-------------|
| `data-en.csv` | English CSV - 190 rows (Date, Rate (%)) |
| `data-mn.csv` | Mongolian CSV - 190 rows (Огноо, Хүү (%)) |
| `data.xlsx` | Excel with EN/MN sheets (wide: months as rows, years as columns) |
| `chart-en.json` | Vega-Lite area chart (English) |
| `chart-mn.json` | Vega-Lite area chart (Mongolian) |

## Key Statistics

- 2008-12: 7.40%
- 2015-01: 5.40%
- 2020-01: 4.41%
- 2023-01: 3.89%
- 2025-12: 4.19%
- 2026-01: 4.22%
