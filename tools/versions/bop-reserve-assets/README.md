# bop-reserve-assets - Version History

This directory contains version history for the `bop-reserve-assets` dataset.

## Dataset Overview

- **ID**: `bop-reserve-assets`
- **Type**: Split dataset (derived from `nso-bop-monthly`)
- **Source**: NSO 1212.mn
- **Category**: Economy / Эдийн засаг

## Version Structure

Each version is stored in a `vN/` subdirectory:

```
bop-reserve-assets/
├── README.md           # This file
├── v1/                 # Version 1
│   ├── VERSION.md          # Version metadata and changelog
│   ├── bop-reserve-assets-en.csv   # English data
│   ├── bop-reserve-assets-mn.csv   # Mongolian data
│   └── bop-reserve-assets.xlsx     # Excel export
└── v2/                 # Future versions...
```

## Version History

### v1 (2025-12-09)
- **Status**: Active
- **Data Period**: 2009-01 to 2025-09 (201 months)
- **Records**: 201 data points
- **Parent Version**: nso-bop-monthly v1
- **Notes**: Initial version created as split from parent BOP dataset

## Update Policy

This dataset is a split from `nso-bop-monthly`. When the parent dataset updates:

1. Parent dataset is fetched from NSO 1212.mn API
2. Filter is applied: `{"indicator": "V. RESERVE ASSETS"}`
3. New version is created in this directory
4. Registry is updated with new version number
5. MDX pages and charts are regenerated

## Data Definition

See the dataset definition file at:
```
tools/sources/nso-1212/datasets/bop-reserve-assets.md
```

This file contains:
- Source API information
- Split filter specification
- Column definitions
- Update instructions
- Chart configuration
- Content generation templates

## Related Datasets

- **Parent**: `nso-bop-monthly` (full Balance of Payments data)
- **Siblings**:
  - `bop-current-account`
  - `bop-trade-balance`
  - `bop-services-balance`
  - `bop-fdi-net`
  - `bop-remittances`

## Notes

- **NEVER delete old versions** - they provide historical context and reproducibility
- Version numbers increment automatically when parent dataset updates
- Each version includes bilingual CSVs (EN + MN) and Excel export
- VERSION.md in each version directory documents data characteristics and changes
