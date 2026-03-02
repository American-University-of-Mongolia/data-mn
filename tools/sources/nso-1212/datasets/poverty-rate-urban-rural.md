# Dataset: Mongolia Poverty Rate by Location (Split)

## Type: SPLIT DATASET

This is a **split dataset** — see the parent definition for full documentation.

## Parent Dataset

- **Parent ID**: `nso-poverty-indicators`
- **Source Table**: `DT_NSO_1900_007V1.px`

## Split Configuration

- **ID**: `poverty-rate-urban-rural`
- **Filter**: `{"Indicator": "Poverty Headcount", "Location": ["Urban", "Rural"]}`
- **Title EN**: Mongolia Poverty Rate by Location (1995–2020)
- **Title MN**: Монгол Улсын ядуурлын түвшин байршлаар (1995–2020)
- **Chart Type**: multi-line

## Description

Poverty headcount rate comparing urban and rural populations in Mongolia from 1995 to 2020. Data is drawn from NSO household surveys (not annual — survey years only).

## Key Statistics (2020)

- Urban: 26.5%
- Rural: 30.5%

## Survey Years

1995, 1998, 2003, 2008, 2009, 2010, 2011, 2012, 2014, 2016, 2018, 2020

## CSV Columns

- `year` (EN) / `он` (MN): Survey year (integer)
- `location` (EN) / `байршил` (MN): Location type ("Urban"/"Rural" in EN, "Хот"/"Хөдөө" in MN)
- `poverty_rate` (EN) / `ядуурлын_түвшин` (MN): Poverty headcount rate as percentage of population

## Source

- **Sector**: Society, development
- **Subsector**: Poverty, inequality and minimum subsistence level
- **Table**: DT_NSO_1900_007V1.px
- **URL**: https://www.1212.mn
