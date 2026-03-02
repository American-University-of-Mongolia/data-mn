# Dataset: Mongolia Monetary Policy Rate

## Identification
- **ID**: `mongolbank-policy-rate`
- **Source**: `mongolbank`
- **Category**: Finance
- **Tags**: policy-rate, interest-rate, monetary-policy

## Source Reference
- **URL**: https://www.mongolbank.mn/en/policy-interest-rate
- **MN URL**: https://www.mongolbank.mn/mn/policy-interest-rate
- **API Endpoint**: `https://www.mongolbank.mn/en/policy-interest-rate/data?startDate={start}&endDate={end}`

## Description

The official monetary policy rate set by the Monetary Policy Committee (MPC) of the Bank of Mongolia. The MPC meets approximately 8 times per year and may adjust the rate at each meeting. This rate determines the cost at which commercial banks can borrow short-term funds from the central bank.

Data is available from May 2016 onwards via the mongolbank.mn API. The page renders via JavaScript, so Playwright is required for extraction.

## Variables

### date
- The date the rate decision came into effect (YYYY-MM-DD)
- Event-based: one row per MPC decision, not per calendar day

### policy_rate_pct
- Policy rate as a percentage number (e.g., 12.0)
- Valid range: approximately 1.0 to 30.0

## Update Instructions

### Check for Updates
Compare the latest date in saved CSV against today. The MPC meets approximately 8 times per year.

MPC meeting schedule is published at: https://www.mongolbank.mn/mn/r/2946

### Fetch Data
Use Playwright to load the page and intercept the API response:

```python
from playwright.sync_api import sync_playwright
import json
import time

all_responses = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context()
    page = ctx.new_page()

    def handle_response(response):
        if 'policy-interest-rate/data' in response.url:
            body = response.body()
            data = json.loads(body)
            all_responses.append(data)

    page.on('response', handle_response)
    page.goto('https://www.mongolbank.mn/en/policy-interest-rate', wait_until='networkidle', timeout=30000)
    time.sleep(5)
    browser.close()

# The API uses a 10-year window: startDate=10yr ago, endDate=today
# To get all available data, just use the default page load
data = all_responses[0]['data']
```

The API URL uses these date parameters:
- `startDate`: 10 years before today (YYYY-MM-DD)
- `endDate`: today (YYYY-MM-DD)

The API only returns data from 2016 onwards. Historical data before 2016 is not available via the API.

### Field Mapping
| API Field | CSV Column |
|-----------|-----------|
| EFFECTIVE_FROM | date |
| POLICY_RATE | policy_rate_pct |

### Validation
- Rates must be positive numbers between 1 and 30
- Dates must be ISO format (YYYY-MM-DD)
- No duplicate dates
- Rows should be sorted by date ascending

### Notes
- The API also returns REPO, OVERNIGHT_DEPOSIT, OVERNIGHT_REPO rates - these are not included in this dataset
- The default API window is 10 years (startDate to endDate)
- Direct HTTP requests without a browser session return empty responses; use Playwright
