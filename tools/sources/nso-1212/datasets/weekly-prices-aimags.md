# Dataset: Weekly Prices of Main Products and Gasoline (Aimags)

## Identification

- **ID**: `nso-weekly-prices-aimags`
- **Source**: `nso-1212`
- **Category**: Economy
- **Tags**: [prices, inflation, food, fuel, gasoline, regional, weekly, aimags]
- **Concept ID**: `weekly-prices`

## Source Reference

- **Table ID**: `DT_NSO_0300_010V5.px`
- **Sector**: `Economy, environment`
- **Subsector**: `Consumer Price Index`
- **API Path**: `/en/NSO/Economy, environment/Consumer Price Index/DT_NSO_0300_010V5.px`

## Title

- **EN**: Weekly Prices of Main Products (Aimags)
- **MN**: Үндсэн бүтээгдэхүүний долоо хоногийн үнэ (Аймгаар)

## Coverage

| Dimension | Value |
|-----------|-------|
| **Geographic** | 21 aimags + 4 regional aggregates |
| **Granularity** | aimag |
| **Time Start** | 2024-01 |
| **Frequency** | weekly |
| **Products** | 11 items |

**⚠️ Coverage Limitation**: This dataset does NOT include Ulaanbaatar prices.

### Related Datasets

| Dataset | Coverage | Table ID | Status |
|---------|----------|----------|--------|
| `weekly-prices-ulaanbaatar` | Ulaanbaatar only | DT_NSO_0600_001V4.px | Not yet added |

For Ulaanbaatar prices, add the related dataset from `DT_NSO_0600_001V4.px` which has:
- 31 products (more than this table's 11)
- 251 time periods (~5 years of history vs ~2 years here)
- No regional breakdown (single UB/national value)

## Description

Weekly price monitoring data for essential food products (beef, mutton, goat meat, milk, flour, rice, sugar, hay) and fuel (petrol A-80, petrol A-92, diesel) across all 21 aimags (provinces) and 4 regional aggregates (Central, Eastern, Western, Khangai) of Mongolia. Data is collected weekly since January 2024. **Note: Ulaanbaatar is not included in this dataset.**

## Variables

### Products (Бүтээгдэхүүн)
| EN | MN |
|----|-----|
| Beef, kg | Үхрийн мах, ястай, кг |
| Mutton, kg | Хонины мах, ястай, кг |
| Goat meat, kg | Ямааны мах, ястай, кг |
| Milk, fresh, not pasteurised, l | Сүү, үнээний, задгай, л |
| Flour, grade 1, prepacked, kg | Гурил, I зэрэг, савласан, кг |
| Rice, prepacked, kg | Цагаан будаа, кг |
| Sugar, prepacked, kg, imported | Элсэн чихэр, кг |
| Hay bale | Боодолтой өвс |
| Petrol, A-80, l | Аи-80 автобензин, л |
| Petrol, A-92, l | Аи-92 автобензин, л |
| Diesel fuel, l | Дизелийн түлш, л |

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

## Update Instructions

### Check for Updates

1. Query the table listing endpoint:
   ```
   GET https://data.1212.mn/api/v1/en/NSO/Economy, environment/Consumer Price Index/
   ```

2. Find `DT_NSO_0300_010V5.px` in the response

3. Compare the `updated` field with `source_updated_at` in registry

4. If API's `updated` is newer, dataset needs updating

### Fetch Data

Use the `datamn-source-nso` skill for bilingual data fetching:

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_0300_010V5.px --output ./output
```

### Validation

- All price values should be positive numbers
- Time values should be valid weekly dates (Mondays)
- Missing values are acceptable (some products not available in all regions)

## Splits

This multi-dimensional dataset is split into the following user-friendly datasets:

### 1. weekly-beef-prices-aimags

- **ID**: `weekly-beef-prices-aimags`
- **Title EN**: Weekly Beef Prices by Region in Mongolia (2024-2025)
- **Title MN**: Үхрийн махны долоо хоногийн үнэ, бүсээр (2024-2025)
- **Filter**:
  - Products: "Beef, kg"
- **Chart Type**: multi-line
- **Chart Config**:
  - X-axis: date (weekly)
  - Y-axis: price (MNT/kg)
  - Color: region (show only 4 regional aggregates for clarity)
- **Description EN**: Weekly beef prices across Mongolia's four regions, showing regional price variations.
- **Description MN**: Монгол Улсын дөрвөн бүсийн үхрийн махны долоо хоног тутмын үнийн хэлбэлзэл.

### 2. weekly-mutton-prices-aimags

- **ID**: `weekly-mutton-prices-aimags`
- **Title EN**: Weekly Mutton Prices by Region in Mongolia (2024-2025)
- **Title MN**: Хонины махны долоо хоногийн үнэ, бүсээр (2024-2025)
- **Filter**:
  - Products: "Mutton, kg"
- **Chart Type**: multi-line
- **Chart Config**:
  - X-axis: date (weekly)
  - Y-axis: price (MNT/kg)
  - Color: region (4 regional aggregates)
- **Description EN**: Weekly mutton prices across Mongolia's four regions, showing regional price variations.
- **Description MN**: Монгол Улсын дөрвөн бүсийн хонины махны долоо хоног тутмын үнийн хэлбэлзэл.

### 3. weekly-gasoline-prices-aimags

- **ID**: `weekly-gasoline-prices-aimags`
- **Title EN**: Weekly Gasoline (A-92) Prices by Region in Mongolia (2024-2025)
- **Title MN**: Аи-92 автобензиний долоо хоногийн үнэ, бүсээр (2024-2025)
- **Filter**:
  - Products: "Petrol, A-92, l"
- **Chart Type**: multi-line
- **Chart Config**:
  - X-axis: date (weekly)
  - Y-axis: price (MNT/l)
  - Color: region (4 regional aggregates)
- **Description EN**: Weekly A-92 petrol prices across Mongolia's four regions, showing regional price variations.
- **Description MN**: Монгол Улсын дөрвөн бүсийн Аи-92 автобензиний долоо хоног тутмын үнийн хэлбэлзэл.

### 4. weekly-diesel-prices-aimags

- **ID**: `weekly-diesel-prices-aimags`
- **Title EN**: Weekly Diesel Prices by Region in Mongolia (2024-2025)
- **Title MN**: Дизелийн түлшний долоо хоногийн үнэ, бүсээр (2024-2025)
- **Filter**:
  - Products: "Diesel fuel, l"
- **Chart Type**: multi-line
- **Chart Config**:
  - X-axis: date (weekly)
  - Y-axis: price (MNT/l)
  - Color: region (4 regional aggregates)
- **Description EN**: Weekly diesel fuel prices across Mongolia's four regions, showing regional price variations.
- **Description MN**: Монгол Улсын дөрвөн бүсийн дизелийн түлшний долоо хоног тутмын үнийн хэлбэлзэл.

### 5. weekly-flour-prices-aimags

- **ID**: `weekly-flour-prices-aimags`
- **Title EN**: Weekly Flour Prices by Region in Mongolia (2024-2025)
- **Title MN**: Гурилын долоо хоногийн үнэ, бүсээр (2024-2025)
- **Filter**:
  - Products: "Flour, grade 1, prepacked, kg"
- **Chart Type**: multi-line
- **Chart Config**:
  - X-axis: date (weekly)
  - Y-axis: price (MNT/kg)
  - Color: region (4 regional aggregates)
- **Description EN**: Weekly flour prices across Mongolia's four regions, showing regional price variations.
- **Description MN**: Монгол Улсын дөрвөн бүсийн гурилын долоо хоног тутмын үнийн хэлбэлзэл.

### 6. weekly-milk-prices-aimags

- **ID**: `weekly-milk-prices-aimags`
- **Title EN**: Weekly Fresh Milk Prices by Region in Mongolia (2024-2025)
- **Title MN**: Сүүний долоо хоногийн үнэ, бүсээр (2024-2025)
- **Filter**:
  - Products: "Milk, fresh, not pasteurised, l"
- **Chart Type**: multi-line
- **Chart Config**:
  - X-axis: date (weekly)
  - Y-axis: price (MNT/l)
  - Color: region (4 regional aggregates)
- **Description EN**: Weekly fresh milk prices across Mongolia's four regions, showing regional price variations.
- **Description MN**: Монгол Улсын дөрвөн бүсийн сүүний долоо хоног тутмын үнийн хэлбэлзэл.

## Content Generation

### Key Findings Template

For each split, auto-extract:
- Latest price (most recent week)
- Price range across regions
- Highest and lowest region
- Price change vs previous week

### Common Tags
- mongolia
- prices
- weekly
- regional

### Excerpt Templates

**weekly-beef-prices-aimags**:
- EN: "Beef prices in Mongolia averaged {avg_price} MNT/kg in {latest_date}, ranging from {min_price} in {min_region} to {max_price} in {max_region}."
- MN: "{latest_date}-д Монгол Улсын үхрийн махны дундаж үнэ {avg_price} төг/кг байсан бөгөөд {min_region}-д {min_price}, {max_region}-д {max_price} байв."

## Notes

- Weekly data provides high-frequency price monitoring
- Regional aggregates (Central, Eastern, Western, Khangai) are useful for overview charts
- Individual aimag data available in full download for detailed analysis
- A-80 petrol data has significant gaps (discontinued in many regions)
- Hay prices are seasonal and may have more missing values
- **Parent dataset**: This dataset (`nso-weekly-prices-main-products`) stores the raw data; only the splits are published to data.mn
