# Dataset: Reserve Asset Changes (Split from BOP Monthly)

## Identification

- **ID**: `bop-reserve-assets`
- **Source**: `nso-1212`
- **Category**: Economy
- **Tags**: [balance-of-payments, bop, reserves, central-bank, monetary-policy, economy]

## Parent Dataset

- **Parent ID**: `nso-bop-monthly`
- **Parent Table**: `DT_NSO_0100_001V10.px`
- **Parent Definition**: `tools/sources/nso-1212/datasets/bop-monthly.md`

## Source Reference

- **Table ID**: `DT_NSO_0100_001V10.px`
- **Sector**: `Economy, environment`
- **Subsector**: `Balance of Payments`
- **API Path**: `/en/NSO/Economy, environment/Balance of Payments/DT_NSO_0100_001V10.px`

## Title

- **EN**: Mongolia Reserve Asset Changes (2009-2025)
- **MN**: Монгол Улсын нөөц хөрөнгийн өөрчлөлт (2009-2025)

## Description

Monthly changes in Mongolia's official reserve assets held by the Bank of Mongolia (central bank). Reserve assets include foreign currency reserves, gold, Special Drawing Rights (SDRs), and other liquid foreign assets that can be used to finance balance of payments deficits and stabilize the exchange rate.

Data follows IMF Balance of Payments Manual 6th Edition (BPM6) standards.

## Split Filter

```json
{
  "indicator": "V. RESERVE ASSETS"
}
```

This filter extracts only the reserve assets line item from the full BOP dataset.

## Variables

### Indicator (Үзүүлэлт)
- `V. RESERVE ASSETS`: Net change in reserve assets (positive = accumulation, negative = depletion)

### Month (Сар)
Monthly data from 2009-01 to 2025-09 (201+ months)

## Data Characteristics

- **Values**: In million USD
- **Sign Convention**:
  - **Positive**: Increase in reserves (accumulation)
  - **Negative**: Decrease in reserves (depletion/use)
- **Frequency**: Monthly
- **Seasonality**: Moderate - driven by trade patterns and foreign investment flows
- **Volatility**: High during crisis periods (2016 economic crisis, 2020 COVID-19)

## Chart Specification

- **Chart Type**: Area chart with gradient fill
- **Chart Config**:
  - X-axis: month (YYYY-MM format)
  - Y-axis: value (million USD)
  - Color: #4c78a8 (primary blue) with gradient fill
  - Interpolation: monotone (smooth line)
  - Tooltip: Month and value with proper formatting

## Key Findings Template

For content generation, calculate:
- Latest month value and direction (accumulation/depletion)
- Year-to-date net change
- 12-month cumulative change
- Comparison with same month previous year
- Identify crisis periods (sharp depletion)
- Current reserve adequacy trend

## Update Instructions

### Check for Updates

This is a split dataset. Updates come from the parent dataset `nso-bop-monthly`.

1. Check parent dataset for updates using registry:
   ```bash
   cd tools && python -m registry info nso-bop-monthly
   ```

2. If parent has updates, re-run the split transformation

### Regenerate Split

```bash
cd tools
python -m registry info bop-reserve-assets  # Check current version
# Parent update will trigger automatic regeneration of this split
```

### Validation

- Values can be positive (accumulation) or negative (depletion)
- Values should align with Bank of Mongolia reserve level announcements
- Sharp changes should correspond to known economic events:
  - 2016: Economic crisis, reserves declined
  - 2017-2019: Recovery, reserve accumulation
  - 2020: COVID-19 impact
  - 2021-present: Commodity boom support

## Related Datasets

- `nso-bop-monthly`: Parent dataset with full BOP structure
- `bop-current-account`: Current account balance (affects reserves)
- `bop-trade-balance`: Trade flows (major driver of reserve changes)
- `bop-fdi-net`: Foreign investment flows
- `mongolbank-reserves`: Bank of Mongolia's official reserve level data (stock vs flow)

## Excerpt Templates

**EN**: "Mongolia's reserve assets {increased/decreased} by ${abs_value}M USD in {month}, {accumulation/depletion} compared to the previous month."

**MN**: "{month} сард Монгол Улсын нөөц хөрөнгө ${abs_value} сая ам.долларын {өсөлт/бууралт} гарч, {өмнөх сартай харьцуулахад} {хуримтлагдсан/зарцуулагдсан}."

## Notes

- **Flow vs Stock**: This dataset shows CHANGES in reserves (flows), not the total level (stock)
- For total reserve levels, see Bank of Mongolia's official statistics
- Positive/negative convention follows BPM6 standards
- Large swings indicate balance of payments pressures or central bank intervention
- Important for assessing Mongolia's external financial stability
- **Data Source**: Derived from parent dataset `nso-bop-monthly`
