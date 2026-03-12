# Dataset: hospital-bed-density

## Overview

- **Dataset ID**: `hospital-bed-density`
- **Source**: NSO 1212.mn
- **Table ID**: `DT_NSO_2100_005V1.px`
- **Category**: Health
- **Update Frequency**: Annual

## Table Location

- **Sector**: `Education, health`
- **Subsector**: `Births, deaths`
- **Table**: `DT_NSO_2100_005V1.px`

## Filter Applied

This dataset is a split of the full `DT_NSO_2100_005V1.px` table, filtered to:

- **Indicator**: `Beds per 1000 population` (MN: `1000 хүнд ногдох ор`)

Note: The indicator values in the API response have leading whitespace (e.g., ` Beds per 1000 population`). Always use `.str.strip()` when filtering.

## Dimensions

| Dimension (EN) | Dimension (MN) | Values |
|----------------|----------------|--------|
| Indicators | Үзүүлэлт | 11 indicator types |
| Annual | Он | 1989–2024 (36 years) |

## Output Columns

| File | Columns |
|------|---------|
| `hospital-bed-density-en.csv` | `year`, `beds_per_1000` |
| `hospital-bed-density-mn.csv` | `он`, `мянган_хүн_тутамд_ор` |

## Fetch Instructions

```python
import requests
import pandas as pd
from urllib.parse import quote

BASE_URL = "https://data.1212.mn/api/v1"
sector_id = "Education, health"
subsector_id = "Births, deaths"
table_id = "DT_NSO_2100_005V1.px"

def fetch(lang):
    url = f"{BASE_URL}/{lang}/NSO/{quote(sector_id)}/{quote(subsector_id)}/{quote(table_id)}"
    meta = requests.get(url, timeout=30).json()
    query = {
        "query": [
            {"code": v["code"], "selection": {"filter": "item", "values": v["values"]}}
            for v in meta.get("variables", [])
        ],
        "response": {"format": "json-stat2"}
    }
    return requests.post(url, json=query, timeout=60).json()

# EN: filter Indicators col where stripped value == "Beds per 1000 population"
# MN: filter Үзүүлэлт col where stripped value == "1000 хүнд ногдох ор"
```

## Key Statistics (as of 2024)

- **Year range**: 1989–2024 (36 data points)
- **2024 value**: 9 beds per 1,000 population
- **Peak**: 12 beds per 1,000 (1989–1991)
- **Lowest**: 6 beds per 1,000 (2010)
