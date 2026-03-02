# Version 1 - Initial Creation

## Metadata

- **Created**: 2025-02-10
- **Data Coverage (split)**: 2016-03 to 2026-01
- **Data Coverage (all)**: 2008-12 to 2026-01
- **Source**: Bank of Mongolia (stat.mongolbank.mn)
- **Reports**: report-142 (Deposit rates), report-172 (Loan rates)

## Files Backed Up

| File | Description |
|------|-------------|
| `data-en.csv` | English split CSV - 357 rows (3 rates × 119 months) |
| `data-mn.csv` | Mongolian split CSV - 357 rows |
| `data-all-en.csv` | English full CSV - 531 rows |
| `data-all-mn.csv` | Mongolian full CSV - 531 rows |
| `data.xlsx` | Excel with EN/MN sheets (wide format) |
| `chart-en.json` | Vega-Lite chart specification (English) |
| `chart-mn.json` | Vega-Lite chart specification (Mongolian) |

## Data Structure

### Split CSV
- **Columns**: Rate Type, Date, Rate (%) / Хүүгийн төрөл, Огноо, Хүү (%)
- **Rate Types**: Lending Rate (MNT), Deposit Rate (MNT), Deposit Rate (FX)
- **Time Range**: March 2016 - January 2026 (119 months)
- **Total Rows**: 357 (3 × 119)

### All CSV
- **Rate Types**: Deposit Rate (MNT, outstanding), Deposit Rate (FX, outstanding), Lending Rate (MNT, newly issued)
- **Time Range**: December 2008 - January 2026
- **Total Rows**: 531

## Key Statistics (January 2026)

- Lending Rate (MNT): 16.83%
- Deposit Rate (MNT): 12.02%
- Deposit Rate (FX): 4.22%
- Lending-Deposit Spread: ~4.8pp
