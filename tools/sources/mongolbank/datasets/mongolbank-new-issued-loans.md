# Dataset: Mongolia Newly Issued Bank Loans

## Identification
- **ID**: `mongolbank-new-issued-loans`
- **Source**: `mongolbank`
- **Category**: Finance
- **Tags**: loans, credit, banking, new-loans, credit-flow

## Source Reference
- **API**: `https://stat.mongolbank.mn/api/indicator/data`
- **Report ID**: 99 (New issued loan)
- **Parent ID**: 97 (Total loan by economic activities)
- **Indicator ID**: `133146` — Loan issued (total)

## Description

Monthly flow of newly issued bank loans in Mongolia from March 2000 to present, in billion MNT. This is a **flow** variable (amount issued each month), not a stock. Covers all economic sectors in aggregate.

## Variables

### date / огноо
- First day of the reference month (YYYY-MM-01)
- Monthly frequency from 2000-03-01

### new_loans_issued_billion_mnt / шинэ_зээлийн_олголт_тэрбум_төгрөг
- Total newly issued loans for the month in billion MNT
- Source unit: million MNT — divide by 1000 for billion MNT

## Update Instructions

### Fetch Data

```python
import requests

headers = {'Content-Type': 'application/json', 'Origin': 'https://stat.mongolbank.mn'}

body = {
    "id": 99, "parentId": 97, "rCheck": 0,
    "cycle_data": {
        "interval": "3", "year_start": "2000", "mq_start": "1", "day_start": "1",
        "year_end": "2026", "mq_end": "12", "day_end": "28"
    },
    "indicators": ["133146"]
}

r = requests.post('https://stat.mongolbank.mn/api/indicator/data?lang=en', headers=headers, json=body)
row = r.json()['result']['report'][0]
```

### Notes
- Data starts 2000-03 (not January 2000)
- Flow variable — compare with outstanding loans to measure credit creation pace
