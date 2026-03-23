# MongolBank Gross External Debt Position

## Source
- **Source ID**: `mongolbank`
- **Portal**: stat.mongolbank.mn (Statistics Portal)
- **Report ID**: 1109 (Gross external debt position by sector, stock)
- **Parent ID**: 1108 (Mongolia Gross External Debt Position)

## API Access

### Indicator List
```
POST /api/indicator/list?lang={en|mn}&reportId=1109
Headers: Content-Type: application/json, Origin: https://stat.mongolbank.mn
Body: {}
```

Returns indicator tree (59 indicators):
- `58755`: General Government (level 1)
- `58768`: Central Bank (level 1)
- `58782`: Deposit-Taking Corporations (level 1)
- `58795`: Other Sectors (level 1)
- `58808`: Direct Investment: Intercompany Lending (level 1)
- `58812`: **Gross External Debt Position** (total aggregate)

### Fetch Data
```
POST /api/indicator/data?lang={en|mn}
Headers: Content-Type: application/json, Origin: https://stat.mongolbank.mn
Body: {
  "id": 1109,
  "parentId": 1108,
  "rCheck": 0,
  "cycle_data": {
    "interval": "1",
    "year_start": "2000",
    "mq_start": "1",
    "day_start": "1",
    "year_end": "2026",
    "mq_end": "12",
    "day_end": "28"
  },
  "indicators": ["58812"]
}
```

**Note**: Uses `interval: "1"` (not "3") because this is quarterly data with full date keys.

## Data Details
- **Frequency**: Quarterly (Q1=Mar, Q2=Jun, Q3=Sep, Q4=Dec)
- **Range**: Q1 2000 to Q4 2025 (104 data points)
- **Unit**: Million USD (no conversion needed)
- **Indicator**: 58812 (Gross External Debt Position — total)

## Dataset: mongolbank-external-debt
- **Content**: Total gross external debt position
- **Columns**: Date, External Debt (USD million)
- **Rows**: 104 (quarterly 2000-Q1 to 2025-Q4)
- **Chart**: Area chart showing debt growth over time

## Update Detection
- Check `report/list?lang=en&parentId=1108` for `maxdate` field
- Current maxdate: 2025-12-01
