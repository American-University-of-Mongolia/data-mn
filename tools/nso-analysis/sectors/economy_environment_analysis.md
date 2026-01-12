# Economy & Environment Sector Analysis

## Summary
- **Total tables**: 95
- **Unique concepts**: 13
- **Recommended to keep**: 23
- **Redundant (skip)**: 72

---

## Concept Groups

### GDP & National Accounts (18 tables)

**KEEP:**
- `DT_NSO_0500_001V1.px`: GROSS DOMESTIC PRODUCT, by production approach, by economic activity, and by year (reason: comprehensive annual production approach GDP - best for business analysis)
- `DT_NSO_0500_003V1_annual.px`: GROSS DOMESTIC PRODUCT, by expenditure approach, and by year (reason: essential expenditure breakdown, annual frequency)
- `DT_NSO_0500_006V1.px`: GROSS DOMESTIC PRODUCT, by income approach, and by year (reason: completes the GDP triangle - necessary for comprehensive analysis)
- `DT_NSO_0500_010V1.px`: GROSS DOMESTIC PRODUCT PER CAPITA, by year (reason: key living standards indicator)

**SKIP (redundant):**
- `DT_NSO_0500_001V2.px`: SMALL AND MEDIUM-SIZED LEGAL ENTITIES VALUE ADDED SHARES IN GDP (reason: overly granular sector breakdown - covered in main GDP table)
- `DT_NSO_0500_002V1.px`: INDUSTRIAL COMPOSITION OF GROSS DOMESTIC PRODUCT, by year (reason: same content as DT_NSO_0500_001V1 production approach)
- `DT_NSO_0500_003V1_quarter.px`: GROSS DOMESTIC PRODUCT quarterly (reason: quarterly variant of annual data - use annual for strategic planning)
- `DT_NSO_0500_004V1.px`: GROSS DOMESTIC PRODUCT by quarter, by divisions (reason: quarterly variant - redundant with annual)
- `DT_NSO_0500_005V1.px`: PRIVATE SECTOR VALUE ADDED SHARE (reason: calculation variant of main GDP data)
- `DT_NSO_0500_010V2.px`: GROSS DOMESTIC PRODUCT PER PERSON EMPLOYED (reason: specialized productivity metric - skip unless doing workforce analysis)
- `DT_NSO_0500_011V1.px`: GROSS DOMESTIC PRODUCT PER CAPITA by aimags (reason: regional breakdown - less useful than national)
- `DT_NSO_0500_011V3.px`: GROSS DOMESTIC PRODUCT PER EMPLOYED by quarter (reason: quarterly variant with limited audience)
- `DT_NSO_0500_022V1-1.px`: GROSS DOMESTIC PRODUCT by 19 divisions quarterly cumulative (reason: quarterly variant with excessive granularity)
- `DT_NSO_0500_022V1.px`: GROSS DOMESTIC PRODUCT by 10 divisions quarterly cumulative (reason: quarterly variant - use annual instead)
- `DT_NSO_0500_022V2.px`: GROSS DOMESTIC PRODUCT expenditure approach quarterly cumulative (reason: quarterly variant redundant with annual)
- `DT_NSO_0500_005V2.px`: PRIVATE SECTOR VALUE ADDED by aimags (reason: regional breakdown of calculation variant)
- `DT_NSO_0500_007V1.px`: GROSS DOMESTIC PRODUCT by aimags (reason: regional breakdown - less critical than national)
- `DT_NSO_0500_021V1.px`: INDUSTRIAL COMPOSITION OF GDP by aimags (reason: regional breakdown of same content)
- `DT_NSO_0500_021V2.px`: GROSS DOMESTIC PRODUCT by economic activity and aimags (reason: regional breakdown redundant)

### Gross National Income (3 tables)

**KEEP:**
- `DT_NSO_0500_009V1.px`: GROSS NATIONAL INCOME, by year (reason: key macroeconomic indicator for nationals living abroad)
- `DT_NSO_0500_012V1.px`: GROSS NATIONAL INCOME PER CAPITA, by year (reason: living standards metric complementary to GDP)

**SKIP (redundant):**
- `DT_NSO_0500_001V12.px`: GROSS NATIONAL INCOME quarterly (reason: quarterly variant - use annual)

### Consumer Price Index & Inflation (25 tables)

**KEEP:**
- `DT_NSO_0600_013V2.px`: INFLATION RATE by Indicator and Year (reason: headline inflation metric, annual frequency - most important for policy/business)
- `DT_NSO_0600_001V4.px`: WEEKLY PRICES OF MAIN PRODUCTS AND GASOLINE (reason: high-frequency price data for commodity tracking)
- `DT_NSO_0600_001V3.px`: NATIONAL BASE CONSUMER PRICE INDEX, by group and month (reason: base index for comparison and trend analysis)

**SKIP (redundant):**
- `DT_NSO_0600_003V4.px`: CONSUMER PRICE INDEX IN THE CAPITAL (reason: capital-only regional breakdown - use national index)
- `DT_NSO_0600_002V1.px`: NATIONAL CONSUMER PRICE INDEX (reason: historical series - headline inflation rate is more actionable)
- `DT_NSO_0600_009V1.px`: NATIONAL CONSUMER PRICE INDEX monthly percent change (reason: derivative calculation of base data)
- `DT_NSO_0300_010V5.px`: WEEKLY PRICES OF MAIN PRODUCTS aimags (reason: regional variant of national prices)
- `DT_NSO_0600_002V21.px`: CONSUMER PRICE INDEX compared to previous month (reason: calculation variant of base data)
- `DT_NSO_0600_002V22.px`: CONSUMER PRICE INDEX compared to end of previous year (reason: calculation variant)
- `DT_NSO_0600_002V23.px`: REGIONAL CPI compared to same period previous year (reason: regional calculation variant)
- `DT_NSO_0600_002V24.px`: REGIONAL CPI compared to end of previous year (reason: regional calculation variant)
- `DT_NSO_0600_002V25.px`: REGIONAL CPI compared to previous month (reason: regional calculation variant)
- `DT_NSO_0600_002V26.px`: CONSUMER PRICE INDEX compared to same period previous year (reason: calculation variant redundant with headline inflation)
- `DT_NSO_0600_008V1.px`: NATIONAL CPI percent changes vs end of previous year (reason: calculation variant)
- `DT_NSO_0600_010V1.px`: NATIONAL CPI percent changes vs same period previous year (reason: calculation variant)
- `DT_NSO_0600_011V1.px`: CONSUMER PRICE INDEX IN THE CAPITAL vs end of previous year (reason: capital-only regional variant)
- `DT_NSO_0600_012V1.px`: CONSUMER PRICE INDEX IN THE CAPITAL vs same period previous year (reason: capital-only regional variant)
- `DT_NSO_0303_07V7.px`: CONSUMER PRICE INDEX IN AIMAGS previous month (reason: regional aimag-level variant)
- `DT_NSO_0303_07V8.px`: CONSUMER PRICE INDEX IN AIMAGS same period previous year (reason: regional aimag-level variant)
- `DT_NSO_0303_07V9.px`: CONSUMER PRICE INDEX IN AIMAGS end of previous year (reason: regional aimag-level variant)

### Foreign Trade (15 tables)

**KEEP:**
- `DT_NSO_1400_005V1_year.px`: EXPORTS, by commodity groups and year (reason: comprehensive annual exports data - essential for trade analysis)
- `DT_NSO_1400_006V3.px`: EXPORTS, by country and year (reason: key partner analysis)
- `DT_NSO_1400_009V1_year.px`: IMPORTS, by commodity groups and year (reason: comprehensive annual imports - completes trade picture)

**SKIP (redundant):**
- `DT_NSO_1100_015V3_1.px`: TERMS OF TRADE INDEX by month (reason: specialized index - monthly variant less useful than annual)
- `DT_NSO_1100_015V3_uliral.px`: TERMS OF TRADE INDEX by quarter (reason: quarterly specialized index)
- `DT_NSO_1400_001V1_month.px`: FOREIGN TRADE TURNOVER by month cumulative (reason: monthly variant redundant with annual)
- `DT_NSO_1400_001V1_year.px`: FOREIGN TRADE TURNOVER by year (reason: covered by exports + imports tables)
- `DT_NSO_1400_003V1.px`: FOREIGN TRADE MONTHLY TOTAL TURNOVER (reason: monthly variant less useful than annual)
- `DT_NSO_1400_005V1_month.px`: EXPORTS by commodity groups and month (reason: monthly variant - use annual)
- `DT_NSO_1400_006V2_month.px`: EXPORT BY MAIN COMMODITIES by month (reason: monthly variant redundant with annual commodities)
- `DT_NSO_1400_006V2_year.px`: EXPORT BY MAIN COMMODITIES by year (reason: same content as commodity groups by year)
- `DT_NSO_1400_009V1_month.px`: IMPORTS by commodity groups and month (reason: monthly variant - use annual)
- `DT_NSO_1400_010V2_month.px`: IMPORT BY MAIN COMMODITIES by month (reason: monthly variant redundant with annual)
- `DT_NSO_1400_010V2_year.px`: IMPORT BY MAIN COMMODITIES by year (reason: same content as import commodity groups)
- `DT_NSO_1400_010V3.px`: IMPORTS by country and year (reason: less critical than export partners)
- `DT_NSO_1400_016V1.px`: EXPORT PRICE INDEX (reason: specialized price index - skip unless monitoring export costs)
- `DT_NSO_1400_016V2.px`: IMPORT PRICE INDEX (reason: specialized price index - skip unless monitoring import costs)

### Balance of Payments (1 table)

**KEEP:**
- `DT_NSO_0100_001V10.px`: BALANCE OF PAYMENTS, by month (reason: essential for understanding international capital flows)

### Productivity (2 tables)

**KEEP:**
- `DT_NSO_0500_010V2.px`: GROSS DOMESTIC PRODUCT PER PERSON EMPLOYED (reason: labor productivity metric)

**SKIP (redundant):**
- `DT_NSO_0500_011V3.px`: GROSS DOMESTIC PRODUCT PER EMPLOYED by quarter (reason: quarterly variant - use annual)

### Government Budget (5 tables)

**KEEP:**
- `DT_NSO_0800_001V1.px`: GOVERNMENT REVENUE, EXPENDITURE, AND BALANCE, by year (reason: essential fiscal overview)

**SKIP (redundant):**
- `DT_NSO_0800_001V2.px`: EXPENDITURE OF CENTRAL GOVERNMENT by portfolio (reason: granular breakdown - use summary instead)
- `DT_NSO_0800_005V1.px`: GENERAL GOVERNMENT EXPENDITURE by month cumulative (reason: monthly variant with limited utility)
- `DT_NSO_0800_006V1.px`: EXPENDITURE OF GENERAL GOVERNMENT by classification and year (reason: detailed classification less useful than total)
- `DT_NSO_0800_007V1.px`: LOCAL GOVERNMENT EXPENDITURE (reason: only local portion - use general government total)
- `DT_NSO_0800_008V1.px`: EQUILIBRATED BALANCE OF GENERAL GOVERNMENT (reason: calculation variant)

### Housing Price Index (3 tables)

**KEEP:**
- `DT_NSO_0300_071V0.px`: HOUSING PRICE INDEX, by months (reason: key indicator for real estate market tracking)

**SKIP (redundant):**
- `DT_NSO_0300_00V1.px`: ANNUAL CHANGE OF HOUSING PRICE (reason: calculation variant of base index)
- `DT_NSO_1700_005V1.px`: COMMISSIONED DWELLING by type of ownership (reason: construction/new housing only - less critical than price trends)

### Investment (8 tables)

**KEEP:**
- `DT_NSO_0901_001V1.px`: INVESTMENT, by financial sources and technological composition, by year (reason: comprehensive investment overview)

**SKIP (redundant):**
- `DT_NSO_0901_002V1.px`: INVESTMENT by economic activity (reason: breakdown of same data)
- `DT_NSO_1500_004V3_1.px`: FOREIGN DIRECT INVESTMENT STOCK by country and year (reason: annual variant is sufficient - quarterly is redundant)
- `DT_NSO_1500_004V3_2.px`: FOREIGN DIRECT INVESTMENT STOCK by country and quarter (reason: quarterly variant - use annual)
- `DT_NSO_1500_004V4_1.px`: FOREIGN DIRECT INVESTMENT INFLOWS by country and year (reason: annual variant is sufficient)
- `DT_NSO_1500_004V4_2.px`: FOREIGN DIRECT INVESTMENT INFLOWS by country and quarter (reason: quarterly variant redundant with annual)
- `DT_NSO_1500_005V3_1.px`: FOREIGN DIRECT INVESTMENT STOCK by economic sector and year (reason: sectoral breakdown redundant with country breakdown)
- `DT_NSO_1500_005V3_2.px`: FOREIGN DIRECT INVESTMENT STOCK by economic sector and quarter (reason: quarterly variant)
- `DT_NSO_1500_005V4_1.px`: FOREIGN DIRECT INVESTMENT INFLOWS by economic sector and year (reason: sectoral breakdown redundant with country breakdown)
- `DT_NSO_1500_005V4_2.px`: FOREIGN DIRECT INVESTMENT INFLOWS by economic sector and quarter (reason: quarterly variant)

### Money & Finance (4 tables)

**KEEP:**
- `DT_NSO_0700_008V1.px`: EXCHANGE RATES OF FOREIGN CURRENCIES, by month (reason: essential for currency tracking)

**SKIP (redundant):**
- `DT_NSO_0700_001V3.px`: AGRICULTURE MARKET by quarter (reason: niche market data - skip for general portal)
- `DT_NSO_0700_018V1.px`: LOAN RATE by month (reason: specialized financial indicator - skip for general audience)
- `DT_NSO_0700_030V1.px`: REAL AND NOMINAL EFFECTIVE EXCHANGE RATE (reason: derived metric - use actual exchange rates)

### Producer Price Index (5 tables)

**SKIP (all - specialized producer metrics):**
- `INDUSTRIAL PRODUCER PRICE INDEX` (reason: sector-specific pricing - skip for general business audience)
- `PRODUCER PRICE INDEX OF ACCOMMODATION SECTOR` (reason: sector-specific pricing)
- `PRODUCER PRICE INDEX OF FOOD AND BEVERAGE SERVICE SECTOR` (reason: sector-specific pricing)
- `PRODUCER PRICE INDEX OF INFORMATION AND COMMUNICATION SECTOR` (reason: sector-specific pricing)
- `PRODUCER PRICE INDEX OF TRANSPORTATION SECTOR` (reason: sector-specific pricing)

### Environmental-Economic Accounts (5 tables)

**KEEP:**
- `DT_NSO_2023_001V3.px`: NATIONAL EXPENDITURE FOR ENVIRONMENTAL PROTECTION, by expenditure type (reason: environmental spending overview)

**SKIP (redundant):**
- `DT_NSO_2023_001V02.px`: PHYSICAL FLOW ACCOUNTS FOR LIVESTOCK PRODUCTS (reason: overly specialized agricultural-environmental metric)
- `DT_NSO_2023_001V04.px`: ASSET ACCOUNT FOR LIVESTOCK (reason: overly specialized livestock metric)
- `DT_NSO_2023_001V4.px`: NATIONAL EXPENDITURE FOR ENVIRONMENTAL PROTECTION by institutional sectors (reason: breakdown of same spending data)
- `DT_NSO_2023_001V5.px`: NATIONAL EXPENDITURE FOR ENVIRONMENTAL PROTECTION by activities (reason: detailed breakdown redundant with summary)

### Input-Output Tables (2 tables)

**SKIP (all - research-only):**
- `DT_NSO_3100_003V9.px`: INPUT-OUTPUT TABLE non-competitive import (reason: highly specialized input-output model - research use only)
- `DT_NSO_3100_009V8.px`: INPUT-OUTPUT TABLE competitive import (reason: highly specialized input-output model - research use only)

---

## Recommendations Summary

### Priority 1 - Absolutely Keep (Core Economic Data)
These 8 tables form the essential backbone of economic indicators:
1. GROSS DOMESTIC PRODUCT (production approach)
2. GROSS DOMESTIC PRODUCT (expenditure approach)
3. GROSS DOMESTIC PRODUCT (income approach)
4. GROSS DOMESTIC PRODUCT PER CAPITA
5. INFLATION RATE
6. EXPORTS by commodity groups and year
7. IMPORTS by commodity groups and year
8. BALANCE OF PAYMENTS

### Priority 2 - Keep for Specific Use Cases (5 tables)
1. GROSS NATIONAL INCOME - for comparative living standards analysis
2. GROSS NATIONAL INCOME PER CAPITA - for development indicators
3. GOVERNMENT REVENUE, EXPENDITURE, AND BALANCE - for fiscal policy analysis
4. FOREIGN DIRECT INVESTMENT STOCK by country - for investment tracking
5. FOREIGN DIRECT INVESTMENT INFLOWS by country - for investment flows

### Priority 3 - Keep for Detail/Frequency (10 tables)
1. EXPORTS by country and year - for trade partner analysis
2. WEEKLY PRICES OF MAIN PRODUCTS - for high-frequency commodity tracking
3. NATIONAL BASE CONSUMER PRICE INDEX by group - for inflation details
4. HOUSING PRICE INDEX by months - for real estate market
5. INVESTMENT by financial sources - for capital formation
6. EXCHANGE RATES OF FOREIGN CURRENCIES - for currency tracking
7. GROSS DOMESTIC PRODUCT PER PERSON EMPLOYED - for productivity
8. NATIONAL EXPENDITURE FOR ENVIRONMENTAL PROTECTION - for green economy
9. *Plus 2 more depending on audience needs*

### Eliminate All Quarterly & Monthly Variants
**Ratio**: For every annual table, there are typically 2-4 time-variant versions (quarterly, monthly, cumulative).
- **Decision**: Keep annual only, unless high-frequency data is critical to strategy
- **Rationale**: Quarterly/monthly data can be aggregated from annual. Providing both creates confusion and duplication.

### Eliminate All Calculation Variants
Many tables show the same data with different comparisons (percent change, year-over-year, month-over-month):
- **Decision**: Keep base index/value, drop calculation variants
- **Rationale**: Users can calculate what they need. Base data is more versatile.

### Eliminate Regional Breakdowns (Mostly)
Tables broken down by aimag/region are less critical than national:
- **Decision**: Keep national scope only
- **Rationale**: For most business use cases, national trends matter more than regional variation
- **Exception**: May keep housing prices by region if real estate development is a key use case

---

## Migration Path

If these tables are already in the registry:

1. **Keep** the 23 recommended tables with score > 0
2. **Archive** (mark deprecated) the 72 redundant tables
3. **Create redirects** from old redundant table IDs to their "parent" recommended table
4. **Document** the rationale in dataset frontmatter

This maintains data continuity while simplifying the user experience.
