# NSO Birth Rates by Age - Version History

## Dataset Type: PARENT

This is a **parent dataset** containing raw multi-dimensional data from NSO 1212.mn.

## Source

- **Table ID**: `DT_NSO_0300_029V1.px`
- **Title**: Birth Rates by Year
- **Sector**: Population, household / Education, health
- **Subsector**: Regular movement of population / Births, deaths
- **API URL**: `https://data.1212.mn/api/v1/{lang}/NSO/Population, household/2_Regular movement of population/DT_NSO_0300_029V1.px`

## Data Structure

- **Dimensions**: Age Group (10 values) x Year (37 values)
- **Total Records**: 370 rows
- **Time Range**: 1980-2024
- **Age Groups**: CBR, GFR, TFR, 15-19, 20-24, 25-29, 30-34, 35-39, 40-44, 45-49

## Split Datasets

This parent dataset produces the following user-friendly splits:

| Split ID | Title | Filter |
|----------|-------|--------|
| `birth-rate-crude` | Mongolia Crude Birth Rate | age_group = "CBR" |
| `fertility-rate-total` | Mongolia Total Fertility Rate | age_group = "TFR" |
| `birth-rate-by-age` | Age-Specific Birth Rates | age_group in [15-19, 20-24, 25-29, 30-34, 35-39, 40-44, 45-49] |
| `birth-rate-heatmap` | Birth Rates Heatmap | age_group in [15-19, 20-24, 25-29, 30-34, 35-39, 40-44, 45-49] |

## Version History

### v1 (Initial)
- **Created**: 2026-01-19
- **Source Updated**: 2025-09-16 (per NSO API metadata)
- **Records**: 370 rows (10 age groups x 37 years)
- **Files**:
  - `nso-0300-029v1-en.csv` - English version
  - `nso-0300-029v1-mn.csv` - Mongolian version

## Update Process

To update this dataset:

1. Check for updates:
   ```bash
   cd .claude/skills/datamn-source-nso
   python3 query_api.py --detailed 0300_029V1
   ```

2. If updated, fetch new data:
   ```bash
   python3 fetch_data.py --table DT_NSO_0300_029V1.px --output ./output
   ```

3. Create new version directory (v2, v3, etc.)

4. Regenerate all split datasets

## Notes

- Early years (1980, 1985, 1990) have 5-year intervals
- Annual data available from 1991 onwards
- CBR = Crude Birth Rate (per 1,000 population)
- TFR = Total Fertility Rate (children per woman)
- GFR = General Fertility Rate (per 1,000 women aged 15-49)
- Age-specific rates are per 1,000 women in each age group
