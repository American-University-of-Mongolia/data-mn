# Dataset: GDP by Major Sectors - Trends Over Time

## Identification

- **ID**: `gdp-sector-trends`
- **Source**: `nso-1212`
- **Category**: Economy
- **Tags**: [gdp, economy, sectors, trends, mining, agriculture, trade, manufacturing]

## Source Reference

- **Table ID**: `DT_NSO_0500_001V1.px`
- **Sector**: `Economy, environment`
- **Subsector**: `National Accounts`
- **API Path**: `/en/NSO/Economy, environment/National Accounts/DT_NSO_0500_001V1.px`

## Parent Dataset

- **Parent ID**: `nso-gdp-by-economic-activity`
- **Parent Definition**: `sources/nso-1212/datasets/gdp-by-economic-activity.md`

## Title

- **EN**: Mongolia GDP by Major Sectors Over Time (1990-2024)
- **MN**: Монгол Улсын ДНБ үндсэн салбаруудаар (1990-2024)

## Description

This is a **split dataset** from the parent `nso-gdp-by-economic-activity` dataset. It shows GDP trends for the six major economic sectors of Mongolia from 1990 to 2024, providing a clear view of structural economic changes over time. The data highlights Mongolia's economic transformation, particularly the rise of the mining sector and shifts in the relative importance of traditional sectors like agriculture.

## Split Filter

```json
{
  "Indicator": "GDP, at current prices",
  "Economic activity": [
    "Mining and quarrying",
    "Agriculture, forestry, fishing and hunting",
    "Wholesale and retail trade; repair of motor vehicles and motorcycles",
    "Manufacturing",
    "Construction",
    "Transportation and storage"
  ]
}
```

## Variables

### Sector (Economic Activity)
Selected major sectors that provide a comprehensive view of Mongolia's economy:

- **Mining and quarrying** (Уул уурхай, олборлолт): Mongolia's dominant economic sector, includes coal, copper, gold, and other minerals
- **Agriculture, forestry, fishing and hunting** (Хөдөө аж ахуй, ой, ан агнуур, загас барилт): Traditional sector, includes livestock herding and crop farming
- **Wholesale and retail trade; repair of motor vehicles and motorcycles** (Бөөний болон жижиглэнгийн худалдаа): Trade and commerce sector
- **Manufacturing** (Үйлдвэрлэл): Industrial manufacturing and processing
- **Construction** (Барилга): Building and infrastructure development
- **Transportation and storage** (Тээвэр, агуулахын үйл ажиллагаа): Logistics and transportation services

### Year (Он)
Years from 1990 to 2024 (35 data points)

### Value
GDP contribution in million MNT at current prices

## Chart Type

**Multi-line chart** showing GDP trends by sector over time

**Chart Config**:
- X-axis: year (Он) - quantitative
- Y-axis: value (GDP in million MNT) - quantitative
- Color: by sector (6 distinct colors from brand palette)
- Interpolate: monotone (smooth lines)
- Hover: nearest point with tooltip showing year, sector, and value

## Key Insights

### Economic Transformation Highlights

1. **Mining Boom**: Mining sector grew from 1.6 billion MNT (1990) to 22 trillion MNT (2024) - approximately 13,750x growth
2. **Agriculture Decline (Relative)**: Agriculture was the largest sector in 1990 but was overtaken by mining around 2003-2004
3. **Trade Growth**: Wholesale/retail trade has grown steadily, becoming the third-largest sector
4. **Manufacturing**: Remained relatively stable but declined in relative importance
5. **Construction**: Shows cyclical patterns tied to mining investment booms
6. **Transport**: Grew alongside mining and trade activities

### Historical Context

- **1990-1995**: Economic transition from Soviet-era planned economy
- **2000-2010**: Mining sector emergence and rapid growth
- **2010-2014**: Mining boom peak period
- **2015-2016**: Commodity price crash impact
- **2017-2024**: Recovery and continued mining dominance

## Update Instructions

### Data Source

This split dataset is **derived from the parent** `nso-gdp-by-economic-activity` dataset. It does not require separate API fetching.

### Update Process

1. **Check parent dataset** for updates:
   ```bash
   cd tools && python -m registry info nso-gdp-by-economic-activity
   ```

2. **When parent updates**, this split will be automatically regenerated with the same filter applied

3. **Manual regeneration** (if needed):
   ```python
   import pandas as pd

   # Load parent data
   parent_df = pd.read_csv('tools/versions/nso-gdp-by-economic-activity/v1/data-en.csv')

   # Apply filter
   filtered_df = parent_df[
       (parent_df['indicator'] == 'GDP, at current prices') &
       (parent_df['economic_activity'].isin([
           'Mining and quarrying',
           'Agriculture, forestry, fishing and hunting',
           'Wholesale and retail trade; repair of motor vehicles and motorcycles',
           'Manufacturing',
           'Construction',
           'Transportation and storage'
       ]))
   ].copy()

   # Export to public datasets
   filtered_df[['economic_activity', 'year', 'value']].to_csv(
       'data.mn/public/datasets/gdp-sector-trends-en.csv',
       index=False
   )
   ```

### Validation

- All GDP values should be positive
- Six sectors should have consistent data across all years
- Year range should be 1990-2024
- Values should show general upward trend (inflation-adjusted growth)
- Mining sector should show dramatic growth from 1990s to 2020s

## Content Generation

### Key Findings

Auto-extracted statistics for the MDX page:

- **Latest year values** for each sector
- **Growth rates** since 1990 for each sector
- **Ranking changes** over time (which sectors overtook others)
- **Inflection points** (when mining overtook agriculture)

### Tags

- mongolia
- gdp
- economy
- sectors
- mining
- agriculture
- trade
- manufacturing
- construction
- transport
- trends
- nso

### Excerpt Template

**EN**: "Mongolia's mining sector experienced explosive growth from 1.6 billion MNT in 1990 to 22 trillion MNT in 2024, overtaking agriculture as the dominant economic sector after 2000."

**MN**: "Монгол Улсын уул уурхайн салбар 1990 онд 1.6 тэрбум төгрөгөөс 2024 онд 22 их наяд төгрөг болж өссөн бөгөөд 2000 оноос хойш хөдөө аж ахуйг гүйцэж эдийн засгийн тэргүүлэх салбар болсон."

## Notes

- This split focuses on the **top 6 sectors** to make the chart readable and user-friendly
- The parent dataset contains **19 economic activity categories** - too many for a clear trend visualization
- Selected sectors represent approximately **70-80%** of total GDP
- Chart uses Statista-style multi-line format for comparing trends
- **Version history** is maintained through the parent dataset; this split inherits version numbers
