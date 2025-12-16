# Dataset: Population by Age Group and Sex

## Identification

- **ID**: `nso-population-by-age-sex`
- **Source**: `nso-1212`
- **Category**: Demographics
- **Tags**: [population, demographics, age, sex, census]

## Source Reference

- **Table ID**: `DT_NSO_0300_003V1.px`
- **Sector**: `Population, household`
- **Subsector**: `1_Population, household`
- **API Path**: `/en/NSO/Population, household/1_Population, household/DT_NSO_0300_003V1.px`

## Title

- **EN**: Population of Mongolia by Sex and Age Group
- **MN**: Монгол Улсын хүн ам, хүйс, насны бүлгээр

## Description

Historical population data for Mongolia broken down by sex (male, female, total) and age groups (0-4, 5-9, 10-14, ... 70+). Data spans from 1956 to 2024, providing a comprehensive view of demographic changes over nearly 70 years.

## Variables

### Sex (Хүйс)
- `0`: Total / Бүгд
- `1`: Male / Эрэгтэй
- `2`: Female / Эмэгтэй

### Age Group (Насны бүлэг)
- `0`: Total / Бүгд
- `1`: 0-4
- `2`: 5-9
- `3`: 10-14
- `4`: 15-19
- `5`: 20-24
- `6`: 25-29
- `7`: 30-34
- `8`: 35-39
- `9`: 40-44
- `10`: 45-49
- `11`: 50-54
- `12`: 55-59
- `13`: 60-64
- `14`: 65-69
- `15`: 70+

### Year (Он)
Years from 1956 to 2024 (40 data points, irregular intervals in early years)

## Update Instructions

### Check for Updates

1. Query the table listing endpoint:
   ```
   GET https://data.1212.mn/api/v1/en/NSO/Population, household/1_Population, household/
   ```

2. Find `DT_NSO_0300_003V1.px` in the response

3. Compare the `updated` field with `source_updated_at` in registry

4. If API's `updated` is newer, dataset needs updating

### Fetch Data

Use the `datamn-source-nso` skill for bilingual data fetching:

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_0300_003V1.px --output ./output
```

Or use direct API calls:

```python
import requests

BASE_URL = "https://data.1212.mn/api/v1"
sector = "Population, household"
subsector = "1_Population, household"
table_id = "DT_NSO_0300_003V1.px"

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

- All population values should be positive integers
- Total should equal sum of Male + Female
- Total age group should equal sum of all age groups
- Year values should be valid years (1956-2024)

## Splits

This multi-dimensional dataset is split into the following user-friendly datasets:

### 1. population-total

- **ID**: `population-total`
- **Title EN**: Mongolia Total Population (1956-2024)
- **Title MN**: Монгол Улсын нийт хүн ам (1956-2024)
- **Filter**:
  - Хүйс (Sex): Total / Бүгд
  - Насны бүлэг (Age Group): Total / Бүгд
- **Chart Type**: line
- **Chart Config**:
  - X-axis: year (Он)
  - Y-axis: population (value)
  - Color: #3b82f6 (blue)
- **Description EN**: Mongolia's total population from 1956 to present, showing overall demographic growth.
- **Description MN**: Монгол Улсын нийт хүн амын тоо 1956 оноос өнөөг хүртэл.
- **Key Findings**:
  - Latest population value
  - Growth multiple (latest / earliest)
  - Fastest growth decade

### 2. population-pyramid

- **ID**: `population-pyramid`
- **Title EN**: Mongolia Population Pyramid (2024)
- **Title MN**: Монгол Улсын хүн амын пирамид (2024)
- **Filter**:
  - Он (Year): latest (2024)
  - Хүйс (Sex): NOT Total (Male, Female only)
  - Насны бүлэг (Age Group): NOT Total (all age groups)
- **Chart Type**: population-pyramid
- **Chart Config**:
  - Y-axis: age_group (Насны бүлэг)
  - X-axis: population signed by sex (negative for male, positive for female)
  - Color: sex (Male=#3b82f6, Female=#ec4899)
- **Description EN**: Age and sex distribution of Mongolia's population, showing demographic structure.
- **Description MN**: Монгол Улсын хүн амын нас, хүйсийн бүтэц.
- **Key Findings**:
  - Largest age group
  - Working age proportion (15-64)
  - Sex ratio

### 3. population-by-sex

- **ID**: `population-by-sex`
- **Title EN**: Mongolia Population by Sex (1956-2024)
- **Title MN**: Монгол Улсын хүн ам хүйсээр (1956-2024)
- **Filter**:
  - Насны бүлэг (Age Group): Total / Бүгд
  - Хүйс (Sex): NOT Total (Male, Female only)
- **Chart Type**: multi-line
- **Chart Config**:
  - X-axis: year (Он)
  - Y-axis: population (value)
  - Color: sex (Male=#3b82f6, Female=#ec4899)
- **Description EN**: Comparison of male and female population in Mongolia over time.
- **Description MN**: Монгол Улсын эрэгтэй, эмэгтэй хүн амын харьцуулалт.
- **Key Findings**:
  - Current male population
  - Current female population
  - Sex ratio trend

## Content Generation

### Key Findings Template

For each split, auto-extract:
- Latest values
- Historical comparison (growth rate)
- Notable patterns

### Common Tags
- mongolia
- population
- demographics
- census
- nso

### Excerpt Templates

**population-total**:
- EN: "Mongolia's population grew {growth_multiple}x from {first_value} in {first_year} to {latest_value} in {latest_year}."
- MN: "Монгол Улсын хүн ам {first_year} оны {first_value}-аас {latest_year} онд {latest_value} болж {growth_multiple} дахин өссөн."

**population-pyramid**:
- EN: "Age and sex distribution of Mongolia's {latest_value} population in {latest_year}."
- MN: "{latest_year} оны Монгол Улсын {latest_value} хүн амын нас, хүйсийн бүтэц."

**population-by-sex**:
- EN: "Male vs female population trends in Mongolia from {first_year} to {latest_year}."
- MN: "{first_year}-{latest_year} оны Монгол Улсын эрэгтэй, эмэгтэй хүн амын динамик."

## Notes

- Early years (1956, 1963, 1969, 1979, 1989) are census years with irregular intervals
- From 1990 onwards, data is available annually
- Population figures are mid-year estimates for non-census years
- **Parent dataset**: This dataset (`nso-population-by-age-sex`) stores the raw data; only the splits are published to data.mn
