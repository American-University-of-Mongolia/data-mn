# Dataset: GDP Growth Rate

## Identification

- **ID**: `gdp-growth-rate`
- **Source**: `nso-1212`
- **Category**: Economy
- **Tags**: [gdp, growth, economy, national-accounts, annual]

## Dataset Type

**This is a SPLIT dataset of the parent dataset `nso-gdp-by-economic-activity`.**

The complete dataset definition, source reference, and update instructions are maintained in the parent definition file:
- **Parent Definition**: `tools/sources/nso-1212/datasets/gdp-by-economic-activity.md`
- **Parent ID**: `nso-gdp-by-economic-activity`

## Source Reference

Inherited from parent dataset:
- **Table ID**: `DT_NSO_0500_001V1.px`
- **Sector**: `Economy, environment`
- **Subsector**: `National Accounts`
- **API Path**: `/en/NSO/Economy, environment/National Accounts/DT_NSO_0500_001V1.px`

## Title

- **EN**: Mongolia GDP Growth Rate (1991-2024)
- **MN**: Монгол Улсын ДНБ-ий өсөлтийн хувь (1991-2024)

## Description

Year-over-year GDP growth rate showing Mongolia's economic expansion and contraction from 1991 to 2024. This dataset measures the annual percentage change in real GDP, providing insight into economic performance cycles, boom-bust patterns, and the impact of major events (Soviet collapse, mining boom, COVID-19, etc.).

## Split Filter

This dataset is created by filtering the parent dataset with:

```json
{
  "Indicator": "Annual changes, by percent",
  "Economic activity": "Total"
}
```

## Variables

### Year (Он)
Years from 1991 to 2024 (34 data points)

Note: Growth rates start in 1991 because 1990 is the base year.

### Value
Annual GDP growth rate in percentage points (%).
- Positive values indicate economic expansion
- Negative values indicate economic contraction
- Can range from approximately -10% to +20% based on historical data

## Chart Configuration

- **Chart Type**: bar (with conditional coloring)
- **Chart Config**:
  - X-axis: year (Он) - quantitative
  - Y-axis: value (% change) - quantitative
  - Color: Conditional
    - Positive values (growth): `#54a24b` (green)
    - Negative values (contraction): `#e45756` (red)
  - Tooltip: Year + value with 1 decimal place
  - Zero baseline emphasized

## Key Periods

- **1991-1993**: Severe contraction during Soviet collapse (-9% to -3%)
- **1994-2008**: Recovery and mining boom era (positive growth)
- **2009**: Global financial crisis impact (-1.3%)
- **2011-2013**: Mining investment peak (17%+ growth)
- **2016**: Commodity price collapse slowdown
- **2020**: COVID-19 pandemic impact (-4.6%)
- **2021**: Strong recovery (1.6%)
- **2022-2024**: Post-pandemic stabilization

## Update Instructions

### Data Source

This split dataset is automatically regenerated when the parent dataset (`nso-gdp-by-economic-activity`) is updated.

**DO NOT update this dataset independently.** Instead, update the parent:

```bash
cd tools
python -m registry info nso-gdp-by-economic-activity  # Check parent status
# Update parent using /data-update command or worker
```

### Validation

After regeneration from parent:
- Year values should be consecutive from 1991 to latest year
- Values should be numeric percentages (can be negative)
- No missing years in the range
- Latest year should match parent dataset's latest year

### Refresh Process

When parent is updated:
1. Parent fetches latest data from NSO API
2. Filter is applied: `Indicator="Annual changes, by percent"` AND `Economic activity="Total"`
3. CSV files are generated (`gdp-growth-rate-en.csv`, `gdp-growth-rate-mn.csv`)
4. Chart JSON is regenerated with conditional coloring
5. MDX pages are validated (no changes unless title/metadata updated)

## Content Generation

### Key Findings Template

Auto-extract for MDX page:
- **Latest year growth**: "Mongolia's GDP grew by X.X% in YYYY"
- **Average growth (last 5 years)**: Calculate mean growth rate
- **Volatility**: Standard deviation of growth rates
- **Notable contractions**: Years with negative growth
- **Peak growth**: Maximum growth year and percentage

### Excerpt Templates

**English**:
- "Mongolia's economy {grew/contracted} by X.X% in YYYY, {comparison to previous year}."
- "Annual GDP growth rate from 1991 to YYYY, showing economic cycles and major events."

**Mongolian**:
- "YYYY онд Монгол Улсын эдийн засаг X.X%-иар {өссөн/унасан}."
- "1991-YYYY оны жилийн ДНБ-ий өсөлтийн хувь, эдийн засгийн мөчлөг болон томоохон үйл явдлуудыг харуулсан."

### Common Tags

- mongolia
- gdp
- growth
- economy
- national-accounts
- nso
- annual

## Notes

- Growth rates can be highly volatile year-to-year, especially for resource-dependent economies like Mongolia
- Mining sector performance has outsized impact on overall GDP growth
- Weather conditions affect agriculture and therefore GDP (especially pre-2000)
- This is a key macroeconomic indicator used by policymakers, investors, and international organizations
- **Storage**: Raw data is stored in parent's version directory at `tools/versions/nso-gdp-by-economic-activity/`
- **Version history**: Tracked through parent dataset versions
