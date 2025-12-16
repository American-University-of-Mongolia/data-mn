# Version History: bop-services-balance

This directory contains version history for the `bop-services-balance` dataset.

## Dataset Information

- **ID**: `bop-services-balance`
- **Type**: Split dataset (derived from parent)
- **Parent**: `nso-bop-monthly`
- **Source**: National Statistical Office of Mongolia (1212.mn)
- **Update Frequency**: Monthly (updated when parent updates)

## About This Dataset

Services Trade Balance represents the net balance of Mongolia's international trade in services, including:
- Tourism and travel
- Transportation services
- Business services
- Financial services
- Communications

This is a filtered view from the broader Balance of Payments data, focusing specifically on the services component.

## Version Directory Structure

Each version (v1, v2, etc.) contains:
- `data-en.csv` - English version of the data
- `data-mn.csv` - Mongolian version of the data
- `metadata.json` - Update timestamp, source version, row counts

## Update Process

This dataset is automatically regenerated when the parent dataset `nso-bop-monthly` is updated:

1. Parent dataset updates from NSO API
2. Filter is applied: `indicator == "2. Services"`
3. Bilingual CSV files are generated
4. New version is created here
5. Registry is updated with new version number

## Filter Criteria

```json
{
  "Indicator": "2. Services"
}
```

This extracts only the services trade balance row from the full BOP table.

## Notes

- Do not manually edit files in version directories
- Versions are immutable once created
- Always increment version number when updating
- Coordinate updates with parent dataset `nso-bop-monthly`
