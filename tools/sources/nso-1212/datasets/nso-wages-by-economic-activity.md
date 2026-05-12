# nso-wages-by-economic-activity

## Dataset Info

- **ID**: nso-wages-by-economic-activity
- **Table ID**: DT_NSO_0400_022V1.px
- **Source**: NSO 1212.mn
- **Category**: Labor Market
- **Frequency**: Annual

## API Path

```
Labour, business / Wages / MONTHLY AVERAGE NOMINAL WAGES, by division of economic activities
```

## Variables

- **SEX**: TOTAL, FEMALE, MALE
- **SECTOR**: 22 economic activities (e.g., National average, Mining and quarrying, etc.)
- **TIME ANNUAL**: 2001–2025 (years as columns in wide format)

## Fetch Instructions

The API returns data in WIDE format (years as columns). Fetch using:

```python
import requests, pandas as pd, io

def fetch(lang='en'):
    path_parts = ['Labour, business', 'Wages', 'MONTHLY AVERAGE NOMINAL WAGES, by division of economic activities']
    path = '/'.join(requests.utils.quote(p, safe='') for p in path_parts)
    meta_url = f'https://data.1212.mn/api/v1/{lang}/NSO/{path}/DT_NSO_0400_022V1.px'
    meta = requests.get(meta_url, timeout=30).json()
    query = [{'code': v['code'], 'selection': {'filter': 'all', 'values': ['*']}} for v in meta['variables']]
    post = requests.post(meta_url, json={'query': query, 'response': {'format': 'csv'}}, timeout=30)
    # Must decode with utf-8-sig to handle BOM
    return pd.read_csv(io.StringIO(post.content.decode('utf-8-sig')))
```

## Chart Selection

Chart shows 6 featured sectors (TOTAL sex only):
- National average
- Mining and quarrying
- Financial and insurance activities
- Manufacturing
- Agriculture, forestry, fishing and hunting
- Public administration and defense; compulsory social security

Full download includes all 22 sectors and all 3 sex categories.

## Notes

- Values are in thousands of MNT (nominal, not inflation-adjusted)
- This table uses the same source (DT_NSO_0400_022V1.px) as the legacy `average-wages` dataset but covers 2001-2025 with all sex breakdowns
