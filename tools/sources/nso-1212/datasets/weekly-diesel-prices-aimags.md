# Dataset: Weekly Diesel Prices by Region (Aimags)

## Identification

- **ID**: `weekly-diesel-prices-aimags`
- **Source**: `nso-1212`
- **Category**: Economy
- **Tags**: [prices, fuel, diesel, regional, weekly, aimags, mongolia]
- **Concept ID**: `weekly-prices`

## Source Reference

- **Parent Table ID**: `DT_NSO_0300_010V5.px`
- **Parent Dataset**: `nso-weekly-prices-aimags`
- **Sector**: `Economy, environment`
- **Subsector**: `Consumer Price Index`
- **API Path**: `/en/NSO/Economy, environment/Consumer Price Index/DT_NSO_0300_010V5.px`

## Title

- **EN**: Weekly Diesel Prices by Region in Mongolia (2024-2025)
- **MN**: Дизелийн түлшний долоо хоногийн үнэ, бүсээр (2024-2025)

## Coverage

| Dimension | Value |
|-----------|-------|
| **Geographic** | 4 representative aimags (chart) / 21 aimags + 4 regions (download) |
| **Granularity** | aimag |
| **Time Start** | 2024-01 |
| **Frequency** | weekly |
| **Product** | Diesel fuel only |

**⚠️ Coverage Limitation**: This dataset does NOT include Ulaanbaatar prices.

### Related Datasets

| Dataset | Coverage | Relation |
|---------|----------|----------|
| `weekly-gasoline-prices-aimags` | Petrol A-92 prices | Same source, fuel alternative |
| `weekly-beef-prices-aimags` | Beef prices | Same source, food category |
| `weekly-mutton-prices-aimags` | Mutton prices | Same source, food category |
| `weekly-flour-prices-aimags` | Flour prices | Same source, food category |
| `weekly-milk-prices-aimags` | Milk prices | Same source, food category |

## Description

Weekly diesel fuel prices across Mongolia's regions, extracted from the parent `nso-weekly-prices-aimags` dataset. This split focuses only on diesel fuel (l), showing regional price variations across representative aimags. Data is collected weekly since January 2024.

**Chart Subset Strategy**: The chart visualization displays 4 representative aimags (Darkhan-Uul, Khovd, Orkhon, Umnugovi) for readability. Full download files contain all 21 aimags plus 4 regional aggregates (Central, Eastern, Western, Khangai).

## Variables

### Product (Fixed)
- **EN**: Diesel fuel, l
- **MN**: Дизелийн түлш, л

### Region (Бүс) - Chart Subset
| EN | MN |
|----|-----|
| Darkhan-Uul | Дархан-Уул |
| Khovd | Ховд |
| Orkhon | Орхон |
| Umnugovi | Өмнөговь |

**Note**: Full download files include all 21 aimags and 4 regional aggregates listed in parent dataset.

### Time (Хугацаа)
Weekly dates from 2024-01-02 to present (97+ time periods)

## Split Filter

This dataset is created by filtering the parent dataset:

```json
{
  "Products": "Diesel fuel,  l"
}
```

**Note**: The Products value includes two spaces before "l" as it appears in the source data.

## Update Instructions

### Check for Updates

1. Check parent dataset `nso-weekly-prices-aimags` for updates
2. If parent has new data, regenerate this split

### Fetch Data

This is a split dataset. Data comes from the parent:

```bash
# Update parent dataset first
cd tools
python -m registry info nso-weekly-prices-aimags

# Then regenerate this split using the parent data
```

### Transformation

```python
import pandas as pd

# Load parent data
parent_df = pd.read_csv("data/tools/versions/nso-weekly-prices-aimags/v1/data.csv")

# Apply filter (note: two spaces before "l")
df = parent_df[parent_df["Products"] == "Diesel fuel,  l"].copy()

# Clean column names
df.columns = [c.lower().replace(' ', '_') for c in df.columns]

# Rename for clarity
df = df.rename(columns={
    "products": "product",
    "бүс": "region",
    "хугацаа": "date",
    "value": "price"
})

# Strip whitespace from string columns (CRITICAL for chart color matching)
for col in df.select_dtypes(include=['object']).columns:
    df[col] = df[col].astype(str).str.strip()

# Chart subset: 4 representative aimags
chart_aimags = ["Darkhan-Uul", "Khovd", "Orkhon", "Umnugovi"]
chart_df = df[df["region"].isin(chart_aimags)].copy()

# Export files
chart_df.to_csv("data/data.mn/public/datasets/weekly-diesel-prices-aimags-en.csv", index=False)
df.to_csv("data/data.mn/public/datasets/weekly-diesel-prices-aimags-all-en.csv", index=False)

# Mongolian versions with translated column names
chart_df_mn = chart_df.rename(columns={
    "region": "бүс",
    "date": "огноо",
    "price": "үнэ"
})
chart_df_mn.to_csv("data/data.mn/public/datasets/weekly-diesel-prices-aimags-mn.csv", index=False)

df_mn = df.rename(columns={
    "region": "бүс",
    "date": "огноо",
    "price": "үнэ"
})
df_mn.to_csv("data/data.mn/public/datasets/weekly-diesel-prices-aimags-all-mn.csv", index=False)
```

### XLSX Export (Wide Format)

```python
from openpyxl.utils import get_column_letter

# Pivot to wide format: rows=date, columns=regions
wide_df = df.pivot_table(
    index='date',
    columns='region',
    values='price',
    aggfunc='first'
).reset_index()

# Export with column formatting
xlsx_path = "data/data.mn/public/datasets/weekly-diesel-prices-aimags.xlsx"
with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
    wide_df.to_excel(writer, index=False, sheet_name='Data')

    worksheet = writer.sheets['Data']
    for idx, col in enumerate(wide_df.columns):
        max_length = max(
            wide_df[col].astype(str).map(len).max(),
            len(str(col))
        ) + 2
        col_letter = get_column_letter(idx + 1)
        worksheet.column_dimensions[col_letter].width = min(max_length, 30)
```

### Validation

- All price values should be positive numbers
- Time values should be valid weekly dates (Mondays)
- Chart subset should have exactly 4 regions
- Full download should have 21+ regions

## Chart Configuration

### Chart Type
Multi-line time series with layered hover interaction

### Chart Fields
- **X-axis**: date (temporal, format: %b %Y)
- **Y-axis**: price (quantitative, format: ,.0f, title: "Price (MNT/liter)")
- **Color**: region (nominal, 4 categories for chart)
- **Tooltip**: region, date (%Y-%m-%d), price (,.0f)

### Chart Features
- Line: strokeWidth 2.5, monotone interpolation
- Point layer: nearest hover selection, size 100
- Config: Brand typography (14px labels, 16px titles)
- Legend: Top orientation, no title

### Color Palette
Uses default Vega-Lite palette (4 colors for 4 regions)

## Content Generation

### Key Findings Template

Auto-extract from latest week:
- Latest average price across chart regions
- Price range (min/max regions)
- Week-over-week change
- Highest and lowest priced region

### Excerpt Templates

**EN**: "Diesel prices in Mongolia averaged {avg_price} MNT/liter in {latest_date}, ranging from {min_price} in {min_region} to {max_price} in {max_region}."

**MN**: "{latest_date}-д Монгол Улсын дизелийн түлшний дундаж үнэ {avg_price} төг/литр байсан бөгөөд {min_region}-д {min_price}, {max_region}-д {max_price} байв."

### Common Keywords
- mongolia
- diesel
- fuel
- prices
- weekly
- regional
- energy
- transportation

### MDX Tags
- mongolia
- diesel-prices
- fuel-prices
- energy
- weekly-data
- regional-data

## Notes

- This is a split dataset derived from `nso-weekly-prices-aimags`
- Chart shows 4 representative aimags for readability
- Full download files contain all 21 aimags + 4 regional aggregates
- Regional aggregates (Central, Eastern, Western, Khangai) provide overview perspective
- Diesel is critical for transportation and agriculture in Mongolia
- Winter months may show supply constraints in remote regions
- **CRITICAL**: Product name in source has two spaces: "Diesel fuel,  l"
