# Dataset: Mongolia International Investment Position

## Identification
- **ID**: `mongolbank-international-investment`
- **Source**: `mongolbank`
- **Category**: Economy
- **Tags**: international-investment, iip, external-assets, external-liabilities, balance-of-payments

## Source Reference
- **API**: `https://stat.mongolbank.mn/api/indicator/data`
- **Report ID**: 1106 (International investment position — stock)
- **Parent ID**: 1105 (International Investment Positions)
- **Indicator IDs**:
  - `122365` — Net International Investment Position
  - `122366` — Assets
  - `122478` — Liabilities

## Description

Quarterly international investment position (IIP) of Mongolia from Q1 2000 to present, in million USD. Shows total external financial assets, total liabilities, and the net IIP (assets minus liabilities). Negative net IIP means Mongolia owes more abroad than it holds.

**Frequency**: Quarterly (interval=4 in the API)

## Variables

### date / огноо
- First day of the reference quarter (YYYY-MM-01, where MM is 01/04/07/10)
- Quarterly frequency from 2000-01-01

### net_iip_million_usd / цэвэр_гадаад_хөрөнгийн_байршил_сая_ам_дол
- Net IIP = Total Assets − Total Liabilities (million USD)

### total_assets_million_usd / нийт_хөрөнгө_сая_ам_дол
- Total external financial assets (million USD)

### total_liabilities_million_usd / нийт_өр_төлбөр_сая_ам_дол
- Total external financial liabilities (million USD)

## Update Instructions

### Fetch Data

```python
import requests

headers = {'Content-Type': 'application/json', 'Origin': 'https://stat.mongolbank.mn'}

body = {
    "id": 1106, "parentId": 1105, "rCheck": 0,
    "cycle_data": {
        "interval": "4",   # quarterly
        "year_start": "2000", "mq_start": "1", "day_start": "1",
        "year_end": "2026", "mq_end": "12", "day_end": "28"
    },
    "indicators": ["122365", "122366", "122478"]
}

Q_TO_MONTH = {'1': '01', '2': '04', '3': '07', '4': '10'}
r = requests.post('https://stat.mongolbank.mn/api/indicator/data?lang=en', headers=headers, json=body)
rows = r.json()['result']['report']
```

### Notes
- **interval=4** for quarterly (not 3 as used for monthly data)
- Date keys format: `'YYYY-Q#...'` — parse year and quarter, map Q to month start
- Values in USD — no currency conversion needed
