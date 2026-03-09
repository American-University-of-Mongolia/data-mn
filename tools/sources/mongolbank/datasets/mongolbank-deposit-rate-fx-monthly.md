# Dataset: FX Deposit Interest Rate (Monthly)

## Identification

- **ID**: `mongolbank-deposit-rate-fx-monthly`
- **Source**: `mongolbank`
- **Category**: Finance
- **Tags**: [mongolia, deposit rate, interest rate, foreign currency, FX, central bank, banking, finance, monetary policy]

## Source Reference

- **Portal**: stat.mongolbank.mn (JavaScript SPA)
- **API**: `POST https://stat.mongolbank.mn/api/indicator/data?lang={lang}`
- **Report ID**: 142 (parentId: 140, "Deposits interest rate")
- **Indicator ID**: 84992
- **EN Name**: DEPOSIT WEIGHTED AVERAGE RATES (outstanding) (foreign currency)
- **MN Name**: Нийт хадгаламжийн үлдэгдэлд жигнэж тооцсон хүү (валют)
- **Data from**: 2008-12

## FX Series Availability

**Available and reliable.** Indicator 84992 provides a dedicated monthly FX deposit rate series from December 2008. No fallback needed.

## Title

- **EN**: Mongolia FX Deposit Interest Rate, Monthly (2008-2026)
- **MN**: Монгол Улсын гадаад валютын хадгаламжийн хүү, сар бүр (2008-2026)

## Description

Monthly weighted average interest rate on outstanding foreign currency (FX) deposits in Mongolian banks. This is the "stock" rate (weighted across all outstanding FX deposits), not the rate on newly-issued deposits.

## Variables

### Date (Огноо)
Monthly date in YYYY-MM format. Starts 2008-12.

### Rate (%) / Хүү (%)
Weighted average FX deposit interest rate as annual percentage.

## Data Files

| File | Description |
|------|-------------|
| `mongolbank-deposit-rate-fx-monthly-en.csv` | Long-form CSV (EN) |
| `mongolbank-deposit-rate-fx-monthly-mn.csv` | Long-form CSV (MN) |
| `mongolbank-deposit-rate-fx-monthly.xlsx` | Wide-form Excel |

## Fetch Instructions

```bash
python .claude/skills/datamn-source-mongolbank/fetch_bulletin_table.py --indicator deposit-rate
```

Or directly:

```python
import requests

body = {
    "id": 142, "parentId": 140, "rCheck": 0,
    "cycle_data": {"interval": "3", "year_start": "2008", "mq_start": "1",
                   "day_start": "1", "year_end": "2026", "mq_end": "12", "day_end": "28"},
    "indicators": ["84992"]
}
resp = requests.post(
    "https://stat.mongolbank.mn/api/indicator/data?lang=en",
    headers={"Content-Type": "application/json", "Origin": "https://stat.mongolbank.mn"},
    json=body, timeout=15
)
data = resp.json()
ind = data["result"]["report"][0]
ts = {k.replace("'","").split("#")[0]: v for k, v in ind.items()
      if "#3" in str(k) and v and v != 0}
```

## Validation

- All rates positive (typically 3-10% range)
- 2008-12: ~7.4%
- Declining trend to ~3-5% range by 2020s
- FX rate should be lower than MNT deposit rate (indicator 84982)
