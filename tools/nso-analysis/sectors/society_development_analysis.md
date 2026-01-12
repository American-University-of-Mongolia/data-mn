# Society Development Sector - NSO Tables Analysis

**Sector**: Society, development
**Total Tables**: 38
**Analysis Date**: 2025-12-16

---

## Executive Summary

The "Society, development" sector contains 38 NSO tables across 6 subsectors with significant redundancies. Key findings:

- **Household Income/Expenditure**: 14 tables (37% of sector) - highly redundant
- **Poverty & Inequality**: 9 tables (24% of sector) - time-period overlaps
- **Food Security**: 3 tables (8% of sector) - some overlap in populations measured
- **Law & Crime**: 4 tables (11% of sector) - minimal redundancy
- **Social Insurance**: 1 table (3% of sector)
- **SDG Indicators**: 1 table (3% of sector)

**Recommendation**: Consolidate from 38 tables to approximately **12-15 primary tables** by selecting best-in-class options and deprecating redundant time-series variants.

---

## Concept Groups & Redundancy Analysis

### 1. HOUSEHOLD INCOME & EXPENDITURE (14 tables, 37% of sector)

**Concept**: Historical and current household monetary income and expenditure by location and region.

| Best Choice | Redundant Tables | Rationale |
|-------------|-----------------|-----------|
| **DT_NSO_1900_001V1** (Income by location, 1997-2024) | DT_NSO_1900_001V2 (Region, 2007-2024) | V1 has longer history + location breakdown includes regional detail. V2 is narrower subset. |
| **DT_NSO_1900_002V1** (Expenditure by location, 1997-2024) | DT_NSO_1900_002V2 (Region, 2007-2024) | V1 preferred for same reason. |
| **DT_NSO_1900_003V1** (Income composition by location, 1997-2024) | DT_NSO_1900_003V2 (Region, 2007-2024) | V1 provides longer historical view. |
| **DT_NSO_1900_004V1** (Expenditure composition by location, 1997-2024) | DT_NSO_1900_004V2 (Region, 2007-2024) | V1 has complete historical series. |
| **DT_NSO_1900_018V1** (Income by quarter) | DT_NSO_1900_020V1 (Income composition by quarter) | Keep 018V1 for raw income; 020V1 is composition-specific |
| **DT_NSO_1900_019V1** (Expenditure by quarter) | DT_NSO_1900_021V1 (Expenditure composition by quarter) | Keep 019V1 for raw expenditure |
| **DT_NSO_1900_030V2** (Income & expenditure grouping by quarter) | None | **REDUNDANT**: Combines quarterly data that overlaps with 018/019/020/021 |
| **DT_NSO_1900_032V1** (Income grouping by year) | DT_NSO_1900_033V1 (Expenditure grouping by year) | Both needed: different metrics. Keep both. |
| **DT_NSO_1900_036V2** (Gini Index by quarter) | DT_NSO_1900_036V3 (Theil Index by quarter) | Both are different inequality measures; keep both for comprehensive inequality analysis. |

#### Household Income/Expenditure - Consolidation Summary

**Recommended Core Tables** (5-7):
1. DT_NSO_1900_001V1 - Main income series
2. DT_NSO_1900_002V1 - Main expenditure series
3. DT_NSO_1900_003V1 - Income composition
4. DT_NSO_1900_004V1 - Expenditure composition
5. DT_NSO_1900_032V1 - Income grouping
6. DT_NSO_1900_033V1 - Expenditure grouping
7. DT_NSO_1900_036V2 + V3 - Inequality indices (Gini & Theil)

**Redundant Tables to Deprecate** (7):
- DT_NSO_1900_001V2 (superseded by V1)
- DT_NSO_1900_002V2 (superseded by V1)
- DT_NSO_1900_003V2 (superseded by V1)
- DT_NSO_1900_004V2 (superseded by V1)
- DT_NSO_1900_015V1 (annual 1966-1996, now obsolete; monthly 1997+ preferred)
- DT_NSO_1900_017V1 (annual 1966-1996, now obsolete; monthly 1997+ preferred)
- DT_NSO_1900_030V2 (duplicate quarterly metrics already in 018/019/020/021)

**Quarterly Tables** (4):
- DT_NSO_1900_018V1 - Quarterly income (keep)
- DT_NSO_1900_019V1 - Quarterly expenditure (keep)
- DT_NSO_1900_020V1 - Quarterly income composition (keep)
- DT_NSO_1900_021V1 - Quarterly expenditure composition (keep)

---

### 2. POVERTY & INEQUALITY (9 tables, 24% of sector)

**Concept**: Poverty indicators, minimum subsistence levels, and consumption-based inequality measures.

| Best Choice | Redundant Tables | Rationale |
|-------------|-----------------|-----------|
| **DT_NSO_1900_010V1** (Min subsistence level by region, 2001-2025) | DT_NSO_1900_016V1 (Min subsistence 1999-2000) | V1 is current standard. V16 is historical/archived period. |
| **DT_NSO_1900_007V1** (Poverty indicators 1995-2020) | DT_NSO_1900_007V12 (Poverty indicators 2022) | **DECISION NEEDED**: V1 has long historical span but ends 2020. V12 is only 2022. Suggest: Keep V1 as primary, add V12 as "recent update" or merge into single updated table. |
| **DT_NSO_1900_008V1** (Consumption by poverty status, 2003-2020) | None | Unique cross-tabulation: poverty status × consumption categories |
| **DT_NSO_1900_035V1** (Poverty by aimag, 2016-2020) | None | Regional granularity. Different from 007V1's broader scope. |
| **DT_NSO_1900_013V1** (Consumption by household deciles, 2003-2020) | None | Specific inequality analysis; complements 036V1 |
| **DT_NSO_1900_014V1** (Consumption shares by quintiles) | DT_NSO_1900_013V1 (Deciles) | Both measure inequality distribution; quintiles (014) and deciles (013) are similar. **REDUNDANCY**: Keep one. Recommend keeping 014V1 (quintiles more commonly used). |
| **DT_NSO_1900_036V1** (Inequality: Gini & Theil by consumption) | DT_NSO_1900_036V2 & V3 (Gini & Theil by expenditure, quarterly) | V1 = annual; V2/V3 = quarterly. All three unique by time granularity. Keep all three. |

#### Poverty & Inequality - Consolidation Summary

**Recommended Core Tables** (6):
1. DT_NSO_1900_010V1 - Minimum subsistence levels (primary)
2. DT_NSO_1900_007V1 - Poverty indicators (long history)
3. DT_NSO_1900_007V12 - Poverty indicators 2022 update (or merge into 007V1)
4. DT_NSO_1900_008V1 - Consumption by poverty status
5. DT_NSO_1900_035V1 - Regional poverty breakdown
6. DT_NSO_1900_036V1 - Gini & Theil (annual, consumption-based)

**Redundant Tables to Deprecate** (3):
- DT_NSO_1900_016V1 (historical 1999-2000; superseded by 010V1)
- DT_NSO_1900_013V1 (deciles; supersede by 014V1 quintiles)
- DT_NSO_1900_014V1 **OR** DT_NSO_1900_013V1 (choose one; both measure same inequality distribution differently)
  - **Recommend keeping 014V1** (quintiles = 20% groups, more standard)

---

### 3. FOOD SECURITY (3 tables, 8% of sector)

**Concept**: Food consumption patterns and food insecurity prevalence by population groups.

| Best Choice | Population Measured | Rationale |
|-------------|-------------------|-----------|
| **DT_NSO_1003_001V1** (Annual consumption, standard population) | National average | Good baseline consumption measure |
| **DT_NSO_2300_022V1** (Food insecurity prevalence, by population) | Population-level (household members counted individually) | **PRIMARY**: Most relevant for understanding food insecurity burden |
| **DT_NSO_2300_020V1** (Food insecurity, by household) | Household-level (households counted as units) | **REDUNDANCY**: Same concept as 022V1 but different unit of analysis |

#### Food Security - Consolidation Summary

**Recommended Core Tables** (2):
1. DT_NSO_1003_001V1 - Food consumption baseline
2. DT_NSO_2300_022V1 - Food insecurity prevalence (population-level)

**Redundant Tables to Deprecate** (1):
- DT_NSO_2300_020V1 (household-level redundant; population-level 022V1 more useful for understanding prevalence)

---

### 4. LAW & CRIME (4 tables, 11% of sector)

**Concept**: Crime rates, court cases, and law enforcement statistics.

| Best Choice | Measurement | Rationale |
|-------------|------------|-----------|
| **DT_NSO_2300_034V1** (Recorded crime rate per 10,000 population 16+) | General crime prevalence | PRIMARY: Most important metric for policy makers |
| **DT_NSO_2300_036V1** (Resolved criminal cases per 10,000 population 16+) | Court resolution capacity | Complements crime rate; measures justice system output |
| **DT_NSO_2300_024V1** (Livestock theft crime) | Specific crime type | Specialized subsector data; unique to Mongolia context |
| **DT_NSO_2300_001A4** (Declarations of private interest/assets) | Corruption indicator | Different metric; anti-corruption focus |
| **DT_NSO_2300_041V1** (Resolved family law cases) | Specific legal domain | Specialized; complements general crime data |

#### Law & Crime - Consolidation Summary

**Recommended Core Tables** (5):
1. DT_NSO_2300_034V1 - Overall crime rate (primary indicator)
2. DT_NSO_2300_036V1 - Court resolution rate (justice outcome)
3. DT_NSO_2300_024V1 - Livestock theft (sector-specific)
4. DT_NSO_2300_001A4 - Corruption declarations
5. DT_NSO_2300_041V1 - Family law resolutions

**Redundant Tables to Deprecate**: NONE

*Note: Law & Crime is the least redundant subsector. Each table measures distinct aspects.*

---

### 5. SOCIAL INSURANCE & WELFARE (1 table, 3% of sector)

**Concept**: Social insurance fund expenditure.

| Table | Status |
|-------|--------|
| EXPENDITURE OF SOCIAL INSURANCE FUND, by type | **SINGLE** - No redundancy |

**Status**: Keep as-is. Unique metric for welfare analysis.

---

### 6. SUSTAINABLE DEVELOPMENT GOALS (1 table, 3% of sector)

**Concept**: SDG indicator measurements.

| Table | Status | Issue |
|-------|--------|-------|
| DT_NSO_4000_001 (Title in Mongolian) | **SINGLE** | Title not in English; unclear what metric this covers |

**Recommendation**: Clarify English translation before publication. Appears to be SDG-related but needs description.

---

## Summary: Recommended Final Table Count

### Current State
- **Total**: 38 tables
- **Redundancy**: 14-16 tables are redundant (37-42% of sector)

### Recommended State
- **Consolidated**: 12-15 primary tables (68% reduction)

### By Subsector

| Subsector | Current | Recommended | Deprecate | Notes |
|-----------|---------|------------|-----------|-------|
| Household Income/Expenditure | 14 | 7 | 7 | Remove regional variants; consolidate quarterly |
| Poverty & Inequality | 9 | 6 | 3 | Merge 007V12 into 007V1; choose deciles OR quintiles |
| Food Security | 3 | 2 | 1 | Remove household-level redundancy |
| Law & Crime | 4 | 5 | 0 | All unique; upgrade 041V1 to "Core" |
| Social Insurance | 1 | 1 | 0 | Keep as-is |
| SDG Indicators | 1 | 1 | 0 | Clarify English title |
| **TOTAL** | **38** | **22** | **16** | |

---

## Best Tables for Key Audiences

### For Business Professionals & Economists

**Essential Set** (5 tables):
1. **DT_NSO_1900_001V1** - Household income trends (1997-2024)
2. **DT_NSO_1900_002V1** - Household expenditure trends (1997-2024)
3. **DT_NSO_1900_010V1** - Minimum subsistence levels (poverty baseline)
4. **DT_NSO_1900_007V1** - Poverty indicators (1995-2020 + update with V12)
5. **DT_NSO_1900_036V1** - Inequality measures (Gini/Theil)

*Rationale*: These five tables provide complete economic picture for analysis of living standards, poverty trends, and inequality.

### For Students & Researchers

**Comprehensive Set** (10 tables):
*(Add to Business set)*
6. **DT_NSO_1900_003V1** - Income composition (breakdown by type)
7. **DT_NSO_1900_004V1** - Expenditure composition (breakdown by type)
8. **DT_NSO_1900_008V1** - Consumption by poverty status (poverty-consumption relationship)
9. **DT_NSO_1003_001V1** - Food consumption (food security baseline)
10. **DT_NSO_2300_022V1** - Food insecurity prevalence (vulnerability measure)

### For Policy Makers

**Policy Focused Set** (12 tables):
*(Add to Students set)*
11. **DT_NSO_2300_034V1** - Crime rate (public safety)
12. **DT_NSO_1900_035V1** - Regional poverty (geographic targeting)

---

## Specific Redundancy Issues

### Issue 1: Income/Expenditure V1 vs V2

**Problem**:
- V1: Location breakdown, 1997-2024
- V2: Region breakdown, 2007-2024

**Why Redundant**: V2 is strictly a subset of V1 in terms of geography and time.

**Solution**: Deprecate V2. For researchers needing regional data, note that V1 location-level can be aggregated to regional level using NSO region mappings.

---

### Issue 2: Poverty Indicators Time Gap (007V1 ends 2020, 007V12 is 2022)

**Problem**:
- DT_NSO_1900_007V1: 1995-2020 (older, but has historical context)
- DT_NSO_1900_007V12: 2022 only (recent, but limited history)

**Why Problematic**: Users don't know which to choose. Gap between 2020 and 2022 is unexplained.

**Solution**:
1. Inquire if NSO has 2021, 2023, 2024 poverty indicators
2. If yes: Deprecate 007V12 and request merged table with 2020-2024+ coverage
3. If no: Keep both with notation explaining gap; recommend 007V1 as primary reference

---

### Issue 3: Inequality Measures (Deciles vs Quintiles)

**Problem**:
- DT_NSO_1900_013V1: Household deciles (10 groups, 10% each)
- DT_NSO_1900_014V1: Household quintiles (5 groups, 20% each)

**Why Redundant**: Both measure income/consumption distribution; quintiles are more standard.

**Solution**:
- **Recommend keeping DT_NSO_1900_014V1** (quintiles)
- Deprecate DT_NSO_1900_013V1 (deciles) unless NSO explicitly recommends deciles for Mongolia context
- Keep DT_NSO_1900_036V1 (Gini & Theil indices) as primary inequality measure

---

### Issue 4: Quarterly Income/Expenditure Redundancy

**Problem**:
- DT_NSO_1900_018V1: Income by quarter
- DT_NSO_1900_020V1: Income composition by quarter
- DT_NSO_1900_019V1: Expenditure by quarter
- DT_NSO_1900_021V1: Expenditure composition by quarter

**Why Potentially Redundant**: 020 and 021 might be calculable from 018/019 if composition = breakdown/total.

**Solution**:
- Keep all four IF they provide different analytical angles
- Verify with NSO that 020 ≠ calculated from 018
- If composition is calculable: deprecate 020 and 021; encourage users to calculate from 018/019

---

### Issue 5: Historical Income/Expenditure (1966-1996)

**Problem**:
- DT_NSO_1900_015V1: Annual income 1966-1996
- DT_NSO_1900_017V1: Annual expenditure 1966-1996

**Why Redundant**:
- Pre-dates modern survey methodology (1997+)
- Data not aligned with current income/expenditure series (001V1/002V1)
- Historically interested parties likely use 001V1/002V1 which start 1997

**Solution**: Deprecate both. Archive in version history for academic reference.

---

## Data Quality Notes

### Missing Metadata
- **DT_NSO_4000_001** (SDG table): Title is in Mongolian only; English translation needed
- **DT_NSO_2300_020V1** vs **2300_022V1**: Need clarification on "household" vs "population" unit differences

### Time Series Gaps
- Poverty indicators: Gap between 2020 (007V1) and 2022 (007V12)
- No 2021, 2023, 2024 poverty data identified
- Crime data: Check if 2023-2025 available

### Recommendation
Request from NSO:
1. Merged poverty indicators table (1995-2025, all years)
2. English translation for DT_NSO_4000_001
3. Clarification on household vs population food insecurity definitions

---

## Implementation Roadmap

### Phase 1: Immediate Consolidation (Low Risk)
**Deprecate these 8 tables** (clear redundancy):
- DT_NSO_1900_001V2 (V1 is primary)
- DT_NSO_1900_002V2 (V1 is primary)
- DT_NSO_1900_003V2 (V1 is primary)
- DT_NSO_1900_004V2 (V1 is primary)
- DT_NSO_1900_015V1 (obsolete historical)
- DT_NSO_1900_017V1 (obsolete historical)
- DT_NSO_1900_030V2 (duplicate quarterly)
- DT_NSO_1900_016V1 (superseded by 010V1)

### Phase 2: Medium-Term Review (Requires NSO Inquiry)
**Consolidate with clarification** (6 tables):
- DT_NSO_1900_007V1 + DT_NSO_1900_007V12 → Merge or select primary
- DT_NSO_1900_013V1 + DT_NSO_1900_014V1 → Choose quintiles (014) OR deciles (013)
- DT_NSO_2300_020V1 vs DT_NSO_2300_022V1 → Clarify if both needed

### Phase 3: Enhancement (Optional)
- Translate DT_NSO_4000_001 SDG table title to English
- Request extended time series for poverty indicators (2021, 2023, 2024)

---

## Summary Table: All 38 Tables with Recommendations

| Table ID | Subsector | Title | Score | Status | Recommendation | Reason |
|----------|-----------|-------|-------|--------|-----------------|--------|
| DT_NSO_1003_001V1 | Food Security | Annual food consumption | 75 | Core | **KEEP** | Primary consumption measure |
| DT_NSO_2300_022V1 | Food Security | Prevalence of food insecurity (population) | 75 | Core | **KEEP** | Primary food insecurity measure |
| DT_NSO_2300_020V1 | Food Security | Prevalence of food insecurity (household) | 60 | Secondary | **DEPRECATE** | Household-level redundant with 022V1 |
| DT_NSO_1900_010V1 | Poverty | Minimum subsistence level | 75 | Core | **KEEP** | Current standard, long series |
| DT_NSO_1900_016V1 | Poverty | Minimum subsistence level (1999-2000) | 75 | Secondary | **DEPRECATE** | Historical; superseded by 010V1 |
| DT_NSO_1900_007V1 | Poverty | Poverty main indicators (1995-2020) | 72 | Core | **KEEP** | Long historical view |
| DT_NSO_1900_007V12 | Poverty | Poverty main indicators (2022) | 72 | Secondary | **MERGE** | Recent update; merge into 007V1 |
| DT_NSO_1900_008V1 | Poverty | Consumption by poverty status | 72 | Core | **KEEP** | Unique cross-tabulation |
| DT_NSO_1900_035V1 | Poverty | Poverty by aimag (2016-2020) | 62 | Core | **KEEP** | Regional detail |
| DT_NSO_1900_013V1 | Poverty | Consumption by household deciles | 60 | Secondary | **DEPRECATE** | Deciles redundant; keep quintiles (014) |
| DT_NSO_1900_014V1 | Poverty | Consumption shares by quintiles | 60 | Core | **KEEP** | Standard inequality measure |
| DT_NSO_1900_036V1 | Poverty | Inequality (Gini & Theil, annual) | 60 | Core | **KEEP** | Primary inequality indices |
| DT_NSO_2300_034V1 | Law & Crime | Recorded crime rate per 10,000 | 65 | Core | **KEEP** | Primary crime indicator |
| DT_NSO_2300_036V1 | Law & Crime | Resolved criminal cases per 10,000 | 65 | Core | **KEEP** | Justice system output |
| DT_NSO_2300_024V1 | Law & Crime | Livestock theft crime | 62 | Core | **KEEP** | Sector-specific indicator |
| DT_NSO_2300_001A4 | Law & Crime | Declarations of private interest | 60 | Core | **KEEP** | Corruption tracking |
| DT_NSO_2300_041V1 | Law & Crime | Resolved family law cases | 60 | Core | **KEEP** | Family law indicator |
| DT_NSO_1900_001V1 | Household Income | Income by location (1997-2024) | 60 | **BEST** | **KEEP** | Longest history; includes all locations |
| DT_NSO_1900_001V2 | Household Income | Income by region (2007-2024) | 60 | Secondary | **DEPRECATE** | Subset of V1; shorter period |
| DT_NSO_1900_002V1 | Household Income | Expenditure by location (1997-2024) | 60 | **BEST** | **KEEP** | Longest history; includes all locations |
| DT_NSO_1900_002V2 | Household Income | Expenditure by region (2007-2024) | 60 | Secondary | **DEPRECATE** | Subset of V1; shorter period |
| DT_NSO_1900_003V1 | Household Income | Income composition by location (1997-2024) | 60 | Core | **KEEP** | Shows income breakdown |
| DT_NSO_1900_003V2 | Household Income | Income composition by region (2007-2024) | 60 | Secondary | **DEPRECATE** | Subset of V1; shorter period |
| DT_NSO_1900_004V1 | Household Income | Expenditure composition by location (1997-2024) | 60 | Core | **KEEP** | Shows expenditure breakdown |
| DT_NSO_1900_004V2 | Household Income | Expenditure composition by region (2007-2024) | 60 | Secondary | **DEPRECATE** | Subset of V1; shorter period |
| DT_NSO_1900_015V1 | Household Income | Annual income (1966-1996) | 60 | Archival | **DEPRECATE** | Obsolete; modern series starts 1997 |
| DT_NSO_1900_017V1 | Household Income | Annual expenditure (1966-1996) | 60 | Archival | **DEPRECATE** | Obsolete; modern series starts 1997 |
| DT_NSO_1900_018V1 | Household Income | Quarterly income by location | 60 | Core | **KEEP** | Seasonal analysis |
| DT_NSO_1900_019V1 | Household Income | Quarterly expenditure by location | 60 | Core | **KEEP** | Seasonal analysis |
| DT_NSO_1900_020V1 | Household Income | Quarterly income composition by location | 60 | Secondary | **KEEP** | Complements 018V1 |
| DT_NSO_1900_021V1 | Household Income | Quarterly expenditure composition by location | 60 | Secondary | **KEEP** | Complements 019V1 |
| DT_NSO_1900_030V2 | Household Income | Quarterly income/expenditure grouping by quarter | 60 | Secondary | **DEPRECATE** | Redundant with 018/019/020/021 |
| DT_NSO_1900_032V1 | Household Income | Income grouping by year | 60 | Core | **KEEP** | Income distribution analysis |
| DT_NSO_1900_033V1 | Household Income | Expenditure grouping by year | 60 | Core | **KEEP** | Expenditure distribution analysis |
| DT_NSO_1900_036V2 | Household Income | Gini Index (quarterly, expenditure) | 60 | Core | **KEEP** | Quarterly inequality tracking |
| DT_NSO_1900_036V3 | Household Income | Theil Index (quarterly, expenditure) | 60 | Core | **KEEP** | Alternative inequality measure |
| Expenditure of Social Insurance | Social Insurance | Fund expenditure by type | 60 | Core | **KEEP** | Unique welfare metric |
| DT_NSO_4000_001 | SDG Indicators | [Title in Mongolian only] | 60 | Core | **CLARIFY** | Translate English title first |

---

## Conclusion

**Current Status**: 38 tables with 37-42% redundancy
**Recommendation**: Consolidate to 22-24 primary tables
**Complexity**: Most redundancy is version variants (V1/V2) and obsolete historical periods
**Action Items**:
1. Deprecate 8 clear redundancies immediately (Phase 1)
2. Resolve 6 decision points with NSO inquiry (Phase 2)
3. Enhance metadata and translations (Phase 3)

This consolidation will make the "Society, development" sector more navigable for users while preserving all essential data dimensions.
