# Dataset: Average Monthly Salary (National)

## Identification

- **ID**: `salary-average-national`
- **Source**: `nso-1212`
- **Category**: Economy
- **Tags**: [salary, wages, income, labour, economy, employment]

## Source Reference

- **Table ID**: `DT_NSO_0400_022V1.px`
- **Sector**: `Labour, business`
- **Subsector**: `Wages`
- **API Path**: `/en/NSO/Labour, business/Wages/DT_NSO_0400_022V1.px`

## Title

- **EN**: Mongolia Average Monthly Salary (2001-2024)
- **MN**: Монгол Улсын сарын дундаж цалин (2001-2024)

## Description

Monthly average nominal wages and salaries in Mongolia from 2001 to 2024. Data includes national average salary and breakdown by economic sectors following ISIC classification. Values are in thousands of MNT.

## Variables

### Year (Он)
Years from 2001 to 2024 (24 data points)

### Economic Sector (Эдийн засгийн салбар)
- `National average`: Overall average salary across all sectors / Үндэсний дундаж
- `Agriculture, forestry, fishing and hunting`: Primary sector
- `Mining and quarrying`: Extractive industries
- `Manufacturing`: Industrial production
- `Electricity, gas, steam and air conditioning supply`: Utilities
- `Water supply, sewerage, waste management and remedation activities`: Water/waste utilities
- `Construction`: Building and infrastructure
- `Wholesale and retail trade, repair of motor vehicles and motorcycles`: Trade
- `Transportation and storage`: Logistics
- `Accomodation and food service activities`: Hospitality
- `Information and communication`: ICT sector
- `Financial and insurance activities`: Finance
- `Real estate activities`: Property
- `Professional, scientific and technical activities`: Professional services
- `Administrative and support service activities`: Support services
- `Public administration and defense; compulsory social security`: Government
- `Education`: Education sector
- `Human health and social work activities`: Healthcare
- `Arts, entertainment and recreation`: Culture
- `Other service activities`: Other services
- `Activities of households as employers; undifferentiated goods-and services-producing activities of household for own use`: Household employment
- `Activities of extraterritorial organizations and bodies`: International organizations

### Salary (Цалин)
Monthly average nominal wage in thousands of MNT (MNT 1000s)

## Update Instructions

### Check for Updates

1. Query the table listing endpoint:
   ```
   GET https://data.1212.mn/api/v1/en/NSO/Labour, business/Wages/
   ```

2. Find `DT_NSO_0400_022V1.px` in the response

3. Compare the `updated` field with `source_updated_at` in registry

4. If API's `updated` is newer, dataset needs updating

### Fetch Data

Use the `datamn-source-nso` skill:

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_0400_022V1.px --output ../../data/tools/versions/salary-average-national
```

Or use direct API calls:

```python
import requests

BASE_URL = "https://data.1212.mn/api/v1"
sector = "Labour, business"
subsector = "Wages"
table_id = "DT_NSO_0400_022V1.px"

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

- All salary values should be positive
- Values are in thousands of MNT (MNT 1000s)
- Year values should be valid years (2001-2024)
- National average should be between lowest and highest sector salaries
- Mining sector typically has highest average salary
- Hospitality sector typically has lowest average salary

## Splits

This multi-dimensional dataset is split into the following user-friendly datasets:

### 1. salary-average-national (this dataset)

- **ID**: `salary-average-national`
- **Title EN**: Mongolia Average Monthly Salary (2001-2024)
- **Title MN**: Монгол Улсын сарын дундаж цалин (2001-2024)
- **Filter**:
  - Economic sector: National average
- **Chart Type**: area
- **Chart Config**:
  - X-axis: year (Он)
  - Y-axis: salary (MNT 1000s)
  - Color: #4c78a8 (blue)
- **Description EN**: Mongolia's national average monthly salary from 2001 to present, showing wage growth over time.
- **Description MN**: Монгол Улсын үндэсний сарын дундаж цалин 2001 оноос өнөөг хүртэл.
- **Key Findings**:
  - Latest salary value
  - Growth multiple (latest / earliest)
  - Average annual growth rate

### 2. salary-by-sector-2024

- **ID**: `salary-by-sector-2024`
- **Title EN**: Average Monthly Salary by Economic Sector (2024)
- **Title MN**: Сарын дундаж цалин эдийн засгийн салбараар (2024)
- **Filter**:
  - Year: latest (2024)
  - Economic sector: NOT National average (all individual sectors)
- **Chart Type**: horizontal-bar
- **Chart Config**:
  - Y-axis: sector (Economic sector name)
  - X-axis: salary (MNT 1000s)
  - Color: #4c78a8
  - Sort: descending by salary
- **Description EN**: Comparison of average monthly salaries across economic sectors in Mongolia (2024).
- **Description MN**: Монгол Улсын эдийн засгийн салбар бүрийн сарын дундаж цалингийн харьцуулалт (2024).
- **Key Findings**:
  - Highest paying sector
  - Lowest paying sector
  - Wage gap between sectors

## Content Generation

### Key Findings Template

For each split, auto-extract:
- Latest values
- Historical comparison (growth rate)
- Notable patterns

### Common Tags
- mongolia
- salary
- wages
- employment
- labour
- economy
- nso

### Excerpt Templates

**salary-average-national**:
- EN: "Mongolia's average monthly salary grew {growth_multiple}x from {first_value} thousand MNT in {first_year} to {latest_value} thousand MNT in {latest_year}."
- MN: "Монгол Улсын сарын дундаж цалин {first_year} оны {first_value} мянган төгрөгөөс {latest_year} онд {latest_value} мянган төгрөг болж {growth_multiple} дахин өссөн."

**salary-by-sector-2024**:
- EN: "Average monthly salaries by economic sector in Mongolia ({latest_year}). Mining sector leads with {max_value} thousand MNT."
- MN: "Монгол Улсын эдийн засгийн салбар бүрийн сарын дундаж цалин ({latest_year}). Уул уурхайн салбар {max_value} мянган төгрөгөөр тэргүүлж байна."

## Notes

- Values are monthly averages in thousands of MNT (not annual)
- Data represents formal sector employment only
- Informal sector wages not included
- Mining sector consistently has highest average wages
- Rapid salary growth from 2007-2013 driven by commodity boom
- 2020 shows COVID-19 impact on certain sectors
- **Parent dataset**: This dataset (`salary-average-national`) is a standalone dataset that also serves as parent for sector splits
