# Dataset: Mongolia SME Loans Outstanding

## Identification
- **ID**: `mongolbank-sme-loans`
- **Source**: `mongolbank`
- **Category**: Finance
- **Tags**: sme, loans, credit, small-medium-enterprise, banking

## Source Reference
- **API**: `https://stat.mongolbank.mn/api/indicator/data`
- **Report ID**: 128 (Outstanding loan — SME)
- **Parent ID**: 127 (Small medium enterprises loan)
- **Indicator ID**: `78889` (SME LOAN ISSUED TO PRIVATE SECTOR, OUTSTANDING LOAN — total)

## Description

Outstanding loans to small and medium enterprises (SMEs) from Mongolia's banking sector, monthly, in billion MNT. Covers January 2017 to present. This is a stock variable (balance at end of month), not a flow.

## Variables

### date / огноо
- First day of the reference month (YYYY-MM-01)
- Monthly frequency from 2017-01-01

### sme_loans_outstanding_billion_mnt / жижиг_дунд_бизнесийн_зээл_тэрбум_төгрөг
- Total outstanding SME loans in billion MNT
- Source unit: million MNT — divide by 1000 for billion MNT

## Update Instructions

### Fetch Data

```python
import requests

headers = {'Content-Type': 'application/json', 'Origin': 'https://stat.mongolbank.mn'}

body = {
    "id": 128,
    "parentId": 127,
    "rCheck": 0,
    "cycle_data": {
        "interval": "3",
        "year_start": "2017",
        "mq_start": "1",
        "day_start": "1",
        "year_end": "2026",
        "mq_end": "12",
        "day_end": "28"
    },
    "indicators": ["78889"]
}

r = requests.post('https://stat.mongolbank.mn/api/indicator/data?lang=en', headers=headers, json=body)
row = r.json()['result']['report'][0]

records = []
for key, val in row.items():
    if isinstance(key, str) and key.startswith("'") and '#3' in key:
        date_str = key.strip("'").split('#3')[0].strip()
        records.append({'date': date_str + '-01', 'sme_loans_outstanding_billion_mnt': round(val / 1000, 3)})

records.sort(key=lambda x: x['date'])
```

### Field Mapping
| API Key Pattern | CSV Column |
|----------------|-----------|
| `'YYYY-MM#3'` | date (→ YYYY-MM-01) |
| row value | sme_loans_outstanding_billion_mnt (÷1000) |

### Validation
- Values must be positive
- Monthly frequency, no gaps expected
- Data starts 2017-01-01
