# Dataset: Poverty Main Indicators by Location

## Identification

- **ID**: `nso-poverty-indicators`
- **Source**: `nso-1212`
- **Category**: Society
- **Tags**: [poverty, inequality, headcount, gap, severity, society, mongolia]

## Source Reference

- **Table ID**: `DT_NSO_1900_007V1.px`
- **Sector**: `Society, development`
- **Subsector**: `Poverty, inequality and minimum subsistence level`
- **API Path**: `/en/NSO/Society, development/Poverty, inequality and minimum subsistence level/DT_NSO_1900_007V1.px`

## Title

- **EN**: Poverty Main Indicators by Location (1995–2020)
- **MN**: Ядуурлын үндсэн үзүүлэлт байршлаар (1995–2020)

## Description

Multi-dimensional poverty data from the National Statistics Office of Mongolia covering poverty headcount, poverty gap, and poverty severity for various location types (national, urban, rural, regions) from 1995 to 2020. Data is collected every 2-5 years through household surveys.

## Variables

### Indicator (Үзүүлэлт)

- `Poverty Headcount`: Share of population living below the poverty line (%)
- `Poverty Gap`: Average shortfall of poor people's consumption from the poverty line (%)
- `Poverty Severity`: Accounts for inequality among the poor (%)

### Location (Суурьшил)

- `National average`: Country-wide aggregate
- `Urban`: All urban areas combined
- `Rural`: All rural areas combined
- `Western region`: Bayan-Olgii, Govi-Altai, Zavkhan, Uvs, Khovd aimags
- `Khangai region`: Arkhangai, Bayankhongor, Bulgan, Orkhon, Ovorkhangai, Khuvsgul aimags
- `Central region`: Govisumber, Darkhan-Uul, Dundgovi, Selenge, Tov aimags
- `Eastern region`: Dornod, Sukhbaatar, Khentii aimags
- `Ulaanbaatar`: Capital city total
- `Capital city`: Ulaanbaatar city
- `Aimag center`: Aimag capital towns
- `Soum center`: Soum (county) center towns
- `Rural area`: Countryside / bag level

### Year (Он)

Survey years: 1995, 1998, 2003, 2008, 2009, 2010, 2011, 2012, 2014, 2016, 2018, 2020 (12 data points)

## Data Summary

- **Row count**: 432 (3 indicators × 12 locations × 12 years)
- **Columns**: Indicator, Location, Year, value
- **MN columns**: Үзүүлэлт, Суурьшил, Он, value
- **Value range**: Varies by indicator (headcount highest, severity lowest)

## Update Instructions

### Check for Updates

1. Query the table listing endpoint:
   ```
   GET https://data.1212.mn/api/v1/en/NSO/Society, development/Poverty, inequality and minimum subsistence level/
   ```

2. Find `DT_NSO_1900_007V1.px` in the response

3. Compare the `updated` field with `source_updated_at` in registry

4. If API's `updated` is newer, dataset needs updating

### Fetch Data

Use the `datamn-source-nso` skill for bilingual data fetching:

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_1900_007V1.px --output ./output
```

### Validation

- All indicator values should be positive percentages (0-100)
- Poverty Headcount values should be higher than Poverty Gap
- Poverty Gap values should be higher than Poverty Severity
- National average should fall between urban and rural values
- Year values should be valid survey years (1995-2020)

## Splits

This multi-dimensional dataset is split into the following user-friendly datasets:

### 1. poverty-headcount-by-location

- **ID**: `poverty-headcount-by-location`
- **Title EN**: Poverty Headcount Rate by Location, % (1995–2020)
- **Title MN**: Ядуурлын хамралтын хүрээ байршлаар, % (1995–2020)
- **Filter**:
  - Indicator: Poverty Headcount
- **Chart Type**: multi-line
- **Chart Config**:
  - X-axis: year (quantitative)
  - Y-axis: value (%)
  - Color: location (national, urban, rural, Ulaanbaatar)
- **Description EN**: Share of Mongolia's population living below the poverty line by location type from 1995 to 2020.
- **Description MN**: 1995–2020 онд Монгол Улсын байршлаар ядуурлын шугамаас доогуур амьдарч буй хүн амын хувь.

### 2. poverty-gap-by-location

- **ID**: `poverty-gap-by-location`
- **Title EN**: Poverty Gap by Location, % (1995–2020)
- **Title MN**: Ядуурлын гүнзгийрэлт байршлаар, % (1995–2020)
- **Filter**:
  - Indicator: Poverty Gap
- **Chart Type**: multi-line
- **Chart Config**:
  - X-axis: year (quantitative)
  - Y-axis: value (%)
  - Color: location (national, urban, rural, Ulaanbaatar)
- **Description EN**: Average gap between poor people's consumption and the poverty line, by location type, from 1995 to 2020.
- **Description MN**: 1995–2020 онд байршлаар ядуу хүмүүсийн хэрэглээний ядуурлын шугамаас зөрүүний дундаж хувь.

### 3. poverty-severity-by-location

- **ID**: `poverty-severity-by-location`
- **Title EN**: Poverty Severity by Location, % (1995–2020)
- **Title MN**: Ядуурлын мэдрэмж байршлаар, % (1995–2020)
- **Filter**:
  - Indicator: Poverty Severity
- **Chart Type**: multi-line
- **Chart Config**:
  - X-axis: year (quantitative)
  - Y-axis: value (%)
  - Color: location (national, urban, rural, Ulaanbaatar)
- **Description EN**: Poverty severity index accounting for inequality among the poor, by location type, from 1995 to 2020.
- **Description MN**: 1995–2020 онд байршлаар ядуу хүмүүсийн тэгш бус байдлыг тооцсон ядуурлын мэдрэмжийн индекс.

### 4. poverty-headcount-national

- **ID**: `poverty-headcount-national`
- **Title EN**: Mongolia National Poverty Headcount Rate, % (1995–2020)
- **Title MN**: Монгол Улсын үндэсний ядуурлын хамралтын хүрээ, % (1995–2020)
- **Filter**:
  - Indicator: Poverty Headcount
  - Location: National average
- **Chart Type**: area
- **Chart Config**:
  - X-axis: year (quantitative)
  - Y-axis: value (%)
  - Color: #4c78a8 (blue)
- **Description EN**: Share of Mongolia's total population living below the poverty line from 1995 to 2020.
- **Description MN**: 1995–2020 онд Монгол Улсын нийт хүн амын ядуурлын шугамаас доогуур амьдарч буй хүн амын хувь.

## Content Generation

### Common Tags

- mongolia
- poverty
- inequality
- headcount
- society
- nso
- location

### Key Findings

- National poverty headcount peaked at 38.8% in 2010
- Poverty declined from 38.8% (2010) to 27.8% (2020)
- Rural poverty consistently higher than urban poverty
- Western region typically shows highest poverty rates

## Notes

- Survey years are not consecutive — data collected every 2-5 years via household surveys
- Location categories overlap (e.g., Ulaanbaatar is a subset of Urban)
- Values are percentages (not ratios); e.g., 27.8 means 27.8%
- **Parent dataset**: This dataset (`nso-poverty-indicators`) stores the raw data; only the splits are published to data.mn
