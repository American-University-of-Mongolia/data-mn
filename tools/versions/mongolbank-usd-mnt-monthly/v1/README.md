# Version 1 - Initial Creation

## Metadata

- **Created**: 2026-03-04
- **Data Coverage**: 1993-01 to 2026-02 (398 months)
- **Source**: Bank of Mongolia (www.mongolbank.mn) monthly average API
- **Currency**: USD/MNT only

## Files Backed Up

| File | Description |
|------|-------------|
| `data-en.csv` | English CSV - 398 rows (Date, Rate (MNT)) |
| `data-mn.csv` | Mongolian CSV - 398 rows (Огноо, Ханш (₮)) |
| `data.xlsx` | Excel with EN and MN sheets (wide: months as rows, years as columns) |
| `chart-en.json` | Vega-Lite area chart (English) |
| `chart-mn.json` | Vega-Lite area chart (Mongolian) |

## Data Structure

### Long-form CSV
- **Columns**: Date (YYYY-MM), Rate (MNT)
- **Rows**: One per month, 1993-01 to 2026-02

## Key Statistics

- 1993-01: 150.00 MNT/USD
- 2000-01: 1,097.00 MNT/USD
- 2010-01: 1,442.00 MNT/USD
- 2020-01: 2,652.00 MNT/USD
- 2025-12: 3,549.18 MNT/USD
- 2026-02: 3,565.87 MNT/USD

## Aggregation Method

Monthly averages from MongolBank API.
The API endpoint `/currency-rate-movement/data/monthly` pre-aggregates daily closing rates to monthly averages.
No additional aggregation needed for this dataset.

## Source API

```
POST https://www.mongolbank.mn/{lang}/currency-rate-movement/data/monthly
Content-Type: application/json
Body: {}
```

Fetch script: `.claude/skills/datamn-source-mongolbank/fetch_exchange_rates.py --currencies USD`
