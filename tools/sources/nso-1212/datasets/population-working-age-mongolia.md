# Dataset: Working Age Population of Mongolia (15-64)

## Identification

- **ID**: `population-working-age-mongolia`
- **Source**: `nso-1212`
- **Category**: Demographics
- **Tags**: [population, demographics, working-age, labor-force, 15-64]

## Parent Dataset

- **Parent ID**: `nso-population-age-sex`
- **Parent Table ID**: `DT_NSO_0300_003V1.px`
- **Sector**: `Population, household`
- **Subsector**: `1_Population, household`
- **API Path**: `/en/NSO/Population, household/1_Population, household/DT_NSO_0300_003V1.px`

## Title

- **EN**: Working Age Population of Mongolia (15-64)
- **MN**: Монгол Улсын ажиллах насны хүн ам (15-64)

## Description

Working age population (15-64 years) time series for Mongolia, showing the demographic foundation for the labor force. This dataset represents the population segment that is considered economically active or potentially active. Data spans from 1956 to 2024, tracking how Mongolia's working age population has grown over nearly 70 years.

The working age population is a critical indicator for:
- Labor force planning
- Economic development potential
- Dependency ratio calculations
- Social security system sustainability
- Workforce availability

## Filter Definition

This split is created by filtering the parent dataset with:

```json
{
  "Sex": "Total",
  "Age group": "working_age"
}
```

**Working age definition**: Sum of age groups 15-19, 20-24, 25-29, 30-34, 35-39, 40-44, 45-49, 50-54, 55-59, 60-64

The filter selects:
- **Sex**: Total (combined male and female)
- **Age groups**: 15-19, 20-24, 25-29, 30-34, 35-39, 40-44, 45-49, 50-54, 55-59, 60-64
- **Years**: All available years (1956-2024)

## Data Transformation

When updating this dataset from the parent:

1. Load parent data from `nso-population-age-sex`
2. Filter to Sex = "Total" (exclude male/female breakdown)
3. Filter to age groups 15-64 (exclude 0-14 and 65+)
4. Sum all working age groups for each year
5. Create time series with columns: `year`, `value`

**Python pseudocode:**
```python
# Load parent data
df = pd.read_csv("nso-population-age-sex.csv")

# Filter to total sex and working age groups
working_age_groups = ['15-19', '20-24', '25-29', '30-34', '35-39',
                       '40-44', '45-49', '50-54', '55-59', '60-64']
df_working = df[
    (df['sex'] == 'Total') &
    (df['age_group'].isin(working_age_groups))
]

# Sum by year
result = df_working.groupby('year')['value'].sum().reset_index()
result.columns = ['year', 'value']
```

## Validation

- All values should be positive integers
- Working age population should be less than total population
- Trend should be generally upward (population growth)
- Latest year should show ~60-65% of total population
- No sudden jumps/drops except for census corrections

## Chart Specification

- **Chart Type**: area (single-series time series)
- **Chart Config**:
  - X-axis: year (Он) - quantitative
  - Y-axis: value (population count) - quantitative
  - Mark: area with gradient fill
  - Color: #4c78a8 (primary brand blue)
  - Interpolation: monotone
- **Chart Files**:
  - `/charts/population-working-age-mongolia-en.json`
  - `/charts/population-working-age-mongolia-mn.json`

## Content Generation

### Excerpt Template

**English:**
"Mongolia's working age population (15-64 years) grew from {first_value} in {first_year} to {latest_value} in {latest_year}, a {growth_multiple}x increase."

**Mongolian:**
"Монгол Улсын ажиллах насны хүн ам (15-64) {first_year} оны {first_value}-аас {latest_year} онд {latest_value} болж {growth_multiple} дахин өссөн."

### Key Findings Template

Auto-extract and display:
- **Latest value**: Current working age population
- **Growth since 1956**: Absolute and percentage increase
- **Share of total population**: Working age as % of total
- **Peak growth period**: Decade with fastest growth
- **Dependency implications**: Ratio of working age to non-working age

### Common Tags

- mongolia
- population
- working-age
- labor-force
- demographics
- economic-development
- dependency-ratio

### Keywords (EN)

- mongolia working age population
- labor force demographics mongolia
- population 15-64 mongolia
- working age population trends
- mongolia workforce size
- economic active population mongolia

### Keywords (MN)

- монгол улсын ажиллах насны хүн ам
- ажиллах хүчний хүн ам зүй
- 15-64 насны хүн ам
- ажиллах насны хүн амын өөрчлөлт
- монгол улсын ажиллах хүчний хэмжээ

## Related Datasets

- `population-total-mongolia` - Total population context
- `population-pyramid-mongolia` - Age structure detail
- `population-by-sex-mongolia` - Gender breakdown
- `labor-force-participation` - Employment context (if available)
- `dependency-ratio` - Demographic burden indicator (if available)

## Update Instructions

This is a **split dataset**. It does not update independently.

### Update Workflow

1. When parent dataset `nso-population-age-sex` receives an update
2. Parent dataset is fetched and saved
3. This split is automatically regenerated using the filter definition above
4. New version is created in `tools/versions/population-working-age-mongolia/v{N}/`
5. Charts and MDX pages are regenerated

### Manual Update (if needed)

```bash
# Update parent first
cd tools
python -m registry update-dataset nso-population-age-sex

# Regenerate this split
python scripts/regenerate_split.py population-working-age-mongolia
```

## Notes

- **Working age definition**: International standard is 15-64, though some countries use 15-59 or 16-64
- **NSO definition**: Mongolia NSO uses 15-64 as working age, consistent with ILO standards
- Early census years (1956, 1963, 1969, 1979, 1989) have irregular intervals
- From 1990 onwards, annual data is available
- Population figures are mid-year estimates for non-census years
- **Split dataset**: This dataset does not fetch data directly; it is derived from parent
