# Dataset: GDP in US Dollars

## Identification

- **ID**: `gdp-usd`
- **Source**: `nso-1212`
- **Category**: Economy
- **Tags**: [gdp, economy, usd, national-accounts, mongolia]

## Source Reference

- **Parent Dataset**: `nso-gdp-by-economic-activity`
- **Parent Table ID**: `DT_NSO_0500_001V1.px`
- **Sector**: `Economy, environment`
- **Subsector**: `National Accounts`
- **API Path**: `/en/NSO/Economy, environment/National Accounts/DT_NSO_0500_001V1.px`

## Title

- **EN**: Mongolia GDP in US Dollars (1990-2024)
- **MN**: Монгол Улсын ДНБ ам.доллараар (1990-2024)

## Description

Mongolia's Gross Domestic Product (GDP) measured in US dollars for international comparison and analysis. This dataset provides GDP values converted from MNT to USD at current exchange rates, enabling direct comparison with other economies and tracking Mongolia's economic performance in international terms.

The data spans from 1990 to 2024, covering the transition period, commodity boom years, and recent economic developments.

## Dataset Type

**Split Dataset** - This is a filtered view of the parent dataset `nso-gdp-by-economic-activity`.

### Split Filter
```json
{
  "Indicator": "GDP, at current price, thousand USD",
  "Economic activity": "Total"
}
```

This filter extracts only the total GDP values in USD from the multi-dimensional parent dataset.

## Variables

### Year (Он)
- **Type**: Quantitative
- **Range**: 1990-2024 (35 data points)
- **Format**: Integer (YYYY)

### Value (Утга)
- **Type**: Quantitative
- **Unit**: Thousand USD
- **Description**: Total GDP of Mongolia in thousands of US dollars
- **Format**: Decimal (to 2 places)
- **Notes**:
  - Values converted from MNT at current exchange rates
  - Suitable for international comparisons
  - Subject to exchange rate fluctuations

## Data Characteristics

### Time Coverage
- **First Year**: 1990
- **Last Year**: 2024
- **Frequency**: Annual
- **Total Observations**: 35

### Value Range (as of 2024)
- **Minimum**: 746,336,470 USD (1993 - transition period collapse)
- **Maximum**: 23,793,357,510 USD (2024 - recent peak)
- **Latest Value**: 23.8 billion USD (2024)

### Key Historical Points
- **1990**: 3.3 billion USD (pre-transition)
- **1991-1993**: Economic collapse period (dropped to 746M USD in 1993)
- **2000s**: Recovery phase (reached 1.1B by 2000)
- **2011**: Major commodity boom (10.4B USD)
- **2020**: COVID-19 impact (13.3B USD)
- **2024**: Record high (23.8B USD)

## Update Instructions

This split dataset updates automatically when the parent dataset (`nso-gdp-by-economic-activity`) is refreshed. No separate update process is required.

### Manual Update Process (if needed)

1. **Check parent for updates**:
   ```bash
   cd tools && python -m registry info nso-gdp-by-economic-activity
   ```

2. **If parent needs update**:
   ```bash
   cd tools && python -m registry update nso-gdp-by-economic-activity
   ```

3. **Regenerate split**:
   - Parent update automatically triggers split regeneration
   - Split filter is applied to new parent data
   - CSV, XLSX, and chart files are regenerated
   - MDX pages are preserved (manual update if needed)

## Validation Rules

- All GDP values must be positive (> 0)
- Year values must be valid years between 1990-2024
- No missing years in the sequence
- Values should show general upward trend (accounting for crisis periods)
- No unrealistic year-over-year changes (>100% jumps would be suspicious)

## Chart Configuration

### Chart Type
Single-series area chart (time series)

### Vega-Lite Specification
- **X-axis**: year (quantitative, format: "d")
- **Y-axis**: value (quantitative, format: ".2s" for billions)
- **Mark**: area with gradient fill
- **Color**: #4c78a8 (primary brand color)
- **Interpolation**: monotone
- **Tooltip**: Shows year and value in billions USD

### Bilingual Charts
- `public/charts/gdp-usd-en.json` - English version
- `public/charts/gdp-usd-mn.json` - Mongolian version

## Related Datasets

### From Same Parent
- `gdp-nominal` - GDP in MNT (current prices)
- `gdp-real` - GDP in MNT (2015 constant prices)
- `gdp-growth-rate` - Annual GDP growth rate (%)
- `gdp-by-sector` - GDP breakdown by economic sector
- `gdp-sector-trends` - Major sectors over time

### Complementary Datasets
- `exchange-rate-usd-mnt` - USD/MNT exchange rate (if available)
- `population-total` - For calculating GDP per capita
- `inflation-rate-annual` - For understanding real vs nominal growth

## Content Generation

### MDX Page Structure
- **Hero section**: Latest value and historical comparison
- **Chart**: Interactive area chart showing full time series
- **Key Findings**:
  - Latest GDP in USD
  - Growth since 1990 (in absolute and percentage terms)
  - Notable historical periods (transition, commodity boom, COVID)
- **Downloads**: CSV and XLSX in both languages

### SEO Keywords
- mongolia gdp usd
- gdp dollars
- mongolia economy
- gdp international
- mongolia economic growth
- mongolia gdp billion

## Use Cases

### For Researchers
- International economic comparisons
- Foreign direct investment analysis
- Economic policy impact studies
- Exchange rate analysis

### For Investors
- Market size assessment
- Economic trend analysis
- Risk evaluation
- Growth trajectory forecasting

### For Government/NGOs
- Economic benchmarking
- Development planning
- International reporting
- Grant/loan applications

## Notes

- **Exchange Rate Impact**: USD values fluctuate with exchange rates, making comparisons more volatile than MNT-based measures
- **Preferred for**: International comparisons, FDI analysis
- **Not Preferred for**: Domestic policy analysis (use `gdp-nominal` or `gdp-real`)
- **1990s Volatility**: Extreme values reflect both economic transition and exchange rate instability
- **2008-2009 Drop**: Global financial crisis impact
- **Recent Growth**: 2020-2024 shows strong recovery and growth, reaching record levels

## Version History

### Version 1 (2025-12-03)
- Initial creation from parent dataset
- Data: 1990-2024 (35 years)
- Source: DT_NSO_0500_001V1.px
- Last fetched: 2025-12-03
