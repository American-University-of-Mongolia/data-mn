# MongolBank Mortgage Loans Outstanding

## Source
- **Source ID**: `mongolbank`
- **Portal**: stat.mongolbank.mn (Statistics Portal)
- **Report ID**: 149 (Outstanding loan — mortgage by source)
- **Parent ID**: 148 (Mortgage loan by source)

## API Access

### Indicator List
```
POST /api/indicator/list?lang={en|mn}&reportId=149
Headers: Content-Type: application/json, Origin: https://stat.mongolbank.mn
Body: {}
```

Returns indicator tree:
- `87560`: Outstanding loan at the end of the period (top-level total)
  - `87561`: By banks' own sources
  - `87564`: By Housing Mortgage Program
    - `184721`: HMP with 6% interest rate
    - `87565`: HMP with 8% interest rate
    - `87567`: HMP with 5% interest rate
  - ... (96 total indicators)

### Fetch Data
```
POST /api/indicator/data?lang={en|mn}
Headers: Content-Type: application/json, Origin: https://stat.mongolbank.mn
Body: {
  "id": 149,
  "parentId": 148,
  "rCheck": 0,
  "cycle_data": {
    "interval": "3",
    "year_start": "2013",
    "mq_start": "1",
    "day_start": "1",
    "year_end": "2026",
    "mq_end": "12",
    "day_end": "28"
  },
  "indicators": ["87560"]
}
```

## Data Details
- **Frequency**: Monthly
- **Range**: June 2013 to February 2026 (153 data points)
- **Unit**: Million MNT (converted to billion in CSV output)
- **Indicator**: 87560 (Outstanding loan at the end of the period)

## Dataset: mongolbank-mortgage-loans
- **Content**: Total outstanding mortgage loan values
- **Columns**: Date, Mortgage Loans (MNT billion)
- **Rows**: 153 (monthly 2013-06 to 2026-02)
- **Chart**: Area chart showing mortgage loan growth over time

## Update Detection
- Check `report/list?lang=en&parentId=148` for `maxdate` field
- Current maxdate: 2026-02-01
