# Version 1 - Youth Unemployment Rate (15-24)

## Version Information

- **Dataset ID**: unemployment-rate-youth
- **Parent Dataset**: nso-unemployment-rate
- **Version**: 1
- **Created**: 2024-12-16
- **Source**: NSO 1212.mn
- **Table ID**: DT_NSO_0400_049V1.px

## Split Filter

```json
{
  "Category": "15-24"
}
```

## Data Description

Youth unemployment rate (ages 15-24) in Mongolia from 2009 to 2024. This is a filtered subset from the parent unemployment rate dataset that includes multiple demographic and geographic dimensions.

## Files

- `data-en.csv` - English language version
- `data-mn.csv` - Mongolian language version

## Data Structure

### Columns
- `category`: Age group (15-24)
- `year`: Year (2009-2024)
- `value`: Unemployment rate as percentage

### Statistics
- **Years covered**: 2009-2024 (16 years)
- **Latest value**: 14.7% (2024)
- **Historical range**: 4.7% (2023, minimum) to 25.1% (2016, maximum)

## Notes

- Data shows significant year-to-year variation
- Youth unemployment consistently higher than overall national rate
- Recent trend shows decline from peak in 2016
- 2023 shows unusually low rate (4.7%) - may be data anomaly or significant labor market change
