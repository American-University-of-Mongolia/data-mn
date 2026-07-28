# Dataset: GDP by Economic Activity

## Identification

- **ID**: `nso-gdp-by-economic-activity`
- **Source**: `nso-1212`
- **Category**: Economy
- **Tags**: [gdp, economy, economic-activity, national-accounts, sectors]

## Source Reference

- **Table ID**: `DT_NSO_0500_001V1.px`
- **Sector**: `Economy, environment`
- **Subsector**: `National Accounts`
- **API Path**: `/en/NSO/Economy, environment/National Accounts/DT_NSO_0500_001V1.px`

## Title

- **EN**: GDP by Production Approach and Economic Activity
- **MN**: ДНБ үйлдвэрлэлийн аргаар, эдийн засгийн салбараар

## Description

Gross Domestic Product (GDP) of Mongolia broken down by production approach and economic activity sectors. Includes current prices, constant prices (2005, 2010, 2015 base years), annual growth rates, sector contributions to growth, and USD values. Data spans from 1990 to 2025.

## Variables

### Indicator (Үзүүлэлт)
- `GDP, at current prices`: GDP at current (nominal) prices in million MNT
- `GDP, at 2015 constant prices`: Real GDP at 2015 base year prices
- `GDP, at 2010 constant prices`: Real GDP at 2010 base year prices
- `GDP, at 2005 constant prices`: Real GDP at 2005 base year prices
- `Annual changes, by percent`: Year-over-year GDP growth rate
- `Contribution of sectors to changes in GDP, percentage points`: Sector contribution to overall GDP growth
- `GDP, at current price, thousand USD`: GDP in US dollars

### Economic Activity (Эдийн засгийн салбар)
- `Total`: All sectors combined
- `Agriculture, forestry, fishing and hunting`: Primary sector
- `Mining and quarrying`: Extractive industries
- `Manufacturing`: Industrial production
- `Electricity, gas, steam, air conditioning supply`: Utilities
- `Water supply; sewerage, waste management and remediation activities`: Utilities
- `Construction`: Building and infrastructure
- `Wholesale and retail trade; repair of motor vehicles and motorcycles`: Trade
- `Transportation and storage`: Logistics
- `Accommodation and food service activities`: Hospitality
- `Information and communication`: ICT sector
- `Financial and insurance activities`: Finance
- `Real estate activities`: Property
- `Professional, scientific and technical activities`: Professional services
- `Administrative and support service activities`: Support services
- `Public administration and defence; compulsory social insurance`: Government
- `Education services`: Education
- `Human health and social work activities`: Healthcare
- `Arts, entertainment and recreation`: Culture
- `Other service activities`: Other services
- `Taxes less subsidies on products`: Net taxes

### Year (Он)
Years from 1990 to 2025 (36 data points)

## Update Instructions

### Check for Updates

1. Query the table listing endpoint:
   ```
   GET https://data.1212.mn/api/v1/en/NSO/Economy, environment/National Accounts/
   ```

2. Find `DT_NSO_0500_001V1.px` in the response

3. Compare the `updated` field with `source_updated_at` in registry

4. If API's `updated` is newer, dataset needs updating

### Fetch Data

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_0500_001V1.px --output /tmp/gdp
```

### Validation

- GDP values should be positive for absolute measures
- Growth rates can be negative
- Total should approximately equal sum of all sectors
- Year values should be valid years (1990-2024)

## Splits

This multi-dimensional dataset is split into the following user-friendly datasets:

### 1. gdp-nominal

- **ID**: `gdp-nominal`
- **Title EN**: Mongolia GDP at Current Prices (1990-2025)
- **Title MN**: Монгол Улсын ДНБ өнөөгийн үнээр (1990-2025)
- **Filter**:
  - Indicator: GDP, at current prices
  - Economic activity: Total
- **Chart Type**: area
- **Chart Config**:
  - X-axis: year (Он)
  - Y-axis: value (GDP in million MNT)
  - Color: #4c78a8 (blue)
- **Description EN**: Mongolia's nominal GDP from 1990 to present, showing overall economic growth in monetary terms.
- **Description MN**: Монгол Улсын нэрлэсэн ДНБ 1990 оноос өнөөг хүртэл.

### 2. gdp-real

- **ID**: `gdp-real`
- **Title EN**: Mongolia Real GDP at 2015 Prices (1990-2025)
- **Title MN**: Монгол Улсын бодит ДНБ 2015 оны үнээр (1990-2025)
- **Filter**:
  - Indicator: GDP, at 2015 constant prices
  - Economic activity: Total
- **Chart Type**: area
- **Chart Config**:
  - X-axis: year (Он)
  - Y-axis: value (GDP in million MNT at 2015 prices)
  - Color: #4c78a8 (blue)
- **Description EN**: Mongolia's real GDP adjusted for inflation, showing true economic growth.
- **Description MN**: Монгол Улсын бодит ДНБ, инфляцид тохируулсан.

### 3. gdp-usd

- **ID**: `gdp-usd`
- **Title EN**: Mongolia GDP in US Dollars (1990-2025)
- **Title MN**: Монгол Улсын ДНБ ам.доллараар (1990-2025)
- **Filter**:
  - Indicator: GDP, at current price, thousand USD
  - Economic activity: Total
- **Chart Type**: area
- **Chart Config**:
  - X-axis: year (Он)
  - Y-axis: value (GDP in thousand USD)
  - Color: #4c78a8 (blue)
- **Description EN**: Mongolia's GDP measured in US dollars for international comparison.
- **Description MN**: Монгол Улсын ДНБ олон улсын харьцуулалтад зориулан ам.доллараар.

### 4. gdp-growth-rate

- **ID**: `gdp-growth-rate`
- **Title EN**: Mongolia GDP Growth Rate (1991-2025)
- **Title MN**: Монгол Улсын ДНБ-ий өсөлтийн хувь (1991-2025)
- **Filter**:
  - Indicator: Annual changes, by percent
  - Economic activity: Total
- **Chart Type**: bar (positive/negative)
- **Chart Config**:
  - X-axis: year (Он)
  - Y-axis: value (% change)
  - Color: Conditional (green for positive, red for negative)
- **Description EN**: Year-over-year GDP growth rate showing economic expansion and contraction.
- **Description MN**: Жилийн ДНБ-ий өсөлт буурлыг харуулсан.

### 5. gdp-by-sector

- **ID**: `gdp-by-sector`
- **Title EN**: Mongolia GDP by Economic Sector (2025)
- **Title MN**: Монгол Улсын ДНБ эдийн засгийн салбараар (2025)
- **Filter**:
  - Indicator: GDP, at current prices
  - Year: 2025
  - Economic activity: NOT Total (all individual sectors)
- **Chart Type**: horizontal-bar
- **Chart Config**:
  - Y-axis: economic_activity (sector name)
  - X-axis: value (GDP contribution)
  - Color: #4c78a8
  - Sort: descending by value
- **Description EN**: Breakdown of Mongolia's GDP by economic sector in the latest year.
- **Description MN**: Монгол Улсын ДНБ-ий эдийн засгийн салбар бүрээр хуваарилалт.

### 6. gdp-sector-trends

- **ID**: `gdp-sector-trends`
- **Title EN**: Mongolia GDP by Major Sectors Over Time (1990-2025)
- **Title MN**: Монгол Улсын ДНБ үндсэн салбаруудаар (1990-2025)
- **Filter**:
  - Indicator: GDP, at current prices
  - Economic activity: Top 6 sectors (Mining, Agriculture, Trade, Manufacturing, Construction, Transport)
- **Chart Type**: multi-line
- **Chart Config**:
  - X-axis: year (Он)
  - Y-axis: value (GDP in million MNT)
  - Color: by sector
- **Description EN**: How major economic sectors have grown over time.
- **Description MN**: Эдийн засгийн үндсэн салбаруудын өсөлтийн динамик.

## Content Generation

### Key Findings Template

For each split, auto-extract:
- Latest values
- Historical comparison (growth rate)
- Notable patterns

### Common Tags
- mongolia
- gdp
- economy
- national-accounts
- nso

## Notes

- 1990-1995 shows significant economic transition effects (Soviet collapse)
- Mining sector became dominant after 2000 due to commodity boom
- 2020 shows COVID-19 impact
- **Parent dataset**: This dataset (`nso-gdp-by-economic-activity`) stores the raw data; only the splits are published to data.mn
