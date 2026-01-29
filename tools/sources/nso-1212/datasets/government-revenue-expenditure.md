# Government Revenue and Expenditure

## Dataset Information

**ID**: `government-revenue-expenditure`
**Parent**: `nso-government-budget`
**Type**: Split Dataset
**Source**: NSO 1212.mn
**Table ID**: `DT_NSO_0800_001V1.px`

## Description

Mongolia's government revenue and expenditure from 1991 to 2025, showing the fiscal transition from Soviet-era economy to market economy. This split dataset extracts only Revenue and Expenditure indicators from the complete government budget table.

## Split Filter

```json
{
  "indicator": ["Revenue", "Expenditure"]
}
```

## Data Structure

### Source Table Dimensions
- **Indicator**: Revenue, Expenditure, Balance
- **Total**: Total (aggregate level)
- **Year**: 1921-2025

### Split Output
- **indicator**: Revenue, Expenditure
- **year**: 1921-2025 (chart shows 1991-2025)
- **value**: Amount in million MNT

## Data Characteristics

- **Temporal Coverage**: 1921-2025 (complete), 1991-2025 (chart)
- **Geographic Coverage**: National
- **Frequency**: Annual
- **Unit**: Million MNT (not adjusted for inflation)

## Files Generated

### Chart Data (1991-2025)
- `government-revenue-expenditure-en.csv` (70 rows)
- `government-revenue-expenditure-mn.csv` (70 rows)

### Download Data (1921-2025)
- `government-revenue-expenditure-all-en.csv` (210 rows)
- `government-revenue-expenditure-all-mn.csv` (210 rows)
- `government-revenue-expenditure.xlsx` (wide format)

### Visualizations
- `government-revenue-expenditure-en.json` (multi-line chart)
- `government-revenue-expenditure-mn.json` (multi-line chart)

### MDX Pages
- `en/government-revenue-expenditure.mdx`
- `mn/government-revenue-expenditure.mdx`

## Key Statistics

- **Year Range**: 1921-2025 (105 years)
- **Chart Range**: 1991-2025 (35 years, post-Soviet transition)
- **Revenue (2025)**: 30,057,666 million MNT
- **Expenditure (2025)**: 31,289,204 million MNT
- **Revenue Growth**: From 7.2 billion (1991) to 30 trillion (2025)
- **Expenditure Growth**: From 8.9 billion (1991) to 31 trillion (2025)

## Chart Design

**Type**: Multi-series line chart with hover tooltips

**Colors**:
- Revenue: `#4c78a8` (primary blue)
- Expenditure: `#f58518` (secondary orange)

**Features**:
- Layered structure for nearest-point hover
- Smooth monotone interpolation
- Legend at top
- Format: Million MNT with comma separators

## Notes

- Chart data filtered to 1991-2025 to focus on post-Soviet era
- Download files include complete historical data from 1921
- Values are nominal (not inflation-adjusted)
- Data shows consistent budget deficits (expenditure > revenue) in most years
- Dramatic growth reflects both economic expansion and inflation

## Update Frequency

Annual updates from NSO (typically released with lag)

## Last Updated

2026-01-29
