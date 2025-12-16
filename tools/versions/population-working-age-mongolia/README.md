# Dataset Versions: population-working-age-mongolia

This directory contains version history for the **Working Age Population of Mongolia (15-64)** dataset.

## Dataset Information

- **ID**: `population-working-age-mongolia`
- **Type**: Split Dataset
- **Parent**: `nso-population-age-sex`
- **Source**: NSO 1212.mn
- **Definition**: `tools/sources/nso-1212/datasets/population-working-age-mongolia.md`

## Version Structure

Each version is stored in a subdirectory `v{N}/` where N is the version number:

```
population-working-age-mongolia/
├── README.md (this file)
├── v1/
│   ├── data.csv
│   ├── metadata.json
│   └── CHANGELOG.md
├── v2/
│   ├── data.csv
│   ├── metadata.json
│   └── CHANGELOG.md
└── ...
```

## Version Files

Each version directory contains:

- **data.csv**: The raw data for this version (CSV format)
- **metadata.json**: Version metadata (date fetched, row count, date range, etc.)
- **CHANGELOG.md**: What changed in this version compared to previous

## Update Workflow

This is a **split dataset**, so it updates when its parent updates:

1. Parent dataset `nso-population-age-sex` is updated
2. Parent data is filtered using split definition
3. New version is created here if data changed
4. Bilingual CSVs and charts are regenerated
5. Version number is incremented in registry

## Current Status

No versions exist yet. The dataset is defined in the registry but has not been fetched.

## Next Steps

To create the first version:

1. Ensure parent dataset `nso-population-age-sex` has data
2. Run split regeneration:
   ```bash
   cd tools
   python scripts/regenerate_split.py population-working-age-mongolia
   ```
3. First version will be created at `v1/`
