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

**Chart Strategy**: The embedded chart is a choropleth map showing all 21 aimags for the latest week. The 4-aimag time-series chart (Darkhan-Uul, Khovd, Orkhon, Umnugovi) is retained but NOT embedded. Full download files contain all 21 aimags plus 4 regional aggregates (Central, Eastern, Western, Khangai).

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
| **Geographic** | 21 aimags, latest week (map) / 21 aimags + 4 regions (download) |
| **Granularity** | aimag |
| **Time Start** | 2024-01 |
| **Frequency** | weekly |

**⚠️ Coverage Limitation**: This dataset does NOT include Ulaanbaatar prices.

## Chart Specification

The page embeds TWO charts: the historical time series first, then the
choropleth map (see `datamn-chart-vega` skill, section 6). Both MUST be
regenerated on every update.

### Embedded 1: Time series (4 selected aimags)
Multi-line chart (Darkhan-Uul, Khovd, Orkhon, Umnugovi) from January 2024
to present, drawn from the 4-aimag chart-subset CSVs.

- **Files**: `weekly-milk-prices-aimags-trend-en.json` / `-trend-mn.json`
- **MDX**: first embed, with the trend caption from the MDX files

### Embedded 2: Choropleth map (latest week)
Geoshape map of all 21 aimags, colored by latest-week price.
Exempt from the max-6-categories rule (maps show all regions by design).

- **Files**: `weekly-milk-prices-aimags-en.json` / `-mn.json`
  (slug-named on purpose — listing thumbnails derive from the slug)
- **Boundaries**: `/maps/mongolia-aimags.json` (static file, do NOT regenerate)
- **Data**: `-latest-en.csv` / `-latest-mn.csv` via `lookup` join
  (EN: `properties.name` ↔ `name`; MN: `properties.name_mn` ↔ `бүс`)
- **Color**: price/үнэ (quantitative, `oranges` scheme)
- **Tooltip**: aimag name + price (,.0f)
- **MDX**: second embed. The map TITLE carries the snapshot date
  (EN: "Week of {Month D, YYYY}"; MN: "{YYYY} оны {M}-р сарын {D}").
  Bump the date on every update — it must always match the `-latest` CSVs.

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

### Transformation (latest-week snapshot for the choropleth map)

```python
# Latest-week snapshot for the choropleth map (max date only)
latest_date = df["date"].max()
latest_df = df[df["date"] == latest_date][["region", "price"]].copy()
latest_df = latest_df.rename(columns={"region": "name"})
latest_df.sort_values("name").to_csv(
    "data/data.mn/public/datasets/weekly-milk-prices-aimags-latest-en.csv", index=False)

# Mongolian latest-week snapshot, derived from the translated MN data
# (key column values must match map `name_mn`)
latest_date_mn = df_mn["огноо"].max()
latest_df_mn = df_mn[df_mn["огноо"] == latest_date_mn][["бүс", "үнэ"]].copy()
latest_df_mn.sort_values("бүс").to_csv(
    "data/data.mn/public/datasets/weekly-milk-prices-aimags-latest-mn.csv",
    index=False, lineterminator="\r\n")
```

### Validation

- All prices should be positive numbers (MNT/l)
- Typical price range: 1,500 - 3,500 MNT/l (based on historical data)
- Missing values are acceptable for some regions/weeks
- Check for data quality issues:
  - Unrealistic price spikes or drops (>50% change week-over-week without explanation)
  - Zero or negative values (data entry errors)
  - Consistent missing data for specific regions (may indicate structural issue)
- Latest-week snapshot must have exactly 21 rows (all aimags, max date only)
- Every `name`/`бүс` in the latest-week snapshots must match a
  `name`/`name_mn` property in `data.mn/public/maps/mongolia-aimags.json`
- Both chart specs must pass `validate_vega.py` (time series AND map)

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
