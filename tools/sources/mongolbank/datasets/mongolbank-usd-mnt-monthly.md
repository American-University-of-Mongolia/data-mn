# Dataset: USD/MNT Monthly Average Exchange Rate

## Identification

- **ID**: `mongolbank-usd-mnt-monthly`
- **Source**: `mongolbank`
- **Category**: Finance
- **Tags**: [mongolia, exchange rate, USD, tugrik, MNT, central bank, finance, forex, currency depreciation]

## Source Reference

- **Portal**: www.mongolbank.mn
- **API Endpoint**: `POST https://www.mongolbank.mn/{lang}/currency-rate-movement/data/monthly`
- **Data available from**: 1993-01

## Title

- **EN**: Mongolia USD/MNT Exchange Rate, Monthly Average (1993-2026)
- **MN**: Монгол Улсын АНУ доллар/Төгрөгийн ханш, сарын дундаж (1993-2026)

## Description

Monthly average official USD/MNT exchange rate as published by the Bank of Mongolia (Mongolbank).
Values represent MNT per 1 USD. The series covers January 1993 to the present.

This is a single-currency focused dataset. For multi-currency annual averages, see `mongolbank-exchange-rates-annual-average-major`.

## Variables

### Date (Огноо)
Monthly date in YYYY-MM format.

### Rate (MNT) / Ханш (₮)
Monthly average exchange rate: MNT per 1 USD.

## Aggregation Method

The MongolBank API endpoint `/currency-rate-movement/data/monthly` provides monthly averages pre-computed from official daily closing rates. No additional aggregation is required for this monthly dataset.

**Note on daily-to-monthly conversion**: Monthly averages are computed by Mongolbank as arithmetic means of all published business-day closing rates within each calendar month.

## Data Files

| File | Description |
|------|-------------|
| `mongolbank-usd-mnt-monthly-en.csv` | Long-form CSV, EN column names |
| `mongolbank-usd-mnt-monthly-mn.csv` | Long-form CSV, MN column names |
| `mongolbank-usd-mnt-monthly.xlsx` | Wide-form Excel (months as rows, years as columns) |

## Update Instructions

```python
import requests

def fetch_usd_monthly(lang="en"):
    url = f"https://www.mongolbank.mn/{lang}/currency-rate-movement/data/monthly"
    headers = {
        "Content-Type": "application/json",
        "Origin": "https://www.mongolbank.mn",
        "Referer": f"https://www.mongolbank.mn/{lang}/currency-rate-movement/monthly"
    }
    resp = requests.post(url, json={}, headers=headers, timeout=30)
    data = resp.json()
    records = [
        {"Date": r["RATE_DATE"], "Rate (MNT)": float(r["USD"].replace(",", ""))}
        for r in reversed(data["data"])
        if r.get("USD") not in (None, "-", "0.00", "0", "")
    ]
    return records

# Or use the skill script:
# python .claude/skills/datamn-source-mongolbank/fetch_exchange_rates.py --currencies USD --monthly
```

## Validation

- Rate should be positive (>0)
- Monotonically increasing trend (with occasional reversals)
- 1993: ~150 MNT/USD
- 2000: ~1,100 MNT/USD
- 2010: ~1,350-1,450 MNT/USD
- 2020: ~2,700-2,900 MNT/USD
- 2025: ~3,500+ MNT/USD
- No month should have rate > 5,000 (as of 2026)

## Chart

Area chart with blue gradient fill showing the long-term depreciation trend.
Single-series chart (no legend needed).

## Notes

- Differs from `mongolbank-exchange-rates-annual-average-major`: this is monthly data for USD only
- Monthly averages are pre-computed by MongolBank from daily closing rates
- The Tugrik has depreciated ~24x since 1993
