# MongolBank Money Supply M1

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

### Indicator
- **ID**: `60442` — Money M1 (narrow money)
- M1 = currency in circulation + demand deposits
- M1 is a subset of M2 (M2 = M1 + other deposits)

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
  "indicators": ["60442"]
}
```

Response has `result.report[]` with time series keys like `'2000-01#3'` (year-month#interval).

## Data Details
- **Frequency**: Monthly (interval=3)
- **Range**: January 2000 to January 2026 (313 data points)
- **Unit**: Million MNT in source (converted to billion MNT in CSV output, divide by 1000)

## Dataset: mongolbank-money-supply-m1
- **Columns EN**: `date`, `m1_billion_mnt`
- **Columns MN**: `огноо`, `м1_тэрбум_төгрөг`
- **Rows**: 313 (monthly 2000-01 to 2026-01)
- **Chart**: Area chart (#ef4444 red) showing M1 trend over time

## Update Detection
- Check `report/list?lang=en&parentId=83` for `maxdate` field
- Compare with stored version to detect new months
