# NSO Regional Development Sector Analysis
## Redundancy Assessment Report

**Date**: December 16, 2025
**Sector**: Regional development
**Total Tables**: 36
**Analysis Focus**: Identify best single table per concept for business users, students, professionals

---

## Executive Summary

The Regional development sector contains **36 tables** organized across **10 subsectors**. Analysis reveals significant redundancies, particularly in:

- **Price indices** (6 tables covering same concept with different perspectives)
- **National accounts/GDP** (4 tables with overlapping regional data)
- **Livestock statistics** (6 detailed operational tables beyond headline count)
- **Trade income** (4 tables with redundant monthly/quarterly splits)
- **Household finance** (5 tables with overlapping income/expenditure data)

### Key Findings:
1. **Multiple CPI tables** represent the SAME data with different calculations (monthly changes, yearly comparisons, etc.)
2. **Regional tables often duplicate national data** under a regional breakdown (e.g., national inflation rates broken down by aimag)
3. **Time-series splits** (monthly vs. annual) create unnecessary table duplication
4. **Agricultural detail tables** add operational metrics not useful for general audience

---

## Concept-Based Analysis

### 1. PRICE INDICES (6 tables)

#### Tables:
| ID | Title | Type | Already Added |
|----|-------|------|---|
| DT_NSO_0600_013V2.px | Inflation Rate by Indicator and Year | National annual | ✓ |
| DT_NSO_0600_001V3.px | National Base Consumer Price Index by group and month | National monthly | ✗ |
| DT_NSO_0600_002V1.px | National Consumer Price Index (1991-1-16=100) | National annual | ✗ |
| DT_NSO_0600_009V1.px | National CPI by group, monthly percent change | National monthly % | ✗ |
| DT_NSO_0600_008V1.px | National CPI by groups and % change vs end of year | National annual % | ✗ |
| DT_NSO_0600_010V1.px | National CPI by groups and % change vs same period | National annual % | ✗ |
| DT_NSO_0303_07V71.px | Consumer Price Index (regional, monthly vs previous month) | Regional monthly % | ✗ |
| DT_NSO_0303_07V81.px | Consumer Price Index (regional, vs same period last year) | Regional annual % | ✗ |
| DT_NSO_0303_07V91.px | Consumer Price Index (regional, vs end of previous year) | Regional annual % | ✗ |

**Analysis:**
- Tables 0600_013V2, 0600_002V1, and 0600_009V1 ALL contain the same core data presented differently
- The 0600_0XX series are ALL NATIONAL LEVEL despite being in "Regional development"
- The 0303_07V series provide REGIONAL breakdown but still calculated from same base data
- All are variations on Consumer Price Index calculations

**Redundancies Identified:**
- DT_NSO_0600_013V2 (Inflation Rate) = already added, preferred by users (simplest, annual)
- DT_NSO_0600_001V3 (Base CPI monthly) = adds granularity but national-only, same data
- DT_NSO_0600_002V1 (CPI index 1991 base) = alternative calculation of same data
- DT_NSO_0600_008V1, 0600_009V1, 0600_010V1 = different percent-change calculations of identical underlying CPI
- DT_NSO_0303_07V71, V81, V91 = regional versions, BUT same data with regional breakdown

**RECOMMENDATION - BEST CHOICE:**
- **PRIMARY**: `DT_NSO_0600_013V2.px` (Inflation Rate by Year) - Already added, simplest for general audience
- **SECONDARY**: `DT_NSO_0303_07V81.px` (Regional CPI vs same period) - IF regional breakdown needed
- **REDUNDANT**: Remove DT_NSO_0600_001V3, 0600_002V1, 0600_008V1, 0600_009V1, 0600_010V1, 0303_07V71, 0303_07V91

**Note**: The national tables are included in Regional development sector but should move to National Accounts sector. The regional variants (0303_07) should be preferred only if regional comparison is needed.

---

### 2. LIVESTOCK (6 tables)

#### Tables:
| ID | Title | Score | Recommendation |
|----|-------|-------|---|
| DT_NSO_1001_109V1.px | **Number of Livestock by type, aimags and Capital, by year** | 92 | T1-Essential ✓ |
| DT_NSO_1001_108V1.px | Survivals of Young Animals | 62 | T2-Recommended |
| DT_NSO_1001_133V1.px | Number of Miscarriage Female Animals | 62 | T2-Recommended |
| DT_NSO_1001_134V1.px | Number of Barren Female Animals | 62 | T2-Recommended |
| DT_NSO_1001_135V1.px | Number of Breeding Stock | 62 | T2-Recommended |
| DT_NSO_1001_136V1.px | Losses of Adult Animals | 62 | T2-Recommended |

**Analysis:**
- Table 109V1 is the **headline livestock count** - most useful for general audience
- Tables 108V1, 133V1, 134V1, 135V1, 136V1 are all **OPERATIONAL/VETERINARY detail** tables
- These operational tables are only useful for:
  - Veterinary research
  - Livestock management professionals
  - Agricultural economists doing deep analysis

**Redundancies Identified:**
- Tables 108, 133, 134, 135, 136 all contribute to understanding livestock herd dynamics
- BUT: They are NOT redundant with each other—they measure different things
- HOWEVER: They are all **secondary to the headline count** in 109V1
- For general business/student use, only the total count matters

**RECOMMENDATION - BEST CHOICE:**
- **PRIMARY**: `DT_NSO_1001_109V1.px` (Number of Livestock) - Already added
- **SECONDARY**: Keep one operational table for livestock scientists: `DT_NSO_1001_108V1.px` (Young Animal Survival) - proxy for herd health
- **REDUNDANT**: DT_NSO_1001_133V1, 134V1, 135V1, 136V1 are specialist operational tables—remove unless serving veterinary/research audience

**Note**: These are specialized tables. For a general data platform (business, students, professionals), the headline count (109V1) is sufficient.

---

### 3. NATIONAL ACCOUNTS / GDP (4 tables)

#### Tables:
| ID | Title | Score | Already Added |
|----|-------|-------|---|
| DT_NSO_0500_007V1 | **Gross Domestic Product by aimags and Capital, by year** | 75 | ✗ |
| DT_NSO_0500_011V1 | Gross Domestic Product Per Capita by aimags and Capital | 75 | ✗ |
| DT_NSO_0500_021V1 | Industrial Composition of GDP by aimags and Capital | 75 | ✗ |
| DT_NSO_0500_021V2 | GDP by economic activity by aimags and Capital | 75 | ✗ |

**Analysis:**
- All 4 tables provide regional breakdown of GDP
- Table 007V1 = **Total GDP in nominal terms** (headline metric)
- Table 011V1 = **GDP per capita** (normalized by population, useful for comparisons)
- Tables 021V1 & 021V2 = **Industrial composition** (sector breakdown, same concept different presentations?)

**Redundancies Identified:**
- Tables 021V1 and 021V2 appear to be the SAME data (industrial composition by region)
- Distinction unclear without examining raw data
- Tables 007V1 and 011V1 are complementary (total vs per capita)

**RECOMMENDATION - BEST CHOICE:**
- **PRIMARY**: `DT_NSO_0500_007V1.px` (Total GDP by Region and Year) - Headline economic metric
- **SECONDARY**: `DT_NSO_0500_011V1.px` (GDP per Capita) - Key comparison metric
- **CONDITIONAL**: Keep only ONE of 021V1/021V2 (need to verify they're not identical)
- **REDUNDANT**: The duplicate industrial composition table

**Note**: Regional tables appropriately included here. Verify 021V1 vs 021V2 to confirm redundancy.

---

### 4. TRADE (4 tables)

#### Tables:
| ID | Title | Score | Type |
|----|-------|-------|------|
| DT_NSO_1600_002V1_year.px | Total Trade Turnover by Aimag (Annual) | 65 | Annual |
| DT_NSO_1600_002V1_month.px | Total Trade Turnover by Aimags and Capital (Monthly) | 65 | Monthly |
| DT_NSO_1602_003V1.px | Income of Hotel Sector by Region and Quarter | 60 | Quarterly |
| DT_NSO_1602_003V1_1.px | Income of Hotel Sector by Region and Month | 60 | Monthly |
| DT_NSO_1602_004V1.px | Income of Food Sector by Region and Quarter | 60 | Quarterly |
| DT_NSO_1602_004V1_1.px | Income of Food Sector by Region and Month | 60 | Monthly |

**Analysis:**
- **Total Trade Turnover**: 2 versions of same data (annual vs monthly) - typical time-series split
- **Hotel Sector Income**: 2 versions of same data (quarterly vs monthly) - redundant time-series
- **Food Sector Income**: 2 versions of same data (quarterly vs monthly) - redundant time-series

**Redundancies Identified:**
- Annual and monthly/quarterly versions of the SAME underlying data
- Duplicate time-series granularity - one version is sufficient

**RECOMMENDATION - BEST CHOICE:**
- **PRIMARY (Trade)**: `DT_NSO_1600_002V1_year.px` (Annual Trade Turnover) - Standard reporting period
- **REDUNDANT**: DT_NSO_1600_002V1_month.px (monthly detail not needed for business/student audience)
- **PRIMARY (Hotel)**: `DT_NSO_1602_003V1.px` (Quarterly Hotel Income) - Quarterly standard
- **REDUNDANT**: DT_NSO_1602_003V1_1.px (monthly granularity excessive)
- **PRIMARY (Food)**: `DT_NSO_1602_004V1.px` (Quarterly Food Sector Income) - Quarterly standard
- **REDUNDANT**: DT_NSO_1602_004V1_1.px (monthly granularity excessive)

**Note**: Keep annual/quarterly versions. Monthly versions are for specialized time-series analysis only.

---

### 5. POPULATION & HOUSEHOLD (3 tables)

#### Tables:
| ID | Title | Score |
|----|-------|-------|
| DT_NSO_0300_004V1.px | Population by location, aimags and Capital, by year | 65 |
| DT_NSO_0300_020V1.px | Marriages and Divorces per 1000 population, by region | 65 |
| DT_NSO_0300_040V1.px | Population Migration by aimags and Capital | 65 |

**Analysis:**
- Each table measures DIFFERENT concepts (population, marriage/divorce rates, migration)
- No redundancy between them
- All appropriate for regional breakdown

**RECOMMENDATION - BEST CHOICE:**
- **KEEP ALL THREE** - Different metrics, no redundancy
- Priority ranking: Population (foundation) > Migration (important indicator) > Marriage/Divorce (demographic detail)

---

### 6. POPULATION LIVELIHOOD (5 tables)

#### Tables:
| ID | Title | Score | Type |
|----|-------|-------|------|
| DT_NSO_1900_001V3.px | Monthly Average Income per Household by region | 60 | Income |
| DT_NSO_1900_002V3.px | Monthly Average Expenditure per Household by region | 60 | Expenditure |
| DT_NSO_1900_003V3.px | Composition of Monthly Average Income per Household | 60 | Income detail |
| DT_NSO_1900_004V3.px | Composition of Monthly Average Expenditure per Household | 60 | Expenditure detail |
| DT_NSO_1900_036V4.px | Inequality (Gini coefficient and Theil index) by region | 60 | Inequality metric |

**Analysis:**
- Tables 001V3 & 003V3 both measure **household income** - one raw, one with composition
- Tables 002V3 & 004V3 both measure **household expenditure** - one raw, one with composition
- Table 036V4 measures **inequality** (Gini, Theil) - different concept but related

**Redundancies Identified:**
- 001V3 (total income) vs 003V3 (income composition) - one is subset of other
- 002V3 (total expenditure) vs 004V3 (expenditure composition) - one is subset of other
- The "composition" tables likely include the totals in the breakdown

**RECOMMENDATION - BEST CHOICE:**
- **PRIMARY**: `DT_NSO_1900_001V3.px` (Monthly Income per Household) - Headline metric
- **PRIMARY**: `DT_NSO_1900_002V3.px` (Monthly Expenditure per Household) - Headline metric
- **REDUNDANT**: DT_NSO_1900_003V3, 004V3 (composition is subset of total)
- **KEEP**: `DT_NSO_1900_036V4.px` (Inequality Gini) - Different metric, important for development

**Note**: The composition tables provide useful breakdown detail but are technically redundant with the total tables if composition data is included in the original source.

---

### 7. SMALL & MEDIUM ENTERPRISES (1 table)

#### Tables:
| ID | Title | Score |
|----|-------|-------|
| DT_NSO_0500_001V9.px | SME Value Added Shares in GDP by aimags and Capital | 75 |

**Analysis:**
- Single table, no redundancy
- Unique metric (SME contribution)

**RECOMMENDATION:**
- **KEEP**: This is the only SME-related table

---

### 8. TRANSPORTATION (1 table)

#### Tables:
| ID | Title | Score |
|----|-------|-------|
| DT_NSO_1200_013V5.px | Number of Imported Vehicles by country, type, and year | 75 |

**Analysis:**
- Single table, no redundancy
- Specific to vehicle imports

**RECOMMENDATION:**
- **KEEP**: This is the only transportation table in this sector

---

### 9. JUSTICE & CRIME (1 table)

#### Tables:
| ID | Title | Score |
|----|-------|-------|
| DT_NSO_2300_024V1.px | Crime of Livestock Theft by region, aimag and capital | 62 |

**Analysis:**
- Single table, specialized topic
- Only crime metric in regional sector

**RECOMMENDATION:**
- **CONDITIONAL KEEP**: Specialized topic (livestock theft). Only include if targeting agriculture/rural development focus.

---

## Summary Table: Keep vs Remove

### TIER 1: ESSENTIAL (Keep Absolutely)

| Concept | Table ID | Title | Reason |
|---------|----------|-------|--------|
| Price | DT_NSO_0600_013V2.px | Inflation Rate | Simplest, already added, general use |
| Livestock | DT_NSO_1001_109V1.px | Number of Livestock | Headline count, already added |
| GDP | DT_NSO_0500_007V1.px | GDP by Region | Regional economic metric |
| GDP per Capita | DT_NSO_0500_011V1.px | GDP per Capita by Region | Key comparison metric |
| Trade | DT_NSO_1600_002V1_year.px | Trade Turnover (Annual) | Regional trade metric |
| Population | DT_NSO_0300_004V1.px | Population by Region | Foundation demographic |
| Income | DT_NSO_1900_001V3.px | Household Income by Region | Living standards metric |
| Expenditure | DT_NSO_1900_002V3.px | Household Expenditure by Region | Living standards metric |

### TIER 2: RECOMMENDED (Keep for Specific Audiences)

| Concept | Table ID | Title | Audience |
|---------|----------|-------|----------|
| Migration | DT_NSO_0300_040V1.px | Population Migration | Development indicators |
| GDP by Industry | DT_NSO_0500_021V1.px | Industrial GDP Composition | Economic analysts |
| SMEs | DT_NSO_0500_001V9.px | SME Share of GDP | Business analysis |
| Vehicles | DT_NSO_1200_013V5.px | Imported Vehicles | Transportation/trade |
| Inequality | DT_NSO_1900_036V4.px | Gini Coefficient | Social development |
| Hotel Income | DT_NSO_1602_003V1.px | Hotel Sector (Quarterly) | Tourism analytics |
| Food Income | DT_NSO_1602_004V1.px | Food Sector (Quarterly) | Food economy |
| Young Animal Survival | DT_NSO_1001_108V1.px | Survivals of Young Animals | Livestock research |
| Regional CPI | DT_NSO_0303_07V81.px | Regional CPI YoY | Regional comparison |
| Marriage/Divorce | DT_NSO_0300_020V1.px | Marriages and Divorces | Demographic detail |

### TIER 3: REDUNDANT (Remove)

| Concept | Table ID | Title | Reason for Removal |
|---------|----------|-------|-------------------|
| Price | DT_NSO_0600_001V3.px | Base CPI Monthly | Duplicate data, monthly detail |
| Price | DT_NSO_0600_002V1.px | CPI Index (1991 base) | Same data as 0600_013V2 |
| Price | DT_NSO_0600_008V1.px | CPI % change vs end of year | Different calc of same data |
| Price | DT_NSO_0600_009V1.px | CPI monthly % change | Different calc of same data |
| Price | DT_NSO_0600_010V1.px | CPI % change YoY | Different calc of same data |
| Price | DT_NSO_0303_07V71.px | Regional CPI vs prev month | Monthly granularity excess |
| Price | DT_NSO_0303_07V91.px | Regional CPI vs end of year | Use 0303_07V81 instead |
| Livestock | DT_NSO_1001_133V1.px | Miscarriage Female Animals | Operational detail, niche use |
| Livestock | DT_NSO_1001_134V1.px | Barren Female Animals | Operational detail, niche use |
| Livestock | DT_NSO_1001_135V1.px | Breeding Stock | Operational detail, niche use |
| Livestock | DT_NSO_1001_136V1.px | Losses of Adult Animals | Operational detail, niche use |
| GDP | DT_NSO_0500_021V2.px | GDP by activity (check dup) | Likely duplicate of 021V1 |
| Trade | DT_NSO_1600_002V1_month.px | Trade Turnover (Monthly) | Monthly detail, use annual |
| Income | DT_NSO_1900_003V3.px | Income Composition | Subset of 001V3 |
| Expenditure | DT_NSO_1900_004V3.px | Expenditure Composition | Subset of 002V3 |
| Crime | DT_NSO_2300_024V1.px | Livestock Theft | Too specialized unless ag-focused |
| Hotel | DT_NSO_1602_003V1_1.px | Hotel Income (Monthly) | Monthly detail, use quarterly |
| Food | DT_NSO_1602_004V1_1.px | Food Sector (Monthly) | Monthly detail, use quarterly |

---

## Key Recommendations

### 1. CONSOLIDATE PRICE INDICES
The sector currently has **9 different CPI tables**. Consolidate to:
- **One primary**: `DT_NSO_0600_013V2.px` (Inflation Rate)
- **One regional option**: `DT_NSO_0303_07V81.px` (Regional CPI YoY)
- **Remove all others** - they are different calculations of identical underlying data

**Impact**: Reduces from 9 tables to 2 (-78% redundancy)

### 2. FOCUS LIVESTOCK ON HEADLINE COUNT
Keep only:
- `DT_NSO_1001_109V1.px` (Headline count)
- Optionally: `DT_NSO_1001_108V1.px` (Young animal survival - proxy for herd health)

**Remove**: Specialist operational tables (miscarriage, barren, breeding stock, losses) unless serving livestock science audience

**Impact**: Reduces from 6 to 1-2 tables (-67% redundancy)

### 3. ELIMINATE TIME-SERIES DUPLICATION
For datasets available in multiple time-series granularities, keep only the most standard period:
- **Trade**: Keep annual only, remove monthly
- **Hotel/Food income**: Keep quarterly only, remove monthly

**Impact**: Reduces by 4 tables (-33% in this category)

### 4. CONSOLIDATE HOUSEHOLD LIVELIHOOD
- Keep total income and total expenditure tables
- Remove composition tables (they're subsets of the totals)
- Keep inequality as separate metric

**Impact**: Reduces from 5 to 3 tables (-40% redundancy)

### 5. VERIFY GDP INDUSTRIAL COMPOSITION
Tables 021V1 and 021V2 appear to measure the same thing. Verify data structures:
- If identical: Keep only one, remove the other
- If different decompositions: Document the distinction

---

## Final Recommended Dataset List

**Total: 36 tables → 18 core tables** (50% reduction through redundancy elimination)

### Tier 1 (Essential - 8 tables):
1. DT_NSO_0600_013V2.px - Inflation Rate
2. DT_NSO_1001_109V1.px - Livestock Count
3. DT_NSO_0500_007V1.px - GDP by Region
4. DT_NSO_0500_011V1.px - GDP per Capita
5. DT_NSO_1600_002V1_year.px - Trade Turnover (Annual)
6. DT_NSO_0300_004V1.px - Population by Region
7. DT_NSO_1900_001V3.px - Household Income
8. DT_NSO_1900_002V3.px - Household Expenditure

### Tier 2 (Recommended - 10 tables):
9. DT_NSO_0303_07V81.px - Regional CPI (for regional comparison)
10. DT_NSO_0300_040V1.px - Population Migration
11. DT_NSO_0300_020V1.px - Marriages & Divorces
12. DT_NSO_0500_001V9.px - SME Share of GDP
13. DT_NSO_0500_021V1.px - GDP by Economic Activity *(verify not dup with 021V2)*
14. DT_NSO_1200_013V5.px - Imported Vehicles
15. DT_NSO_1900_036V4.px - Inequality (Gini)
16. DT_NSO_1001_108V1.px - Young Animal Survival (livestock health proxy)
17. DT_NSO_1602_003V1.px - Hotel Sector Income (Quarterly)
18. DT_NSO_1602_004V1.px - Food Sector Income (Quarterly)

**Remove (18 tables):**
DT_NSO_0600_001V3, 0600_002V1, 0600_008V1, 0600_009V1, 0600_010V1, 0303_07V71, 0303_07V91, 1001_133V1, 1001_134V1, 1001_135V1, 1001_136V1, 0500_021V2 *(if dup)*, 1600_002V1_month, 1602_003V1_1, 1602_004V1_1, 1900_003V3, 1900_004V3, 2300_024V1

---

## Appendix: Regional Data Flagged

### National Tables in Regional Sector:
The following are **NATIONAL-LEVEL ONLY** tables included in the "Regional development" sector (should be in different sector):
- DT_NSO_0600_013V2.px - Inflation Rate (National)
- DT_NSO_0600_001V3.px - Base CPI (National)
- DT_NSO_0600_002V1.px - CPI (National)
- DT_NSO_0600_008V1.px - CPI % change (National)
- DT_NSO_0600_009V1.px - CPI % change (National)
- DT_NSO_0600_010V1.px - CPI % change (National)

**Recommendation**: These should be migrated to "National Accounts" or "Price" sector. Only the regional variants (DT_NSO_0303_07Vxx) should remain in the Regional development sector.

---

## Analysis Methodology

This analysis applied the following criteria to identify redundancy:

1. **Same underlying data with different calculations**: Multiple representations of identical base data (e.g., CPI as index, percentage change, year-over-year change)
2. **Time-series granularity duplication**: Same metric available in monthly/quarterly/annual granularities when annual is sufficient
3. **Subset relationships**: Tables that contain the same data as another table but filtered or aggregated (e.g., income composition vs total income)
4. **Conceptual overlap**: Multiple tables measuring the same core concept (e.g., 4 variants of industrial composition of GDP)
5. **Niche/specialist tables**: Tables with limited audience utility that don't serve the primary user groups (business people, students, professionals)

Scoring and recommendation levels from the original data were used as secondary factors in decision-making.
