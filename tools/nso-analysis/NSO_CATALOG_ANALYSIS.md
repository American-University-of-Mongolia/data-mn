# NSO Catalog Analysis: 80% Utility Recommendations

**Generated:** December 2024
**Total Tables Analyzed:** 1,136
**Target Audience:** Business people, students, professionals (NOT researchers)

---

## Executive Summary

| Tier | Tables | % of Total | Action |
|------|--------|------------|--------|
| **T1-Essential** | 37 | 3.3% | **ADD ALL** - Core indicators everyone needs |
| **T2-Recommended** | 225 | 19.8% | **ADD MOST** - Good coverage, some redundancy |
| **T3-Consider** | 196 | 17.3% | **SKIP** - Niche or aimag-level only |
| **T4-Skip** | 678 | 59.7% | **SKIP** - Soum-level, MDG derived, historical |

**Bottom line:** For 80% utility, add **~260 tables** (T1 + T2). Skip the other **~875**.

---

## What Makes a Table Essential?

### High-Value Topics (80% audience cares about these)
- GDP, GNI, Economic Growth
- Inflation, CPI, Prices
- Employment, Unemployment, Wages
- Population, Demographics
- Trade (Exports/Imports)
- Poverty, Household Income

### Low-Value Topics (researcher-only)
- MDG/SDG derived indicators (duplicate data)
- Election results, Parliament composition
- Intellectual property, Patents
- Religious institutions (monasteries, temples)
- Civil servant statistics

### Geographic Granularity Rules
| Level | Recommendation |
|-------|----------------|
| National | ✓ Always include |
| Aimag (province) | ✓ Include if topic is high-value |
| District | ⚠️ Include sparingly |
| Soum/Bag/Khoroo | ✗ Skip (too granular for 80% audience) |

---

## T1-Essential Tables (37 total)

These are the must-haves. 11 already added, 26 remaining.

### Economy - Core (20 tables)
| Table ID | Title | Already Added |
|----------|-------|---------------|
| DT_NSO_0500_001V1 | GDP by production approach, by economic activity | ✓ |
| DT_NSO_0100_001V10 | Balance of Payments, by month | ✓ |
| DT_NSO_0600_013V2 | Inflation Rate | ✓ |
| DT_NSO_0400_049V1 | Unemployment Rate | ✓ |
| DT_NSO_0600_003V4 | CPI in Capital, monthly change | ✓ |
| DT_NSO_1400_005V1_year | Exports by commodity groups | ✓ |
| DT_NSO_0500_010V1 | GDP Per Capita | |
| DT_NSO_0500_003V1_quarter | GDP by expenditure, quarterly | |
| DT_NSO_0600_001V3 | National Base CPI by group | |
| DT_NSO_0500_001V12 | GNI, Gross Disposable Income | |

### Livestock & Agriculture (2 tables)
| Table ID | Title | Already Added |
|----------|-------|---------------|
| Regional livestock | Number of Livestock by type, aimag | ✓ |

### Weekly Prices (2 tables)
| Table ID | Title | Already Added |
|----------|-------|---------------|
| DT_NSO_0300_010V5 | Weekly Prices, aimags | ✓ |
| Weekly prices national | Weekly Prices national | ✓ |

---

## Redundancy Patterns Identified

### 1. Calculation Variants (Skip all but one)
Many tables exist in 3-4 versions with different calculation methods:
- "compared with previous month"
- "compared with same period of previous year"
- "compared with end of previous year"

**Recommendation:** Keep only the YoY comparison (most intuitive for general audience).

### 2. Geographic Duplicates (Keep national, skip granular)
Example: Population data exists at 4 levels:
- National total ✓ Keep
- By aimag ✓ Keep (useful for regional analysis)
- By soum ✗ Skip
- By bag/khoroo ✗ Skip

### 3. MDG Derived Data (Skip all 47)
The "Millennium Development Goals Indicators" subsector contains 47 tables that are:
- Derived from primary data already available elsewhere
- Formatted for UN reporting, not general use
- Often identical to primary tables with different names

### 4. Historical Archive (Skip most)
104 tables in "Historical data" sector are:
- Legacy archives from pre-2000
- Often have newer equivalents in other sectors
- Inconsistent naming and formatting

---

## Recommended Next Steps

### Phase 1: Add T1-Essential (26 remaining)
These 26 tables should be added immediately:
1. Remaining GDP tables (quarterly, per capita, by expenditure approach)
2. GNI tables
3. Additional CPI breakdowns
4. Key labor indicators

### Phase 2: Curate T2-Recommended (225 tables)
Before adding all 225, review for:
1. **Within-concept redundancy** - Multiple trade tables might overlap
2. **Aimag-level necessity** - Does every topic need aimag breakdown?
3. **Freshness** - Skip tables with stale data (last_updated check)

Suggested T2 priority order:
1. Trade & Finance (exports, imports, FDI)
2. Population & Demographics
3. Social indicators (education, health, poverty)
4. Industry (construction, tourism, transportation)

### Phase 3: Never Add T4-Skip (678 tables)
These include:
- 47 MDG derived tables
- 117 soum-level tables
- 89 district-level tables
- ~100 historical archive tables
- Niche topics (elections, IP, religious)

---

## File Reference

The updated `nso-catalog.xlsx` now includes:

| Sheet | Contents |
|-------|----------|
| **Recommendations** | Summary of tier distribution |
| **Summary** | Original subsector breakdown |
| **NSO Tables** | All 1,136 tables with recommendations |

### New Columns Added
- `Recommendation` - T1-Essential, T2-Recommended, T3-Consider, T4-Skip
- `Final_Score` - Numeric priority score (higher = more important)

### How to Use
1. Sort by `Recommendation` column (A→Z sorts T1 first)
2. Focus on T1 and T2 rows
3. Use `Already Added` column to see what's done
4. Use `Include` column to mark your final decisions
