# Dataset: National Unemployment Rate

## Identification

- **ID**: `unemployment-rate-national`
- **Source**: `nso-1212`
- **Category**: Economy
- **Tags**: [unemployment, labor, economy, labor market, employment, statistics]

## Source Reference

- **Table ID**: `DT_NSO_0400_049V1.px`
- **Sector**: `Labour, business`
- **Subsector**: `Decent work`
- **API Path**: `/en/NSO/Labour, business/Decent work/DT_NSO_0400_049V1.px`

## Title

- **EN**: Mongolia National Unemployment Rate (2009-2024)
- **MN**: Монгол Улсын ажилгүйдлийн түвшин (2009-2024)

## Description

Annual unemployment rate for Mongolia from 2009 to 2024. This dataset provides a simple, clear view of the national unemployment rate trend, showing overall labor market performance. The data is based on SDG Indicator 8.5.2 (Unemployment Rate), which measures the percentage of the labor force that is unemployed.

## Variables

### Category (Ангилал)
- `0`: Total / Бүгд
- `1`: Male / Эрэгтэй
- `2`: Female / Эмэгтэй
- `3`: Urban / Хот
- `4`: Rural / Хөдөө
- `5`: 15-24 (Youth)
- `6`: 25-64 (Prime working age)
- `7`: 65+ (Elderly)
- `8`: Western region / Баруун бүс
- `9`: Khangai region / Хангайн бүс
- `10`: Central region / Төв бүс
- `11`: Eastern region / Зүүн бүс
- `12`: Ulaanbaatar / Улаанбаатар
- `13`: With disabilities / Хөгжлийн бэрхшээлтэй
- `14`: No disabilities / Хөгжлийн бэрхшээлгүй

### Year (Он)
Years from 2009 to 2024 (16 data points)

## Update Instructions

### Check for Updates

1. Query the table listing endpoint:
   ```
   GET https://data.1212.mn/api/v1/en/NSO/Labour, business/Decent work/
   ```

2. Find `DT_NSO_0400_049V1.px` in the response

3. Compare the `updated` field with `source_updated_at` in registry

4. If API's `updated` is newer, dataset needs updating

### Fetch Data

Use the `datamn-source-nso` skill for bilingual data fetching:

```python
import requests
import pandas as pd

BASE_URL = "https://data.1212.mn/api/v1"
sector = "Labour, business"
subsector = "Decent work"
table_id = "DT_NSO_0400_049V1.px"

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
    # Convert json-stat2 to DataFrame - see datamn-source-nso skill for implementation
```

### Data Transformation

For the `unemployment-rate-national` dataset (this is a standalone dataset, not a split):

1. **Filter to Total category only**:
   - Category (Ангилал): Total / Бүгд (code "0")
   - This gives the national-level unemployment rate

2. **Clean column names**:
   - Rename columns to: `Category`, `Year`, `value`
   - Strip whitespace from all string columns

3. **Data validation**:
   - All unemployment rates should be between 0 and 100
   - Values should be numeric (percentage)
   - Year values should be valid years (2009-2024)

4. **Export files**:
   - Chart CSV: `unemployment-rate-national-en.csv` (Total category only)
   - Download CSV: Same as chart (simple single-series dataset)
   - Excel XLSX: `unemployment-rate-national-en.xlsx` (wide format: year as rows, value as column)

### Validation

- All unemployment values should be positive percentages
- Values should be realistic (typically 5-15% range)
- Year values should be valid years (2009-2024)
- No missing values for years in range

## Chart Configuration

### Chart Type
Single-series area chart with gradient fill

### Chart Spec
- **X-axis**: Year (temporal type)
- **Y-axis**: Unemployment Rate (%, quantitative)
- **Mark**: Area with line overlay and hover points
- **Color**: Primary blue (#1f77b4)
- **Gradient**: Vertical gradient from transparent to semi-opaque blue

### Features
- Hover interaction shows exact year and rate
- Nearest-point selection for easy interaction
- No zero baseline (starts near minimum for better readability)
- Grid lines disabled for cleaner look

## Content Generation

### Key Findings Template

Auto-extract:
- Latest unemployment rate (2024 value)
- Historical comparison (2024 vs 2009)
- Lowest rate year and value
- Highest rate year and value
- Overall trend (declining/increasing/stable)

### Common Tags
- mongolia
- unemployment
- labor-market
- economy
- employment
- nso
- labor

### Keywords
- mongolia unemployment rate
- labor market
- jobless rate
- economy
- economic indicators
- employment statistics

### Excerpt Templates

**English**:
"Annual unemployment rate in Mongolia from 2009 to 2024, showing overall labor market trends."

**Mongolian**:
"Монгол Улсын ажилгүйдлийн түвшин 2009-2024 онд, хөдөлмөрийн зах зээлийн ерөнхий чиг хандлагыг харуулсан."

## Notes

- This is a **standalone dataset** (not a parent with splits)
- Simple single-series time series showing national trend
- Data comes from SDG Indicator 8.5.2
- Parent table contains many categories (sex, age, region, disability) but this dataset shows only the national total
- Updated annually by NSO
- Last API update: 2025-09-29
