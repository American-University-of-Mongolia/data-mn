# Industry, Service Sector - NSO Table Redundancy Analysis

**Total Tables Analyzed**: 16
**Analysis Date**: 2025-12-16

---

## Executive Summary

The Industry, service sector contains 16 tables across 8 subsectors. **5 concept groups have 2+ tables**, revealing significant redundancies:

1. **Trade (3 tables)**: Recommend DT_NSO_1600_001V1 (national-level annual trade turnover)
2. **Livestock (4 tables)**: Recommend DT_NSO_1001_001V1 (annual gross livestock output)
3. **Industry (2 tables)**: Recommend DT_NSO_1100_016V4 (industrial producer price index)
4. **Intellectual Property (2 tables)**: Both unique but complementary
5. **Tourism (2 tables)**: Recommend DT_NSO_1800_005V2 (detailed inbound foreign passengers)

**Actionable Result**: Remove 4 redundant tables, keep 12 core tables.

---

## Detailed Analysis by Concept Group

### 1. TRADE, HOTEL AND RESTAURANT (3 tables)

#### Comparison

| Table ID | Title | Dimensions | Temporal | Score | Recommendation |
|----------|-------|-----------|----------|-------|-----------------|
| **DT_NSO_1600_001V1** | Total Trade Turnover by trade sub-sector | Sub-sector × Year | Annual | 75 | **✓ BEST** |
| DT_NSO_1600_002V1_month | Total Trade Turnover by region | Region × Month | Monthly | 65 | REDUNDANT |
| DT_NSO_1600_002V1_year | Total Trade Turnover by region | Region × Year | Annual | 65 | REDUNDANT |
| DT_NSO_1602_002V1 | Income of Food Service Sector | Region × Month | Monthly | 60 | SPECIALIZED |

#### Analysis

**Best Table**: `DT_NSO_1600_001V1` (Score: 75)
- **Why**: Provides comprehensive national-level trade turnover by sub-sector (hotels, restaurants, wholesale, retail) with annual granularity
- **Audience**: Business analysts, policy makers, students studying trade sector trends
- **Coverage**: Complete picture without geographic drill-down
- **Credibility**: Highest score in group

**Redundant Tables**:
- `DT_NSO_1600_002V1_month` & `DT_NSO_1600_002V1_year`: These are geographic splits (by region/aimag) of the same underlying data. While useful for regional analysis, they complicate the data catalog and are less useful for general analysis.
  - **Action**: Deprecate both; users needing regional data can contact NSO directly or use parent table

**Specialized Table**:
- `DT_NSO_1602_002V1` (Food Service Income): Very narrow focus on food service only. This is complementary to the main trade table rather than redundant.
  - **Action**: Keep as specialized dataset for hospitality research

#### Recommendation
- **Keep**: DT_NSO_1600_001V1 (main), DT_NSO_1602_002V1 (specialized)
- **Remove**: DT_NSO_1600_002V1_month, DT_NSO_1600_002V1_year

---

### 2. LIVESTOCK (4 tables)

#### Comparison

| Table ID | Title | Metric | Temporal | Score | Recommendation |
|----------|-------|--------|----------|-------|-----------------|
| **DT_NSO_1001_001V1** | Gross Livestock Output | Production value | Annual | 72 | **✓ BEST** |
| DT_NSO_1001_008V1 | Number of Survival | Head count | Quarterly | 62 | REDUNDANT |
| DT_NSO_1001_011V1 | Losses of Adult Animals | Mortality count | Quarterly | 62 | OPERATIONAL |
| DT_NSO_1001_040V2 | Market Price of Livestock Products | Price index | Monthly | 62 | OPERATIONAL |

#### Analysis

**Best Table**: `DT_NSO_1001_001V1` (Score: 72)
- **Why**: Captures total livestock economic output in monetary value, most relevant for business/economic analysis
- **Audience**: Farmers, agricultural businesses, policy makers, economists
- **Coverage**: Annual granularity sufficient for strategic decisions
- **Credibility**: Highest score in livestock group

**Redundant Tables**:
- `DT_NSO_1001_008V1` (Survival/Head Count): Shows livestock population by type and region. While informative, the GROSS OUTPUT table encompasses this information in economic terms.
  - **Action**: Deprecate; more granular than needed for general analysis

**Operational Tables** (Keep - serve specific business needs):
- `DT_NSO_1001_011V1` (Animal Losses): Mortality data crucial for farmers to understand herd health and production risk
  - **Action**: Keep; complements gross output with operational risk insights
- `DT_NSO_1001_040V2` (Market Prices): Essential for farmers and traders to price products and understand market dynamics
  - **Action**: Keep; critical for business decision-making

#### Recommendation
- **Keep**: DT_NSO_1001_001V1 (overview), DT_NSO_1001_011V1 (risk), DT_NSO_1001_040V2 (pricing)
- **Remove**: DT_NSO_1001_008V1

---

### 3. INDUSTRY (2 tables)

#### Comparison

| Table ID | Title | Metric | Coverage | Score | Recommendation |
|----------|-------|--------|----------|-------|-----------------|
| **DT_NSO_1100_016V4** | Industrial Producer Price Index | Price index (2015=100) | By division × month | 60 | **✓ BEST** |
| DT_NSO_1100_010V1 | Balance of Coal | Tons | Annual | 60 | SPECIALIZED |

#### Analysis

**Best Table**: `DT_NSO_1100_016V4` (Score: 60)
- **Why**: Covers all industrial sectors with time-series price data (indexed to 2015), allowing comparison across industries and tracking inflation trends
- **Audience**: Economists, industrial sector analysts, financial planners, policy makers
- **Coverage**: Broad industrial coverage; monthly updates show market dynamics

**Specialized Table**:
- `DT_NSO_1100_010V1` (Coal Balance): Highly specific to the coal sector, measuring supply/demand balance in physical units (tons)
  - **Action**: Keep as specialized dataset; not redundant with price index; serves mining/energy sector specifically

#### Recommendation
- **Keep**: Both tables (different purposes)
  - Primary: DT_NSO_1100_016V4 (general industrial insights)
  - Specialized: DT_NSO_1100_010V1 (coal sector analysis)

---

### 4. CONSTRUCTION (1 table)

#### Analysis

| Table ID | Title | Metric | Score |
|----------|-------|--------|-------|
| DT_NSO_1100_015V2 | Construction Cost Index | Index by construction type | 60 |

**Status**: No redundancy. Single table covering construction costs by type with quarterly granularity.

#### Recommendation
- **Keep**: DT_NSO_1100_015V2 (no alternatives available)

---

### 5. INTELLECTUAL PROPERTY (2 tables)

#### Comparison

| Table ID | Title | Coverage | Score | Recommendation |
|----------|-------|----------|-------|-----------------|
| **COPYRIGHT, BY TYPES OF WORK** | Works protected | By work type | 60 | **✓ KEEP** |
| **THE WORKS PROTECTED BY COPYRIGHT** | Protected works inventory | Detailed works | 60 | **✓ KEEP** |

#### Analysis

These two tables appear to serve different purposes within copyright tracking:
- First focuses on **types of work** (patents, designs, trademarks, literary works, etc.)
- Second focuses on **actual protected works** (inventory/catalog of registered works)

Both are complementary; no clear redundancy without seeing the actual data dimensions.

#### Recommendation
- **Keep**: Both tables (appear complementary; need data inspection to confirm)

---

### 6. TOURISM (2 tables)

#### Comparison

| Table ID | Title | Dimensions | Score | Recommendation |
|----------|-------|-----------|-------|-----------------|
| **DT_NSO_1800_005V2** | Inbound Foreign Passengers | By purpose, region, year | 60 | **✓ BEST** |
| Number of inbound and outbound foreign passengers by country of origin | Passenger flow by country | By country, direction | 60 | REDUNDANT |

#### Analysis

**Best Table**: `DT_NSO_1800_005V2` (Score: 60)
- **Why**: Captures WHY tourists visit (purpose) and WHERE they come FROM (geographical region) with annual data
- **Audience**: Tourism industry analysts, hospitality business operators, policy makers
- **Coverage**: More strategic (purpose-driven) than simple passenger counts

**Redundant Table**:
- `Number of inbound and outbound foreign passengers by country of origin`: Provides country-of-origin breakdown but lacks PURPOSE dimension; more granular but less strategically useful
  - **Action**: Deprecate; country-level detail not essential for general tourism analysis

#### Recommendation
- **Keep**: DT_NSO_1800_005V2 (strategic overview)
- **Remove**: "Number of inbound and outbound foreign passengers by country of origin"

---

### 7. TRANSPORTATION (1 table)

#### Analysis

| Table ID | Title | Metric | Score |
|----------|-------|--------|-------|
| DT_NSO_1200_013V5 | Number of Imported Vehicles | By country, vehicle type | 75 |

**Status**: No redundancy. Single table covering vehicle imports with detailed breakdown.

#### Recommendation
- **Keep**: DT_NSO_1200_013V5 (no alternatives; highest score in sector)

---

## Summary of Actions

### Tables to Keep (12 total)

| Subsector | Table ID | Rationale |
|-----------|----------|-----------|
| Trade | DT_NSO_1600_001V1 | National trade turnover (best score) |
| Trade | DT_NSO_1602_002V1 | Specialized food service data |
| Livestock | DT_NSO_1001_001V1 | Gross livestock output (best score) |
| Livestock | DT_NSO_1001_011V1 | Animal losses (operational insights) |
| Livestock | DT_NSO_1001_040V2 | Market prices (business critical) |
| Industry | DT_NSO_1100_016V4 | Industrial producer price index |
| Industry | DT_NSO_1100_010V1 | Coal balance (specialized) |
| Construction | DT_NSO_1100_015V2 | Construction cost index |
| Transportation | DT_NSO_1200_013V5 | Imported vehicles |
| Intellectual Property | COPYRIGHT, BY TYPES OF WORK | Complementary |
| Intellectual Property | THE WORKS PROTECTED BY COPYRIGHT | Complementary |
| Tourism | DT_NSO_1800_005V2 | Inbound passengers by purpose/region |

### Tables to Remove (4 total)

| Subsector | Table ID | Reason |
|-----------|----------|--------|
| Trade | DT_NSO_1600_002V1_month | Geographic split; regional drill-down not essential |
| Trade | DT_NSO_1600_002V1_year | Geographic split; redundant with DT_NSO_1600_001V1 |
| Livestock | DT_NSO_1001_008V1 | Redundant with gross output (stock count captured in economics) |
| Tourism | Number of inbound/outbound by country | Country detail not essential; purpose dimension more strategic |

---

## Recommendations for Data.mn

1. **Immediate**: Add the 12 "Keep" tables to data.mn catalog
2. **Deprecation**: Mark the 4 redundant tables as deprecated with reason and successor table link
3. **Priority Order** (by score):
   - High (score 70+): DT_NSO_1001_001V1, DT_NSO_1600_001V1, DT_NSO_1200_013V5
   - Medium (60-69): All others
4. **Specialized Focus**: Consider creating splits for:
   - Livestock: "Market Prices" as separate dataset for farmer/trader audience
   - Trade: "Food Service Income" as separate hospitality dataset
5. **Geographic Data**: If regional drill-down is needed, users should request custom NSO reports rather than adding geographic variations to the catalog

---

## Data Quality Notes

All tables marked "T2-Recommended" by NSO, indicating they are quality-verified and suitable for publication. The grouping above is based on logical overlap and strategic value for different user personas (business people, students, professionals).
