# Dataset: Unemployment Rate by Category and Year

## Identification

- **ID**: `nso-unemployment-rate`
- **Source**: `nso-1212`
- **Category**: Labor Market
- **Tags**: [unemployment, labor, employment, workforce, nso]

## Source Reference

- **Table ID**: `DT_NSO_0400_049V1.px`
- **Sector**: `Labour, business`
- **Subsector**: `Unemployment`
- **API Path**: `/en/NSO/Labour, business/Unemployment/DT_NSO_0400_049V1.px`

## Title

- **EN**: Unemployment Rate by Category and Year
- **MN**: Ажилгүйдлийн түвшин ангилал, жилээр

## Description

Unemployment rate data for Mongolia from 2009 to present. The data includes breakdowns by age groups, sex, geographic location (urban/rural), and regional divisions. This multi-dimensional dataset provides comprehensive insights into labor market conditions across different demographic and geographic segments.

## Variables

### Category (Ангилал)
- `Total`: Total / Бүгд
- `15-24`: Youth (15-24 years) / Залуучууд (15-24 нас)
- `25-34`: Young adults (25-34 years) / Залуу насныхан (25-34 нас)
- `35-44`: Middle age (35-44 years) / Дунд нас (35-44 нас)
- `45-54`: Mature (45-54 years) / Дунд нас (45-54 нас)
- `55-64`: Pre-retirement (55-64 years) / Тэтгэвэрийн өмнөх нас (55-64 нас)
- `Male`: Male / Эрэгтэй
- `Female`: Female / Эмэгтэй
- `Urban`: Urban areas / Хот
- `Rural`: Rural areas / Хөдөө
- Regional breakdown: Provinces and capital city

### Year (Он)
Annual data from 2009 to 2024

### Value (Утга)
Unemployment rate as percentage (%)

## Update Instructions

### Check for Updates

1. Query the table listing endpoint:
   ```
   GET https://data.1212.mn/api/v1/en/NSO/Labour, business/Unemployment/
   ```

2. Find `DT_NSO_0400_049V1.px` in the response

3. Compare the `updated` field with `source_updated_at` in registry

4. If API's `updated` is newer, dataset needs updating

### Fetch Data

Use direct API calls to fetch bilingual data:

```python
import requests
import pandas as pd

BASE_URL = "https://data.1212.mn/api/v1"
sector = "Labour, business"
subsector = "Unemployment"
table_id = "DT_NSO_0400_049V1.px"

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
    # Implementation in datamn-source-nso skill
```

### Validation

- All unemployment rate values should be between 0-100 (percentage)
- Values should be positive numbers
- Year values should be valid years (2009-2024)
- Category labels should be consistent with NSO taxonomy

## Splits

This multi-dimensional dataset is split into the following user-friendly datasets:

### 1. unemployment-rate-total

- **ID**: `unemployment-rate-total`
- **Title EN**: Unemployment Rate of Mongolia
- **Title MN**: Монгол Улсын ажилгүйдлийн түвшин
- **Filter**:
  - Category: Total / Бүгд
- **Chart Type**: area
- **Chart Config**:
  - X-axis: year (Он)
  - Y-axis: unemployment rate (%)
  - Color: #4c78a8 (primary blue)
- **Description EN**: Overall unemployment rate in Mongolia showing labor market conditions from 2009 to present.
- **Description MN**: Монгол Улсын нийт ажилгүйдлийн түвшин 2009 оноос өнөөг хүртэл.
- **Key Findings**:
  - Current unemployment rate
  - Historical trend
  - Economic cycle correlation

### 2. unemployment-rate-youth

- **ID**: `unemployment-rate-youth`
- **Title EN**: Youth Unemployment Rate (15-24)
- **Title MN**: Залуучуудын ажилгүйдлийн түвшин (15-24)
- **Filter**:
  - Category: 15-24
- **Chart Type**: area
- **Chart Config**:
  - X-axis: year (Он)
  - Y-axis: unemployment rate (%)
  - Color: #4c78a8 (primary blue)
- **Description EN**: Unemployment rate among youth aged 15-24, showing challenges young workers face entering the labor market.
- **Description MN**: 15-24 насны залуучуудын ажилгүйдлийн түвшин, ажлын зах зээлд залуучуудын тулгамдаж буй асуудлыг харуулна.
- **Key Findings**:
  - Current youth unemployment rate
  - Comparison with total unemployment
  - Education-employment gap

### 3. unemployment-rate-by-age

- **ID**: `unemployment-rate-by-age`
- **Title EN**: Unemployment Rate by Age Group
- **Title MN**: Ажилгүйдлийн түвшин насны бүлгээр
- **Filter**:
  - Category: 15-24, 25-34, 35-44, 45-54, 55-64 (age groups, excluding Total)
- **Chart Type**: multi-line
- **Chart Config**:
  - X-axis: year (Он)
  - Y-axis: unemployment rate (%)
  - Color: age groups (palette: #4c78a8, #f58518, #e45756, #72b7b2, #54a24b)
- **Description EN**: Unemployment rates across different age groups showing age-specific labor market dynamics.
- **Description MN**: Өөр өөр насны бүлгийн ажилгүйдлийн түвшин, насны онцлогтой холбоотой хөдөлмөрийн зах зээлийн динамик.
- **Key Findings**:
  - Age groups most affected
  - Youth vs mature worker comparison
  - Age-specific trends

### 4. unemployment-rate-by-sex

- **ID**: `unemployment-rate-by-sex`
- **Title EN**: Unemployment Rate by Sex
- **Title MN**: Ажилгүйдлийн түвшин хүйсээр
- **Filter**:
  - Category: Male, Female (excluding Total)
- **Chart Type**: multi-line
- **Chart Config**:
  - X-axis: year (Он)
  - Y-axis: unemployment rate (%)
  - Color: Male=#4c78a8, Female=#e45756
- **Description EN**: Comparison of unemployment rates between male and female workers in Mongolia.
- **Description MN**: Монгол Улсын эрэгтэй, эмэгтэй хөдөлмөрийн хүчний ажилгүйдлийн түвшний харьцуулалт.
- **Key Findings**:
  - Gender unemployment gap
  - Trend convergence/divergence
  - Gender-specific labor market challenges

### 5. unemployment-rate-by-location

- **ID**: `unemployment-rate-by-location`
- **Title EN**: Unemployment Rate by Location
- **Title MN**: Ажилгүйдлийн түвшин байршлаар
- **Filter**:
  - Category: Urban, Rural (excluding Total)
- **Chart Type**: multi-line
- **Chart Config**:
  - X-axis: year (Он)
  - Y-axis: unemployment rate (%)
  - Color: Urban=#4c78a8, Rural=#f58518
- **Description EN**: Urban vs rural unemployment rates showing geographic disparities in labor markets.
- **Description MN**: Хот, хөдөөгийн ажилгүйдлийн түвшний ялгаа, хөдөлмөрийн зах зээлийн газарзүйн тэнцвэргүй байдал.
- **Key Findings**:
  - Urban-rural gap
  - Migration impact
  - Regional economic development

### 6. unemployment-rate-by-region

- **ID**: `unemployment-rate-by-region`
- **Title EN**: Unemployment Rate by Region
- **Title MN**: Ажилгүйдлийн түвшин бүс нутгаар
- **Filter**:
  - Category: Regional breakdown (provinces and capital)
  - Latest year only for readability
- **Chart Type**: horizontal bar
- **Chart Config**:
  - X-axis: unemployment rate (%)
  - Y-axis: region names
  - Color: #4c78a8
  - Sort: descending by value
- **Description EN**: Regional unemployment rates across Mongolia's provinces and capital city.
- **Description MN**: Монгол Улсын аймаг, нийслэлээр ажилгүйдлийн түвшин.
- **Key Findings**:
  - Regional disparities
  - Economic activity centers
  - Resource-dependent regions

## Content Generation

### Key Findings Template

For each split, auto-extract:
- Latest year value
- Change from previous year
- Historical minimum and maximum
- Average over period
- Trend direction (increasing/decreasing)

### Common Tags
- mongolia
- unemployment
- labor
- employment
- workforce
- nso
- annual

### Excerpt Templates

**unemployment-rate-total**:
- EN: "Mongolia's unemployment rate was {latest_value}% in {latest_year}, {change} from {previous_year}."
- MN: "{latest_year} онд Монгол Улсын ажилгүйдлийн түвшин {latest_value}% байв."

**unemployment-rate-youth**:
- EN: "Youth unemployment (15-24) was {latest_value}% in {latest_year}, {comparison} the national average."
- MN: "Залуучуудын (15-24) ажилгүйдлийн түвшин {latest_year} онд {latest_value}% байв."

**unemployment-rate-by-age**:
- EN: "Unemployment rates vary significantly by age group, with {highest_group} experiencing the highest rate at {highest_value}%."
- MN: "Насны бүлгээр ажилгүйдлийн түвшин ихээхэн ялгаатай, {highest_group} хамгийн өндөр {highest_value}%."

## Notes

- Data is annual (not monthly or quarterly)
- Based on Labor Force Survey methodology
- Follows ILO (International Labour Organization) definitions
- Unemployment rate = (Unemployed / Labor Force) × 100
- **Parent dataset**: This dataset (`nso-unemployment-rate`) stores the raw data; only the splits are published to data.mn
- The dataset structure includes multiple categories in a single table (age, sex, location, regions)
- Filters are applied when creating split datasets to extract specific dimensions
