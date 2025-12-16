# Version 1 - Unemployment Rate National

## Version Information

- **Version**: 1
- **Created**: 2025-12-16
- **Source Updated**: 2025-09-29 (from NSO API)
- **Dataset ID**: unemployment-rate-national

## Data Coverage

- **Time Period**: 2009-2024
- **Frequency**: Annual
- **Rows**: 16 (one per year)
- **Columns**: 3 (Category, Year, value)

## Source Details

- **Source**: NSO 1212.mn API
- **Table ID**: DT_NSO_0400_049V1.px
- **Sector**: Labour, business
- **Subsector**: Decent work
- **API Path**: `/en/NSO/Labour, business/Decent work/DT_NSO_0400_049V1.px`

## Data Filter

This dataset uses the following filter from the parent table:
- **Category**: Total (code "0") - National level unemployment rate only

## Files in This Version

- `unemployment-rate-national-en.csv` - English version (262 bytes)
- `unemployment-rate-national-mn.csv` - Mongolian version (336 bytes)

## Key Statistics

- **First Year**: 2009
- **Last Year**: 2024
- **Lowest Rate**: 5.3% (2023)
- **Highest Rate**: 11.6% (2009)
- **Latest Rate**: 5.9% (2024)

## Notes

- This is version 1 - initial dataset creation
- Data shows declining unemployment trend from 11.6% (2009) to 5.9% (2024)
- Contains only the national total - parent table has breakdowns by sex, age, region, and disability status
- Could create additional split datasets for different demographic groups in the future
