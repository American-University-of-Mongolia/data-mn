# Dataset: Mongolia Consolidated Bank Balance Sheet

## Identification
- **ID**: `mongolbank-bank-balance-sheet`
- **Source**: `mongolbank`
- **Category**: Finance
- **Tags**: banking, balance-sheet, assets, liabilities, capital, financial-sector

## Source Reference
- **API**: `https://stat.mongolbank.mn/api/indicator/data`
- **Report ID**: 86 (Consolidated balance sheet — Active banks)
- **Parent ID**: 85 (Consolidated balance sheet)
- **Indicator IDs**:
  - `60481` — Total Assets
  - `60563` — Total Liabilities
  - `60637` — Capital (Equity)

## Description

Monthly consolidated balance sheet of Mongolia's active banking sector from January 2004 to present. Includes total assets, total liabilities, and capital (equity) in billion MNT. Measures the overall size and financial health of Mongolia's banking system.

## Variables

### date / огноо
- First day of the reference month (YYYY-MM-01)
- Monthly frequency from 2004-01-01

### total_assets_billion_mnt / нийт_хөрөнгө_тэрбум_төгрөг
- Total consolidated assets of active banks in billion MNT

### total_liabilities_billion_mnt / нийт_өр_төлбөр_тэрбум_төгрөг
- Total consolidated liabilities of active banks in billion MNT

### capital_billion_mnt / өөрийн_хөрөнгө_тэрбум_төгрөг
- Total equity/capital of active banks in billion MNT

All values sourced in million MNT — divide by 1000 for billion MNT.

## Update Instructions

### Fetch Data

```python
import requests

headers = {'Content-Type': 'application/json', 'Origin': 'https://stat.mongolbank.mn'}

body = {
    "id": 86, "parentId": 85, "rCheck": 0,
    "cycle_data": {
        "interval": "3", "year_start": "2004", "mq_start": "1", "day_start": "1",
        "year_end": "2026", "mq_end": "12", "day_end": "28"
    },
    "indicators": ["60481", "60563", "60637"]
}

r = requests.post('https://stat.mongolbank.mn/api/indicator/data?lang=en', headers=headers, json=body)
rows = r.json()['result']['report']
by_id = {row['ID_T']: row for row in rows}
```

### Validation
- Total Assets >= Total Liabilities + Capital (approximately)
- All values positive
- Monthly frequency, no gaps expected from 2004-01
