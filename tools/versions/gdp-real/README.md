# Dataset Version History: gdp-real

## Dataset Information

- **ID**: `gdp-real`
- **Type**: Split Dataset (derived from parent)
- **Parent**: `nso-gdp-by-economic-activity`
- **Definition**: `sources/nso-1212/datasets/gdp-real.md`

## About This Directory

This directory stores version history for the `gdp-real` dataset.

**Note**: Since `gdp-real` is a **split dataset** (filtered subset of the parent), it does not store raw source data here. The raw source data is stored in the parent dataset's version directory:

```
tools/versions/nso-gdp-by-economic-activity/
```

## What Gets Versioned

When the dataset is updated, the following files are versioned here:

- **Processed data files**: The filtered CSV files (EN/MN)
- **Metadata**: Information about the update (date, version, changes)
- **Generation script**: If custom transformation was used

## Current Version

**Version 1** (created: 2025-12-03)
- Initial dataset creation
- Data range: 2015-2024 (10 years)
- Source: NSO table DT_NSO_0500_001V1.px
- Filter: GDP at 2015 constant prices, Total economic activity

## Data Lineage

```
NSO 1212.mn API
    ↓
DT_NSO_0500_001V1.px (raw table)
    ↓
nso-gdp-by-economic-activity (parent dataset)
    ↓ [Filter: Indicator=2015 prices, Activity=Total]
gdp-real (this split dataset)
    ↓
Published files:
  - data.mn/public/datasets/gdp-real-en.csv
  - data.mn/public/datasets/gdp-real-mn.csv
  - data.mn/public/datasets/gdp-real.xlsx
```

## Update Process

To update this dataset:

1. Update the parent dataset (`nso-gdp-by-economic-activity`)
2. Re-apply the split filter to generate new data files
3. Increment version number
4. Store previous version files here for rollback capability

See parent dataset definition for NSO API update instructions.
