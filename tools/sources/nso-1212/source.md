# NSO 1212.mn - National Statistics Office of Mongolia

## Source Information

- **ID**: `nso-1212`
- **Name**: National Statistics Office of Mongolia
- **Name (MN)**: Монгол Улсын Үндэсний Статистикийн Хороо
- **URL**: https://data.1212.mn
- **Type**: REST API
- **Update Frequency**: Varies by dataset (monthly, quarterly, yearly)

## API Documentation

### Base URL

```
https://data.1212.mn/api/v1/{lang}/NSO/
```

Languages: `en` (English), `mn` (Mongolian)

### Endpoints

#### List Sectors
```
GET /{lang}/NSO/
```
Returns: Array of `{id, type, text}`

8 main sectors:
1. Education, health (Боловсрол, эрүүл мэнд)
2. Regional development (Бүсчилсэн хөгжил)
3. Society, development (Нийгэм, хөгжил)
4. Historical data (Түүхэн Статистик)
5. Industry, service (Үйлдвэрлэл, үйлчилгээ)
6. Labour, business (Хөдөлмөр, бизнес)
7. Population, household (Хүн ам, өрх)
8. Economy, environment (Эдийн засаг, байгаль орчин)

#### List Subsectors
```
GET /{lang}/NSO/{sector}/
```
Returns: Array of `{id, type, text}`

#### List Tables
```
GET /{lang}/NSO/{sector}/{subsector}/
```
Returns: Array of `{id, type, text, updated}`

The `updated` field contains the last update timestamp - **use this for checking freshness**.

#### Get Table Metadata
```
GET /{lang}/NSO/{sector}/{subsector}/{table_id}.px
```
Returns: `{title, variables: [{code, text, values, valueTexts}]}`

### Fetching Data

Use direct HTTP requests (via `requests` library):

```python
import requests
import pandas as pd

BASE_URL = "https://data.1212.mn/api/v1"

def fetch_table_data(sector_id, subsector_id, table_id, language='en'):
    """Fetch data from NSO API using direct HTTP requests."""

    base_path = f"{BASE_URL}/{language}/NSO"
    url = f"{base_path}/{sector_id}/{subsector_id}/{table_id}"

    # First get metadata to discover available variables
    response = requests.get(url)
    metadata = response.json()

    # Build query selecting all values from all variables
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

    # POST request to fetch actual data
    data_response = requests.post(url, json=query)
    data = data_response.json()

    # Convert json-stat2 to DataFrame (see datamn-source-nso skill for full implementation)
    return data

# For complete implementation including DataFrame conversion,
# use the datamn-source-nso skill: .claude/skills/datamn-source-nso/fetch_data.py
```

## Checking for Updates

For a specific dataset:

1. Query the table listing endpoint for the dataset's sector/subsector
2. Find the table by its ID
3. Extract the `updated` field
4. Compare with the dataset's `source_updated_at` in the registry
5. If API's `updated` is newer, mark dataset as needing update

Example:
```python
import requests

sector = "Population, household"
subsector = "1_Population, household"
table_id = "DT_NSO_0300_001V2.px"

url = f"https://data.1212.mn/api/v1/en/NSO/{sector}/{subsector}/"
response = requests.get(url)
tables = response.json()

for table in tables:
    if table['id'] == table_id:
        source_updated = table['updated']  # e.g., "2025-09-16T17:08:44"
        break
```

## Handling Changes

If the API structure changes:

1. **New sectors/subsectors**: The hierarchical structure may change. If a path doesn't work:
   - First, re-fetch the sector list from root endpoint
   - Find the table by searching through subsectors
   - Update the dataset's `source_path` in registry

2. **API errors**: The API occasionally has downtime. Retry with exponential backoff.

3. **Table renames**: Tables may be replaced with new IDs. If a table ID doesn't exist:
   - Search for similar tables by name keywords
   - Report the issue and suggest updating the dataset definition

## Metadata Cache

The registry includes NSO metadata tables (`nso_sectors`, `nso_subsectors`, `nso_tables`) for fast searching without hitting the API repeatedly.

To refresh the metadata cache:
```python
# This would be implemented in the api-query skill
# Fetches all sectors → subsectors → tables and updates local cache
```

## Common Mongolian Terms

- Хүн ам = Population
- Өрх = Household
- Ажил эрхлэлт = Employment
- Ажилгүйдэл = Unemployment
- Орлого = Income
- Үнэ = Price
- Дундаж = Average
- Аймаг = Province
- Дүүрэг = District
- Нийслэл = Capital

## Rate Limits

The API doesn't have strict rate limits but be respectful:
- Metadata queries: ~1 second between requests
- Data queries: These can be large, allow 5-10 seconds for complex tables
