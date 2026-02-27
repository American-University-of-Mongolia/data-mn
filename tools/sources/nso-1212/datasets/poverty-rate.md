# Poverty Rate

## Source Table
- **Table ID**: DT_NSO_1900_007V1.px (1995-2020) + DT_NSO_1900_007V12.px (2022)
- **Sector**: Society, development
- **Subsector**: Poverty, inequality and minimum subsistence level

## Variables
- **Indicator** (3 values): Poverty Headcount, Poverty Gap, Poverty Severity
- **Location** (12 values): National average, Urban, Rural, Western region, Khangai region, Central region, Eastern region, Ulaanbaatar, Capital city, Aimag center, Soum center, Rural area
- **Year** (13 values): 1995, 1998, 2003, 2008, 2009, 2010, 2011, 2012, 2014, 2016, 2018, 2020, 2022

## Notes
- "Capital city" and "Ulaanbaatar" have identical values; "Capital city" is excluded from output
- Values are percentages (%)
- Regional data (Western, Khangai, Central, Eastern) not available before 2003
- Data collected from Household Socio-Economic Survey (HSES)

## Split Filter
- **poverty-rate**: Indicator = "Poverty Headcount", Location in [National average, Urban, Rural]

## Update Instructions
1. Check both V1 and V12 tables for updates
2. Fetch EN data from both tables
3. Combine and rebuild CSVs using single EN source with order index
4. Regenerate XLSX in wide format
