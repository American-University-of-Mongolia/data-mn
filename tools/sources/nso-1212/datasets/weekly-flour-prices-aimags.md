# Dataset: Weekly Flour Prices by Region

## Identification

- **ID**: `weekly-flour-prices-aimags`
- **Source**: `nso-1212`
- **Category**: Economy
- **Tags**: [prices, flour, food, regional, weekly, aimags, mongolia, inflation]
- **Concept ID**: `weekly-prices`

## Source Reference

- **Parent Dataset**: `nso-weekly-prices-aimags`
- **Parent Table ID**: `DT_NSO_0300_010V5.px`
- **Sector**: `Economy, environment`
- **Subsector**: `Consumer Price Index`
- **API Path**: `/en/NSO/Economy, environment/Consumer Price Index/DT_NSO_0300_010V5.px`

## Title

- **EN**: Weekly Flour Prices by Region in Mongolia (2024-2025)
- **MN**: Гурилын долоо хоногийн үнэ, бүсээр (2024-2025)

## Description

Weekly monitoring of flour prices (grade 1, prepacked) across Mongolia's four major regions (Central, Eastern, Western, and Khangai). This dataset tracks price variations and trends for a key staple food item that is essential for household budgeting and food security analysis.

The data is collected weekly since January 2024 and provides high-frequency price monitoring to track inflation, regional disparities, and market dynamics for flour, one of Mongolia's most important food commodities.

## Dataset Type

**Split Dataset** - This is a filtered view of the parent dataset `nso-weekly-prices-aimags`.

### Split Filter
```json
{
  "Products": "Flour, grade 1, prepacked, kg"
}
```

This filter extracts only flour prices from the multi-dimensional parent dataset which includes 11 different products (meat, dairy, grains, and fuel).

## Variables

### Date (Огноо)
- **Type**: Temporal
- **Range**: 2024-01-02 to present (97+ weekly observations)
- **Format**: YYYY-MM-DD (weekly, typically Mondays)
- **Frequency**: Weekly

### Region (Бүс)
- **Type**: Nominal
- **Values**: 4 regional aggregates + 21 individual aimags
- **Display**: Regional aggregates used in chart (4 series for clarity)
- **Full Data**: All 25 regions available in download files

**4 Regional Aggregates**:
- Central region (Төвийн бүс)
- Eastern region (Зүүн бүс)
- Western region (Баруун бүс)
- Khangai region (Хангайн бүс)

**21 Individual Aimags**: Arkhangai, Bayan-Ulgii, Bayankhongor, Bulgan, Darkhan-Uul, Dornod, Dornogovi, Dundgovi, Govi-Altai, Govisumber, Khentii, Khovd, Khuvsgul, Orkhon, Selenge, Sukhbaatar, Tuv, Umnugovi, Uvs, Uvurkhangai, Zavkhan

### Price (Үнэ)
- **Type**: Quantitative
- **Unit**: MNT per kilogram (₮/кг)
- **Description**: Average weekly retail price for grade 1 prepacked flour
- **Format**: Decimal (to 2 places)
- **Notes**:
  - Prices are averages across reporting locations within each region
  - Prepacked flour (standardized product for consistency)
  - Grade 1 quality specification

## Data Characteristics

### Time Coverage
- **First Date**: 2024-01-02
- **Latest Date**: 2025-12-01 (updated weekly)
- **Frequency**: Weekly (typically Monday observations)
- **Total Observations**: 97+ weeks × 4 regions = 388+ data points (chart subset)

### Value Range (as of December 2025)
- **Minimum**: ~1,000 MNT/kg
- **Maximum**: ~1,500 MNT/kg
- **Latest Average**: ~1,200-1,400 MNT/kg (varies by region)

### Regional Patterns
- **Price Variation**: Western and remote regions typically show higher prices due to transportation costs
- **Seasonality**: Limited seasonal variation (flour is not seasonal)
- **Volatility**: Moderate week-to-week changes, influenced by wheat harvest cycles and import prices

## Update Instructions

This split dataset updates automatically when the parent dataset (`nso-weekly-prices-aimags`) is refreshed. No separate update process is required.

### Manual Update Process (if needed)

1. **Check parent for updates**:
   ```bash
   cd tools && python -m registry info nso-weekly-prices-aimags
   ```

2. **If parent needs update**:
   ```bash
   cd tools && python -m registry update nso-weekly-prices-aimags
   ```

3. **Regenerate split**:
   - Parent update automatically triggers split regeneration
   - Split filter is applied to new parent data
   - CSV, XLSX, and chart files are regenerated
   - MDX pages are preserved (manual update if needed)

## Validation Rules

- All price values must be positive (> 0)
- Date values must be valid weekly dates (typically Mondays)
- Prices should be within reasonable range (500-3000 MNT/kg)
- No unrealistic week-to-week jumps (>50% change would be suspicious)
- Missing values are acceptable (some regions may have reporting gaps)

## Chart Configuration

### Chart Type
Multi-line chart (time series comparison)

### Chart Data Strategy
- **Chart CSV** (`weekly-flour-prices-aimags-{lang}.csv`): 4 regional aggregates only (for readability)
- **Download CSV** (`weekly-flour-prices-aimags-all-{lang}.csv`): All 25 regions (comprehensive data)
- **Download XLSX** (`weekly-flour-prices-aimags.xlsx`): Wide format with all regions as columns

### Vega-Lite Specification
- **X-axis**: date (temporal, weekly)
- **Y-axis**: price (quantitative, format: ",.0f" for MNT)
- **Mark**: line with interpolation
- **Color**: region (4 series, brand color palette)
- **Interaction**: Nearest-point hover with tooltip
- **Tooltip**: Shows date, region, and price

### Bilingual Charts
- `public/charts/weekly-flour-prices-aimags-en.json` - English version
- `public/charts/weekly-flour-prices-aimags-mn.json` - Mongolian version

## Related Datasets

### From Same Parent
- `weekly-beef-prices-aimags` - Weekly beef prices by region
- `weekly-mutton-prices-aimags` - Weekly mutton prices by region
- `weekly-milk-prices-aimags` - Weekly fresh milk prices by region
- `weekly-gasoline-prices-aimags` - Weekly A-92 petrol prices by region
- `weekly-diesel-prices-aimags` - Weekly diesel prices by region

### Complementary Datasets
- `inflation-rate-annual` - Overall inflation context
- `weekly-prices-ulaanbaatar` - UB-specific prices (if available)
- `food-basket-prices` - Food basket price index

## Content Generation

### MDX Page Structure
- **Hero section**: Latest average price and regional comparison
- **Chart**: Interactive multi-line chart showing 4 regional trends
- **Key Findings**:
  - Latest average price across regions
  - Highest and lowest priced regions
  - Price change vs previous week
  - Price change since start of tracking (Jan 2024)
- **Downloads**: CSV (chart subset and full data) and XLSX in both languages

### SEO Keywords
- mongolia flour prices
- weekly flour prices mongolia
- flour price regional mongolia
- aimag flour prices
- mongolia food prices
- flour inflation mongolia

### Excerpt Template

**EN**: "Flour prices in Mongolia averaged {avg_price} MNT/kg in week ending {latest_date}, ranging from {min_price} MNT/kg in {min_region} to {max_price} MNT/kg in {max_region}."

**MN**: "{latest_date}-д Монгол Улсын гурилын дундаж үнэ {avg_price} ₮/кг байсан бөгөөд {min_region}-д {min_price} ₮/кг, {max_region}-д {max_price} ₮/кг байв."

## Use Cases

### For Households
- Budget planning for staple food purchases
- Understanding regional price differences
- Timing bulk purchases

### For Policymakers
- Food security monitoring
- Inflation early warning signals
- Regional development equity analysis
- Price stabilization policy evaluation

### For Researchers
- Food price volatility studies
- Regional market integration analysis
- Supply chain efficiency research
- Inflation transmission studies

### For Businesses
- Retail pricing benchmarking
- Supply chain optimization
- Market entry analysis (regional differences)

## Notes

- **Coverage**: Covers 21 aimags + 4 regional aggregates; **Ulaanbaatar data NOT included** (separate dataset)
- **Product Specification**: Grade 1, prepacked flour (standardized for consistency)
- **Regional Aggregates**: Useful for high-level trends; individual aimags available in full downloads
- **Transportation Impact**: Remote/western regions show higher prices due to logistics costs
- **Weekly Updates**: High-frequency data enables real-time price monitoring
- **Data Source**: National Statistical Office price monitoring program
- **Reporting Method**: Averages across multiple retail locations within each region

## Version History

### Version 1 (2025-12-16)
- Initial creation from parent dataset
- Data: 2024-01-02 to 2025-12-01 (97+ weeks)
- Source: DT_NSO_0300_010V5.px
- Filter: "Flour, grade 1, prepacked, kg"
- Chart: 4 regional aggregates
- Downloads: All 25 regions
