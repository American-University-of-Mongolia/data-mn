# Dataset: Youth Unemployment Rate (15-24)

## Identification

- **ID**: `unemployment-rate-youth`
- **Source**: `nso-1212`
- **Category**: Labor Market
- **Tags**: [mongolia, unemployment, youth, labor, labor market, employment, 15-24]

## Source Reference

- **Table ID**: `DT_NSO_0400_049V1.px`
- **Sector**: `Labour, business`
- **Subsector**: `Decent work`
- **API Path**: `/en/NSO/Labour, business/Decent work/DT_NSO_0400_049V1.px`

## Title

- **EN**: Youth Unemployment Rate (15-24), % (2009-2024)
- **MN**: Залуучуудын ажилгүйдлийн түвшин (15-24 нас), % (2009-2024)

## Description

Unemployment rate among young people aged 15-24 in Mongolia from 2009 to 2024. Youth unemployment is a critical economic indicator, as high rates can lead to long-term career scarring and social issues. This data is part of SDG Indicator 8.5.2.

## Dataset Type

**Split Dataset** - This is a filtered view of the parent unemployment rate dataset.

### Split Filter

```json
{
  "category": ["15-24"]
}
```

## Variables

### Category (Ангилал)
Single category:
- `15-24`: Youth age group

### Year (Он)
Years from 2009 to 2024 (16 data points)

### Value
- **Unit**: Percentage (%)
- **Range**: 0-100 (typically 5-25% range)

## Update Instructions

### Check for Updates

1. Query the table listing endpoint:
   ```
   GET https://data.1212.mn/api/v1/en/NSO/Labour, business/Decent work/
   ```

2. Find `DT_NSO_0400_049V1.px` in the response

3. Compare the `updated` field with `source_updated_at` in registry

4. If API's `updated` is newer, dataset needs updating

### Fetch Data

Use the `datamn-source-nso` skill for bilingual data fetching:

```python
import requests
import pandas as pd

BASE_URL = "https://data.1212.mn/api/v1"
sector = "Labour, business"
subsector = "Decent work"
table_id = "DT_NSO_0400_049V1.px"

# Fetch in both English and Mongolian
for lang in ['en', 'mn']:
    url = f"{BASE_URL}/{lang}/NSO/{sector}/{subsector}/{table_id}"

    # Get metadata and data
    metadata = requests.get(url).json()

    # Build query filtering for 15-24 age group
    query = {
        "query": [
            {
                "code": "category",
                "selection": {
                    "filter": "item",
                    "values": ["15-24"]  # Youth age group
                }
            },
            # ... include year selection
        ],
        "response": {"format": "json-stat2"}
    }

    data = requests.post(url, json=query).json()
```

### Data Transformation

1. **Filter to youth category only**:
   - Category (Ангилал): 15-24 age group

2. **Clean column names**:
   - Rename columns to: `category`, `year`, `value`
   - Strip whitespace from all string columns

3. **Data validation**:
   - All unemployment rates should be between 0 and 100
   - Values should be numeric (percentage)
   - Year values should be valid years (2009-2024)

4. **Export files**:
   - Chart CSV: `unemployment-rate-youth-en.csv` and `unemployment-rate-youth-mn.csv`
   - Excel XLSX: `unemployment-rate-youth.xlsx` (with English and Mongolian sheets)

### Validation

- All unemployment values should be positive percentages (0-100)
- Youth unemployment typically ranges 5-25%
- Year values should be valid years (2009-2024)
- No missing values for years in range

## Chart Configuration

### Chart Type
Single-series area chart with gradient fill

### Visual Encoding

- **X-axis**: Year (temporal type)
- **Y-axis**: Unemployment Rate (%, quantitative)
- **Mark**: Area with line overlay and hover points
- **Color**: Orange/amber (#f58518) - warning color highlighting youth vulnerability
- **Gradient**: Vertical gradient from transparent to semi-opaque

### Tooltip

Display for each point:
- Year
- Category (15-24)
- Unemployment rate (formatted as "##.#%")

## Content Generation

### Key Findings Template

Auto-extract for MDX page:
- Latest youth unemployment rate (2024 value)
- Historical comparison (2024 vs 2009)
- Lowest rate year and value
- Highest rate year and value
- Comparison to national unemployment rate
- Trend analysis (improving/worsening)

### Common Tags
- mongolia
- unemployment
- youth
- labor-market
- economy
- employment
- 15-24
- nso
- labor
- young-people

### Keywords (EN)
- youth unemployment mongolia
- young people unemployment
- 15-24 unemployment rate
- labor market mongolia
- jobless youth
- employment statistics

### Keywords (MN)
- залуучуудын ажилгүйдэл
- 15-24 насныхны ажилгүйдэл
- хөдөлмөрийн зах зээл
- ажилгүйдлийн түвшин

### Excerpt Templates

**EN**: "Unemployment rate among young people aged 15-24 in Mongolia from 2009 to 2024."

**MN**: "Монгол Улсын 15-24 насны залуучуудын ажилгүйдлийн түвшин 2009-2024 онд."

## Analysis Notes

### Key Patterns
- Youth unemployment is typically 1.5-2x higher than national rate
- Shows significant volatility compared to overall unemployment
- COVID-19 (2020-2021) had disproportionate impact on youth employment
- 2023 data shows sharp decline, possibly due to methodological changes

### Historical Context
- **2009-2011**: Post-global financial crisis recovery
- **2012-2016**: Mining downturn period - highest youth unemployment
- **2017-2019**: Economic recovery
- **2020-2021**: COVID-19 pandemic impact
- **2022-2024**: Post-pandemic recovery, significant improvement

### Use Cases
- Monitor youth labor market conditions
- Analyze generational employment gaps
- Policy planning for youth employment programs
- Education and training program targeting
- International comparison (SDG 8.5.2)

## Notes

- This is a **split dataset** from the main unemployment dataset
- Data comes from SDG Indicator 8.5.2
- Youth unemployment is a key policy concern globally
- The sharp decline in 2023-2024 may warrant investigation
- Updated annually by NSO
- Last API update: 2025-09-29
