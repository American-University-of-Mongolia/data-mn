# Dataset: Annual Inflation Rate

## Identification

- **ID**: `nso-inflation-annual`
- **Source**: `nso-1212`
- **Category**: Economy
- **Tags**: [inflation, cpi, economy, prices, consumer-prices]

## Source Reference

- **Table ID**: `DT_NSO_0600_013V2.px`
- **Sector**: `Economy, environment`
- **Subsector**: `Inflation, CPI` (or similar - verify from API)
- **API Path**: `/en/NSO/Economy, environment/{subsector}/DT_NSO_0600_013V2.px`

## Title

- **EN**: Mongolia Annual Inflation Rate (1991-2024)
- **MN**: Монгол Улсын жилийн инфляцийн түвшин (1991-2024)

## Description

Annual inflation rate (Consumer Price Index year-over-year change) for Mongolia from 1991 to present. The data shows Mongolia's transition from hyperinflation in the early 1990s following Soviet collapse to more stable price levels in recent decades. Key historical periods include the 325.5% hyperinflation peak in 1992, stabilization in the late 1990s, commodity boom volatility in the 2000s, and recent moderate inflation levels.

## Variables

### Indicator (Үзүүлэлт)
- `Annual inflation rate`: Year-over-year percentage change in Consumer Price Index

### Year (Он)
Years from 1991 to 2024 (34 data points)

## Update Instructions

### Check for Updates

1. Query the table listing endpoint:
   ```
   GET https://data.1212.mn/api/v1/en/NSO/Economy, environment/{subsector}/
   ```

2. Find `DT_NSO_0600_013V2.px` in the response

3. Compare the `updated` field with `source_updated_at` in registry

4. If API's `updated` is newer, dataset needs updating

### Fetch Data

Use the `datamn-source-nso` skill for bilingual data fetching:

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_0600_013V2.px --output ../../data/tools/versions/inflation-annual
```

Or use direct API calls:

```python
import requests
import pandas as pd

BASE_URL = "https://data.1212.mn/api/v1"
sector = "Economy, environment"
subsector = "{subsector}"  # Verify from API
table_id = "DT_NSO_0600_013V2.px"

# Fetch in both English and Mongolian
for lang in ['en', 'mn']:
    url = f"{BASE_URL}/{lang}/NSO/{sector}/{subsector}/{table_id}"

    # Get metadata
    metadata = requests.get(url).json()

    # Build query for all data
    query = {
        "query": [
            {
                "code": var['code'],
                "selection": {
                    "filter": "item",
                    "values": var['values']
                }
            }
            for var in metadata.get('variables', [])
        ],
        "response": {"format": "json-stat2"}
    }

    # Fetch data (POST request)
    data = requests.post(url, json=query).json()
    # Convert json-stat2 to DataFrame
```

### Validation

- All inflation values should be numeric (can be positive or negative)
- Expect very high values in early 1990s (>100%)
- Recent years should be single-digit to low double-digit
- Year values should be valid years (1991-2024)
- Check for 1992 peak of ~325.5%

## Splits

This is a simple time series, so the published dataset is essentially the same as the parent.

### 1. inflation-annual (published dataset)

- **ID**: `inflation-annual`
- **Title EN**: Mongolia Annual Inflation Rate (1991-2024)
- **Title MN**: Монгол Улсын жилийн инфляцийн түвшин (1991-2024)
- **Filter**: None (all data)
- **Chart Type**: area
- **Chart Config**:
  - X-axis: year (quantitative)
  - Y-axis: value (inflation rate %)
  - Color: #4c78a8 (primary blue)
  - Gradient: Linear gradient from light to medium blue
  - Interpolation: monotone
- **Description EN**: Mongolia's inflation rate was 9.0% at the end of 2024. The country experienced hyperinflation in the early 1990s, reaching 325.5% in 1992.
- **Description MN**: Монгол Улсын инфляцийн түвшин 2024 оны эцэст 9.0% байна. Улс 1990-ээд оны эхээр хэт инфляцийг туулж, 1992 онд 325.5%-д хүрсэн.
- **Key Findings**:
  - Current inflation rate (2024)
  - Historical peak (1992)
  - Decades of stabilization
  - Recent volatility (COVID-19, commodity prices)

## Content Generation

### Key Findings Template

Auto-extract:
- Latest value (2024)
- Historical comparison (1992 vs 2024)
- Average over last decade (2014-2024)
- Lowest recorded value
- Highest recorded value

### Common Tags
- mongolia
- inflation
- economy
- cpi
- prices
- nso

### Excerpt Templates

**inflation-annual**:
- EN: "Mongolia's inflation rate was {latest_value}% at the end of {latest_year}. The country experienced hyperinflation in the early 1990s, reaching {peak_value}% in 1992."
- MN: "Монгол Улсын инфляцийн түвшин {latest_year} оны эцэст {latest_value}% байна. Улс 1990-ээд оны эхээр хэт инфляцийг туулж, 1992 онд {peak_value}%-д хүрсэн."

## Notes

- 1991-1995: Post-Soviet transition period with hyperinflation
- 1992: Peak hyperinflation of 325.5%
- 1996-2006: Stabilization period, averaging ~20% early then single digits
- 2007-2008: Commodity boom drove inflation up to 22.1%
- 2015-2016: Lowest modern inflation (~1-2%)
- 2020-present: Moderate inflation with COVID-19 and global commodity impacts
- **Parent dataset**: This dataset (`nso-inflation-annual`) is the parent; `inflation-annual` is the published split (identical in this case as it's a simple time series)
