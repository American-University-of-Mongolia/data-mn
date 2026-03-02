# Dataset: Mongolia Poverty Rate (Split)

## Type: SPLIT DATASET

This is a **split dataset** - see the parent definition for full documentation.

## Parent Dataset

- **Parent ID**: `nso-poverty-indicators`
- **Source Table**: `DT_NSO_1900_007V1.px`

## Split Configuration

- **ID**: `poverty-rate-national`
- **Filter**: `{"Indicator": "Poverty Headcount", "Location": "National average"}`
- **Title EN**: Mongolia Poverty Rate (1995–2020)
- **Title MN**: Монгол Улсын ядуурлын түвшин (1995–2020)
- **Chart Type**: area

## Description

National poverty headcount rate as a percentage of the total population, derived from the NSO poverty indicators table. Data is available for survey years only (not every year), from 1995 to 2020.

## Key Statistics

- **1995**: 36.3%
- **2003**: 36.1% (peak)
- **2014**: 21.6% (lowest recorded)
- **2020**: 27.8%

## Survey Years

Data is not available annually. Survey years: 1995, 1998, 2003, 2008, 2009, 2010, 2011, 2012, 2014, 2016, 2018, 2020.

## CSV Columns

- `year` (EN) / `он` (MN): Survey year (integer)
- `poverty_rate` (EN) / `ядуурлын_түвшин` (MN): Poverty headcount rate as percentage of population

## Source

- **Sector**: Society, development
- **Subsector**: Poverty, inequality and minimum subsistence level
- **Table**: DT_NSO_1900_007V1.px
- **URL**: https://www.1212.mn
