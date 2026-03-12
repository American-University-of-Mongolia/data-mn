# Dataset: household-expenditure-by-location

## Overview

- **Dataset ID**: `household-expenditure-by-location`
- **Source**: NSO 1212.mn
- **Table ID**: `DT_NSO_1900_002V1.px`
- **Title**: Monthly Average Expenditure per Household, by Location and by Year (1997–2024)
- **Category**: Household & Income
- **Unit**: Mongolian Tugrik (MNT)

## Source Table Structure

**Sector**: Society, development
**Subsector**: Household income and expenditure

### Dimensions

| Dimension (MN code) | EN Label | Values |
|---------------------|----------|--------|
| Байршил | Location | National average (0), Urban (1), Rural (2) |
| Зарлагын төрөл | Types of expenditure | Total (0), Monetary (1), Food (2), Non-food (3), Savings (4), Gifts (5), Free (6), Own farming (7) |
| Он | Year | 1997–2024 (28 values, newest first) |

## Filter Applied

- **Expenditure Type**: Total expenditure only (`Зарлагын төрөл = '0'`)
- **Location**: All 3 locations (National, Urban, Rural)
- **Year**: All years (1997–2024)

## Output Files

| File | Description |
|------|-------------|
| `household-expenditure-by-location-en.csv` | Chart CSV (EN): year, location, expenditure_mnt |
| `household-expenditure-by-location-mn.csv` | Chart CSV (MN): он, байршил, зарлага_төгрөг |
| `household-expenditure-by-location.xlsx` | Wide format: year x location pivot |

## Column Mapping

### EN CSV
- `year` - Year (1997–2024)
- `location` - Location: National, Urban, Rural
- `expenditure_mnt` - Monthly expenditure in MNT

### MN CSV
- `он` - Year
- `байршил` - Location: Улсын дүн, Хот, Хөдөө
- `зарлага_төгрөг` - Monthly expenditure in MNT

## Location Value Mapping

| API (EN) | Output EN | API (MN) | Output MN |
|----------|-----------|----------|-----------|
| National average | National | Улсын дундаж | Улсын дүн |
| Urban | Urban | Хот | Хот |
| Rural | Rural | Хөдөө | Хөдөө |

## Version History

| Version | Date | Notes |
|---------|------|-------|
| v1 | 2026-03-09 | Initial creation, data 1997–2024 |

## Fetch Instructions

```python
import requests
from urllib.parse import quote

BASE_URL = 'https://data.1212.mn/api/v1'
sector_id = 'Society, development'
subsector_id = 'Household income and expenditure'
table_id = 'DT_NSO_1900_002V1.px'

for lang in ['en', 'mn']:
    url = f'{BASE_URL}/{lang}/NSO/{quote(sector_id)}/{quote(subsector_id)}/{quote(table_id)}'
    meta = requests.get(url).json()
    query = {
        'query': [
            {'code': v['code'], 'selection': {'filter': 'item', 'values': v['values']}}
            for v in meta['variables']
        ],
        'response': {'format': 'json-stat2'}
    }
    data = requests.post(url, json=query).json()
    # Then filter to 'Total expenditure' / 'Нийт зарлага' and transform columns
```
