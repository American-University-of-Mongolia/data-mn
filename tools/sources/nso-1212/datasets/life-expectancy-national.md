# Life Expectancy at Birth - National (Total)

## Dataset Information

**ID**: `life-expectancy-national`
**Parent**: `nso-life-expectancy`
**Type**: Split Dataset
**Source**: NSO 1212.mn
**Table ID**: `DT_NSO_0300_039V1.px`

## Description

Mongolia's life expectancy at birth for the total population from 1992 to 2024. Life expectancy rose steadily from 62.8 years in 1992 to 71.8 years in 2024, reflecting improvements in public health, healthcare access, and living conditions.

## Split Filter

```json
{"Sex": "Total"}
```

## Data Structure

### Output
- **year**: 1992-2024 (with some gaps for years not reported by NSO)
- **life_expectancy_years**: Life expectancy at birth in years

## Data Characteristics

- **Temporal Coverage**: 1992-2024
- **Geographic Coverage**: National
- **Frequency**: Annual
- **Unit**: Years

## Files Generated

### Chart Data
- `life-expectancy-national-en.csv`
- `life-expectancy-national-mn.csv`

### Download Data
- `life-expectancy-national.xlsx`

### Visualizations
- `life-expectancy-national-en.json`
- `life-expectancy-national-mn.json`

### MDX Pages
- `en/life-expectancy-national.mdx`
- `mn/life-expectancy-national.mdx`

## Key Statistics

- **Year Range**: 1992-2024
- **1992 Value**: 62.8 years
- **2024 Value**: 71.8 years
- **Trend**: Consistent increase over the period

## Notes

- Life expectancy at birth is a key composite indicator of population health
- Data for some years (e.g., 1993, 1994, 1996, 1999) are not available in the NSO series
- Parent dataset `nso-life-expectancy` contains breakdowns by sex (Male, Female, Total)

## Update Frequency

Annual updates from NSO

## Last Updated

2026-02-26
