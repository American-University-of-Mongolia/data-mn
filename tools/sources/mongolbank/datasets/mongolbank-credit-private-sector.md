# MongolBank Credit to Private Sector

## Source

- **Source ID**: `mongolbank`
- **Dataset ID**: `mongolbank-credit-private-sector`
- **Portal**: stat.mongolbank.mn (Statistics Portal)
- **Report ID**: 90 (Depository corporations survey)
- **Parent ID**: 88 (Domestic claims)
- **Indicator ID**: `60870` ("Private sector" / "Хувийн байгууллага")

## Description

Outstanding credit to the private sector from Mongolia's depository corporations, as reported under the Depository Corporations Survey. This series covers domestic claims on the private sector and is a key indicator of bank lending activity in Mongolia.

- **EN name**: "Private sector" (under Domestic claims → Depository corporations survey)
- **MN name**: "Хувийн байгууллага"

## API Access

The stat.mongolbank.mn portal exposes an undocumented REST API.

### Endpoint

```
POST https://stat.mongolbank.mn/api/indicator/data?lang={en|mn}
Headers: Content-Type: application/json
         Origin: https://stat.mongolbank.mn
```

### Request Body

```json
{
  "id": 90,
  "parentId": 88,
  "rCheck": 0,
  "cycle_data": {
    "interval": "3",
    "year_start": "2004",
    "mq_start": "1",
    "day_start": "1",
    "year_end": "2026",
    "mq_end": "12",
    "day_end": "28"
  },
  "indicators": ["60870"]
}
```

### Response

`result.report[]` contains time series with keys like `'2004-01#3'` (year-month#interval).
Values are in million MNT. Divide by 1000 to convert to billion MNT.

## Data Details

- **Frequency**: Monthly (interval=3)
- **Range**: January 2004 to January 2026 (265 data points)
- **Unit**: Million MNT in API → converted to billion MNT in CSV output
- **Language**: Bilingual (both EN and MN endpoints return identical numeric values)

## CSV Columns

| Language | Date column | Value column |
|----------|-------------|--------------|
| English  | `date`      | `credit_billion_mnt` |
| Mongolian | `огноо`    | `зээл_тэрбум_төгрөг` |

## Update Detection

Check `report/list?lang=en&parentId=88` for `maxdate` field.
Compare with stored version to detect new months.

## Chart

Area chart with green color (`#10b981`) to distinguish from monetary series (M2, policy rate).
Y-axis uses `scale.zero: false` to show the growth trend clearly.
