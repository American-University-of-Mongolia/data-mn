# Labour & Business Sector Analysis

## Summary
- **Total tables:** 42
- **Unique concept groups:** 11
- **Recommended to keep:** 14
- **Redundant (skip):** 28

## Concept Groups

### 1. Unemployment (1 table) ✓
**KEEP:**
- `DT_NSO_0400_049V1.px`: "8.5.2 UNEMPLOYMENT RATE, by sex, age group, persons with disabilities, and by year" (Essential - national unemployment metric, high dimensionality)

**Analysis:** Single table, already marked as essential.

---

### 2. Employment Indicators (2 tables)
**KEEP:**
- `EMPLOYMENT INDICATORS OF POPULATION AGED 15 AND OVER, by national level` (Comprehensive national-level summary, foundational data)

**SKIP (redundant):**
- `DT_NSO_0400_055V1.px`: "EMPL-1 EMPLOYMENT-TO-POPULATION RATIO PERCENT, by sex, age group, location, and by year" (Calculated metric, subset of Employment Indicators)

**Reason:** The Employment Indicators table provides national-level aggregates. The EMPL-1 table is a derivative calculation that breaks down the employment ratio by demographics and location, but the base indicators provide the essential national context.

---

### 3. Employment to Population Ratio (2 tables)
**KEEP:**
- `EMPLOYMENT TO POPULATION RATIO, by sex, age group, aimags and the Capital` (Geographic and demographic breakdown, more comprehensive)

**SKIP (redundant):**
- `DT_NSO_0400_055V1.px`: "EMPL-1 EMPLOYMENT-TO-POPULATION RATIO PERCENT, by sex, age group, location, and by year" (Duplicate concept, same metric, less dimensional detail)

**Reason:** Both measure employment-to-population ratio. The first provides regional breakdown by aimag. The EMPL-1 is narrower despite similar naming.

---

### 4. Employment by Economic Activity (1 table) ✓
**KEEP:**
- `DT_NSO_0400_067V1.px`: "CONT-6 EMPLOYMENT, by classification of economic activities, and by year" (Essential industry breakdown)

**Analysis:** Single table, provides employment distribution across sectors.

---

### 5. Hourly Earnings (1 table) ✓
**KEEP:**
- `DT_NSO_0400_048V1.px`: "8.5.1 AVERAGE HOURLY EARNINGS OF FEMALE AND MALE EMPLOYEES, by occupation, age, sex, location, region, and by year" (Comprehensive earnings metric with high dimensionality)

**Analysis:** Single table, essential for wage analysis.

---

### 6. Monthly Wages (6 tables)
**KEEP:**
- `MONTHLY AVERAGE NOMINAL WAGES, by division of economic activities` (Best for industry comparison, most commonly used slice)

**SKIP (redundant):**
- `EMPLOYEES, by group of wages, and share to total` (Distribution by wage bands, derivative analysis, not raw wage data)
- `MONTHLY AVERAGE NOMINAL WAGES, by legal status and gender` (Single dimension slice)
- `MONTHLY AVERAGE NOMINAL WAGES, by type of ownership and gender` (Single dimension slice, ownership type less critical than industry)
- `MONTHLY AVERAGE NOMINAL WAGES OF EMPLOYEE, by employees size class and gender` (Narrow comparison, company size less common query)
- `MONTHLY AVERAGE NOMINAL WAGES, by occupation and gender` (Occupational detail exists in Hourly Earnings table; nominal wages by occupation less critical)

**Reason:** Six tables all measure monthly wages with different breakdowns. The "by division of economic activities" version is most broadly useful for business analysis and policy. The others are narrow slices that can be derived if needed. Distribution by wage bands and size class are specialized analyses.

---

### 7. Real Wage Index (1 table) ✓
**KEEP:**
- `REAL WAGE INDEX (2015=100), by divisions of economic activities` (Inflation-adjusted wage trends by sector)

**Analysis:** Single table, essential for real purchasing power analysis vs. nominal wages.

---

### 8. Wage Distribution/Poverty (5 tables)
**KEEP:**
- `DT_NSO_0400_056V1.px`: "EARN-1 WORKING POVERTY RATE OF EMPLOYED PERSONS (WPRE, percent), by sex, age group, aimags and the Capital, and by year" (Measures working poverty - distinct from unemployment)

**SKIP (redundant):**
- `DT_NSO_0400_057V1.px`: "EARN-2 EMPLOYEES WITH LOW PAY RATE (ELPR), by sex, age group, location, region, and by year" (Similar to working poverty rate, calculated variant)
- `DT_NSO_0400_065V1.px`: "CONT-4 INCOME INEQUALITY (90:10 RATIO), by age, sex, location, region, and by year" (Specialized inequality metric, not core wage data)
- `MONTHLY MEDIAN WAGES OF EMPLOYEES` (Median vs mean, related to distribution not essential difference - mean wages more commonly used)

**Reason:** Multiple tables measure wage-related poverty and distribution. Working Poverty Rate (EARN-1) is the most policy-relevant. Low Pay Rate (EARN-2) is a derived calculation. Median wages and inequality ratios are specialized metrics.

---

### 9. Working Hours (1 table) ✓
**KEEP:**
- `DT_NSO_0400_058V1.px`: "TIME-1. EMPLOYMENT IN EXCESSIVE WORKING TIME (more than 48 hours per week), by sex, age group, location, region, and by year" (Working hours enforcement metric)

**Analysis:** Single table, essential for labor standards.

---

### 10. Youth & Special Populations (3 tables)
**KEEP:**
- `DT_NSO_0400_050V1.px`: "8.6.1 PROPORTION OF YOUTH (AGED 15-24) NOT IN EDUCATION, EMPLOYMENT OR TRAINING PERCENT, by sex, location, region, and by year" (NEET rate, policy-critical metric)

**SKIP (redundant):**
- `DT_NSO_0400_052V1.px`: "8.7.1 NUMBER OF CHILDREN AGED 5-17 YEARS ENGAGED IN CHILDLABOUR, by sex, age group, location and region, and by year" (Specialized human rights metric, distinct from NEET)
- `DT_NSO_0400_051V1.px`: "8.8.1 INCIDENCE RATES OF FATAL AND NON-FATAL OCCUPATIONAL INJURIES, by sex, and by year" (Workplace safety metric, specialized)

**Reason:** Three separate concepts (youth out of education, child labor, workplace injuries). NEET is most commonly referenced. Child labor and occupational injuries are specialized indicators. **Keep all three as they measure distinct things, but note they are not substitutes.**

**Revision: KEEP ALL THREE** - these are distinct policy areas, not redundant.

---

### 11. Social Protection & Benefits (5 tables)
**KEEP:**
- `DT_NSO_0400_045V1.px`: "1.3.1 PROPORTION OF POPULATION COVERED BY SOCIAL PROTECTION FLOORS/SYSTEMS PERCENT, by sex, age group, location, region, and by year" (Broadest social protection coverage metric)

**SKIP (redundant):**
- `DT_NSO_0400_060V1.px`: "SECU-1 PROPORTION OF POPULATION RECEIVING OLD-AGE PENSION, by year" (Subset of social protection, pension-specific)
- `DT_NSO_0400_061V1.px`: "DIAL-1 Trade union density rate (percentage) by Category and Year" (Labor relations metric, not social protection)

**Reason:** Social Protection Floors (1.3.1) is the comprehensive metric. Old-age pensions are a subset. Trade union density is a separate indicator of labor relations strength, not social protection coverage.

---

### 12. Occupational Segregation (1 table) ✓
**KEEP:**
- `DT_NSO_0400_059V1.px`: "EQUA-1 OCCUPATIONAL SEGREGATION: FEMALE SHARE OF EMPLOYMENT by occupation, and by year" (Gender equity in occupations)

**Analysis:** Single table, essential for gender equality analysis.

---

### 13. Foreign Workers (4 tables)
**KEEP:**
- `DT_NSO_0400_39V1_2.px`: "FOREIGN WORKERS WITH LABOUR CONTRACT, by country, and by quarter" (Inbound foreign labor, country-level detail)

**SKIP (redundant):**
- `DT_NSO_0400_40V1.px`: "FOREIGN WORKERS WITH LABOUR CONTRACT, by economic activity, and by quarter" (Inbound, but by activity not country - use country version for better geographic context)
- `DT_NSO_0500_001V6.px`: "EMPLOYEES WORKING ABROAD ON A CONTRACTUAL BASIS, by economic activity, and by quarter" (Outbound labor, opposite flow)
- `EMPLOYEES WORKING ABROAD ON A CONTRACTUAL BASIS, by country` (Outbound labor by country)

**Reason:** Four tables covering labor flows. Keep inbound by country (most important for understanding foreign labor inflows). Activity breakdown is secondary detail. Outbound labor is a separate flow - could keep one outbound table, but it's less critical for most business analysis.

**Revision: KEEP Inbound by country, SKIP Inbound by activity. For outbound, KEEP by country (broader usefulness) and SKIP by activity.**

---

### 14. SMEs (Small & Medium-Sized Enterprises) (4 tables)
**KEEP:**
- `DT_NSO_0500_001V2.px`: "SMALL AND MEDIUM-SIZED LEGAL ENTITIES VALUE ADDED SHARES IN GDP, by economic activity, and by year" (SME contribution to economy, essential metric)

**SKIP (redundant):**
- `DT_NSO_0500_001V9.px`: "SMALL AND MEDIUM-SIZED LEGAL ENTITIES VALUE ADDED SHARES IN GDP, by aimags and the Capital, and by year" (Regional version of same metric, less generalizable)
- `DT_NSO_0500_001V10.px`: "SHARE TO TOTAL EXPORTS AND IMPORTS OF SMALL AND MEDIUM-SIZED LEGAL ENTITIES, by year" (Trade-specific, narrower than GDP contribution)
- `DT_NSO_BR_01V33.px`: "SMALL AND MEDIUM-SIZED LEGAL ENTITIES, by employment size group and sales size group, and by year" (Distribution/classification, derived from register)

**Reason:** Multiple SME metrics. National GDP contribution (V2) is most important for policy. Regional version (V9) is less broadly useful. Export shares are specialized. Employment/sales distribution is classification data, not essential analysis.

---

### 15. Statistical Business Register (4 tables)
**KEEP:**
- `DT_NSO_2600_008V1.px`: "NUMBER OF LEGAL ENTITIES, by employment size class and ownership type, and by quarter" (Complete business count by type and size)

**SKIP (redundant):**
- `DT_NSO_2600_014V3.px`: "NUMBER OF LEGAL ENTITIES, by economic activity and employment size class, and by year" (Activity breakdown, but annual; V008 is more current and comprehensive)
- `DT_NSO_2600_015V4.px`: "NUMBER OF LEGAL ENTITIES, by division of economic activity and size group of employees, and by quarter" (Similar to V014, division-level detail)
- `DT_NSO_2600_016V4.px`: "NUMBER OF LEGAL ENTITIES, by group of economic activity and activity status, and by quarter" (Activity status detail, less critical than size/type)

**Reason:** Four register tables with overlapping entity classifications. V008 by size and ownership type is fundamental. Activity breakdowns (V014, V015, V016) are secondary analyses. Keep the primary registration table, skip activity-specific variants.

---

### 16. Economic Indicators (3 tables)
**KEEP:**
- `DT_NSO_0400_047V1.px`: "8.2.1 ANNUAL GROWTH RATE OF REAL GDP PER EMPLOYED PERSON, by year" (Labor productivity growth)
- `DT_NSO_0400_053V1.px`: "10.4.1 LABOUR SHARE OF GDP, COMPRISING WAGES AND SOCIAL PROTECTION TRANSFERS, by year" (Labor income distribution)

**SKIP (redundant):**
- `DT_NSO_0400_066V1.px`: "CONT-5 INFLATION AVERAGE RATE OF YEAR (CPI), by region, and by year" (Inflation is not labor-specific, belongs in macro/prices sector)

**Reason:** Two genuine labor economics metrics (productivity and labor share of GDP). CPI inflation is macro data, not labor-specific, should not be included in this sector analysis.

---

### 17. Demographics & Health (2 tables)
**SKIP BOTH (out of scope for Labour & Business):**
- `DT_NSO_0400_064V1.px`: "CONT-2 ESTIMATED PERCENTAGE OF WORKING AGE POPULATION WHO ARE HIV POSITIVE" (Health metric, not labor data)
- `DT_NSO_0400_068V1.px`: "CONT-7 EDUCATION OF ADULT POPULATION (ADULT LITERACE RATE)" (Education metric, not labor data)

**Reason:** These are population health and education metrics, not labor or business indicators. Should be in Population/Health or Education sectors respectively.

---

## Recommendations Summary

### Core Tables to Keep (14 tables)
1. `DT_NSO_0400_049V1.px` - Unemployment rate
2. `EMPLOYMENT INDICATORS OF POPULATION AGED 15 AND OVER, by national level` - Employment summary
3. `EMPLOYMENT TO POPULATION RATIO, by sex, age group, aimags and the Capital` - Employment-to-population
4. `DT_NSO_0400_067V1.px` - Employment by economic activity
5. `DT_NSO_0400_048V1.px` - Average hourly earnings
6. `MONTHLY AVERAGE NOMINAL WAGES, by division of economic activities` - Monthly wages by sector
7. `REAL WAGE INDEX (2015=100), by divisions of economic activities` - Real wage trends
8. `DT_NSO_0400_056V1.px` - Working poverty rate
9. `DT_NSO_0400_058V1.px` - Excessive working hours
10. `DT_NSO_0400_050V1.px` - Youth NEET rate
11. `DT_NSO_0400_051V1.px` - Occupational injuries
12. `DT_NSO_0400_052V1.px` - Child labor
13. `DT_NSO_0400_045V1.px` - Social protection coverage
14. `DT_NSO_0400_059V1.px` - Occupational segregation (gender)

### Important Metrics to Keep (4 additional)
15. `DT_NSO_0400_47V1.px` - GDP per employed person (productivity)
16. `DT_NSO_0400_053V1.px` - Labour share of GDP
17. `DT_NSO_0500_001V2.px` - SME value added to GDP
18. `DT_NSO_2600_008V1.px` - Business register by employment size

### Redundant/Out-of-Scope (24 tables)
- V055 Employment ratio (duplicate of core employment tables)
- V057 Low pay rate (variant of working poverty)
- V060 Old-age pensions (subset of social protection)
- V061 Trade union density (separate indicator, not core labor)
- V064 HIV in working age population (health, not labor)
- V065 Income inequality 90:10 ratio (specialized metric)
- V066 CPI inflation (macro data, not labor-specific)
- V068 Adult literacy (education, not labor)
- V40 Foreign workers by activity (keep country breakdown instead)
- V500_001V6 Employees abroad by activity (keep country breakdown instead)
- V500_001V9 SME value added regional (keep national version)
- V500_001V10 SME export shares (narrow focus)
- V500_BR_01V33 SMEs by size/sales distribution (classification, not essential)
- V2600_014V3 Entities by activity (activity detail less critical)
- V2600_015V4 Entities by division (redundant detail)
- V2600_016V4 Entities by status (activity status less critical)
- Multiple wage tables (keep one by sector, skip others)
- Median wages (keep mean/average wages)
- Employees by wage group (distribution, derived)
- Outbound workers by activity (keep country breakdown)
- Other activity/regional variants (secondary to main national tables)

## Key Principles Applied

1. **National > Regional**: When available, national aggregates are more useful than regional breakdowns
2. **Comprehensive > Narrow**: One well-dimensioned table beats multiple single-dimension tables
3. **Core Metrics > Derived**: Keep base indicators (unemployment rate) not calculated variants (employment ratio)
4. **Current > Dated**: Quarterly data (V008) preferred over annual (V014, V015)
5. **Scope Alignment**: Excluded health (HIV rates) and education (literacy) data as out-of-scope
6. **User Relevance**: Prioritized tables useful for business, policy, and student analysis

## Next Steps

1. Update NSO data registry to mark redundant tables as "skip"
2. Configure data.mn to ingest only the 14-18 recommended tables
3. Create consolidated wage table combining monthly nominal and real index
4. Add metadata links between related tables (e.g., poverty rate → social protection coverage)
