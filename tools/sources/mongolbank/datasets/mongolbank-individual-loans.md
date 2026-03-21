# MongolBank Individual Outstanding Loans

## Source
- **Source ID**: `mongolbank`
- **Portal**: stat.mongolbank.mn (Statistics Portal)
- **Report ID**: 103 (Outstanding loan — Individuals)
- **Parent ID**: 102 (Individuals' loan)

## API Access

### Indicator List
```
POST /api/indicator/list?lang={en|mn}&reportId=103
Headers: Content-Type: application/json, Origin: https://stat.mongolbank.mn
Body: {}
```

Returns indicator tree (297 indicators):
- `133442`: Total outstanding loan (top-level total)
  - `133443`: Agriculture, Forestry, Fishing and Hunting
  - `133446`: Mining and quarrying
  - `133447`: Manufacturing
  - ... (economic sectors)

### Fetch Data
```
POST /api/indicator/data?lang={en|mn}
Headers: Content-Type: application/json, Origin: https://stat.mongolbank.mn
Body: {
  "id": 103,
  "parentId": 102,
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
  "indicators": ["133442"]
}
```

## Data Details
- **Frequency**: Quarterly (2000-2016), then Monthly (2016-present)
- **Range**: March 2000 to February 2026 (184 data points)
- **Unit**: Million MNT (converted to billion in CSV output)
- **Indicator**: 133442 (Total outstanding loan)

## Dataset: mongolbank-individual-loans
- **Content**: Total individual/consumer outstanding loan values
- **Columns**: Date, Individual Loans (MNT billion)
- **Rows**: 184 (quarterly 2000-03 to 2016-03, monthly 2016-04 to 2026-02)
- **Chart**: Area chart showing individual loan growth over time

## Update Detection
- Check `report/list?lang=en&parentId=102` for `maxdate` field
- Current maxdate: 2026-02-01
