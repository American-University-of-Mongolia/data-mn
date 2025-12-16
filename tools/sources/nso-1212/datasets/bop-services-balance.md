# Dataset: Services Trade Balance

## Identification

- **ID**: `bop-services-balance`
- **Source**: `nso-1212`
- **Parent ID**: `nso-bop-monthly`
- **Category**: Economy
- **Tags**: [balance-of-payments, bop, services, trade, tourism, transport, economy]

## Source Reference

- **Parent Table ID**: `DT_NSO_0100_001V10.px`
- **Sector**: `Economy, environment`
- **Subsector**: `Balance of Payments`
- **API Path**: `/en/NSO/Economy, environment/Balance of Payments/DT_NSO_0100_001V10.px`

## Title

- **EN**: Mongolia Services Trade Balance (2009-2025)
- **MN**: Монгол Улсын үйлчилгээний худалдааны тэнцэл (2009-2025)

## Description

Mongolia's monthly services trade balance including transport, tourism, and other services. This dataset is extracted from the broader Balance of Payments statistics and focuses specifically on the services component of the current account.

Services trade represents an important part of Mongolia's external accounts, particularly driven by:
- Tourism and travel services (seasonal patterns)
- Transportation services (linked to mining exports)
- Other business and personal services
- Financial and telecommunications services

The COVID-19 pandemic had a significant impact on services trade, particularly tourism.

## Split Filter

This is a split dataset derived from the parent `nso-bop-monthly` dataset.

**Filter criteria**:
```json
{
  "Indicator": "2. Services"
}
```

This extracts only the "Services" row from the BOP indicator hierarchy, which represents the net services trade balance (services exports minus services imports).

## Variables

### Month (Сар)
Monthly data from 2009-01 to present (format: YYYY-MM)

### Value
Services trade balance in million USD
- **Positive values**: Services trade surplus (exports > imports)
- **Negative values**: Services trade deficit (imports > exports)

## Update Instructions

### Data Source

This dataset is automatically updated when the parent dataset `nso-bop-monthly` is updated.

**Do not fetch data directly**. Instead:

1. Check if parent dataset has updates:
   ```bash
   cd /home/ritz/Insync/robert@aum.edu.mn/Google Drive/data/tools
   python -m registry info nso-bop-monthly
   ```

2. If parent has been updated, regenerate this split:
   ```bash
   # Load parent data
   parent_data = pd.read_csv("versions/nso-bop-monthly/v{N}/data-en.csv")

   # Apply filter
   split_data = parent_data[parent_data['indicator'] == '2. Services'].copy()

   # Save to version directory
   split_data.to_csv("versions/bop-services-balance/v{N}/data-en.csv", index=False)
   ```

### Validation

- Values can be positive or negative
- Values are in million USD
- Month format should be YYYY-MM
- Should have continuous monthly data from 2009-01 onwards
- Expected seasonal patterns (tourism peaks in summer months)

## Chart Specification

### Chart Type
Area chart with line overlay

### Visual Encoding

- **X-axis**: month (temporal)
- **Y-axis**: value (million USD, quantitative)
- **Mark**: Area with gradient fill + line
- **Color**: #4c78a8 (primary brand color)
- **Interpolation**: monotone (smooth curves)

### Chart Features

- Gradient fill showing positive/negative areas
- Hover tooltips with exact values
- Zero reference line
- Responsive width (no fixed dimensions)

### Expected Patterns

- **Seasonality**: Summer peaks (tourism season)
- **COVID-19 Impact**: Sharp decline in 2020-2021
- **Recovery**: Gradual improvement post-2022
- **Baseline**: Historically negative (Mongolia imports more services than exports)

## Content Generation

### Key Findings

Auto-extract:
- Latest month value and trend
- Year-to-date aggregate
- Same period last year comparison
- 12-month moving average
- COVID-19 impact magnitude (comparing 2019 vs 2020)
- Tourism seasonality strength (summer vs winter)

### Tags
- mongolia
- balance-of-payments
- bop
- services
- trade
- tourism
- transport
- economy
- nso
- monthly

### Keywords (EN)
- "Mongolia services trade"
- "services balance"
- "tourism Mongolia"
- "transport services"
- "services exports imports"
- "travel balance"

### Excerpt Template

**EN**: "Mongolia's services trade balance was ${value}M USD in {month}, showing {trend_direction}. Services trade is driven primarily by tourism and transport sectors."

**MN**: "{month} сард Монгол Улсын үйлчилгээний худалдааны тэнцэл ${value} сая ам.доллар байв. Үйлчилгээний худалдаа голчлон аялал жуулчлал, тээврийн салбараас хамаардаг."

### Related Datasets

- `bop-current-account` - Overall current account (includes services)
- `bop-trade-balance` - Goods trade (complementary to services)
- `bop-monthly` - Parent dataset with full BOP structure

## Notes

- Data follows IMF Balance of Payments Manual 6th Edition (BPM6) standards
- Services component includes:
  - Transport (air, rail, road freight and passenger)
  - Travel and tourism
  - Communications services
  - Construction services
  - Insurance and financial services
  - Computer and information services
  - Other business services
  - Personal, cultural, and recreational services
- Mongolia typically runs a services trade deficit
- Seasonal patterns are strong due to tourism
- COVID-19 pandemic severely impacted this indicator in 2020-2021
- **Split dataset**: Derived from parent `nso-bop-monthly`, automatically updated when parent updates
