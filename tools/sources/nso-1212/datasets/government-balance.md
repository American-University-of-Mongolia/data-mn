# Government Budget Balance

## Dataset Information

**ID**: `government-balance`
**Parent**: `nso-government-budget`
**Type**: Split Dataset
**Source**: NSO 1212.mn
**Table ID**: `DT_NSO_0800_001V1.px`

## Description

Mongolia's government budget balance (revenue minus expenditure) from 1991 to 2025. This split dataset extracts only the Balance indicator from the complete government budget table, showing fiscal surplus or deficit over time.

## Split Filter

```json
{
  "indicator": ["Balance"]
}
```

## Data Structure

### Source Table Dimensions
- **Indicator**: Revenue, Expenditure, Balance
- **Total**: Total (aggregate level)
- **Year**: 1921-2025

### Split Output
- **year**: 1991-2025
- **value**: Balance amount in million MNT (positive = surplus, negative = deficit)

## Data Characteristics

- **Temporal Coverage**: 1991-2025
- **Geographic Coverage**: National
- **Frequency**: Annual
- **Unit**: Million MNT

## Files Generated

### Chart Data
- `government-balance-en.csv`
- `government-balance-mn.csv`

### Download Data
- `government-balance-all-en.csv`
- `government-balance-all-mn.csv`
- `government-balance.xlsx`

### Visualizations
- `government-balance-en.json`
- `government-balance-mn.json`

### MDX Pages
- `en/government-balance.mdx`
- `mn/government-balance.mdx`

## Key Statistics

- **Year Range**: 1991-2025
- **Budget Deficit (2025)**: -1,231,538 million MNT
- **Historical Pattern**: Consistent deficits in most years

## Notes

- Negative values indicate budget deficit
- Positive values indicate budget surplus
- Values are nominal (not inflation-adjusted)

## Update Frequency

Annual updates from NSO

## Last Updated

2026-01-29
