# Version History: weekly-beef-prices-aimags

## About This Dataset

Weekly beef prices by region in Mongolia (2024-2025).

This is a split dataset derived from the parent dataset `nso-weekly-prices-aimags` (Table: DT_NSO_0300_010V5.px).

**Filter**: Products = "Beef, kg"

## Version Directory Structure

Each version directory (`v1/`, `v2/`, etc.) contains:
- `data.csv` - Raw data snapshot from NSO (all 25 regions)
- `metadata.json` - Version metadata (fetch date, row count, etc.)

## Current Version

**v1**: Initial version

## Update Policy

This dataset is updated automatically when the parent dataset is updated. Versions are incremented when:
- NSO publishes new weekly data
- Significant data corrections are made
- Filter criteria are modified

## Notes

- Split dataset: Only includes beef prices (parent has 11 products)
- Chart displays 4 regional aggregates for clarity
- Full download includes all 21 aimags + 4 regional aggregates
- Ulaanbaatar data is in a separate NSO table (not included)
