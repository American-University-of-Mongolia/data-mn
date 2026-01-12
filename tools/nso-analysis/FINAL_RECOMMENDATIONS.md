# NSO Catalog Analysis: Final Recommendations

**Generated:** 2025-12-16
**Methodology:** 7 parallel AI agents analyzed 262 T1+T2 tables by sector
**Target Audience:** 80% utility for business people, students, professionals

---

## Executive Summary

| Metric | Before | After | Reduction |
|--------|--------|-------|-----------|
| **T1+T2 Tables** | 262 | ~110 | **58%** |
| **Total NSO Catalog** | 1,136 | ~110 | **90%** |

### Sector-by-Sector Results

| Sector | Input | Keep | Skip | Keep Rate |
|--------|-------|------|------|-----------|
| Economy & Environment | 95 | 23 | 72 | 24% |
| Labour & Business | 42 | 18 | 24 | 43% |
| Regional Development | 36 | 18 | 18 | 50% |
| Society & Development | 38 | 22 | 16 | 58% |
| Population & Household | 19 | 14 | 5 | 74% |
| Industry & Service | 16 | 12 | 4 | 75% |
| Education & Health | 16 | 12 | 4 | 75% |
| **TOTAL** | **262** | **~119** | **~143** | **45%** |

---

## Key Redundancy Patterns Found

### 1. Calculation Variants (Most Common)
Same data with different comparisons:
- "compared with previous month"
- "compared with same period of previous year"
- "compared with end of previous year"

**Rule:** Keep base data or YoY comparison only.

### 2. Geographic Granularity
Same data at multiple levels:
- National → Aimag → Soum → District

**Rule:** Keep national + aimag (if high-value); skip soum/district.

### 3. Temporal Variants
Same data at different frequencies:
- Monthly, Quarterly, Annual

**Rule:** Keep annual (or quarterly for economic indicators); skip monthly.

### 4. Version Duplicates
Same table with V1, V2, V3 suffixes:
- Often same data with minor updates

**Rule:** Keep highest version number or already-added version.

### 5. Population Base Confusion
"Resident" vs "Total" population tables:
- Same metric, different population definition

**Rule:** Keep resident population (census-aligned).

---

## Recommended Tables by Category

### Core Economic Indicators (~20 tables)
1. GDP (production approach) - DT_NSO_0500_001V1
2. GDP (expenditure approach) - DT_NSO_0500_003V1_annual
3. GDP (income approach) - DT_NSO_0500_006V1
4. GDP per capita - DT_NSO_0500_010V1
5. GNI - DT_NSO_0500_009V1
6. Balance of Payments - DT_NSO_0100_001V10
7. Inflation Rate - DT_NSO_0600_013V2
8. CPI Base Index - DT_NSO_0600_001V3
9. Housing Price Index - DT_NSO_0300_071V0
10. Exports by commodity - DT_NSO_1400_005V1_year
11. Imports by commodity - DT_NSO_1400_009V1_year
12. Exports by country - DT_NSO_1400_006V3
13. Government Budget - DT_NSO_0800_001V1
14. FDI Stock - DT_NSO_1500_004V3_1
15. Investment - DT_NSO_0901_001V1
16. Exchange Rates - DT_NSO_0700_008V1
17. Weekly Prices - DT_NSO_0600_001V4
18. Environmental Expenditure - DT_NSO_2023_001V3

### Demographics & Population (~10 tables)
1. Population by age/sex - DT_NSO_0300_001V2
2. Population by age groups - DT_NSO_0300_003V1
3. Population by location - DT_NSO_0300_027V1
4. Population migration - DT_NSO_0300_040V1
5. Population projection - DT_NSO_0300_076V12
6. Vital statistics (births/deaths) - DT_NSO_0300_001V1
7. Birth rates by age - DT_NSO_0300_029V1
8. Marriages & divorces - DT_NSO_0300_020V1
9. Life expectancy - DT_NSO_0100_01T28

### Labour & Employment (~15 tables)
1. Unemployment rate - DT_NSO_0400_049V1
2. Employment indicators - national level
3. Employment-to-population ratio
4. Employment by economic activity - DT_NSO_0400_067V1
5. Average hourly earnings - DT_NSO_0400_048V1
6. Monthly wages by sector
7. Real wage index
8. Working poverty rate - DT_NSO_0400_056V1
9. Youth NEET rate - DT_NSO_0400_050V1
10. Social protection coverage - DT_NSO_0400_045V1
11. Labor productivity (GDP per employed) - DT_NSO_0400_047V1
12. Labour share of GDP - DT_NSO_0400_053V1
13. SME value added - DT_NSO_0500_001V2
14. Business register - DT_NSO_2600_008V1

### Livestock & Agriculture (~8 tables)
1. Livestock count - DT_NSO_1001_109V1
2. Gross livestock output - DT_NSO_1001_001V1
3. Animal losses - DT_NSO_1001_011V1
4. Market prices - DT_NSO_1001_040V2
5. Young animal survival - DT_NSO_1001_108V1

### Social Indicators (~20 tables)
1. Household income - DT_NSO_1900_001V1
2. Household expenditure - DT_NSO_1900_002V1
3. Income composition - DT_NSO_1900_003V1
4. Expenditure composition - DT_NSO_1900_004V1
5. Poverty indicators - DT_NSO_1900_007V1
6. Minimum subsistence level - DT_NSO_1900_010V1
7. Gini/Theil inequality - DT_NSO_1900_036V1
8. Poverty by aimag - DT_NSO_1900_035V1
9. Food security - DT_NSO_1003_001V1
10. Food insecurity prevalence - DT_NSO_2300_022V1
11. Crime rate - DT_NSO_2300_034V1
12. Court resolution rate - DT_NSO_2300_036V1

### Industry & Services (~10 tables)
1. Trade turnover - DT_NSO_1600_001V1
2. Industrial PPI - DT_NSO_1100_016V4
3. Coal balance - DT_NSO_1100_010V1
4. Construction cost index - DT_NSO_1100_015V2
5. Imported vehicles - DT_NSO_1200_013V5
6. Inbound tourists - DT_NSO_1800_005V2
7. Food service income - DT_NSO_1602_002V1

### Education & Health (~12 tables)
1. Birth rates - DT_NSO_0300_029V1
2. Infant mortality - DT_NSO_2100_014V2
3. Cancer statistics - DT_NSO_2100_045V1
4. Health spending - DT_NSO_2100_030V1
5. Health insurance fund - DT_NSO_2100_30V001
6. Inpatients per 10,000 - DT_NSO_0300_071V02
7. Education spending - DT_NSO_2002_055V1
8. School enrollment - DT_NSO_2002_065V1
9. Adolescent fertility - DT_NSO_2100_047V1
10. Family planning - DT_NSO_2100_051V1

### Housing (~3 tables)
1. Houses by type/rooms - DT_NSO_3500_003V0
2. Household utilities - DT_NSO_3500_005V1

---

## Tables to Skip (Major Categories)

### Skip: MDG/SDG Derived Tables (47 tables)
- Millennium Development Goals indicators
- Duplicate data reformatted for UN reporting

### Skip: Soum/District Level (206+ tables)
- Bag, khoroo, soum, district granularity
- Too detailed for 80% utility audience

### Skip: Historical Archive (104 tables)
- Pre-2000 legacy data
- Inconsistent with modern methodology

### Skip: Calculation Variants (~100 tables)
- Monthly/quarterly variants when annual exists
- Different comparison base calculations

### Skip: Regional Duplicates (~50 tables)
- Aimag-level when national is sufficient
- Same data at multiple geographic levels

---

## Implementation Recommendations

### Phase 1: Essential (~50 tables)
Add these immediately - core indicators everyone needs:
- GDP, Inflation, Trade, Population, Employment, Poverty

### Phase 2: Comprehensive (~60 additional tables)
Add for full coverage:
- Detailed sector breakdowns
- Regional variants for high-value topics
- Specialized social indicators

### Phase 3: Specialist (~20 additional tables)
Add on demand:
- Niche topics (IP, religious, elections)
- Deep operational metrics (livestock health)
- Very granular breakdowns

---

## File Reference

### Generated Analysis Files
```
nso-analysis/
├── FINAL_RECOMMENDATIONS.md       # This file
├── NSO_CATALOG_ANALYSIS.md        # Phase 1 overview
├── nso-catalog.xlsx               # Updated with recommendations
└── sectors/
    ├── economy_environment_analysis.md
    ├── labour_business_analysis.md
    ├── regional_development_analysis.md
    ├── society_development_analysis.md
    ├── population_household_analysis.md
    ├── industry_service_analysis.md
    └── education_health_analysis.md
```

### How to Use
1. **Browse recommendations:** Read this file for overview
2. **Deep dive by sector:** Read individual sector analysis files
3. **Update registry:** Use nso-catalog.xlsx to mark final decisions
4. **Add datasets:** Follow the categorized table lists above

---

## Notes

- All recommendations prioritize **national-level, annual frequency** data
- Regional breakdowns included only for high-value topics (GDP, population, poverty)
- Tables already added to data.mn are marked with ✓ in sector analyses
- Each sector analysis includes detailed rationale for keep/skip decisions
