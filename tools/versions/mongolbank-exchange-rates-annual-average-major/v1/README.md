# Version 1 - Initial Creation

## Metadata

- **Created**: 2026-03-04
- **Data Coverage**: 1993 to 2026 (partial)
- **Source**: Bank of Mongolia (www.mongolbank.mn) monthly average API
- **Currencies**: USD, EUR, CNY, RUB, JPY, KRW

## Files Backed Up

| File | Description |
|------|-------------|
| `data-en.csv` | English long-form CSV - 193 rows (6 currencies × 34 years, less where unavailable) |
| `data-mn.csv` | Mongolian long-form CSV - 193 rows |
| `data.xlsx` | Excel with EN and MN sheets (wide format, years as rows) |
| `chart-en.json` | Vega-Lite chart specification (English) |
| `chart-mn.json` | Vega-Lite chart specification (Mongolian) |

## Data Structure

### Long-form CSV (EN)
- **Columns**: Currency, Year, Rate (MNT)
- **Currencies**: US Dollar, Euro, Chinese Yuan, Russian Ruble, Japanese Yen, South Korean Won
- **Note**: Euro starts 1999; some currencies have data gaps in early years

### Wide-form XLSX
- **Rows**: One per year (1993-2026)
- **Columns**: Year, USD, EUR, CNY, RUB, JPY, KRW

## Key Statistics (2025 Annual Average)

- USD: 3,545.14 MNT
- EUR: 3,939.04 MNT
- CNY: 492.09 MNT
- RUB: 44.79 MNT
- JPY: 23.07 MNT
- KRW: 2.54 MNT

## Aggregation Method

Monthly averages from MongolBank API → arithmetic mean per calendar year.
2026 value covers Jan-Feb 2026 only (partial year).

## Source API

```
POST https://www.mongolbank.mn/{lang}/currency-rate-movement/data/monthly
Content-Type: application/json
Body: {}
```

Response: Array of monthly records with RATE_DATE and currency fields.
