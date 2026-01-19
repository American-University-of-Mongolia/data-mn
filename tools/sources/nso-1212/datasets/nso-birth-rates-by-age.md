# Dataset: Birth Rates by Age Group

## Identification

- **ID**: `nso-birth-rates-by-age`
- **Source**: `nso-1212`
- **Category**: Demographics
- **Tags**: [birth rate, fertility, demographics, age, reproductive health]

## Source Reference

- **Table ID**: `DT_NSO_0300_029V1.px`
- **Sector**: `Population, household`
- **Subsector**: `2_Regular movement of population`
- **API Path**: `/en/NSO/Population, household/2_Regular movement of population/DT_NSO_0300_029V1.px`

## Title

- **EN**: Birth Rates by Age Group (1980-2024)
- **MN**: Төрөлтийн түвшин насны бүлгээр (1980-2024)

## Description

Age-specific birth rates for Mongolia from 1980 to 2024, including summary indicators (Crude Birth Rate, General Fertility Rate, Total Fertility Rate). This dataset documents Mongolia's dramatic demographic transition from high to moderate fertility over 44 years.

## Variables

### Age Group (Насны бүлэг)
- `CBR`: Crude Birth Rate (per 1,000 population)
- `GFR`: General Fertility Rate (per 1,000 women aged 15-49)
- `TFR`: Total Fertility Rate (children per woman)
- `15-19`: Age-specific rate for women aged 15-19
- `20-24`: Age-specific rate for women aged 20-24
- `25-29`: Age-specific rate for women aged 25-29
- `30-34`: Age-specific rate for women aged 30-34
- `35-39`: Age-specific rate for women aged 35-39
- `40-44`: Age-specific rate for women aged 40-44
- `45-49`: Age-specific rate for women aged 45-49

### Year (Он)
Years from 1980 to 2024 (37 data points)
- 1980, 1985, 1990 (5-year intervals in early period)
- 1991-2024 (annual data)

## Update Instructions

### Check for Updates

1. Query the table listing endpoint:
   ```
   GET https://data.1212.mn/api/v1/en/NSO/Population, household/2_Regular movement of population/
   ```

2. Find `DT_NSO_0300_029V1.px` in the response

3. Compare the `updated` field with `source_updated_at` in registry

4. If API's `updated` is newer, dataset needs updating

### Fetch Data

Use the `datamn-source-nso` skill for bilingual data fetching:

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_0300_029V1.px --output ./output
```

### Validation

- All rate values should be positive numbers
- CBR should typically be 10-50 per 1,000
- TFR should typically be 1.0-8.0 children per woman
- Age-specific rates should decrease for older age groups (35+)
- Year values should be valid years (1980-2024)

## Splits

This multi-dimensional dataset is split into the following user-friendly datasets:

### 1. birth-rate-crude

- **ID**: `birth-rate-crude`
- **Title EN**: Mongolia Crude Birth Rate (1980-2024)
- **Title MN**: Монгол Улсын төрөлтийн түвшин (1980-2024)
- **Filter**:
  - Age Group: CBR (Crude birth rate)
- **Chart Type**: area
- **Chart Config**:
  - X-axis: year
  - Y-axis: value (rate per 1,000)
  - Color: #4c78a8 (blue)
- **Description EN**: Crude birth rate (births per 1,000 population) showing Mongolia's demographic transition.
- **Description MN**: Монгол Улсын төрөлтийн түвшин (1,000 хүн тутамд).
- **Key Findings**:
  - Declined from 39.2 (1980) to 16.9 (2024)
  - 57% decline over 44 years

### 2. fertility-rate-total

- **ID**: `fertility-rate-total`
- **Title EN**: Mongolia Total Fertility Rate (1980-2024)
- **Title MN**: Монгол Улсын нийт төрөлтийн түвшин (1980-2024)
- **Filter**:
  - Age Group: TFR (Total fertility rate)
- **Chart Type**: area
- **Chart Config**:
  - X-axis: year
  - Y-axis: value (children per woman)
  - Color: #4c78a8 (blue)
- **Description EN**: Average number of children a woman would have over her lifetime.
- **Description MN**: Нэг эмэгтэй насан туршдаа дунджаар хэдэн хүүхэд төрүүлэх тоо.
- **Key Findings**:
  - Declined from 6.4 (1980) to 2.5 (2024)
  - Now slightly above replacement level (2.1)

### 3. birth-rate-by-age

- **ID**: `birth-rate-by-age`
- **Title EN**: Mongolia Age-Specific Birth Rates (1980-2024)
- **Title MN**: Монгол Улсын насны бүлгээрх төрөлтийн түвшин (1980-2024)
- **Filter**:
  - Age Group: 15-19, 20-24, 25-29, 30-34, 35-39, 40-44, 45-49 (exclude summary indicators)
- **Chart Type**: multi-line
- **Chart Config**:
  - X-axis: year
  - Y-axis: value (rate per 1,000 women)
  - Color: age_group (7 distinct colors)
- **Description EN**: Birth rates by age group showing the shift in peak childbearing age.
- **Description MN**: Насны бүлгээрх төрөлтийн түвшин.
- **Key Findings**:
  - Peak fertility shifted from 25-29 (1980s) to 20-24 (2020s)
  - Dramatic decline across all age groups

### 4. birth-rate-heatmap

- **ID**: `birth-rate-heatmap`
- **Title EN**: Mongolia Birth Rates Heatmap by Age and Year (1980-2024)
- **Title MN**: Монгол Улсын төрөлтийн түвшний халуун газрын зураг (1980-2024)
- **Filter**:
  - Age Group: 15-19, 20-24, 25-29, 30-34, 35-39, 40-44, 45-49 (exclude summary indicators)
- **Chart Type**: heatmap
- **Chart Config**:
  - X-axis: year
  - Y-axis: age_group
  - Color: value (sequential red scale, 0-350)
- **Description EN**: Heatmap visualization showing fertility transition patterns across age and time.
- **Description MN**: Насны бүлэг болон цаг хугацаагаар төрөлтийн түвшний өөрчлөлтийг харуулах халуун газрын зураг.
- **Key Findings**:
  - Visual pattern shows dramatic decline from 1980s to 2020s
  - Peak fertility (darkest red) concentrated in 20-29 age range

## Content Generation

### Key Findings Template

For each split, auto-extract:
- First and last values with years
- Percentage change over time period
- Notable inflection points

### Common Tags
- mongolia
- birth-rate
- fertility
- demographics
- reproductive-health
- nso

### Excerpt Templates

**birth-rate-crude**:
- EN: "Mongolia's crude birth rate declined 57% from 39.2 per 1,000 in 1980 to 16.9 per 1,000 in 2024."
- MN: "Монгол Улсын төрөлтийн түвшин 1980 оны 1,000 хүн тутамд 39.2-оос 2024 онд 16.9 болж 57%-иар буурсан."

**fertility-rate-total**:
- EN: "Mongolia's total fertility rate fell from 6.4 to 2.5 children per woman between 1980-2024."
- MN: "Монгол Улсын нийт төрөлтийн түвшин 1980-2024 онд нэг эмэгтэйд 6.4-өөс 2.5 хүүхэд болж буурсан."

**birth-rate-by-age**:
- EN: "Age-specific birth rates in Mongolia from 1980-2024, showing peak fertility shift from ages 25-29 to 20-24."
- MN: "1980-2024 оны Монгол Улсын насны бүлгээрх төрөлтийн түвшин, хамгийн өндөр төрөлт 25-29 насны бүлгээс 20-24 нас руу шилжсэн."

**birth-rate-heatmap**:
- EN: "Heatmap showing Mongolia's fertility transition from 1980-2024 across all reproductive age groups."
- MN: "1980-2024 оны Монгол Улсын бүх үржихүйн насны бүлгийн төрөлтийн шилжилтийг харуулсан халуун газрын зураг."

## Notes

- Early years (1980, 1985, 1990) have 5-year intervals; annual data from 1991 onwards
- Age-specific rates are per 1,000 women in that age group
- CBR is per 1,000 total population
- TFR is the sum of age-specific rates, representing children per woman
- GFR is births per 1,000 women aged 15-49
- **Parent dataset**: This dataset (`nso-birth-rates-by-age`) stores the raw data; only the splits are published to data.mn
