# Dataset: Weekly Fresh Milk Prices by Region (Split from Weekly Prices Aimags)

## Identification

- **ID**: `weekly-milk-prices-aimags`
- **Source**: `nso-1212`
- **Category**: Economy
- **Tags**: [prices, milk, dairy, food, regional, weekly, aimags, inflation]
- **Concept ID**: `weekly-prices`

## Parent Dataset

- **Parent ID**: `nso-weekly-prices-main-products`
- **Parent Table**: `DT_NSO_0300_010V5.px`
- **Parent Definition**: `tools/sources/nso-1212/datasets/weekly-prices-aimags.md`

## Source Reference

- **Table ID**: `DT_NSO_0300_010V5.px`
- **Sector**: `Economy, environment`
- **Subsector**: `Consumer Price Index`
- **API Path**: `/en/NSO/Economy, environment/Consumer Price Index/DT_NSO_0300_010V5.px`

## Title

- **EN**: Weekly Fresh Milk Prices by Region in Mongolia (2024-2025)
- **MN**: Сүүний долоо хоногийн үнэ, бүсээр (2024-2025)

## Description

Weekly price monitoring data for fresh, unpasteurized milk (per liter) across all 21 aimags (provinces) and 4 regional aggregates (Central, Eastern, Western, Khangai) of Mongolia. Data is collected weekly since January 2024 as part of the National Statistics Office's consumer price monitoring program.

**Note**: This dataset does NOT include Ulaanbaatar prices. For capital city milk prices, refer to the related Ulaanbaatar dataset when available.

## Split Filter

```json
{
  "product": "Milk, fresh, not pasteurised, l"
}
```

This filter extracts only the fresh milk price data from the full weekly prices dataset containing 11 products.

## Variables

### Product (Бүтээгдэхүүн)
- `Milk, fresh, not pasteurised, l` (MN: `Сүү, үнээний, задгай, л`)

### Region (Бүс)
| EN | MN |
|----|-----|
| Arkhangai | Архангай |
| Bayan-Ulgii | Баян-Өлгий |
| Bayankhongor | Баянхонгор |
| Bulgan | Булган |
| Darkhan-Uul | Дархан-Уул |
| Dornod | Дорнод |
| Dornogovi | Дорноговь |
| Dundgovi | Дундговь |
| Govi-Altai | Говь-Алтай |
| Govisumber | Говьсүмбэр |
| Khentii | Хэнтий |
| Khovd | Ховд |
| Khuvsgul | Хөвсгөл |
| Orkhon | Орхон |
| Selenge | Сэлэнгэ |
| Sukhbaatar | Сүхбаатар |
| Tuv | Төв |
| Umnugovi | Өмнөговь |
| Uvs | Увс |
| Uvurkhangai | Өвөрхангай |
| Zavkhan | Завхан |
| Central region | Төвийн бүс |
| Eastern region | Зүүн бүс |
| Western region | Баруун бүс |
| Khangai region | Хангайн бүс |

### Time (Хугацаа)
Weekly dates from 2024-01-02 to present (97+ time periods)

## Data Characteristics

- **Values**: In Mongolian Tugrik (MNT) per liter
- **Frequency**: Weekly
- **Seasonality**: Strong seasonal pattern - milk production peaks in summer months (June-September)
- **Regional Variation**: Significant price differences between aimags based on local production and transportation costs
- **Missing Values**: Acceptable - some regions may have limited fresh milk availability, especially in winter

## Coverage

| Dimension | Value |
|-----------|-------|
| **Geographic** | 21 aimags + 4 regional aggregates |
| **Granularity** | aimag |
| **Time Start** | 2024-01 |
| **Frequency** | weekly |

**⚠️ Coverage Limitation**: This dataset does NOT include Ulaanbaatar prices.

## Chart Specification

- **Chart Type**: Multi-line chart
- **Chart Config**:
  - X-axis: date (weekly, temporal)
  - Y-axis: price (MNT/l, quantitative)
  - Color: region (nominal)
    - **For chart visualization**: Show only 4 regional aggregates (Central, Eastern, Western, Khangai)
    - **For downloads**: Include all 21 aimags + 4 regional aggregates
  - Color scale:
    - Central region: `#4c78a8` (primary blue)
    - Eastern region: `#f58518` (secondary orange)
    - Western region: `#e45756` (tertiary red)
    - Khangai region: `#72b7b2` (quaternary teal)
  - Interpolation: monotone (smooth line)
  - Tooltip: Date, region name, price with "MNT/l" suffix

## Key Findings Template

For content generation, calculate:
- Latest week average price across all regions
- Price range (minimum and maximum region)
- Regional price leaders (highest/lowest)
- Week-over-week change
- Seasonal trends (summer vs winter pricing)
- Regional disparities (standard deviation or coefficient of variation)

## Update Instructions

### Check for Updates

This is a split dataset. Updates come from the parent dataset `nso-weekly-prices-main-products`.

1. Check parent dataset for updates using registry:
   ```bash
   cd tools && python -m registry info nso-weekly-prices-main-products
   ```

2. If parent has updates, re-run the split transformation

### Regenerate Split

```bash
cd tools
python -m registry info weekly-milk-prices-aimags  # Check current version
# Parent update will trigger automatic regeneration of this split
```

### Validation

- All prices should be positive numbers (MNT/l)
- Typical price range: 1,500 - 3,500 MNT/l (based on historical data)
- Missing values are acceptable for some regions/weeks
- Check for data quality issues:
  - Unrealistic price spikes or drops (>50% change week-over-week without explanation)
  - Zero or negative values (data entry errors)
  - Consistent missing data for specific regions (may indicate structural issue)

## Related Datasets

| Dataset | Coverage | Table ID | Status |
|---------|----------|----------|--------|
| `weekly-prices-ulaanbaatar` | Ulaanbaatar only | DT_NSO_0600_001V4.px | Not yet added |
| `weekly-beef-prices-aimags` | Beef prices (same parent) | DT_NSO_0300_010V5.px | Active |
| `weekly-mutton-prices-aimags` | Mutton prices (same parent) | DT_NSO_0300_010V5.px | Active |
| `weekly-flour-prices-aimags` | Flour prices (same parent) | DT_NSO_0300_010V5.px | Active |
| `weekly-gasoline-prices-aimags` | A-92 petrol (same parent) | DT_NSO_0300_010V5.px | Active |
| `weekly-diesel-prices-aimags` | Diesel fuel (same parent) | DT_NSO_0300_010V5.px | Active |

## Excerpt Templates

**EN**: "Fresh milk prices in Mongolia averaged {avg_price} MNT/l in week {latest_date}, ranging from {min_price} MNT/l in {min_region} to {max_price} MNT/l in {max_region}."

**MN**: "{latest_date}-ийн долоо хоногт Монгол Улсын сүүний дундаж үнэ {avg_price} төг/л байсан бөгөөд {min_region}-д {min_price} төг/л, {max_region}-д {max_price} төг/л байв."

## Notes

- **Seasonal patterns**: Summer months typically see lower prices due to higher production
- **Regional variations**: Pastoral regions may have lower prices due to local supply
- **Urban vs Rural**: Urban aimags (Darkhan-Uul, Orkhon) may have higher prices due to processing/distribution costs
- **Quality note**: "Fresh, not pasteurised" refers to raw milk sold directly from producers or local markets
- **Data Source**: Derived from parent dataset `nso-weekly-prices-main-products`
- **Parent dataset**: The parent stores the raw data; only the splits are published to data.mn
- **Chart subset strategy**: Visualizations show 4 regional aggregates for clarity; full aimag-level data available in downloads
