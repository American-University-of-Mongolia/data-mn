# Dataset: Real GDP at 2015 Constant Prices

## Identification

- **ID**: `gdp-real`
- **Parent Dataset**: `nso-gdp-by-economic-activity`
- **Source**: `nso-1212`
- **Category**: Economy
- **Tags**: [gdp, economy, real-gdp, constant-prices, economic-growth, mongolia]

## Dataset Type

**Split Dataset** - This is a filtered subset of the parent dataset `nso-gdp-by-economic-activity`.

## Parent Reference

- **Parent ID**: `nso-gdp-by-economic-activity`
- **Parent Table**: `DT_NSO_0500_001V1.px`
- **Parent Definition**: `sources/nso-1212/datasets/gdp-by-economic-activity.md`

## Title

- **EN**: Mongolia Real GDP at 2015 Prices (2015-2024)
- **MN**: Монгол Улсын бодит ДНБ 2015 оны үнээр (2015-2024)

## Description

Mongolia's real GDP measured at constant 2015 prices, adjusted for inflation. This shows true economic growth by removing the effect of price changes, allowing for accurate comparison of economic output across time. Data spans from 2015 to 2024.

Real GDP is the most reliable indicator for tracking actual economic expansion or contraction, as it measures the volume of goods and services produced rather than their monetary value.

## Split Filter

This dataset is created by filtering the parent dataset with:

```json
{
  "Indicator": "GDP, at 2015 constant prices",
  "Economic activity": "Total"
}
```

This extracts:
- **Only** the "GDP, at 2015 constant prices" indicator (excludes nominal GDP, growth rates, sector contributions, etc.)
- **Only** the "Total" economic activity (excludes individual sectors)
- **All** years from 2015 to 2024 (base year onwards)

## Data Structure

### Columns

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `year` | integer | Year of observation | 2024 |
| `value` | float | Real GDP in million MNT (2015 prices) | 42789563.0 |

### Data Characteristics

- **Temporal Coverage**: 2015-2024 (10 years)
- **Frequency**: Annual
- **Geographic Coverage**: Mongolia (national level)
- **Units**: Million MNT at 2015 constant prices
- **Base Year**: 2015 prices (inflation-adjusted)

**Note**: The parent dataset contains GDP data from 1990 onwards, but this split only includes data from 2015 (the base year) forward. Earlier years use different base years (2005, 2010) and are available in separate datasets.

## Chart Specification

### Chart Type
Single-series area chart with gradient fill

### Visual Encoding

- **X-axis**: `year` (quantitative, format: "d")
  - Title: "Year" / "Он"
  - Grid: disabled
  - Tick step: 5 years
- **Y-axis**: `value` (quantitative, format: ".2s")
  - Title EN: "Real GDP, Billion MNT (2015 prices)"
  - Title MN: "Бодит ДНБ, тэрбум төгрөг (2015 оны үнээр)"
  - Abbreviation: Shows billions as "42.8B" instead of "42,789,563,000"
- **Color**: `#4c78a8` (brand primary blue)
  - Line: solid, 2.5px width
  - Fill: vertical gradient from 30% opacity (top) to 1% opacity (bottom)
- **Interpolation**: monotone (smooth curve)
- **Hover**: Nearest-point interaction with tooltip showing year and formatted value

### Key Visual Features

- Responsive sizing (no fixed width/height)
- Clean, minimal axis styling
- Hover tooltips with comma-formatted values
- Smooth area gradient emphasizing growth trend

## Update Instructions

### Data Source

This split dataset is regenerated whenever the parent dataset (`nso-gdp-by-economic-activity`) is updated.

**Do not fetch data directly for this split.** Instead:

1. Update the parent dataset using its update instructions
2. The split will be automatically regenerated with the new filter applied

### Manual Regeneration

If needed, regenerate this split from parent data:

```python
import pandas as pd

# Load parent data
parent_df = pd.read_csv('tools/versions/nso-gdp-by-economic-activity/nso-0500-001v1-en.csv')

# Apply filter
filtered_df = parent_df[
    (parent_df['indicator'] == 'GDP, at 2015 constant prices') &
    (parent_df['economic_activity'] == 'Total')
].copy()

# Select and rename columns
gdp_real = filtered_df[['year', 'value']].copy()

# Sort by year
gdp_real = gdp_real.sort_values('year').reset_index(drop=True)

# Save
gdp_real.to_csv('data/data.mn/public/datasets/gdp-real-en.csv', index=False)
```

Repeat for Mongolian version using `nso-0500-001v1-mn.csv`.

### Validation

- All values should be positive
- Years should be continuous from 2015 to 2024 (10 data points)
- Real GDP should show general upward trend (with some fluctuations)
- 2020 shows COVID-19 impact (visible dip from 27.9T to 26.7T MNT)
- Values should be in millions of MNT (e.g., 32,132,739 million = 32.1 trillion MNT)

## Key Insights & Context

### Economic Significance

- **2015 Base Year**: The current national accounts standard uses 2015 as the base year for constant prices
- **Inflation Adjustment**: Real GDP removes the effect of price increases, showing actual economic volume growth
- **Policy Indicator**: Central banks and government use real GDP growth to guide monetary and fiscal policy

### Historical Patterns (2015-2024)

- **2015-2019**: Steady growth averaging ~6% annually
- **2020**: COVID-19 pandemic impact (-4.6% contraction, GDP fell from 27.9T to 26.7T MNT)
- **2021-2024**: Post-pandemic recovery and expansion (40% total growth from 2015 to 2024)

### Relationship to Other Metrics

- **Nominal GDP** (`gdp-nominal`): Real GDP × GDP deflator = Nominal GDP
- **GDP Growth Rate** (`gdp-growth-rate`): % change in Real GDP year-over-year
- **GDP by Sector** (`gdp-sector-trends`): Sum of all sectors = Total Real GDP

## Content Generation

### Excerpt Templates

**English**:
"Mongolia's real GDP, adjusted for inflation using 2015 constant prices, grew from {first_value} million MNT in {first_year} to {latest_value} million MNT in {latest_year}, representing a {growth_multiple}x increase in actual economic output."

**Mongolian**:
"Монгол Улсын бодит ДНБ 2015 оны тогтмол үнээр тооцсон {first_year} оны {first_value} сая төгрөгөөс {latest_year} онд {latest_value} сая төгрөг болж, бодит эдийн засгийн үйлдвэрлэл {growth_multiple} дахин өссөн байна."

### Key Findings (Auto-calculated)

When generating MDX pages, calculate:
- Latest real GDP value (2024)
- Total growth multiple (latest / earliest)
- Average annual growth rate (CAGR)
- Highest growth year (year with biggest increase)
- Lowest/recession year (year with biggest decrease)

### Related Datasets

- `gdp-nominal` - Nominal GDP at current prices
- `gdp-growth-rate` - Annual GDP growth rate (%)
- `gdp-usd` - GDP in US dollars
- `gdp-by-sector` - GDP breakdown by economic sector
- `gdp-sector-trends` - Sectoral GDP trends over time

## Notes

- Real GDP is more useful than nominal GDP for tracking long-term economic performance
- The 2015 base year may be updated in future (NSO typically rebases every 10 years)
- Values are stored in **millions** (not billions) in the CSV to maintain precision
- Chart displays values in **billions** for readability (using `.2s` format)
- **Parent dataset**: Raw multi-dimensional data stored in `nso-gdp-by-economic-activity`
