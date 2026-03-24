# MongolBank Total Outstanding Bank Loans

## Source
- **Source ID**: `mongolbank`
- **Portal**: stat.mongolbank.mn (Statistics Portal)
- **Report ID**: 98 (Outstanding loan)
- **Parent ID**: 97 (Total loan by economic activities)

## API Access

### Base URL
```
https://stat.mongolbank.mn/api/
```

### Indicator List
```
POST /api/indicator/list?lang={en|mn}&reportId=98
Headers: Content-Type: application/json, Origin: https://stat.mongolbank.mn
Body: {}
```

Returns indicator tree:
- `132850`: Total outstanding loan (top-level)
  - `132851`: Agriculture, Forestry, Fishing and Hunting
  - ... (other economic sectors)

### Fetch Data
```
POST /api/indicator/data?lang={en|mn}
Headers: Content-Type: application/json, Accept: application/json, Origin: https://stat.mongolbank.mn
Body: {
  "id": 98,
  "parentId": 97,
  "rCheck": 0,
  "cycle_data": {
    "interval": "3",
    "year_start": "2000",
    "mq_start": "1",
    "day_start": "1",
    "year_end": "2026",
    "mq_end": "12",
    "day_end": "28"
  },
  "indicators": ["132850"]
}
```

Response has `result.report[]` with time series keys like `'2000-03#3'` (year-month#interval).

## Data Details
- **Frequency**: Quarterly (2000-2016), then Monthly (2016-present)
- **Range**: March 2000 to February 2026 (184 data points)
- **Unit**: Million MNT (converted to billion in CSV output)
- **Indicator fetched**: 132850 (Total outstanding loan)

## Dataset: mongolbank-total-bank-loans
- **Content**: Total outstanding bank loan values
- **Columns**: Date, Total Loans (MNT billion)
- **Rows**: 184 (quarterly 2000-03 to 2016-03, monthly 2016-04 to 2026-02)
- **Chart**: Area chart showing loan growth over time

## Update Detection
- Check `report/list?lang=en&parentId=97` for `maxdate` field
- Current maxdate: 2026-02-01
- Compare with stored version to detect new months
