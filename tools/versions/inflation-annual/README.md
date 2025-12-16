# Dataset Version History: inflation-annual

This directory contains version backups of the `inflation-annual` dataset.

## Structure

Each version is stored in a subdirectory named `v{N}/`:

```
inflation-annual/
├── README.md          # This file
├── v1/                # Version 1
│   ├── metadata.json  # Version metadata
│   ├── data-en.csv    # English data
│   └── data-mn.csv    # Mongolian data
└── v2/                # Version 2 (future)
    └── ...
```

## Version History

### v1 (2024-12-06)
- **Rows**: 34 (1991-2024)
- **Source**: NSO 1212.mn (DT_NSO_0600_013V2.px)
- **Notes**: Initial version created from existing data.mn deployment

## Dataset Information

- **Name (EN)**: Mongolia Annual Inflation Rate (1991-2024)
- **Name (MN)**: Монгол Улсын жилийн инфляцийн түвшин (1991-2024)
- **Source**: National Statistics Office of Mongolia (NSO 1212.mn)
- **Table ID**: DT_NSO_0600_013V2.px
- **Category**: Economy
- **Tags**: inflation, cpi, economy, prices, consumer-prices

## Key Statistics

- **Latest Value**: 9.0% (2024)
- **Historical Peak**: 325.5% (1992)
- **Historical Low**: 1.3% (2016)
- **Time Span**: 1991-2024 (34 years)

## Update Process

When the dataset is updated:

1. New version directory is created (e.g., `v2/`)
2. Raw data files are saved (`data-en.csv`, `data-mn.csv`)
3. Metadata file is created with version info
4. This README is updated with new version entry
5. Registry is updated to point to new version

## Files

- **data-en.csv**: English language version (columns: year, value)
- **data-mn.csv**: Mongolian language version (columns: он, утга)
- **metadata.json**: Version metadata including stats, date, source info
