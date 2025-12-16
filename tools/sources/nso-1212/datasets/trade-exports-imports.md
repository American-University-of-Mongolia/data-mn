# Dataset: Mongolia Exports and Imports

## Identification

- **ID**: `trade-exports-imports`
- **Source**: `nso-1212`
- **Category**: Trade
- **Tags**: [mongolia, trade, economy, foreign-trade, export, import]

## Source Reference

- **Table ID**: `DT_NSO_1400_001V1_year.px`
- **Sector**: `Foreign Trade`
- **Subsector**: `Foreign trade`
- **API Path**: `/en/NSO/Foreign Trade/Foreign trade/DT_NSO_1400_001V1_year.px`

## Title

- **EN**: Mongolia Exports and Imports, Million USD (1924-2024)
- **MN**: Монгол Улсын экспорт, импорт, сая ам.доллар (1924-2024)

## Description

Mongolia's historical exports and imports from 1924 to 2024, showing the breakdown of foreign trade by direction in million USD. This long-running time series provides a century of trade data, capturing the transition from Soviet-era trade patterns to modern market economy trade flows.

## Variables

### Indicator (Үзүүлэлт)
Two indicators/series:
- `Exports`: Total exports (FOB value)
- `Imports`: Total imports (FOB value)

### Year (Он)
Annual data from 1924 to 2024 (101 years)

### Value
- **Unit**: Million USD
- **Range**: Positive values only

## Update Instructions

### Check for Updates

1. Query the table listing endpoint:
   ```
   GET https://data.1212.mn/api/v1/en/NSO/Foreign Trade/Foreign trade/
   ```

2. Find `DT_NSO_1400_001V1_year.px` in the response

3. Compare the `updated` field with `source_updated_at` in registry

4. If API's `updated` is newer, dataset needs updating

### Fetch Data

Use the `datamn-source-nso` skill for bilingual data fetching:

```python
import requests
import pandas as pd

BASE_URL = "https://data.1212.mn/api/v1"
sector = "Foreign Trade"
subsector = "Foreign trade"
table_id = "DT_NSO_1400_001V1_year.px"

# Fetch in both English and Mongolian
for lang in ['en', 'mn']:
    url = f"{BASE_URL}/{lang}/NSO/{sector}/{subsector}/{table_id}"

    # Get metadata
    metadata = requests.get(url).json()

    # Build query for all data
    query = {
        "query": [
            {
                "code": var['code'],
                "selection": {
                    "filter": "item",
                    "values": var['values']
                }
            }
            for var in metadata.get('variables', [])
        ],
        "response": {"format": "json-stat2"}
    }

    # Fetch data (POST request)
    data = requests.post(url, json=query).json()
```

### Data Transformation

1. **Filter to Exports and Imports only**:
   - Indicator: Exports, Imports

2. **Clean column names**:
   - Rename columns to: `indicator`, `year`, `value`
   - Strip whitespace from all string columns

3. **Data validation**:
   - All trade values should be positive
   - Year values should be valid years (1924-2024)

4. **Export files**:
   - Chart CSV: `trade-exports-imports-en.csv` and `trade-exports-imports-mn.csv`
   - Excel XLSX: `trade-exports-imports.xlsx` (with English and Mongolian sheets)

### Validation

- Export and Import values should be positive
- Year values should be valid years (1924-2024)
- No missing years in the series
- Both series (Exports/Imports) should have matching years

## Chart Configuration

### Chart Type
Multi-line chart with two series

### Visual Encoding

- **X-axis**: year (temporal)
- **Y-axis**: value in million USD (quantitative)
- **Color Scale**:
  - Exports: `#54a24b` (green - goods going out, positive for economy)
  - Imports: `#e45756` (red - goods coming in, money going out)
- **Interpolation**: monotone (smooth curves)
- **Legend**: Top horizontal, showing both series

### Tooltip

Display for each point:
- Year
- Indicator name (Exports/Imports)
- Value (formatted as "$###,###M USD")

## Content Generation

### Key Findings Template

Auto-extract for MDX page:
- Latest year's export value
- Latest year's import value
- Historical comparison (growth since 1924)
- Peak year for exports
- Peak year for imports
- Overall trend analysis

### Common Tags
- mongolia
- trade
- exports
- imports
- foreign-trade
- economy
- nso
- annual

### Keywords (EN)
- Mongolia exports
- Mongolia imports
- foreign trade
- trade balance
- international trade
- economic history

### Keywords (MN)
- Монгол экспорт
- Монгол импорт
- гадаад худалдаа
- худалдааны тэнцэл
- олон улсын худалдаа

### Excerpt Templates

**EN**: "Mongolia's exports and imports from 1924 to 2024, showing the breakdown of foreign trade by direction in million USD."

**MN**: "Монгол Улсын экспорт, импорт 1924-2024 онд, сая ам.долларын хэмжээгээр."

## Notes

- One of the longest-running economic time series in Mongolia
- Values are in million USD
- FOB (Free On Board) basis for both exports and imports
- Captures transition from Soviet-era trade to market economy
- Updated annually by NSO
