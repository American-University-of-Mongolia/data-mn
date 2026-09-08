# Dataset: Weekly Gasoline (A-92) Prices by Region in Mongolia

## Identification

- **ID**: `weekly-gasoline-prices-aimags`
- **Parent ID**: `nso-weekly-prices-aimags`
- **Source**: `nso-1212`
- **Category**: Economy
- **Tags**: [gasoline, fuel, prices, regional, weekly, aimags, mongolia]
- **Concept ID**: `weekly-prices`

## Parent Reference

- **Parent Dataset**: `nso-weekly-prices-aimags`
- **Parent Table ID**: `DT_NSO_0300_010V5.px`
- **Split Filter**:
  ```json
  {
    "product": "Petrol, A-92, l"
  }
  ```

## Title

- **EN**: Weekly Gasoline (A-92) Prices by Region in Mongolia (2024-2025)
- **MN**: Аи-92 автобензиний долоо хоногийн үнэ, бүсээр (2024-2025)

## Coverage

| Dimension | Value |
|-----------|-------|
| **Geographic** | 21 aimags, latest week (map) / 21 aimags + 4 regions (download) |
| **Granularity** | aimag |
| **Time Start** | 2024-01 |
| **Frequency** | weekly |
| **Product** | Petrol A-92 only |

**⚠️ Coverage Limitation**: This dataset does NOT include Ulaanbaatar prices.

### Related Datasets

| Dataset | Coverage | Status |
|---------|----------|--------|
| `weekly-diesel-prices-aimags` | Diesel fuel prices | Active |
| `weekly-beef-prices-aimags` | Beef prices | Active |
| `weekly-mutton-prices-aimags` | Mutton prices | Active |
| `weekly-flour-prices-aimags` | Flour prices | Active |
| `weekly-milk-prices-aimags` | Milk prices | Active |

## Description

Weekly A-92 petrol (gasoline) prices across all 21 aimags (provinces) and 4 regional aggregates (Central, Eastern, Western, Khangai) of Mongolia. Data is collected weekly since January 2024. This dataset provides insight into regional fuel price variations and trends. **Note: Ulaanbaatar is not included in this dataset.**

A-92 is the most common gasoline grade used in Mongolia, making this a key indicator for transportation costs and inflation monitoring.

**Chart Strategy**: The embedded chart is a choropleth map showing all 21 aimags for the latest week. The 4-aimag time-series chart (Darkhan-Uul, Khovd, Orkhon, Umnugovi) is retained but NOT embedded. Full download files contain all 21 aimags plus 4 regional aggregates (Central, Eastern, Western, Khangai).

## Variables

### Product (Fixed)
- **EN**: Petrol, A-92, l
- **MN**: Аи-92 автобензин, л

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

## Chart Specification

The embedded chart is the CHOROPLETH MAP (see `datamn-chart-vega` skill,
section 6). It MUST be regenerated on every update.

### Embedded: Choropleth map (latest week)
Geoshape map of all 21 aimags, colored by latest-week price.
Exempt from the max-6-categories rule (maps show all regions by design).

- **Files**: `weekly-gasoline-prices-aimags-en.json` / `-mn.json`
  (slug-named on purpose — listing thumbnails derive from the slug)
- **Boundaries**: `/maps/mongolia-aimags.json` (static file, do NOT regenerate)
- **Data**: `-latest-en.csv` / `-latest-mn.csv` via `lookup` join
  (EN: `properties.name` ↔ `name`; MN: `properties.name_mn` ↔ `бүс`)
- **Color**: price/үнэ (quantitative, `oranges` scheme)
- **Tooltip**: aimag name + price (,.0f)
- **MDX**: single embed with the caption from the MDX files
  (do NOT hardcode the latest date in the caption — it must stay correct
  between updates)

### Hidden: Time series (NOT embedded)
The 4-aimag multi-line chart (`-trend-en.json` / `-trend-mn.json`) is
intentionally NOT embedded in the MDX. Keep its spec files and the 4-aimag
chart-subset CSVs in place (referenced by nothing, retained for now) —
but do NOT re-add the embed on update.

## Update Instructions

This is a split dataset. Updates are handled automatically when the parent dataset (`nso-weekly-prices-aimags`) is updated.

### Manual Update (if needed)

1. Update parent dataset first
2. Re-run split transformation with filter:
   ```python
   df = df[df['product'] == 'Petrol, A-92, l']
   ```
3. Regenerate charts and MDX pages

### Transformation (latest-week snapshot for the choropleth map)

```python
# Latest-week snapshot for the choropleth map (max date only).
# NOTE: the EN source file contains duplicate rows for some aimags at
# recent weeks (a stale frozen value plus the updated value); keep the
# LAST row per region, which matches the MN file.
latest_date = df["date"].max()
latest_df = df[df["date"] == latest_date].drop_duplicates(
    subset="region", keep="last")[["region", "price"]].copy()
latest_df = latest_df.rename(columns={"region": "name"})
latest_df.sort_values("name").to_csv(
    "data/data.mn/public/datasets/weekly-gasoline-prices-aimags-latest-en.csv", index=False)

# Mongolian latest-week snapshot, derived from the translated MN data
# (key column values must match map `name_mn`)
latest_date_mn = df_mn["огноо"].max()
latest_df_mn = df_mn[df_mn["огноо"] == latest_date_mn][["бүс", "үнэ"]].copy()
latest_df_mn.sort_values("бүс").to_csv(
    "data/data.mn/public/datasets/weekly-gasoline-prices-aimags-latest-mn.csv",
    index=False, lineterminator="\r\n")
```

### Validation

- All price values should be positive numbers (MNT per liter)
- Typical range: 2,000-4,000 MNT/l
- Time values should be valid weekly dates (Mondays)
- Missing values are acceptable (temporary supply issues)
- Latest-week snapshot must have exactly 21 rows (all aimags, max date only)
- Every `name`/`бүс` in the latest-week snapshots must match a
  `name`/`name_mn` property in `data.mn/public/maps/mongolia-aimags.json`
- Both chart specs must pass `validate_vega.py` (time series AND map)

## Content Generation

### Key Findings Template

Auto-extract from latest data:
- **Latest average price**: Mean across all regions
- **Price range**: Minimum and maximum region
- **Week-over-week change**: % change from previous week
- **Month-over-month change**: % change from 4 weeks ago
- **Regional variation**: Standard deviation or range

### Excerpt Template

**EN**: "A-92 petrol prices in Mongolia averaged {avg_price} MNT/l in the week of {latest_date}, ranging from {min_price} in {min_region} to {max_price} in {max_region}. Prices {increased/decreased/remained stable} by {change}% compared to the previous week."

**MN**: "{latest_date}-ны долоо хоногт Монгол Улсын Аи-92 автобензиний дундаж үнэ {avg_price} төг/л байсан бөгөөд {min_region}-д {min_price}, {max_region}-д {max_price} байв. Өмнөх долоо хоноготой харьцуулахад үнэ {change}%-иар {өссөн/буурсан/хэвийн}."

### Keywords

**EN**: gasoline prices Mongolia, A-92 petrol, fuel costs, regional prices, weekly prices, transportation costs, inflation, energy prices

**MN**: автобензин үнэ Монгол, Аи-92 бензин, түлшний үнэ, бүсчилсэн үнэ, долоо хоногийн үнэ, тээврийн зардал, инфляци, эрчим хүчний үнэ

### Common Tags
- mongolia
- gasoline
- petrol
- fuel
- prices
- weekly
- regional
- economy
- inflation

## Notes

- A-92 is the most widely available gasoline grade in Mongolia
- Prices typically vary due to:
  - Distance from fuel depots (Ulaanbaatar, border crossings)
  - Transportation costs
  - Local market competition
  - Seasonal demand (winter heating needs affecting diesel supply)
- Regional aggregates smooth out local variations and show broader geographic patterns
- **Full individual aimag data** available in download files for detailed analysis
- **This is a split dataset**: Parent data stored in `nso-weekly-prices-aimags`
