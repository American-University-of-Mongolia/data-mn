# Dataset: Weekly Mutton Prices by Region in Mongolia

## Identification

- **ID**: `weekly-mutton-prices-aimags`
- **Source**: `nso-1212`
- **Parent Dataset**: `nso-weekly-prices-main-products`
- **Category**: Economy
- **Tags**: [mutton, meat, prices, weekly, regional, aimags, mongolia]
- **Concept ID**: `weekly-prices`

## Source Reference

- **Parent Table ID**: `DT_NSO_0300_010V5.px`
- **Sector**: `Economy, environment`
- **Subsector**: `Consumer Price Index`
- **API Path**: `/en/NSO/Economy, environment/Consumer Price Index/DT_NSO_0300_010V5.px`

## Title

- **EN**: Weekly Mutton Prices by Region in Mongolia (2024-2025)
- **MN**: Хонины махны долоо хоногийн үнэ, бүсээр (2024-2025)

## Description

- **EN**: Weekly mutton prices across Mongolia's four regions (Central, Eastern, Western, Khangai), showing regional price variations for bone-in mutton per kilogram.
- **MN**: Монгол Улсын дөрвөн бүсийн хонины махны (ястай) долоо хоног тутмын үнийн хэлбэлзэл, килограммаар.

**Chart Strategy**: The embedded chart is a choropleth map showing all 21 aimags for the latest week. The 4-aimag time-series chart (Darkhan-Uul, Khovd, Orkhon, Umnugovi) is retained but NOT embedded. Full download files contain all 21 aimags plus 4 regional aggregates (Central, Eastern, Western, Khangai).

## Coverage

| Dimension | Value |
|-----------|-------|
| **Geographic** | 21 aimags, latest week (map) / 21 aimags + 4 regions (download) |
| **Granularity** | aimag |
| **Time Start** | 2024-01 |
| **Frequency** | weekly |
| **Product** | Mutton (bone-in, kg) |

**⚠️ Coverage Limitation**: This dataset does NOT include Ulaanbaatar prices.

## Split Filter

This is a split from the parent dataset `nso-weekly-prices-main-products`:

```json
{
  "product": "Mutton, kg"
}
```

## Variables

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
Weekly dates from 2024-01-02 to present

### Value (Price)
- **EN**: Price (MNT/kg)
- **MN**: Үнэ (төг/кг)
- Format: Positive decimal numbers

## Chart Configuration

The page embeds TWO charts: the historical time series first, then the
choropleth map (see `datamn-chart-vega` skill, section 6). Both MUST be
regenerated on every update.

### Embedded 1: Time series (4 selected aimags)
Multi-line chart (Darkhan-Uul, Khovd, Orkhon, Umnugovi) from January 2024
to present, drawn from the 4-aimag chart-subset CSVs.

- **Files**: `weekly-mutton-prices-aimags-trend-en.json` / `-trend-mn.json`
- **MDX**: first embed, with the trend caption from the MDX files

### Embedded 2: Choropleth map (latest week)
Geoshape map of all 21 aimags, colored by latest-week price.
Exempt from the max-6-categories rule (maps show all regions by design).

- **Files**: `weekly-mutton-prices-aimags-en.json` / `-mn.json`
  (slug-named on purpose — listing thumbnails derive from the slug)
- **Boundaries**: `/maps/mongolia-aimags.json` (static file, do NOT regenerate)
- **Data**: `-latest-en.csv` / `-latest-mn.csv` via `lookup` join
  (EN: `properties.name` ↔ `name`; MN: `properties.name_mn` ↔ `бүс`)
- **Color**: price/үнэ (quantitative, `oranges` scheme)
- **Tooltip**: aimag name + price (,.0f)
- **MDX**: second embed. The map TITLE carries the snapshot date
  (EN: "Week of {Month D, YYYY}"; MN: "{YYYY} оны {M}-р сарын {D}").
  Bump the date on every update — it must always match the `-latest` CSVs.

## Update Instructions

This is a split dataset. Updates are triggered automatically when the parent dataset (`nso-weekly-prices-main-products`) is updated.

### Manual Update Process

If updating independently:

1. Load parent data from `tools/versions/nso-weekly-prices-main-products/v{N}/data-en.csv`
2. Filter to rows where `product == "Mutton, kg"`
3. For chart CSV: Select 4 regional aggregates only
4. For download CSV: Include all 25 regions
5. Export bilingual files (`-en.csv` and `-mn.csv`)
6. Regenerate chart JSON files

### Transformation (latest-week snapshot for the choropleth map)

```python
# Latest-week snapshot for the choropleth map (max date only)
latest_date = df["date"].max()
latest_df = df[df["date"] == latest_date][["region", "price"]].copy()
latest_df = latest_df.rename(columns={"region": "name"})
latest_df.sort_values("name").to_csv(
    "data/data.mn/public/datasets/weekly-mutton-prices-aimags-latest-en.csv", index=False)

# Mongolian latest-week snapshot, derived from the translated MN data
# (key column values must match map `name_mn`)
latest_date_mn = df_mn["огноо"].max()
latest_df_mn = df_mn[df_mn["огноо"] == latest_date_mn][["бүс", "үнэ"]].copy()
latest_df_mn.sort_values("бүс").to_csv(
    "data/data.mn/public/datasets/weekly-mutton-prices-aimags-latest-mn.csv",
    index=False, lineterminator="\r\n")
```

### Validation

- All price values should be positive numbers
- Time values should be valid weekly dates (Mondays)
- Missing values are acceptable (seasonal availability)
- Regional aggregates should always have values (they are averages)
- Latest-week snapshot must have exactly 21 rows (all aimags, max date only)
- Every `name`/`бүс` in the latest-week snapshots must match a
  `name`/`name_mn` property in `data.mn/public/maps/mongolia-aimags.json`
- Both chart specs must pass `validate_vega.py` (time series AND map)

## Content Generation

### Excerpt Template

**EN**: "Mutton prices in Mongolia averaged {avg_price} MNT/kg in {latest_date}, ranging from {min_price} in {min_region} to {max_price} in {max_region}."

**MN**: "{latest_date}-д Монгол Улсын хонины махны дундаж үнэ {avg_price} төг/кг байсан бөгөөд {min_region}-д {min_price}, {max_region}-д {max_price} байв."

### Key Statistics to Calculate

- Latest average price (across 4 regions)
- Price range (min to max)
- Highest and lowest price regions
- Week-over-week price change (%)
- Year-over-year change (if available)

### Keywords

**EN**: `mongolia mutton prices weekly regional meat livestock`

**MN**: `монгол улс хонины мах үнэ долоо хоногийн бүсээр`

## Notes

- Mutton is a staple meat in Mongolia (traditionally more common than beef)
- Prices vary significantly by region due to livestock density
- Seasonal patterns expected (higher supply in autumn after slaughter season)
- Regional aggregates smooth out local variations
- Chart shows 4 regions for readability; full 25-region data in downloads
