# Dataset: Annual Average Exchange Rates (Major Currencies)

## Identification

- **ID**: `mongolbank-exchange-rates-annual-average-major`
- **Source**: `mongolbank`
- **Category**: Finance
- **Tags**: [mongolia, exchange rate, currency, tugrik, USD, EUR, CNY, central bank, finance, forex]

## Source Reference

- **Portal**: www.mongolbank.mn (JavaScript SPA)
- **API Endpoint**: `POST https://www.mongolbank.mn/{lang}/currency-rate-movement/data/monthly`
- **Discovered via**: JS bundle reverse-engineering (`/js/main.min.js`)
- **Data available from**: 1993-01

## Title

- **EN**: Mongolia Annual Average Exchange Rates, Major Currencies (1993-2026)
- **MN**: Монгол Улсын жилийн дундаж валютын ханш, гол валютуудаар (1993-2026)

## Description

Annual average official exchange rates for six major currencies (USD, EUR, CNY, RUB, JPY, KRW) against the Mongolian Tugrik from 1993 to 2026. Values represent MNT per 1 unit of foreign currency.

## Currencies

| Code | EN Name | MN Name |
|------|---------|---------|
| USD | US Dollar | АНУ-ын доллар |
| EUR | Euro | Евро |
| CNY | Chinese Yuan | Хятадын юань |
| RUB | Russian Ruble | Оросын рубль |
| JPY | Japanese Yen | Японы иен |
| KRW | South Korean Won | БНСУ-ын вон |

## Aggregation Method

**Daily → Monthly → Annual average**:
1. MongolBank publishes official daily closing rates
2. The API pre-aggregates to monthly averages (`/currency-rate-movement/data/monthly`)
3. We compute annual averages as the arithmetic mean of all monthly averages within each calendar year
4. Months with no data (value `"-"` or `"0.00"`) are excluded from the average

This is the standard method used by central banks and international organizations (IMF, World Bank) for annual average exchange rate reporting.

## Variables

### Currency (Валют)
One of: US Dollar, Euro, Chinese Yuan, Russian Ruble, Japanese Yen, South Korean Won

### Year (Жил)
Calendar year (YYYY format).

### Rate (MNT) / Ханш (₮)
Annual average exchange rate: MNT per 1 unit of foreign currency, rounded to 2 decimal places.

**Note**: For JPY and KRW, the rate is per 1 unit (e.g., 1 JPY ≈ 23 MNT, not 100 JPY).

## Data Files

| File | Description |
|------|-------------|
| `mongolbank-exchange-rates-annual-average-major-en.csv` | Long-form CSV (EN column names) |
| `mongolbank-exchange-rates-annual-average-major-mn.csv` | Long-form CSV (MN column names) |
| `mongolbank-exchange-rates-annual-average-major.xlsx` | Excel with EN and MN sheets (wide format) |

## Update Instructions

### Check for Updates

The monthly data updates each month. To check:
1. POST to `https://www.mongolbank.mn/en/currency-rate-movement/data/monthly`
2. Check `RATE_DATE` of first record (sorted newest-first)
3. Compare with last fetched year

### Fetch Data

```python
import requests

def fetch_monthly(lang="en"):
    url = f"https://www.mongolbank.mn/{lang}/currency-rate-movement/data/monthly"
    headers = {
        "Content-Type": "application/json",
        "Origin": "https://www.mongolbank.mn",
        "Referer": f"https://www.mongolbank.mn/{lang}/currency-rate-movement/monthly"
    }
    resp = requests.post(url, json={}, headers=headers, timeout=30)
    data = resp.json()
    assert data["success"], "API failure"
    return data["data"]  # List of monthly records

# Full script: .claude/skills/datamn-source-mongolbank/fetch_exchange_rates.py
```

### Reaggregate Annual Averages

```python
from collections import defaultdict

CURRENCIES = ["USD", "EUR", "CNY", "RUB", "JPY", "KRW"]

def aggregate_annual(records):
    yearly = defaultdict(lambda: defaultdict(list))
    for rec in records:
        year = rec["RATE_DATE"].split("-")[0]
        for cur in CURRENCIES:
            val_str = rec.get(cur, "-")
            if val_str not in ("-", "0.00", "0", "", None):
                try:
                    val = float(val_str.replace(",", ""))
                    if val > 0:
                        yearly[year][cur].append(val)
                except ValueError:
                    pass
    return [{
        "Year": year,
        **{cur: round(sum(vals)/len(vals), 2) if vals else None
           for cur, vals in yearly[year].items()}
    } for year in sorted(yearly.keys())]
```

## Validation

- USD should show monotonic growth from 150 (1993) to ~3500 (2025)
- EUR should only appear from 1999 onward (Euro launched 1999-01-01)
- CNY should appear throughout but with significant growth post-2000
- RUB should spike dramatically after 2022 Ukraine sanctions
- JPY rate should be in range 10-30 MNT per JPY
- KRW rate should be in range 1-4 MNT per KRW

## Chart

Multi-line chart showing USD, EUR, CNY, RUB (4 currencies on comparable scale).
JPY and KRW are excluded from the chart due to scale mismatch but available in CSV/XLSX.

- Blue (#2563eb): US Dollar
- Green (#16a34a): Euro
- Red (#dc2626): Chinese Yuan
- Purple (#7c3aed): Russian Ruble

## Notes

- EUR data starts in 1999 (Euro introduction)
- RUB shows extreme volatility post-2022 due to Ukraine war sanctions
- MongolBank website redesigned in 2024-2025; old `.aspx` URLs no longer work
- API endpoint discovered via JS bundle: `/js/main.min.js` contains path `/currency-rate-movement/data/monthly`
