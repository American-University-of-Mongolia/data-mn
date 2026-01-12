# NSO Population & Household Sector Analysis
## Redundancy Assessment and Recommendations

**Analyzed Date**: 2025-12-16
**Sector**: Population, household
**Total Tables**: 19
**Subsectors**: 4 (Population, Regular movement, Herdsmen, Infrastructure/housing)

---

## Executive Summary

The Population & Household sector contains **19 NSO tables** distributed across 4 subsectors. Analysis reveals **clear redundancies within concept groups**, with multiple tables covering the same demographic dimensions at different levels of detail.

**Key Finding**: There are **8 conceptual groups**, of which **5 have redundancy issues**. The analysis identifies a single "best" table for each concept suitable for business professionals, students, and general users.

---

## Concept Groups & Redundancy Analysis

### 1. POPULATION BY AGE & SEX (Single-Year Detail)

**Purpose**: Detailed population counts by individual age years and gender

| Table ID | Title | Score | Differences | Assessment |
|----------|-------|-------|-------------|------------|
| DT_NSO_0300_001V2.px | **RESIDENT POPULATION** by sex, single year, year | 75 | Resident population definition | BEST |
| DT_NSO_0300_001V3.px | **POPULATION** by sex, single year, year | 75 | Total population definition | REDUNDANT |

**Recommendation**:
- **KEEP**: `DT_NSO_0300_001V2.px` (Resident Population)
  - More precise for demographic analysis
  - Aligns with census methodology
  - Better for international comparisons
- **DEPRECATE**: `DT_NSO_0300_001V3.px`
  - Duplicate with different population base
  - Total population less useful for single-year granularity

**Why**: Residents provide legally resident population; total includes temporary/registered visitors with less demographic relevance.

---

### 2. POPULATION BY AGE GROUPS & SEX (Grouped Ages)

**Purpose**: Population counts using age bands (5-year, 10-year groups) instead of single years

| Table ID | Title | Score | Details |
|----------|-------|-------|---------|
| DT_NSO_0300_003V1.px | **POPULATION by age group and year** | 75 | By Sex, Age group, Year |

**Recommendation**:
- **KEEP**: `DT_NSO_0300_003V1.px` (ONLY TABLE IN GROUP)
  - No redundancy
  - Better for aggregate analysis
  - Easier interpretation for stakeholders

**Note**: This complements the single-year table; both should be retained as they serve different use cases.

---

### 3. POPULATION BY LOCATION (Urban/Rural)

**Purpose**: Population distribution between urban and rural areas

| Table ID | Title | Score | Differences | Assessment |
|----------|-------|-------|-------------|------------|
| DT_NSO_0300_027V1.px | **POPULATION by location, sex, year** | 75 | National summary by location | BEST |
| DT_NSO_0300_002V1.px | **MID-YEAR TOTAL POPULATION by aimags and Capital** | 65 | Regional breakdown | DERIVATIVE |
| DT_NSO_0300_004V1.px | **POPULATION by location, aimags and Capital, year** | 65 | Location + regional breakdown | DERIVATIVE |

**Recommendation**:
- **KEEP**: `DT_NSO_0300_027V1.px` (Population by Location)
  - Higher score (75)
  - Cleanest urban/rural distinction
  - National view for overall trends
- **CONDITIONAL KEEP**: `DT_NSO_0300_002V1.px` or `DT_NSO_0300_004V1.px`
  - Tables 002 and 004 are quasi-redundant (both have regional + location data)
  - **Recommend keeping 004 over 002** (more detailed dimensions)
  - Lower scores reflect duplicated dimensions
- **DEPRECATE**: `DT_NSO_0300_002V1.px`
  - Same data as 004 but fewer dimensions
  - Mid-year timing less critical for annual reporting

**Why**: Table 027 provides the core urban/rural split. Tables 002/004 add regional context but duplicate each other's geography.

---

### 4. POPULATION MIGRATION (Domestic Movement)

**Purpose**: Population movement between regions (in-migration, out-migration, net migration)

| Table ID | Title | Score | Details | Assessment |
|----------|-------|-------|---------|------------|
| DT_NSO_0300_040V1.px | **POPULATION MIGRATION by aimags, Capital, year** | 65 | Indicator, Region, Year | ONLY |

**Recommendation**:
- **KEEP**: `DT_NSO_0300_040V1.px` (ONLY TABLE IN GROUP)
  - No redundancy
  - Critical for understanding regional population dynamics
  - Important for labor market and urban development analysis

---

### 5. VITAL STATISTICS (Births, Deaths, Natural Increase)

**Purpose**: Population dynamics measured as rates (per 1000 population)

| Table ID | Title | Score | Coverage | Assessment |
|----------|-------|-------|----------|------------|
| DT_NSO_0300_001V1.px | **BIRTHS, DEATHS, NATURAL INCREASE per 1000** by aimags, quarter | 65 | Quarterly, regional | BEST |
| DT_NSO_0300_024V1.px | **BIRTH, DEATH, NATURAL INCREASE per 1000** by aimag/Capital, year | 65 | Annual, regional | EQUIVALENT |
| DT_NSO_0300_029V1.px | **BIRTH RATES by age group, year** | 72 | Age-specific rates | SPECIALIZED |

**Recommendation**:
- **KEEP**: `DT_NSO_0300_001V1.px` (Quarterly data)
  - Higher temporal granularity
  - Allows trend analysis beyond annual patterns
  - Quarterly data can be aggregated to annual
- **DEPRECATE**: `DT_NSO_0300_024V1.px`
  - Duplicate annual data (covered in 001V1 aggregated)
  - Redundant with quarterly table
- **KEEP**: `DT_NSO_0300_029V1.px` (Birth Rates by Age)
  - Different dimension (age-specific, not regional)
  - Complements regional table; no true redundancy
  - Essential for fertility analysis and population projections

**Why**: Quarterly births/deaths subsume annual data. Age-specific rates are complementary demographic measures.

---

### 6. FAMILY FORMATION (Marriages & Divorces)

**Purpose**: Marriage and divorce rates as population indicators

| Table ID | Title | Score | Coverage | Assessment |
|----------|-------|-------|----------|------------|
| DT_NSO_0300_020V1.px | **MARRIAGES AND DIVORCES per 1000 population** by marital status, region, year | 65 | Regional, annual | ONLY |

**Recommendation**:
- **KEEP**: `DT_NSO_0300_020V1.px` (ONLY TABLE IN GROUP)
  - No redundancy
  - Family formation essential for demographic analysis
  - Critical for social trend analysis

---

### 7. ADOPTION (Family Formation/Household Composition)

**Purpose**: Adoption rates as indicator of family structure changes

| Table ID | Title | Score | Coverage | Assessment |
|----------|-------|-------|----------|------------|
| DT_NSO_0300_052V1.px | **ADOPTION per 1000 population** by indicator, region, year | 65 | Regional, annual | ONLY |

**Recommendation**:
- **KEEP**: `DT_NSO_0300_052V1.px` (ONLY TABLE IN GROUP)
  - No redundancy
  - Limited audience but important for social scientists
  - Niche but necessary for comprehensive household data

**Note**: Adoption is a lower-priority table; could be deprecated if data.mn focuses only on major indicators.

---

### 8. POPULATION PROJECTION (2020-2050)

**Purpose**: Future population estimates under different scenarios

| Table ID | Title | Score | Scenario | Differences | Assessment |
|----------|-------|-------|----------|-------------|------------|
| DT_NSO_0300_076V12.px | **PROJECTION by sex, age, medium scenario 1B** (Resident base) | 75 | Scenario 1B | National, by age/sex | BEST |
| DT_NSO_0300_076V13.px | **PROJECTION by sex, age, medium scenario 2B** (Total pop base) | 75 | Scenario 2B | National, by age/sex | REDUNDANT BASE |
| DT_NSO_0300_076V11.px | **PROJECTION by sex, age, aimags, scenario 1B** | 65 | Scenario 1B | Regional detail | DERIVATIVE |

**Recommendation**:
- **KEEP**: `DT_NSO_0300_076V12.px` (Scenario 1B, National)
  - Based on Resident Population (methodology-consistent)
  - Higher score and simpler dimensions
  - Standard for national planning
- **DEPRECATE**: `DT_NSO_0300_076V13.px`
  - Same time period and granularity as V12
  - Different population base (Total vs. Resident) unnecessarily confuses
  - Two scenarios of same model is redundant; keep primary scenario
- **CONDITIONAL KEEP**: `DT_NSO_0300_076V11.px`
  - Regional breakdown adds value if there's demand
  - Complements national table for regional planning
  - Score of 65 (vs. 75) suggests regional detail is secondary priority
  - Recommendation: Keep if regional planning is priority; deprecate if resource-constrained

**Why**: Projection tables with different population bases (Resident vs. Total) are methodologically confusing. Scenario 1B should be the standard. Regional projections (V11) are complementary but lower priority.

---

### 9. HERDING HOUSEHOLDS (Livestock)

**Purpose**: Household classification for herding populations

| Table ID | Title | Score | Coverage | Assessment |
|----------|-------|-------|----------|------------|
| DT_NSO_1001_031V1.px | **GROUPING OF LIVESTOCK by herder households** | 62 | Herder households, region, year | ONLY |

**Recommendation**:
- **KEEP**: `DT_NSO_1001_031V1.px` (ONLY TABLE IN GROUP)
  - Unique demographic segment
  - Important for rural economy analysis
  - Lower score reflects niche audience
  - Keep if livestock/rural focus is priority

**Note**: This table is from a different NSO series (1001, not 0300), indicating it's a specialized subset.

---

### 10. HOUSING INFRASTRUCTURE (Dwellings)

**Purpose**: Housing stock characteristics and utilities

| Table ID | Title | Score | Dimension | Assessment |
|----------|-------|-------|-----------|------------|
| DT_NSO_3500_003V0.px | **NUMBER OF HOUSES by type, room count, census year** | 60 | Type + rooms | BEST |
| DT_NSO_3500_003V2.px | **NUMBER OF DWELLINGS by type, floor material, census year** | 60 | Type + floor material | EQUIVALENT |
| DT_NSO_3500_005V1.px | **HOUSEHOLDS IN APARTMENTS with centralized systems** | 60 | Utility access | SPECIALIZED |

**Recommendation**:
- **KEEP**: `DT_NSO_3500_003V0.px` (Houses by Type & Rooms)
  - Most useful dimension for real estate/urban planning
  - Room count is more actionable than floor material
- **DEPRECATE**: `DT_NSO_3500_003V2.px`
  - Duplicate housing stock data
  - Floor material less relevant for policy than type + rooms
  - Same dimensions as 003V0 but different secondary variable
- **KEEP**: `DT_NSO_3500_005V1.px` (Utility Access)
  - Different dimension (infrastructure access vs. type)
  - Complements physical housing with service access
  - Important for urban development and quality of life analysis

**Why**: Tables 003V0 and 003V2 both categorize the housing stock with different secondary splits. Keep the more useful (rooms). Table 005 is complementary, not redundant.

---

## Summary Table: Recommendations by Action

### KEEP (High Priority)
- `DT_NSO_0300_001V2.px` - Resident Population by Age & Sex (single-year)
- `DT_NSO_0300_003V1.px` - Population by Age Group & Sex
- `DT_NSO_0300_027V1.px` - Population by Location
- `DT_NSO_0300_004V1.px` - Population by Location + Region
- `DT_NSO_0300_040V1.px` - Population Migration
- `DT_NSO_0300_001V1.px` - Vital Statistics (Quarterly)
- `DT_NSO_0300_029V1.px` - Birth Rates by Age
- `DT_NSO_0300_020V1.px` - Marriages & Divorces
- `DT_NSO_3500_003V0.px` - Houses by Type & Rooms

**Total: 9 tables**

### CONDITIONAL KEEP (Specialized/Niche)
- `DT_NSO_0300_076V12.px` - Population Projection (Scenario 1B)
- `DT_NSO_0300_076V11.px` - Population Projection Regional (if regional planning is priority)
- `DT_NSO_1001_031V1.px` - Herding Households (if livestock/rural focus)
- `DT_NSO_0300_052V1.px` - Adoption Rates (if comprehensive family data needed)
- `DT_NSO_3500_005V1.px` - Household Utilities (if infrastructure focus)

**Total: 5 tables (depending on priorities)**

### DEPRECATE (Redundant)
- `DT_NSO_0300_001V3.px` - Total Population (duplicate of Resident, less useful)
- `DT_NSO_0300_002V1.px` - Mid-Year Population by Region (covered by 004 with better dimensions)
- `DT_NSO_0300_024V1.px` - Annual Vital Stats (covered by quarterly 001V1)
- `DT_NSO_0300_076V13.px` - Projection Scenario 2B (methodologically confusing with V12)
- `DT_NSO_3500_003V2.px` - Houses by Floor Material (covered by 003V0 with better dimensions)

**Total: 5 tables**

---

## Key Insights for Data.mn Platform

### Tier 1: Core Essential Tables (Always Include)
These represent the minimal dataset needed for population analysis:
1. Population by age & sex (single-year): **DT_NSO_0300_001V2.px**
2. Population by age groups & sex: **DT_NSO_0300_003V1.px**
3. Population by location (urban/rural): **DT_NSO_0300_027V1.px**
4. Population migration: **DT_NSO_0300_040V1.px**
5. Vital statistics (births/deaths): **DT_NSO_0300_001V1.px**
6. Housing characteristics: **DT_NSO_3500_003V0.px**

### Tier 2: Demographic Specialists
Additional tables for advanced analysis:
- Birth rates by age: **DT_NSO_0300_029V1.px** (fertility, projections)
- Marriages & divorces: **DT_NSO_0300_020V1.px** (family formation)
- Population projection: **DT_NSO_0300_076V12.px** (future planning)
- Regional breakdown: **DT_NSO_0300_004V1.px** (geographic analysis)

### Tier 3: Specialized/Lower Priority
Niche audiences only:
- Regional projections: **DT_NSO_0300_076V11.px**
- Herding households: **DT_NSO_1001_031V1.px**
- Adoption rates: **DT_NSO_0300_052V1.px**
- Household utilities: **DT_NSO_3500_005V1.px**

---

## Redundancy Patterns Observed

1. **Population Base Confusion**: V2 vs. V3 tables use "Resident" vs. "Total" population definitions. Choose one standard.

2. **Temporal Granularity**: Quarterly and annual data on same metric (vital statistics) - quarterly is superior.

3. **Geographic Redundancy**: Multiple tables with Region + Location dimensions - consolidate to avoid confusion.

4. **Housing Splits**: Two tables split the same data (dwellings) by different secondary dimensions. Keep the more useful one.

5. **Projection Scenarios**: Multiple scenarios of same projection model - standardize on primary scenario.

---

## Recommendations for Data.mn Implementation

1. **Start with Tier 1**: These 6 tables provide complete core demographic data
2. **Add Tier 2 selectively**: Birth rates and vital stats are high-value for students/researchers
3. **Label clearly**: When multiple tables exist (e.g., single-year vs. age groups), explain the difference
4. **Create splits**: Consider creating filtered views:
   - Population pyramid (age/sex specific)
   - Urban vs. rural trends (location specific)
   - Regional breakdowns (for regional analysis)
5. **Deprecate thoughtfully**: Don't add redundant tables; redirect users to recommended table

---

## Notes on Scoring

Table scores (60-75) appear to reflect data quality and completeness, not redundancy. Redundancy assessment focuses on:
- Conceptual overlap (same population dimension measured multiple ways)
- Additive value (does this table add new insights?)
- Audience usefulness (is it the best choice for the target user?)

Redundancy ≠ Low Score: Some low-scoring tables (e.g., adoption at 62) are not redundant, just lower priority.
