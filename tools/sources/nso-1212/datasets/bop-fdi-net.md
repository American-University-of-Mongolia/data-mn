# Dataset: Mongolia Foreign Direct Investment, Net

## Identification

- **ID**: `bop-fdi-net`
- **Source**: `nso-1212`
- **Category**: Finance
- **Tags**: [mongolia, balance-of-payments, economy, fdi, foreign-investment]

## Dataset Type

**Split Dataset** - This is a filtered view from the parent dataset.

- **Parent Dataset**: `nso-bop-monthly`
- **Parent Definition**: `sources/nso-1212/datasets/bop-monthly.md`
- **Split Filter**: `{"indicator": "1. Direct investment"}`

## Title

- **EN**: Mongolia Foreign Direct Investment, Net, Million USD (2009-2025)
- **MN**: Монгол Улсын шууд хөрөнгө оруулалт, цэвэр (2009-2025)

## Description

Net foreign direct investment flows into Mongolia, primarily driven by mining sector investments. Shows monthly FDI inflows and outflows following IMF BPM6 standards.

**Coverage**:
- Time period: January 2009 to present
- Update frequency: Monthly
- Unit: Million USD
- Source: Balance of Payments - Financial Account

## Data Structure

This split extracts a single indicator from the parent BOP dataset:

### Variables
- **month**: Time period (YYYY-MM format)
- **value**: Net FDI in million USD (can be positive or negative)
  - Positive: Net FDI inflow
  - Negative: Net FDI outflow

## Chart Configuration

- **Chart Type**: Area chart (single-series time series)
- **X-axis**: month (temporal)
- **Y-axis**: value in million USD
- **Color**: #4c78a8 (primary blue)
- **Gradient**: Top-down fade from 30% to 1% opacity

## Update Process

This split is automatically regenerated when the parent dataset `nso-bop-monthly` is updated.

### Manual Update
If needed, regenerate this split:

```bash
cd tools
python -m registry regenerate-split bop-fdi-net
```

## Key Insights

**Typical Analysis Points**:
- FDI trend by year
- Mining investment cycles
- Recent investment momentum
- Comparison with other BOP components

**Notable Patterns**:
- Large negative values (outflows) are common in Mongolia's FDI data
- 2016 shows significant spike due to major mining project
- Seasonal patterns less pronounced than goods trade
- COVID-19 impact visible in 2020-2021

## Related Datasets

From same parent (`nso-bop-monthly`):
- `bop-current-account` - Current account balance
- `bop-trade-balance` - Goods trade
- `bop-services-balance` - Services trade
- `bop-reserve-assets` - Reserve changes
- `bop-remittances` - Personal transfers

## Version History

- **v1** (2025-12-09): Initial creation from parent BOP dataset

## Notes

- Data follows IMF Balance of Payments Manual 6th Edition (BPM6)
- Values are in million USD
- Negative values indicate net outflows (common for Mongolia)
- This is filtered data; for full BOP analysis see parent dataset
- Version directory: `tools/versions/bop-fdi-net/v1/`
