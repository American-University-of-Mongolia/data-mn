# Dataset Version History: labor-participation-national

This directory contains versioned backups of the labour force participation rate dataset.

## Dataset Information

- **ID**: `labor-participation-national`
- **Source**: NSO 1212.mn
- **Table ID**: `DT_NSO_0400_018V1_1.px`
- **Category**: Labor Market
- **Published Pages**:
  - English: `/en/data/labor-participation-national`
  - Mongolian: `/mn/data/labor-participation-national`

## Version History

### v1 (2025-12-06)
- **Status**: Initial version backup
- **Data Range**: 1992-2024 (33 years)
- **Latest Value**: 61.3% (2024)
- **Historical High**: 75.8% (1992)
- **Row Count**: 33
- **Files**:
  - `data-en.csv` - English version
  - `data-mn.csv` - Mongolian version
  - `data.xlsx` - Excel format
  - `metadata.json` - Version metadata

## Version Directory Structure

Each version directory (`vN/`) contains:
- `data-en.csv` - English language data
- `data-mn.csv` - Mongolian language data
- `data.xlsx` - Excel format (bilingual or primary language)
- `metadata.json` - Version metadata (date, statistics, file info)

## Notes

- Versions are incremental (v1, v2, v3, etc.)
- Create a new version when source data is updated
- Keep all versions for historical tracking
- Metadata file tracks data statistics and update context
