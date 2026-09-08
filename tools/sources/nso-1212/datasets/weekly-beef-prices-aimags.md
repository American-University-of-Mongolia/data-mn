# Dataset: Weekly Beef Prices by Region in Mongolia

## Identification

- **ID**: `weekly-beef-prices-aimags`
- **Source**: `nso-1212`
- **Parent**: `nso-weekly-prices-aimags`
- **Category**: Economy
- **Tags**: [prices, beef, meat, food, weekly, regional, aimags, mongolia]
- **Concept ID**: `weekly-prices`

## Source Reference

- **Parent Table ID**: `DT_NSO_0300_010V5.px`
- **Sector**: `Economy, environment`
- **Subsector**: `Consumer Price Index`
- **API Path**: `/en/NSO/Economy, environment/Consumer Price Index/DT_NSO_0300_010V5.px`

## Title

- **EN**: Weekly Beef Prices by Region in Mongolia (2024-2025)
- **MN**: Үхрийн махны долоо хоногийн үнэ, бүсээр (2024-2025)

## Coverage

| Dimension | Value |
|-----------|-------|
| **Geographic** | 20 aimags, latest week (map; Umnugovi n/a in latest week) / 21 aimags + 4 regions (download) |
| **Granularity** | aimag |
| **Time Start** | 2024-01 |
| **Frequency** | weekly |
| **Products** | Beef only |

**⚠️ Coverage Limitation**: This dataset does NOT include Ulaanbaatar prices. See related dataset `weekly-beef-prices-ulaanbaatar` for UB data.

### Related Datasets

| Dataset | Coverage | Status |
|---------|----------|--------|
| `weekly-prices-aimags` | All products, all regions | Parent dataset |
| `weekly-beef-prices-ulaanbaatar` | Beef prices in UB | Not yet added |

## Description

Weekly beef prices (per kilogram, with bone) across Mongolia's four major regions: Central, Eastern, Western, and Khangai. This split dataset provides a focused view of beef price variations across regions, making it easy to compare regional price differences and track trends. Data is collected weekly since January 2024.

**Note**: This is a split from the parent dataset `nso-weekly-prices-aimags` which contains all 11 products. Ulaanbaatar prices are available in a separate NSO table (DT_NSO_0600_001V4.px).

**Chart Strategy**: The embedded chart is a choropleth map showing all 21 aimags for the latest week. The 4-aimag time-series chart (Darkhan-Uul, Khovd, Orkhon, Umnugovi) is retained but NOT embedded. Full download files contain all 21 aimags plus 4 regional aggregates (Central, Eastern, Western, Khangai).

## Split Filter

This dataset is created by filtering the parent dataset:

```json
{
  "Products": "Beef, kg"
}
```

**Translated filter (MN)**:
```json
{
  "Бүтээгдэхүүн": "Үхрийн мах, ястай, кг"
}
```

## Variables

### Region (Бүс)
Chart displays only 4 regional aggregates for clarity:

| EN | MN |
|----|-----|
| Central region | Төвийн бүс |
| Eastern region | Зүүн бүс |
| Western region | Баруун бүс |
| Khangai region | Хангайн бүс |

**Note**: Full download CSV includes all 21 individual aimags plus these 4 regional aggregates (25 total regions).

### Time (Хугацаа)
Weekly dates from 2024-01-02 to present (97+ time periods)

### Price (Үнэ)
Price in MNT per kilogram

## Chart Configuration

The page embeds TWO charts: the historical time series first, then the
choropleth map (see `datamn-chart-vega` skill, section 6). Both MUST be
regenerated on every update.

### Embedded 1: Time series (4 selected aimags)
Multi-line chart (Darkhan-Uul, Khovd, Orkhon, Umnugovi) from January 2024
to present, drawn from the 4-aimag chart-subset CSVs.

- **Files**: `weekly-beef-prices-aimags-trend-en.json` / `-trend-mn.json`
- **MDX**: first embed, with the trend caption from the MDX files

### Embedded 2: Choropleth map (latest week)
Geoshape map of all 21 aimags, colored by latest-week price.
Exempt from the max-6-categories rule (maps show all regions by design).

- **Files**: `weekly-beef-prices-aimags-en.json` / `-mn.json`
  (slug-named on purpose — listing thumbnails derive from the slug)
- **Boundaries**: `/maps/mongolia-aimags.json` (static file, do NOT regenerate)
- **Data**: `-latest-en.csv` / `-latest-mn.csv` via `lookup` join
  (EN: `properties.name` ↔ `name`; MN: `properties.name_mn` ↔ `бүс`)
- **Color**: price/үнэ (quantitative, `oranges` scheme)
- **Tooltip**: aimag name + price (,.0f)
- **MDX**: second embed. The map TITLE carries the snapshot date
  (EN: "Week of {Month D, YYYY}"; MN: "{YYYY} оны {M}-р сарын {D}").
  Bump the date on every update — it must always match the `-latest` CSVs.

## Data Export Strategy

**CRITICAL**: Chart data vs download data have different content!

### Chart CSV (`weekly-beef-prices-aimags-{lang}.csv`)
- **Subset**: 4 regional aggregates only
- **Purpose**: Optimized for chart visualization
- **Format**: Long form (date, region, price)
- **Rows**: ~400 (97 weeks × 4 regions)

### Download CSV (`weekly-beef-prices-aimags-all-{lang}.csv`)
- **Complete**: All 21 aimags + 4 regional aggregates
- **Purpose**: Full data for analysis
- **Format**: Long form (date, region, price)
- **Rows**: ~2,500 (97 weeks × 25 regions)

### Download XLSX (`weekly-beef-prices-aimags.xlsx`)
- **Complete**: All 25 regions
- **Purpose**: Excel users
- **Format**: Wide/pivot (rows=dates, columns=regions)
- **Columns**: date + 25 region columns

## Update Instructions

This split dataset is updated automatically when the parent dataset (`nso-weekly-prices-aimags`) is updated.

### Manual Update Process

If needed, update manually:

1. **Fetch parent data**: See parent dataset update instructions
2. **Filter data**:
   ```python
   import pandas as pd

   # Load parent data
   df = pd.read_csv("path/to/parent-data.csv")

   # Apply filter
   df_beef = df[df["Products"] == "Beef, kg"].copy()

   # Strip whitespace from all string columns (CRITICAL!)
   for col in df_beef.select_dtypes(include=['object']).columns:
       df_beef[col] = df_beef[col].astype(str).str.strip()
   ```

3. **Create chart subset**:
   ```python
   # Chart CSV: 4 regional aggregates only
   regional_aggregates = [
       "Central region", "Eastern region",
       "Western region", "Khangai region"
   ]
   chart_df = df_beef[df_beef["region"].isin(regional_aggregates)].copy()
   ```

4. **Export files**:
   - Chart CSVs (EN/MN with 4 regions)
   - Download CSVs (EN/MN with all 25 regions)
   - Download XLSX (wide format with all 25 regions)

5. **Regenerate chart**: Update Vega-Lite spec if needed
6. **Update MDX**: Refresh statistics in frontmatter

### Transformation (latest-week snapshot for the choropleth map)

```python
# Latest-week snapshot for the choropleth map (max date only)
latest_date = df["date"].max()
latest_df = df[df["date"] == latest_date][["region", "price"]].copy()
latest_df = latest_df.rename(columns={"region": "name"})
latest_df.sort_values("name").to_csv(
    "data/data.mn/public/datasets/weekly-beef-prices-aimags-latest-en.csv", index=False)

# Mongolian latest-week snapshot, derived from the translated MN data
# (key column values must match map `name_mn`)
latest_date_mn = df_mn["огноо"].max()
latest_df_mn = df_mn[df_mn["огноо"] == latest_date_mn][["бүс", "үнэ"]].copy()
latest_df_mn.sort_values("бүс").to_csv(
    "data/data.mn/public/datasets/weekly-beef-prices-aimags-latest-mn.csv",
    index=False, lineterminator="\r\n")
```

### Validation

- All price values should be positive numbers
- Regional aggregate names must match exactly (whitespace matters!)
- Dates should be valid Mondays (weekly period starts)
- Missing values are acceptable (some regions may have gaps)
- Latest-week snapshot must have exactly 21 rows (all aimags, max date only)
  — currently 20: Umnugovi has no source data since 2025-04-07
- Every `name`/`бүс` in the latest-week snapshots must match a
  `name`/`name_mn` property in `data.mn/public/maps/mongolia-aimags.json`
- Both chart specs must pass `validate_vega.py` (time series AND map)

## Content Generation

### Key Findings Template

Auto-extract for MDX excerpt:
- Latest average price across regions
- Price range (min/max region and values)
- Price change vs previous week
- Year-over-year comparison (if available)

### Example Excerpt

**EN**: "Beef prices in Mongolia averaged {avg_price} MNT/kg in {latest_date}, ranging from {min_price} in {min_region} to {max_price} in {max_region}."

**MN**: "{latest_date}-д Монгол Улсын үхрийн махны дундаж үнэ {avg_price} төг/кг байсан бөгөөд {min_region}-д {min_price}, {max_region}-д {max_price} байв."

### Common Tags
- mongolia
- prices
- beef
- meat
- food
- weekly
- regional
- cpi
- inflation

### Keywords (EN)
- "Mongolia beef prices"
- "weekly meat prices"
- "regional food prices"
- "beef price trends"
- "consumer price index"

## Notes

- Weekly data provides high-frequency price monitoring
- Regional aggregates smooth out individual aimag volatility
- Individual aimag data available in full download for detailed analysis
- Beef is one of the most important food items in Mongolian diet
- Prices show seasonal patterns and regional variations due to transportation costs
- **Ulaanbaatar data is in a separate NSO table** - not included here
- Parent dataset: `nso-weekly-prices-aimags` stores the raw multi-product data
- This split is published to data.mn as a standalone dataset with its own URL
