# Education & Health Sector Analysis - Redundancy Report

**Analysis Date**: 2025-12-16
**Sector**: Education, health
**Total Tables**: 16
**Status**: 16 tables analyzed for redundancy

---

## Executive Summary

The Education & Health sector contains **significant redundancies** across 5 concept groups:

| Concept | Tables | Redundant | Recommendation |
|---------|--------|-----------|-----------------|
| **Infant & Neonatal Mortality** | 3 | 2 | Keep DT_NSO_2100_014V2.px |
| **Health Insurance Fund** | 3 | 2 | Keep DT_NSO_2100_30V001.px |
| **Cancer Statistics** | 2 | 1 | Keep DT_NSO_2100_045V1.px |
| **Primary Education Enrollment** | 1 | 0 | Keep DT_NSO_2002_065V1.px |
| **Births & Demographic** | 5 | 0 | Keep all (different metrics) |

**Potential Coverage**: After deduplication, 11 unique datasets would remain (vs 16 currently).

---

## Detailed Analysis by Concept Group

### 1. Infant & Neonatal Mortality (3 tables)

**Group Concept**: Child mortality rates broken down by region and time period.

| Table ID | Title | Subsector | Dimensions | Score |
|----------|-------|-----------|-----------|-------|
| **DT_NSO_2100_014V2.px** ✓ BEST | **INFANT MORTALITY RATE**, per 1000 live births, aimags and the Capital and by month | Births, deaths | Region × Month | 62 |
| **DT_NSO_2100_015V1.px** ✗ REDUNDANT | **INFANT MORTALITY RATE**, per 1000 live births, aimags and the Capital and by month | Births, deaths | Region × Month | 62 |
| **DT_NSO_2100_040V2.px** ✗ REDUNDANT | **NEONATAL MORTALITY RATE**, per 1000 live births, aimags and the Capital and by month | Births, deaths | Region × Month | 62 |

**Analysis**:
- `DT_NSO_2100_014V2.px` and `DT_NSO_2100_015V1.px` have **identical titles and structure**
  - Same metric: Infant mortality rate per 1000 live births
  - Same dimensions: Region (aimags + Capital) × Month
  - Same score: 62
  - These are exact duplicates
- `DT_NSO_2100_040V2.px` measures a related but distinct metric: **neonatal mortality** (subset of infant mortality: first 28 days of life)
  - Technically different demographic indicator
  - However, follows same pattern as infant mortality table

**Recommendation**:
- **BEST**: Keep **DT_NSO_2100_014V2.px** (infant mortality) - broader indicator, more commonly requested
- **DELETE**: **DT_NSO_2100_015V1.px** - exact duplicate
- **CONSIDER**: Whether to keep **DT_NSO_2100_040V2.px** separately
  - If users need neonatal-specific data: Keep it (specialized demographic metric)
  - If duplication must be minimized: Neonatal data could be a filtered split of the infant table
  - **Recommendation**: Keep separate (neonatal is specific indicator for demographers/health policy)

**For Business Users**: Use **DT_NSO_2100_014V2.px** for infant survival trends by region.

---

### 2. Health Insurance Fund Revenue/Expenditure (3 tables)

**Group Concept**: Health insurance system financial data with different time aggregation levels.

| Table ID | Title | Dimensions | Granularity | Score |
|----------|-------|-----------|-------------|-------|
| **DT_NSO_2100_30V001.px** ✓ BEST | **REVENUE AND EXPENDITURE OF HEALTH INSURANCE FUND**, by type, and by **year** | Indicator × Year | Annual | 60 |
| **DT_NSO_2100_033V1.px** (appears 2x) ✗ REDUNDANT | **REVENUE AND EXPENDITURE OF HEALTH INSURANCE FUND**, by type, and by **month (cumulative)** | Indicator × Month | Monthly (cumulative) | 60 |
| **DT_NSO_2100_033V1.px** (row 12) | Same as above | Indicator × Month | Monthly (cumulative) | 60 |

**Analysis**:
- `DT_NSO_2100_033V1.px` appears **twice in the dataset** (rows 12-15 and 126-131)
  - Identical table, appearing with different subsector labels
  - Row 12: Subsector = "Health insurance"
  - Row 126: Subsector = "Main indicators for Health sector"
  - This is a **duplicate entry** in the sector list
- `DT_NSO_2100_30V001.px` provides **annual aggregation** (standard reporting period)
- `DT_NSO_2100_033V1.px` provides **monthly cumulative data** (operational monitoring)

**Recommendation**:
- **BEST**: Keep **DT_NSO_2100_30V001.px** (annual data for most users)
- **DELETE**: Remove duplicate entry of `DT_NSO_2100_033V1.px` from row 126-131
- **OPTIONAL**: Keep monthly table if real-time monitoring is needed, but it's less useful for most audiences
  - **Decision**: Delete the monthly table for simplicity; annual suffices for business reporting

**For Business Users**: Use **DT_NSO_2100_30V001.px** for year-over-year health insurance trends.

---

### 3. Cancer Statistics (2 tables)

**Group Concept**: Cancer incidence and mortality across Mongolia.

| Table ID | Title | Metric | Dimensions | Score |
|----------|-------|--------|-----------|-------|
| **DT_NSO_2100_045V1.px** ✓ BEST | **NEW CASES AND MORTALITY OF CANCER** (combined), per 10000 population | Incidence + Mortality | Region × Year | 65 |
| **DT_NSO_2100_012V1.px** ✗ REDUNDANT | **NEW CASES OF CANCER**, per 10000 population | Incidence only | Cancer type × Year | 75 |
| **DT_NSO_2100_013V1.px** ✗ REDUNDANT | **DEATHS OF CANCER**, per 10000 population | Mortality only | Year only | 75 |

**Analysis**:
- `DT_NSO_2100_045V1.px` combines both incidence and mortality with **geographic breakdown** (aimags + Capital)
  - Shows where cancer cases and deaths occur (policy-relevant)
  - Enables regional health planning
- `DT_NSO_2100_012V1.px` breaks down incidence by **cancer type** but lacks geography
- `DT_NSO_2100_013V1.px` shows mortality without geographic or type detail

**Hierarchy**:
```
DT_NSO_2100_045V1.px (BEST) ← Most comprehensive for decision-makers
  ├─ Shows incidence + mortality by region
  └─ Enables comparative analysis across aimags

DT_NSO_2100_012V1.px (GOOD but supplementary)
  ├─ Incidence by cancer type
  └─ Use if detailed medical breakdown needed

DT_NSO_2100_013V1.px (REDUNDANT)
  └─ Mortality data is already in DT_NSO_2100_045V1.px
```

**Recommendation**:
- **BEST**: Keep **DT_NSO_2100_045V1.px** (regional overview, highest decision-making value)
- **OPTIONAL**: Keep **DT_NSO_2100_012V1.px** if cancer type breakdown is needed (scores higher at 75)
  - Medical professionals may need cancer-type detail
  - Recommend as supplementary dataset
- **DELETE**: **DT_NSO_2100_013V1.px** (redundant; mortality data in table 045)

**For Business Users**: Use **DT_NSO_2100_045V1.px** for cancer burden by region. Use **DT_NSO_2100_012V1.px** as supplement if detailed type breakdown is needed.

---

### 4. Births & Demographic Indicators (5 tables)

**Group Concept**: Birth rates, fertility, and reproductive health at different demographic levels.

| Table ID | Title | Metric | Dimensions | Score |
|----------|-------|--------|-----------|-------|
| **DT_NSO_0300_029V1.px** ✓ | **BIRTH RATES**, by year | Overall birth rate | Age group × Year | 72 |
| **DT_NSO_2100_047V1.px** ✓ | **ADOLESCENT BIRTH RATE** (ages 10-14, 15-19) | Adolescent fertility | Age bracket × Region × Year | 62 |
| **DT_NSO_2100_051V1.px** ✓ | **FAMILY PLANNING DEMAND** (% women 15-49 unmet need) | Contraceptive coverage | Indicators × Time | 60 |
| **DT_NSO_0300_071V02.px** ✗ | **INPATIENTS PER 10000 POPULATION** (10 leading diseases) | Health service use | Disease × Year | 75 |

**Analysis**:
- These tables represent **distinct demographic/reproductive health metrics**, not redundancies
  - Birth rates (overall fertility): DT_NSO_0300_029V1.px
  - Adolescent-specific fertility: DT_NSO_2100_047V1.px (important for youth health)
  - Family planning/contraceptive use: DT_NSO_2100_051V1.px (reproductive health)
  - Inpatient health service data: DT_NSO_0300_071V02.px (healthcare access)
- Each serves a different analytical purpose:
  - Demographers need birth rates
  - Youth health programs need adolescent rates
  - Family planning programs need contraceptive coverage
  - Health systems need inpatient data

**Recommendation**:
- **KEEP ALL** - These are complementary indicators, not redundant
- All represent core demographic/health indicators that shouldn't be merged

---

### 5. Education Indicators (2 tables, 1 standalone)

**Group Concept**: Education sector metrics.

| Table ID | Title | Metric | Dimensions | Score |
|----------|-------|--------|-----------|-------|
| **DT_NSO_2002_065V1.px** ✓ | **NET INTAKE RATE (NIR) IN FIRST GRADE** | School enrollment | Sex × Region × Year | 60 |
| **DT_NSO_2002_055V1.px** ✓ | **EXPENDITURE ON EDUCATIONAL SECTOR**, by type and year | Education spending | Type × Year | 60 |

**Analysis**:
- No redundancy: These are distinct metrics
  - Enrollment: Who is accessing primary education
  - Expenditure: How much is being spent on education
  - Together: Needed to assess education system efficiency

**Recommendation**:
- **KEEP BOTH** - Complementary education indicators

---

### 6. Health Sector Expenditure

**Group Concept**: Health system spending.

| Table ID | Title | Metric | Dimensions | Score |
|----------|-------|--------|-----------|-------|
| **DT_NSO_2100_030V1.px** ✓ BEST | **EXPENDITURE ON HEALTH SECTOR**, by year | Overall health spending | Indicator × Year | 60 |

**Analysis**:
- Unique indicator, no redundancy
- Complements health insurance fund data (broader health spending)

**Recommendation**:
- **KEEP** - Important macro health indicator

---

## Redundancy Summary Table

| Concept | Best Table | Redundant Tables | Action |
|---------|-----------|------------------|--------|
| **Infant Mortality** | DT_NSO_2100_014V2.px | DT_NSO_2100_015V1.px | DELETE duplicate |
| **Neonatal Mortality** | DT_NSO_2100_040V2.px | (specialized; optional) | KEEP (if neonatal-specific data needed) |
| **Health Insurance Fund** | DT_NSO_2100_30V001.px | DT_NSO_2100_033V1.px (2 entries) | DELETE monthly version + duplicate entry |
| **Cancer Stats** | DT_NSO_2100_045V1.px | DT_NSO_2100_013V1.px | DELETE mortality-only table |
| **Cancer Type Detail** | DT_NSO_2100_012V1.px | (supplementary) | KEEP as optional supplement |
| **Birth Rates** | DT_NSO_0300_029V1.px | (none) | KEEP |
| **Adolescent Fertility** | DT_NSO_2100_047V1.px | (none) | KEEP |
| **Family Planning** | DT_NSO_2100_051V1.px | (none) | KEEP |
| **Inpatients/Health Service** | DT_NSO_0300_071V02.px | (none) | KEEP |
| **Education Enrollment** | DT_NSO_2002_065V1.px | (none) | KEEP |
| **Education Spending** | DT_NSO_2002_055V1.px | (none) | KEEP |
| **Health Spending** | DT_NSO_2100_030V1.px | (none) | KEEP |

---

## Deduplication Recommendations

### Immediate Actions (High Confidence)

1. **DELETE DT_NSO_2100_015V1.px**
   - Exact duplicate of DT_NSO_2100_014V2.px
   - Loss: None
   - Reason: Identical table

2. **DELETE duplicate entry of DT_NSO_2100_033V1.px** (row 126-131)
   - Same table appears twice in sector list
   - Loss: None (keeping monthly version once if needed)
   - Reason: Data entry error

3. **DELETE DT_NSO_2100_013V1.px**
   - Cancer mortality-only table
   - Loss: Separate mortality aggregation (but available in combined table DT_NSO_2100_045V1.px)
   - Reason: DT_NSO_2100_045V1.px provides same data with geographic detail

### Recommended Actions (Medium Confidence)

4. **DELETE DT_NSO_2100_033V1.px (monthly health insurance)**
   - Monthly cumulative data less useful than annual
   - Loss: Intra-year tracking capability
   - Reason: Annual table sufficient for most users
   - **Alternative**: Keep if real-time monitoring is a stated requirement

### Optional Actions (Low Confidence - Specialty Use Cases)

5. **KEEP DT_NSO_2100_040V2.px** (neonatal mortality)
   - Specialized indicator (first 28 days of life)
   - Useful for: Neonatal health specialists, maternal/child health programs
   - Recommendation: KEEP if neonatal-specific reporting is needed

6. **KEEP DT_NSO_2100_012V1.px** (cancer by type)
   - Provides cancer type breakdown missing in DT_NSO_2100_045V1.px
   - Useful for: Cancer researchers, oncologists, public health planning
   - Recommendation: KEEP as supplementary dataset

---

## Impact Assessment

### Current State
- **Total Tables**: 16
- **True Redundancies**: 3-4 tables
- **Data Entry Errors**: 1 duplicate entry

### After Deduplication (High Confidence)
- **Remaining Tables**: 12
- **Tables Removed**: 4 (DT_NSO_2100_015V1, DT_NSO_2100_013V1, duplicate entry of DT_NSO_2100_033V1, monthly health insurance)
- **Coverage Loss**: Minimal (mortgage monthly insurance monitoring, have alternative sources)

### After Full Optimization (Including Optional)
- **Remaining Tables**: 10-11 (depending on neonatal/cancer type decisions)
- **Coverage**: Still comprehensive for education & health analysis
  - Birth/mortality trends ✓
  - Disease patterns ✓
  - Health system economics ✓
  - Education enrollment & spending ✓
  - Family planning ✓

---

## Recommendations for Data.mn

### For Business Users & Analysts
**Recommended Dataset to Add**:
- Keep **DT_NSO_2100_045V1.px** (Cancer cases & mortality by region)
- Keep **DT_NSO_0300_029V1.px** (Birth rates by age)
- Keep **DT_NSO_2100_030V1.px** (Health spending)
- Keep **DT_NSO_2100_30V001.px** (Health insurance fund)
- Keep **DT_NSO_0300_071V02.px** (Health service use)
- Keep **DT_NSO_2002_055V1.px** (Education spending)
- Keep **DT_NSO_2002_065V1.px** (School enrollment)

**Do Not Add**:
- DT_NSO_2100_015V1.px (duplicate)
- DT_NSO_2100_013V1.px (covered by cancer/mortality table)
- DT_NSO_2100_033V1.px (monthly version; keep annual only)

### For Specialist Datasets (Optional)
- DT_NSO_2100_040V2.px (Neonatal mortality - if neonatal-specific analysis desired)
- DT_NSO_2100_012V1.px (Cancer by type - if cancer type breakdown needed)
- DT_NSO_2100_047V1.px (Adolescent fertility - for youth health focus)
- DT_NSO_2100_051V1.px (Family planning - for reproductive health focus)

---

## Technical Notes

### Data Quality Observations
1. **Duplicate Entries**: DT_NSO_2100_033V1.px appears with two different subsector classifications
   - May indicate inconsistent metadata
   - Suggest: Verify NSO API and clean up catalog
2. **Version Numbers**: Some tables have version suffixes (V1, V2, V001, V01, V02)
   - Unclear if versions represent different NSO releases
   - Recommend: Check NSO catalog for version tracking standards
3. **Naming Inconsistency**: Cancer tables use "NEW CASES OF CANCER" vs "NEW CASES AND MORTALITY"
   - Makes redundancy detection harder
   - Suggest: Use consistent terminology in NSO source

---

## Conclusion

The Education & Health sector has **3-4 tables that should be removed immediately** due to clear redundancy or duplication:
1. **DT_NSO_2100_015V1.px** - Exact duplicate
2. **DT_NSO_2100_013V1.px** - Covered by better table
3. **DT_NSO_2100_033V1.px** - Duplicate entry in list + less useful (monthly)

After deduplication, the sector will remain **comprehensive** with 11-12 high-quality tables covering:
- Mortality & births (demographic foundation)
- Disease & health service use
- Health system economics
- Education access & spending
- Reproductive health & family planning

This provides an excellent foundation for a data.mn education & health section.
