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

## Coverage

| Dimension | Value |
|-----------|-------|
| **Geographic** | 21 aimags + 4 regional aggregates |
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

### Chart Type
Multi-line chart

### Axes
- **X-axis**: date (temporal, weekly)
  - Title EN: "Date"
  - Title MN: "Огноо"
- **Y-axis**: price (quantitative)
  - Title EN: "Price (MNT/kg)"
  - Title MN: "Үнэ (төг/кг)"
  - Format: `.0f` (integer, no decimals)

### Color Scale
Show 4 regional aggregates for clarity:
- Central region: `#4c78a8` (primary)
- Eastern region: `#f58518` (secondary)
- Western region: `#72b7b2` (quaternary)
- Khangai region: `#54a24b` (quinary)

**Note**: Individual aimag data available in full download CSV for detailed analysis.

### Tooltip
- Date (formatted as date)
- Region name
- Price (MNT/kg, formatted with thousand separators)

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

### Validation

- All price values should be positive numbers
- Time values should be valid weekly dates (Mondays)
- Missing values are acceptable (seasonal availability)
- Regional aggregates should always have values (they are averages)

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
