# Dataset: Lending & Deposit Reference Rates

## Identification

- **ID**: `mongolbank-reference-rates`
- **Source**: `mongolbank`
- **Category**: Finance
- **Tags**: [mongolia, interest rates, lending, deposit, central bank, finance, banking]

## Source Reference

- **Portal**: stat.mongolbank.mn (JavaScript SPA)
- **API Base**: `https://stat.mongolbank.mn/api/`
- **Reports**:
  - Report 142 (parentId=140): Deposit interest rates and maturities
  - Report 172 (parentId=170): Loan interest rates by sector
- **Key Indicators**:
  - 171821: Weighted interest rate of total issued loans (MNT)
  - 84982: Deposit weighted average rate (MNT, outstanding)
  - 84992: Deposit weighted average rate (FX, outstanding)
  - 85171: Deposit weighted average rate (MNT, newly issued)

## Title

- **EN**: Mongolia Lending & Deposit Reference Rates, Monthly (2016-2026)
- **MN**: Монгол Улсын зээл, хадгаламжийн лавлагааны хүү, сар бүр (2016-2026)

## Description

Monthly weighted average lending and deposit interest rates in Mongolia from March 2016 to present. The split dataset includes 3 key rates: lending rate (MNT, newly issued), deposit rate (MNT, outstanding), and deposit rate (FX, outstanding). The "all" dataset extends deposit history back to December 2008.

## Variables

### Date (Огноо)
Monthly dates in YYYY-MM format.
- Split: March 2016 to latest (common start date for all 3 rates)
- All: December 2008 to latest (full deposit history)

### Rate Type (Хүүгийн төрөл)
- `Lending Rate (MNT)` / `Зээлийн хүү (төгрөг)` — Weighted average interest rate on newly issued MNT loans
- `Deposit Rate (MNT)` / `Хадгаламжийн хүү (төгрөг)` — Weighted average interest rate on outstanding MNT deposits
- `Deposit Rate (FX)` / `Хадгаламжийн хүү (валют)` — Weighted average interest rate on outstanding FX deposits

### Rate (%) / Хүү (%)
Annual percentage rate, rounded to 2 decimal places.

## Data Files

| File | Description |
|------|-------------|
| `mongolbank-reference-rates-en.csv` | Split: 3 rates × ~119 months (EN) |
| `mongolbank-reference-rates-mn.csv` | Split: 3 rates × ~119 months (MN) |
| `mongolbank-reference-rates-all-en.csv` | Full history including deposit data from 2008 (EN) |
| `mongolbank-reference-rates-all-mn.csv` | Full history including deposit data from 2008 (MN) |
| `mongolbank-reference-rates.xlsx` | Excel with EN and MN sheets (wide format) |

## Update Instructions

### Check for Updates

The MongolBank statistics portal updates monthly. To check:

1. Fetch the latest data point from the API
2. Compare with the most recent date in existing CSV

### Fetch Data

```python
import requests

BASE_API = "https://stat.mongolbank.mn/api"
HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://stat.mongolbank.mn"
}

def fetch_indicators(report_id, parent_id, indicator_ids, lang, year_start="2008", year_end="2026"):
    body = {
        "id": report_id,
        "parentId": parent_id,
        "rCheck": 0,
        "cycle_data": {
            "interval": "3",
            "year_start": year_start,
            "mq_start": "1",
            "day_start": "1",
            "year_end": year_end,
            "mq_end": "12",
            "day_end": "28"
        },
        "indicators": indicator_ids
    }
    resp = requests.post(f"{BASE_API}/indicator/data?lang={lang}", headers=HEADERS, json=body)
    return resp.json()

# Deposit rates (report 142, parent 140)
dep_data = fetch_indicators(142, 140, ["84982", "84992"], "en")

# Loan rates (report 172, parent 170)
loan_data = fetch_indicators(172, 170, ["171821"], "en", year_start="2016")
```

### Extract Time Series

Time series values are in the report response under `result.report[]`. Each indicator has an `ID_T` field matching the indicator ID. Date values are keyed as `'YYYY-MM#3'` where `#3` indicates monthly frequency.

```python
def extract_ts(api_data, indicator_id):
    for ind in api_data['result']['report']:
        if ind['ID_T'] == indicator_id:
            ts = {}
            for key, val in ind.items():
                if '#3' in str(key):
                    date_str = key.replace("'", "").split('#')[0]
                    ts[date_str] = val
            return ind.get('NAME_T', ''), ts
    return None, None
```

## Validation

- All rate values should be positive percentages (typically 1-25%)
- Lending rate should be higher than deposit rate
- FX deposit rate should be lower than MNT deposit rate
- No gaps in monthly sequence
- EN and MN CSVs must have identical numeric values

## Chart

Multi-line chart with:
- Red (#ef4444): Lending Rate (MNT)
- Blue (#3b82f6): Deposit Rate (MNT)
- Green (#10b981): Deposit Rate (FX)
- `scale.zero: false` since rates are always positive
- `interpolate: monotone` for smooth lines

## Notes

- Values are annual percentage rates
- Deposit rates are for outstanding balances (stock), not newly issued
- Lending rate is for newly issued loans only (flow)
- The "all" CSV includes additional rate types with full qualifier names
- Deposit data extends back to Dec 2008; lending data starts Mar 2016
- The spread between lending and deposit rates is typically 4-5 percentage points
