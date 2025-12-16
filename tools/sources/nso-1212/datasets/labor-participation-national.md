# Dataset: Labour Force Participation Rate (National)

## Identification

- **ID**: `labor-participation-national`
- **Source**: `nso-1212`
- **Category**: Labor Market
- **Tags**: [labour, participation, employment, economy, workforce]

## Source Reference

- **Table ID**: `DT_NSO_0400_018V1_1.px`
- **Sector**: `Labour market`
- **Subsector**: `4_Labour market`
- **API Path**: `/en/NSO/Labour market/4_Labour market/DT_NSO_0400_018V1_1.px`

## Title

- **EN**: Mongolia Labour Force Participation Rate, % (1992-2024)
- **MN**: Монгол Улсын ажиллах хүчний эдийн засгийн идэвхжил, % (1992-2024)

## Description

Labour force participation rate represents the percentage of Mongolia's working-age population (15 years and older) that is economically active - either employed or actively seeking employment. This national-level indicator tracks overall economic engagement over three decades, from the post-transition period (1992) to present (2024).

The rate peaked at 75.8% in 1992 during the transition period and has gradually declined to around 60-61% in recent years, reflecting structural changes in the economy, education patterns, and demographic shifts.

## Variables

### Year (Он)
Years from 1992 to 2024 (33 data points)

### Value (Утга)
Labour force participation rate as percentage (%)

## Update Instructions

### Check for Updates

1. Query the table listing endpoint:
   ```
   GET https://data.1212.mn/api/v1/en/NSO/Labour market/4_Labour market/
   ```

2. Find `DT_NSO_0400_018V1_1.px` in the response

3. Compare the `updated` field with `source_updated_at` in registry

4. If API's `updated` is newer, dataset needs updating

### Fetch Data

Use the `datamn-source-nso` skill for bilingual data fetching:

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_0400_018V1_1.px --output ./output
```

Or use direct API calls:

```python
import requests

BASE_URL = "https://data.1212.mn/api/v1"
sector = "Labour market"
subsector = "4_Labour market"
table_id = "DT_NSO_0400_018V1_1.px"

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
    # Convert json-stat2 to DataFrame - see datamn-source-nso skill for implementation
```

### Validation

- Values should be between 0 and 100 (percentage)
- Values should show realistic variation (not jump >10% year-over-year)
- Year values should be valid years (1992-2024)
- Latest year should match current or previous year

## Splits

This is a simple single-series dataset and does not require splits. It is published directly as `labor-participation-national`.

## Content Generation

### Key Findings

Auto-extract:
- Latest value (2024)
- Historical high and low
- Long-term trend (1992 vs 2024)
- Decade averages (1990s, 2000s, 2010s, 2020s)
- Recent trends (last 5 years)

### Common Tags
- mongolia
- labour
- participation
- employment
- workforce
- economy
- nso

### Excerpt Templates

**English**:
"Mongolia's labour force participation rate was {latest_value}% in 2024, showing {trend_description} from {comparison_value}% in {comparison_year}."

**Mongolian**:
"2024 онд Монгол Улсын ажиллах хүчний эдийн засгийн идэвхжил {latest_value}% байсан нь {comparison_year} оны {comparison_value}%-аас {trend_description}."

## Notes

- Data represents national average (all regions combined)
- Working-age population defined as 15+ years
- Participation rate includes both employed and unemployed (actively seeking work)
- Historical high during transition period (1992) due to universal employment in planned economy
- Gradual decline reflects increased education enrollment, early retirement, and structural economic changes
- **This is a published dataset** - not a parent dataset with splits
