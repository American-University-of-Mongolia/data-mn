# GDP in US Dollars - Version 1

## Version Information

- **Version**: 1
- **Created**: 2025-12-03
- **Source**: NSO 1212.mn (DT_NSO_0500_001V1.px)
- **Parent Dataset**: nso-gdp-by-economic-activity
- **Data Period**: 1990-2024 (35 years)
- **Source Updated**: 2025-09-17T10:10:46

## Files

- `data-en.csv` - English CSV (year, value) - 576 bytes
- `data-mn.csv` - Mongolian CSV (он, утга) - 615 bytes
- `data.xlsx` - Excel format (wide layout) - 6.6 KB
- `chart-en.json` - English Vega-Lite chart specification - 2.3 KB
- `chart-mn.json` - Mongolian Vega-Lite chart specification - 2.3 KB

## Dataset Description

Mongolia's GDP in US dollars (thousands), converted from MNT at current exchange rates. This is a split dataset filtered from the parent multi-dimensional GDP table.

### Split Filter
```json
{
  "Indicator": "GDP, at current price, thousand USD",
  "Economic activity": "Total"
}
```

## Key Statistics

- **First Year**: 1990 (3,317,079.87 thousand USD)
- **Last Year**: 2024 (23,793,357.51 thousand USD)
- **Total Observations**: 35
- **Minimum Value**: 746,336.47 thousand USD (1993 - transition crisis)
- **Maximum Value**: 23,793,357.51 thousand USD (2024 - record high)
- **Growth (1990-2024)**: 7.2x increase in USD terms

## Historical Context

- **1990-1993**: Economic transition period with sharp decline
- **1994-2000**: Recovery phase
- **2000-2011**: Commodity boom years (rapid growth)
- **2012-2015**: Slowdown period
- **2020**: COVID-19 impact (slight decline)
- **2021-2024**: Strong recovery and growth to record levels

## Data Quality Notes

- All values are positive (as expected for GDP)
- No missing years in sequence
- Values show realistic year-over-year changes
- 1990s volatility reflects both economic transition and exchange rate instability
- Recent growth trajectory is consistent with commodity prices and economic expansion

## Validation Status

- ✓ All years present (1990-2024)
- ✓ All values positive
- ✓ No unrealistic jumps
- ✓ Bilingual CSV files match in structure
- ✓ Chart specifications validated

## Update Notes

This version was created as part of the initial dataset definition and version directory setup. Future updates will occur automatically when the parent dataset (`nso-gdp-by-economic-activity`) is refreshed from the NSO API.
