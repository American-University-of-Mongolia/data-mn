# Dataset: nso-labour-force-national

## Overview

Mongolia's national labour force from 2009 to 2024, broken down by sex (Total, Male, Female).

## Source

- **Source ID**: nso-1212
- **Table ID**: DT_NSO_0400_012V1_1.px
- **API Path**: `Labour, business / Labour / LABOUR FORCE, by sex, age group, aimags and the Capital`
- **URL**: https://data.1212.mn/api/v1/en/NSO/Labour%2C%20business/Labour/LABOUR%20FORCE%2C%20by%20sex%2C%20age%20group%2C%20aimags%20and%20the%20Capital/DT_NSO_0400_012V1_1.px

## Filters Applied

- Age group = Total
- Region = Total (Улсын дүн)
- Sex = Total, Male, Female

## Data Schema

### EN CSV (nso-labour-force-national-en.csv)
| Column | Type | Description |
|--------|------|-------------|
| sex | string | Total / Male / Female |
| year | integer | Year (2009–2024) |
| labour_force | integer | Number of persons in labour force |

### MN CSV (nso-labour-force-national-mn.csv)
| Column | Type | Description |
|--------|------|-------------|
| хүйс | string | Нийт / Эрэгтэй / Эмэгтэй |
| жил | integer | Year (2009–2024) |
| ажиллах_хүч | integer | Number of persons in labour force |

## Fetch Script

```python
import requests, pandas as pd, io

table_id = 'DT_NSO_0400_012V1_1.px'
subsection = 'LABOUR FORCE, by sex, age group, aimags and the Capital'

for lang in ['en', 'mn']:
    path_parts = ['Labour, business', 'Labour', subsection]
    path = '/'.join(requests.utils.quote(p, safe='') for p in path_parts)
    url = f'https://data.1212.mn/api/v1/{lang}/NSO/{path}/{table_id}'
    
    r = requests.get(url)
    meta = r.json()
    query = [{'code': v['code'], 'selection': {'filter': 'item', 'values': v['values']}} for v in meta['variables']]
    post = requests.post(url, json={'query': query, 'response': {'format': 'csv'}})
    content = post.content.decode('utf-8-sig')
    df = pd.read_csv(io.StringIO(content))
    df.to_csv(f'raw-{lang}.csv', index=False)
```

## Version History

| Version | Date | Notes |
|---------|------|-------|
| v1 | 2026-05-12 | Initial creation, data through 2024 |
