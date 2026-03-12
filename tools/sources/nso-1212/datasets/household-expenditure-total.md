# Dataset: household-expenditure-total

## Overview

- **Dataset ID**: `household-expenditure-total`
- **Source**: NSO 1212.mn (`nso-1212`)
- **Table ID**: `DT_NSO_1900_002V1.px`
- **Title EN**: Mongolia Total Household Expenditure, MNT (1997-2024)
- **Title MN**: Монгол Улсын өрхийн нийт зарлага, төгрөг (1997-2024)
- **Category EN**: Household & Income
- **Category MN**: Өрх ба орлого

## Source Table

- **Name**: MONTHLY AVERAGE EXPENDITURE PER HOUSEHOLD, by location, and by year /1997-2024/
- **Sector**: Society, development
- **Subsector**: Household income and expenditure
- **Table ID**: `DT_NSO_1900_002V1.px`
- **Unit**: Mongolian Tugrik (MNT)
- **Last Updated**: 2025-05-23

## Dimensions

| Dimension | Code | Selected Value |
|-----------|------|----------------|
| Location | `Байршил` | `0` = National average |
| Types of expenditure | `Зарлагын төрөл` | `0` = Total expenditure |
| Year | `Он` | All (1997-2024, 28 years) |

## Fetch Instructions

```python
import requests
from urllib.parse import quote

BASE_URL = 'https://data.1212.mn/api/v1'
sector_id = 'Society, development'
subsector_id = 'Household income and expenditure'
table_id = 'DT_NSO_1900_002V1.px'

query = {
    "query": [
        {"code": "Байршил", "selection": {"filter": "item", "values": ["0"]}},
        {"code": "Зарлагын төрөл", "selection": {"filter": "item", "values": ["0"]}},
        {"code": "Он", "selection": {"filter": "item", "values": ["0","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27"]}}
    ],
    "response": {"format": "json-stat2"}
}

url = f'{BASE_URL}/en/NSO/{quote(sector_id)}/{quote(subsector_id)}/{quote(table_id)}'
r = requests.post(url, json=query, timeout=60)
data = r.json()
```

## Output Files

| File | Description |
|------|-------------|
| `household-expenditure-total-en.csv` | Chart data (EN columns: year, expenditure_mnt) |
| `household-expenditure-total-mn.csv` | Chart data (MN columns: он, зарлага_төгрөг) |
| `household-expenditure-total-all-en.csv` | Download data EN (same as chart for this simple series) |
| `household-expenditure-total-all-mn.csv` | Download data MN (same as chart for this simple series) |
| `household-expenditure-total.xlsx` | Wide format download |

## Notes

- Data represents **monthly average** expenditure per household, national average
- Filter applied: Location = National average, Expenditure Type = Total
- 28 data points (1997-2024)
- Values in Mongolian Tugrik (MNT)
