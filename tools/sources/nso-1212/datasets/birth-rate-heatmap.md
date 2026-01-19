# Dataset: Birth Rate Heatmap (Split)

## Type: SPLIT DATASET

This is a **split dataset** - see the parent definition for full documentation.

## Parent Dataset

- **Parent ID**: `nso-birth-rates-by-age`
- **Parent Definition**: `tools/sources/nso-1212/datasets/nso-birth-rates-by-age.md`

## Split Configuration

- **ID**: `birth-rate-heatmap`
- **Filter**: `{"age_group": ["15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49"]}`
- **Title EN**: Mongolia Birth Rates Heatmap by Age and Year (1980-2024)
- **Title MN**: Монгол Улсын төрөлтийн түвшний халуун газрын зураг (1980-2024)
- **Chart Type**: heatmap

## Description

Heatmap visualization showing age-specific birth rates (per 1,000 women) across all reproductive age groups from 1980-2024. The color intensity represents the birth rate value, allowing visual identification of fertility transition patterns.

## Visualization Details

- **X-axis**: Year (1980-2024)
- **Y-axis**: Age groups (15-19, 20-24, 25-29, 30-34, 35-39, 40-44, 45-49)
- **Color**: Sequential red scale (0-350 births per 1,000)

## Key Patterns Visible

- Peak fertility (darkest red) concentrated in ages 20-29 during 1980s
- Dramatic decline across all age groups from 1990s onward
- Modern fertility levels much lower across all ages by 2024

## See Also

For complete documentation including:
- Source reference and API details
- All variable definitions
- Update instructions
- All available splits

See: [nso-birth-rates-by-age.md](nso-birth-rates-by-age.md)
