# Dataset: Mongolia Daily Exchange Rates

## Identification
- **ID**: `mongolbank-exchange-rates-daily`
- **Source**: `mongolbank`
- **Category**: Finance
- **Tags**: exchange-rates, currency, MNT, finance
- **Update Frequency**: Daily

## Source Reference
- **URL**: https://www.mongolbank.mn/mn/currency-rates
- **Historical URL**: https://www.mongolbank.mn/mn/currency-rate-movement
- **API Endpoint**: `POST https://www.mongolbank.mn/mn/currency-rates/data?startDate=YYYY-MM-DD&endDate=YYYY-MM-DD`

## Data Access Method

The MongolBank website is JavaScript-rendered (Vue.js) and uses reCAPTCHA token verification.
Direct HTTP POST calls to the API endpoint succeed when made from within the page context
(Playwright browser with valid reCAPTCHA session).

### Fetch Script

```python
from playwright.sync_api import sync_playwright
import json

def fetch_rates(start_date, end_date):
    captured = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        def handle_response(response):
            if '/currency-rates/data' in response.url:
                body = response.json()
                if body.get('success'):
                    captured.extend(body['data'])

        page.on('response', handle_response)
        page.goto('https://www.mongolbank.mn/mn/currency-rates', wait_until='networkidle')

        # Use page.evaluate to trigger API call for custom date range
        result = page.evaluate(f"""
            async () => {{
                const resp = await fetch('/mn/currency-rates/data?startDate={start_date}&endDate={end_date}', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest'}},
                    body: JSON.stringify({{}}),
                }});
                return await resp.json();
            }}
        """)
        if result.get('success'):
            captured.extend(result['data'])

        browser.close()
    return captured
```

## API Response Format

Wide format JSON (one row per date, one column per currency):

```json
{
  "success": true,
  "data": [
    {
      "RATE_DATE": "2025-02-27",
      "USD": "3,465.69",
      "EUR": "3,630.48",
      "JPY": "23.22",
      "CNY": "476.87",
      "RUB": "39.74",
      "KRW": "2.40",
      ...
    }
  ]
}
```

## Target Currencies

| Code | English Name | Mongolian Name |
|------|-------------|----------------|
| USD | US Dollar | Америк доллар |
| EUR | Euro | Евро |
| CNY | Chinese Yuan | Хятад юань |
| RUB | Russian Ruble | Оросын рубль |
| JPY | Japanese Yen | Японы иен |
| KRW | South Korean Won | Солонгосын вон |

## Variables

### rate_mnt
- MNT per 1 unit of foreign currency (official closing rate)
- Values are provided as strings with commas (e.g., "3,465.69") — strip commas to parse

## Output CSV Format

**English** (`mongolbank-exchange-rates-daily-en.csv`):
```
date,currency_code,currency_name,rate_mnt
2025-02-27,USD,US Dollar,3465.69
```

**Mongolian** (`mongolbank-exchange-rates-daily-mn.csv`):
```
огноо,валютын_код,валютын_нэр,ханш_төгрөг
2025-02-27,USD,Америк доллар,3465.69
```

## Update Instructions

### Check for Updates

```python
import pandas as pd
df = pd.read_csv('data.mn/public/datasets/mongolbank-exchange-rates-daily-en.csv')
last_date = df['date'].max()
print(f"Last date in dataset: {last_date}")
```

### Fetch New Data

```python
# Set date range from day after last_date to today
from datetime import date, timedelta
start = (pd.to_datetime(last_date) + timedelta(days=1)).strftime('%Y-%m-%d')
end = date.today().strftime('%Y-%m-%d')

new_records = fetch_rates(start, end)
# ... convert and append to existing CSVs
```

### Validation Checklist
- All 6 currencies present for each date
- Rates are positive float values (no commas in numeric columns)
- Date column is ISO format YYYY-MM-DD
- Weekend/holiday dates carry forward the previous day's rate (normal behavior)
