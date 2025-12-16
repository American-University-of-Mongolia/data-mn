# Dataset: GDP at Current Prices (Nominal GDP)

## Identification

- **ID**: `gdp-nominal`
- **Source**: `nso-1212`
- **Parent Dataset**: `nso-gdp-by-economic-activity`
- **Category**: Economy
- **Tags**: [gdp, economy, mongolia, nominal-gdp, current-prices, national-accounts]

## Source Reference

- **Parent Table ID**: `DT_NSO_0500_001V1.px`
- **Sector**: `Economy, environment`
- **Subsector**: `National Accounts`
- **API Path**: `/en/NSO/Economy, environment/National Accounts/DT_NSO_0500_001V1.px`

## Title

- **EN**: Mongolia GDP at Current Prices, Million MNT (1990-2024)
- **MN**: Монгол Улсын ДНБ өнөөгийн үнээр, сая төгрөг (1990-2024)

## Description

Mongolia's Gross Domestic Product (GDP) measured at current market prices from 1990 to 2024. This nominal GDP dataset shows the total economic output in millions of Mongolian Tugriks (MNT) without adjusting for inflation, reflecting both real economic growth and price changes over time.

This dataset is a filtered view from the parent multi-dimensional GDP dataset, extracting only the total GDP at current prices for simplified visualization and analysis.

## Variables

### Year (Он)
- Type: Temporal
- Range: 1990-2024 (35 data points)
- Format: YYYY

### Value (Утга)
- Type: Quantitative
- Unit: Million MNT (сая төгрөг)
- Description: Total GDP at current (nominal) prices
- Data source: Sum of all economic activities plus net taxes on products

## Split Filter

This dataset is created from the parent `nso-gdp-by-economic-activity` using:

```json
{
  "Indicator": "GDP, at current prices",
  "Economic activity": "Total"
}
```

## Data Structure

**Chart CSV** (`gdp-nominal-en.csv`, `gdp-nominal-mn.csv`):
- 2 columns: year, value
- 35 rows (1990-2024)
- Bilingual column names

**Download XLSX** (`gdp-nominal.xlsx`):
- Sheet 1: Data (wide format)
- Same structure as CSV for this simple time series

## Update Instructions

### Update Frequency

This dataset updates automatically when the parent dataset (`nso-gdp-by-economic-activity`) is updated, typically:
- **Frequency**: Quarterly
- **Source Update**: NSO updates GDP data quarterly with preliminary estimates, annual revisions

### Update Process

1. **Check parent dataset for updates:**
   ```bash
   cd tools
   python -m registry info nso-gdp-by-economic-activity
   ```

2. **Update parent dataset if needed** (this will cascade to all splits):
   ```bash
   /data-update --dataset nso-gdp-by-economic-activity
   ```

3. **This dataset will be regenerated automatically** from the parent data using the split filter.

### Manual Regeneration

If needed to regenerate this split without updating parent:

```python
import pandas as pd
import json

# Load parent data
parent_df = pd.read_csv('tools/versions/nso-gdp-by-economic-activity/nso-0500-001v1-en.csv')

# Apply split filter
filter_config = {
    "Indicator": "GDP, at current prices",
    "Economic activity": "Total"
}

filtered_df = parent_df.copy()
for column, value in filter_config.items():
    filtered_df = filtered_df[filtered_df[column] == value]

# Select relevant columns
output_df = filtered_df[['Year', 'value']].copy()
output_df.columns = ['year', 'value']

# Sort by year
output_df = output_df.sort_values('year').reset_index(drop=True)

# Save
output_df.to_csv('data.mn/public/datasets/gdp-nominal-en.csv', index=False)
```

## Validation

### Data Quality Checks

- GDP values should be positive
- Values should generally increase over time (nominal GDP rarely decreases)
- Year-over-year growth should be reasonable (typically 5-30% in Mongolia's case)
- No missing years in the 1990-2024 range

### Expected Patterns

- **1990-1995**: High nominal growth due to hyperinflation during transition period
- **2000s**: Strong growth driven by commodity boom
- **2020**: Slight decline due to COVID-19 pandemic
- **2021-2024**: Strong recovery and continued growth

### Chart Validation

```bash
cd tools
python3 scripts/validate_vega.py ../data.mn/public/charts/gdp-nominal-en.json --data ../data.mn/public/datasets/gdp-nominal-en.csv
python3 scripts/validate_vega.py ../data.mn/public/charts/gdp-nominal-mn.json --data ../data.mn/public/datasets/gdp-nominal-mn.csv
```

## Chart Configuration

**Type**: Single-series area chart with gradient fill

**Visual Encoding**:
- **X-axis**: year (quantitative, 1990-2024)
- **Y-axis**: value (GDP in million MNT, formatted with SI prefix)
- **Color**: Primary brand blue (#4c78a8)
- **Fill**: Gradient from transparent to semi-transparent blue
- **Hover**: Nearest-point tooltip with year and formatted GDP value

**Interactivity**:
- Hover shows year and GDP value
- Gradient fill provides visual emphasis
- Responsive sizing (no fixed width/height)

## Content Generation

### Excerpt Templates

**English**:
"Mongolia's nominal GDP reached {latest_value} million MNT in {latest_year}, showing {trend} from the previous year."

**Mongolian**:
"{latest_year} онд Монгол Улсын нэрлэсэн ДНБ {latest_value} сая төгрөгт хүрч, өмнөх оноос {trend}."

### Key Findings (Auto-Generated)

Extract these statistics:
- Latest year GDP value
- 5-year CAGR (Compound Annual Growth Rate)
- Decade comparisons (1990s, 2000s, 2010s, 2020s)
- Peak year and value
- COVID-19 impact (2020 vs 2019)

### Common Keywords

- mongolia
- gdp
- gross domestic product
- nominal gdp
- current prices
- economy
- economic growth
- national accounts
- nso
- mongolia economy

## Related Datasets

- `gdp-real` - GDP adjusted for inflation (2015 constant prices)
- `gdp-usd` - GDP measured in US dollars
- `gdp-growth-rate` - Year-over-year GDP growth percentage
- `gdp-by-sector` - Breakdown by economic sector
- `gdp-per-capita` - GDP divided by population

## Notes

- **Units**: Values are in millions of MNT (not billions or actual MNT)
- **Inflation**: This is nominal GDP (current prices), not adjusted for inflation
- **Comparison**: For real economic growth analysis, use `gdp-real` instead
- **International Comparison**: For comparing with other countries, use `gdp-usd`
- **Source**: National Statistical Office of Mongolia (NSO)
- **Methodology**: Follows System of National Accounts (SNA) 2008 standards
- **Revisions**: NSO may revise historical data as new information becomes available

## Historical Context

### 1990-1999: Transition Period
- Mongolia transitioned from centrally-planned to market economy
- High inflation caused rapid nominal GDP growth
- Economic structure shifted from Soviet-dependent to market-oriented

### 2000-2010: Commodity Boom
- Mining sector expansion (especially copper and coal)
- Foreign direct investment increased
- Nominal GDP grew rapidly

### 2011-2015: Mining Boom Peak
- Oyu Tolgoi copper mine development
- Record FDI inflows
- Tugrik depreciation increased nominal values

### 2016-2019: Stabilization
- Economic diversification efforts
- Steady growth with moderate inflation

### 2020-2024: Post-Pandemic
- 2020: COVID-19 impact (minimal GDP decline)
- 2021-2024: Strong recovery driven by commodity prices and domestic demand
