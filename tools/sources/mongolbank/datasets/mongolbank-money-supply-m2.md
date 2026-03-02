# MongolBank Money Supply M2

## Source
- **Source ID**: `mongolbank`
- **Portal**: stat.mongolbank.mn (Statistics Portal)
- **Report ID**: 84 (Money supply)
- **Parent ID**: 83 (Monetary indicators)

## API Access

The stat.mongolbank.mn portal is a JavaScript SPA with an undocumented REST API.

### Base URL
```
https://stat.mongolbank.mn/api/
```

### Indicator List
```
POST /api/indicator/list?lang={en|mn}&reportId=84
Headers: Content-Type: application/json, Origin: https://stat.mongolbank.mn
Body: {}
```

Returns indicator tree:
- `60441`: Money M2 (top-level)
  - `60442`: Money M1
    - `60443`: Current account (domestic)
    - `60449`: Currency outside depository corporations
  - `60450`: Other deposits and current accounts
    - `60451`: Deposits (domestic)
    - `60457`: Deposits (foreign currency)
    - `60463`: Current accounts (foreign currency)
    - `60469`: Certificate of deposit (domestic)
    - `60475`: Certificate of deposit (foreign)

### Fetch Data
```
POST /api/indicator/data?lang={en|mn}
Headers: Content-Type: application/json, Accept: application/json, Origin: https://stat.mongolbank.mn
Body: {
  "id": 84,
  "parentId": 83,
  "rCheck": 0,
  "cycle_data": {
    "interval": "3",
    "year_start": "2000",
    "mq_start": "1",
    "day_start": "1",
    "year_end": "2026",
    "mq_end": "2",
    "day_end": "28"
  },
  "indicators": ["60441", "60442", "60450"]
}
```

Response has `result.report[]` with time series keys like `'2000-01#3'` (year-month#interval).

## Data Details
- **Frequency**: Monthly (interval=3)
- **Range**: January 2000 to December 2025 (312 data points)
- **Unit**: Million MNT (converted to billion in CSV output)
- **Indicators fetched**: M2 (total), M1, Other deposits

## Split: mongolbank-money-supply-m2
- **Content**: M2 total monthly values
- **Columns**: Date, M2 (MNT billion)
- **Rows**: 312 (monthly 2000-01 to 2025-12)
- **Chart**: Area chart showing M2 trend over time

## All data
- **Content**: M2, M1, Other Deposits monthly values
- **Columns**: Indicator, Date, Value (MNT billion)
- **Rows**: 936 (3 indicators × 312 months)

## Update Detection
- Check `report/list?lang=en&parentId=83` for `maxdate` field
- Current maxdate: 2025-12-01
- Compare with stored version to detect new months
