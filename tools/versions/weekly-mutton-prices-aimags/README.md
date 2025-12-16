# Dataset Version History: weekly-mutton-prices-aimags

This directory contains version history for the **Weekly Mutton Prices by Region in Mongolia** dataset.

## Dataset Information

- **ID**: `weekly-mutton-prices-aimags`
- **Parent Dataset**: `nso-weekly-prices-main-products`
- **Source**: NSO 1212.mn
- **Table ID**: `DT_NSO_0300_010V5.px`
- **Type**: Split dataset (filtered from parent)

## Split Filter

This dataset contains only mutton price data from the parent multi-product dataset:

```json
{
  "product": "Mutton, kg"
}
```

## Version Directory Structure

Each version (`v1/`, `v2/`, etc.) should contain:

- `data-en.csv` - English version of mutton prices (filtered from parent)
- `data-mn.csv` - Mongolian version of mutton prices (filtered from parent)
- `metadata.json` - Version metadata (timestamp, row count, etc.)

## Update Process

This is a split dataset. Updates should:

1. Load parent data from `nso-weekly-prices-main-products/v{N}/`
2. Filter to rows where `product == "Mutton, kg"`
3. Strip whitespace from all string columns
4. Export bilingual CSVs
5. Save to new version directory

## Notes

- Split datasets inherit their data from parent datasets
- Always verify parent dataset is updated before updating splits
- Version numbers should align with parent updates when possible
