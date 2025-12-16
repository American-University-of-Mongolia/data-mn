# Dataset: CPI in Ulaanbaatar (Month-over-Month)

## Identification
- **ID**: nso-cpi-ulaanbaatar-mom
- **Category**: Economy
- **Tags**: [cpi, inflation, prices, ulaanbaatar, monthly]

## Source Reference
- **Table ID**: DT_NSO_0600_003V4.px
- **Title**: CONSUMER PRICE INDEX IN THE CAPITAL, by groups, compared with previous month
- **URL**: https://data.1212.mn

## Variables

### Reference year (Суурь он)
Base year for the index calculation:
- `2015=100`: Historical data (2001-2022)
- `2020=100`: Current data (2020-2025)
- `2023=100`: Latest base (2023-2025)

### Group (Бүлэг)
CPI expenditure categories:
- `Overall index`: Total CPI (aggregate)
- `Food and non-alcoholic beverages`
- `Alcoholic beverages and tobacco`
- `Clothing, footwear and cloth`
- `Housing, water, electricity and fuels`
- `Furnishings, household equipment and tools`
- `Health, medical care and services`
- `Transport`
- `Communication`
- `Recreation and culture`
- `Education services`
- `Restaurants and hotels`
- `Insurance and financial services`
- `Miscellaneous goods and services`

### Month (Сар)
Monthly time dimension: 2001-01 to 2025-11

## Update Instructions

### Check for Updates
1. Query NSO API for table DT_NSO_0600_003V4.px
2. Check `updated` timestamp against last fetch
3. If newer data available, proceed to fetch

### Fetch Data
```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table "DT_NSO_0600_003V4.px" --lang both --output /tmp/cpi-capital-mom
```

### Validation
- Check for null values in recent months
- Verify reference year coverage
- Values should be percentages typically between -5% and +10%

## Splits

### 1. cpi-monthly-ulaanbaatar

- **ID**: `cpi-monthly-ulaanbaatar`
- **Title EN**: Monthly Inflation in Ulaanbaatar (2020-2025)
- **Title MN**: Улаанбаатар хотын сарын инфляци (2020-2025)
- **Filter**:
  - Reference year: 2020=100
  - Group: Overall index
- **Chart Type**: area (with line)
- **Chart Config**:
  - X-axis: month (temporal)
  - Y-axis: value (% change)
- **Description EN**: Month-over-month consumer price index change in Ulaanbaatar city.
- **Description MN**: Улаанбаатар хотын хэрэглээний үнийн индексийн сар бүрийн өөрчлөлт.

### 2. cpi-by-category-ulaanbaatar

- **ID**: `cpi-by-category-ulaanbaatar`
- **Title EN**: CPI by Category in Ulaanbaatar (Latest Month)
- **Title MN**: Улаанбаатар хотын ХҮИ ангиллаар (Сүүлийн сар)
- **Filter**:
  - Reference year: 2023=100
  - Month: Latest with data
  - Group: All except "Overall index"
- **Chart Type**: horizontal bar
- **Chart Config**:
  - Y-axis: group (category)
  - X-axis: value (% change)
  - Color: Conditional (positive/negative)
- **Description EN**: Consumer price changes by expenditure category in Ulaanbaatar for the latest month.
- **Description MN**: Улаанбаатар хотын хэрэглээний үнийн өөрчлөлт ангиллаар, сүүлийн сар.

### 3. cpi-food-ulaanbaatar

- **ID**: `cpi-food-ulaanbaatar`
- **Title EN**: Food Price Changes in Ulaanbaatar (2020-2025)
- **Title MN**: Улаанбаатар хотын хүнсний үнийн өөрчлөлт (2020-2025)
- **Filter**:
  - Reference year: 2020=100
  - Group: Food and non-alcoholic beverages
- **Chart Type**: area (with line)
- **Chart Config**:
  - X-axis: month (temporal)
  - Y-axis: value (% change)
- **Description EN**: Month-over-month food price changes in Ulaanbaatar city.
- **Description MN**: Улаанбаатар хотын хүнсний үнийн сар бүрийн өөрчлөлт.

## Content Generation

### CRITICAL: Data pages must be MINIMAL

When generating MDX pages for splits, follow these rules strictly:

1. **NO prose sections** - Do not create "Overview", "Key Findings", "Analysis" sections
2. **Only include:**
   - Frontmatter with metadata
   - Import statement
   - One excerpt sentence (factual, with key numbers)
   - VegaChart component
3. **The chart IS the content** - Let the visualization tell the story

### Key Findings Template
- For monthly trend: Latest month's inflation rate, YTD average
- For category breakdown: Highest/lowest category changes
- For food: Latest food inflation vs overall

### Common Tags
EN: [mongolia, cpi, inflation, prices, ulaanbaatar, monthly]
MN: [монгол, хэрэглээний үнийн индекс, инфляци, үнэ, улаанбаатар, сар бүр]
