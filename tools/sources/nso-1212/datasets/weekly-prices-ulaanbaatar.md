# Dataset: Weekly Prices of Main Products and Gasoline (Ulaanbaatar)

## Identification

- **ID**: `nso-weekly-prices-ulaanbaatar`
- **Source**: `nso-1212`
- **Category**: Economy
- **Tags**: [prices, inflation, food, fuel, gasoline, ulaanbaatar, weekly]
- **Concept ID**: `weekly-prices`

## Source Reference

- **Table ID**: `DT_NSO_0600_001V4.px`
- **Sector**: `Economy, environment`
- **Subsector**: `Consumer Price Index`
- **API Path**: `/en/NSO/Economy, environment/Consumer Price Index/DT_NSO_0600_001V4.px`

## Title

- **EN**: Weekly Prices of Main Products and Gasoline (Ulaanbaatar)
- **MN**: Үндсэн бүтээгдэхүүн, шатахууны долоо хоногийн үнэ (Улаанбаатар)

## Coverage

| Dimension | Value |
|-----------|-------|
| **Geographic** | Ulaanbaatar only |
| **Granularity** | city (capital) |
| **Time Start** | 2021-01-06 |
| **Frequency** | weekly |
| **Products** | 31 items |

**Note**: This dataset complements `nso-weekly-prices-aimags` which covers 21 aimags but excludes Ulaanbaatar.

### Related Datasets

| Dataset | Coverage | Table ID | Status |
|---------|----------|----------|--------|
| `nso-weekly-prices-aimags` | 21 aimags (no UB) | DT_NSO_0300_010V5.px | Active |

## Description

Weekly price monitoring data for essential food products (flour, bread, rice, meat, dairy, vegetables, eggs) and fuel (petrol A-80, petrol A-92, diesel) in Ulaanbaatar, Mongolia's capital where ~50% of the population lives. Data is collected weekly since January 2021 (251 weeks of history).

## Variables

### Products (Бүтээгдэхүүн) - 31 items

#### Grains & Bread
| Code | EN | MN |
|------|----|----|
| 1 | Flour, premium, prepacked, kg | Гурил, дээд зэрэг, савласан, кг |
| 2 | Flour, highest grade, prepacked, kg | Гурил, хамгийн өндөр зэрэг, савласан, кг |
| 3 | Flour, grade 1, prepacked, kg | Гурил, I зэрэг, савласан, кг |
| 4 | Flour, grade 2, prepacked, kg | Гурил, II зэрэг, савласан, кг |
| 5 | Bread, piece | Талх, ширхэг |
| 6 | Sliced bread, 600 gr, piece | Хэрчсэн талх, 600 гр, ширхэг |
| 7 | Bread, rye, piece | Хар талх, ширхэг |
| 8 | Rice, prepacked, kg | Цагаан будаа, савласан, кг |

#### Meat
| Code | EN | MN |
|------|----|----|
| 9 | Mutton, kg | Хонины мах, кг |
| 10 | Beef, kg | Үхрийн мах, кг |
| 11 | Beef, without bones, kg | Үхрийн мах, ясгүй, кг |
| 12 | Horse meat, kg | Адууны мах, кг |
| 13 | Goat meat, kg | Ямааны мах, кг |

#### Dairy
| Code | EN | MN |
|------|----|----|
| 14 | Milk, fresh, not pasteurised, l | Сүү, задгай, л |
| 15 | Milk, pasteurised, 500 g | Сүү, пастержуулсан, 500 гр |
| 16 | Milk, pasteurised, l | Сүү, пастержуулсан, л |
| 17 | Yoghurt, Tsutsgiitei, plain, 900 g | Тараг, Цуцгийтэй, 900 гр |
| 18 | Butter cream, Sain zuuhii, 450 g | Зөөхий, Сайн зуухий, 450 гр |

#### Other Groceries
| Code | EN | MN |
|------|----|----|
| 19 | Vegetable oil, l, imported | Ургамлын тос, импорт, л |
| 20 | Sugar, prepacked, kg, imported | Элсэн чихэр, импорт, кг |
| 21 | Green tea, prepacked, 90 g | Ногоон цай, 90 гр |
| 22 | Egg, piece, domestic | Өндөг, дотоодын, ширхэг |

#### Vegetables & Fruit
| Code | EN | MN |
|------|----|----|
| 23 | Apple, kg, China | Алим, Хятад, кг |
| 24 | Tomato, kg | Улаан лооль, кг |
| 25 | Carrot, kg | Лууван, кг |
| 26 | Cabbage, kg | Байцаа, кг |
| 27 | Beet, kg | Манжин, кг |
| 28 | Onion, kg | Сонгино, кг |

#### Fuel
| Code | EN | MN |
|------|----|----|
| 29 | Petrol, A-80, l | Аи-80 автобензин, л |
| 30 | Petrol, A-92, l | Аи-92 автобензин, л |
| 31 | Diesel fuel, l | Дизелийн түлш, л |

### Time (Хугацаа)
Weekly dates from 2021-01-06 to present (251 time periods as of December 2025)

## Update Instructions

### Check for Updates

1. Query the table listing endpoint:
   ```
   GET https://data.1212.mn/api/v1/en/NSO/Economy, environment/Consumer Price Index/
   ```

2. Find `DT_NSO_0600_001V4.px` in the response

3. Compare the `updated` field with `source_updated_at` in registry

4. If API's `updated` is newer, dataset needs updating

### Fetch Data

Use the `datamn-source-nso` skill for bilingual data fetching:

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_0600_001V4.px --output ./output
```

### Validation

- All price values should be positive numbers
- Time values should be valid weekly dates
- Products should match the expected list

## Splits

This multi-dimensional dataset is split into 6 category-based user-friendly datasets:

### 1. weekly-meat-prices-ulaanbaatar

- **ID**: `weekly-meat-prices-ulaanbaatar`
- **Title EN**: Weekly Meat Prices in Ulaanbaatar (2021-2025)
- **Title MN**: Улаанбаатар дахь махны долоо хоногийн үнэ (2021-2025)
- **Filter**:
  - Products: Mutton, Beef, Beef (boneless), Horse meat, Goat meat
- **Chart Type**: multi-line
- **Chart Config**:
  - X-axis: date (weekly)
  - Y-axis: price (MNT/kg)
  - Color: product type
- **Description EN**: Weekly prices for different meat types in Ulaanbaatar, including mutton, beef, horse meat, and goat meat.
- **Description MN**: Улаанбаатар хотын хонины мах, үхрийн мах, адууны мах, ямааны махны долоо хоног тутмын үнэ.

### 2. weekly-dairy-prices-ulaanbaatar

- **ID**: `weekly-dairy-prices-ulaanbaatar`
- **Title EN**: Weekly Dairy Prices in Ulaanbaatar (2021-2025)
- **Title MN**: Улаанбаатар дахь сүү, сүүн бүтээгдэхүүний долоо хоногийн үнэ (2021-2025)
- **Filter**:
  - Products: Milk (fresh), Milk (pasteurized 500g), Milk (pasteurized 1L), Yoghurt, Butter cream
- **Chart Type**: multi-line
- **Chart Config**:
  - X-axis: date (weekly)
  - Y-axis: price (MNT/unit)
  - Color: product type
- **Description EN**: Weekly prices for dairy products in Ulaanbaatar, including fresh milk, pasteurized milk, yoghurt, and butter cream.
- **Description MN**: Улаанбаатар хотын задгай сүү, пастержуулсан сүү, тараг, зөөхийн долоо хоног тутмын үнэ.

### 3. weekly-bread-prices-ulaanbaatar

- **ID**: `weekly-bread-prices-ulaanbaatar`
- **Title EN**: Weekly Bread & Grain Prices in Ulaanbaatar (2021-2025)
- **Title MN**: Улаанбаатар дахь талх, гурилын бүтээгдэхүүний долоо хоногийн үнэ (2021-2025)
- **Filter**:
  - Products: Flour (premium, grade 1), Bread (regular, sliced, rye), Rice
- **Chart Type**: multi-line
- **Chart Config**:
  - X-axis: date (weekly)
  - Y-axis: price (MNT/unit)
  - Color: product type
- **Description EN**: Weekly prices for bread, flour, and rice in Ulaanbaatar.
- **Description MN**: Улаанбаатар хотын талх, гурил, цагаан будааны долоо хоног тутмын үнэ.

### 4. weekly-grocery-prices-ulaanbaatar

- **ID**: `weekly-grocery-prices-ulaanbaatar`
- **Title EN**: Weekly Grocery Prices in Ulaanbaatar (2021-2025)
- **Title MN**: Улаанбаатар дахь хүнсний бүтээгдэхүүний долоо хоногийн үнэ (2021-2025)
- **Filter**:
  - Products: Vegetable oil, Sugar, Green tea, Egg
- **Chart Type**: multi-line
- **Chart Config**:
  - X-axis: date (weekly)
  - Y-axis: price (MNT/unit)
  - Color: product type
- **Description EN**: Weekly prices for common grocery items in Ulaanbaatar, including vegetable oil, sugar, tea, and eggs.
- **Description MN**: Улаанбаатар хотын ургамлын тос, чихэр, цай, өндөгний долоо хоног тутмын үнэ.

### 5. weekly-vegetable-prices-ulaanbaatar

- **ID**: `weekly-vegetable-prices-ulaanbaatar`
- **Title EN**: Weekly Vegetable Prices in Ulaanbaatar (2021-2025)
- **Title MN**: Улаанбаатар дахь хүнсний ногооны долоо хоногийн үнэ (2021-2025)
- **Filter**:
  - Products: Apple, Tomato, Carrot, Cabbage, Beet, Onion
- **Chart Type**: multi-line
- **Chart Config**:
  - X-axis: date (weekly)
  - Y-axis: price (MNT/kg)
  - Color: product type
- **Description EN**: Weekly prices for vegetables and fruits in Ulaanbaatar, including tomatoes, carrots, cabbage, onions, beets, and apples.
- **Description MN**: Улаанбаатар хотын хүнсний ногооны (улаан лооль, лууван, байцаа, сонгино, манжин) болон алимны долоо хоног тутмын үнэ.

### 6. weekly-fuel-prices-ulaanbaatar

- **ID**: `weekly-fuel-prices-ulaanbaatar`
- **Title EN**: Weekly Fuel Prices in Ulaanbaatar (2021-2025)
- **Title MN**: Улаанбаатар дахь шатахууны долоо хоногийн үнэ (2021-2025)
- **Filter**:
  - Products: Petrol A-80, Petrol A-92, Diesel
- **Chart Type**: multi-line
- **Chart Config**:
  - X-axis: date (weekly)
  - Y-axis: price (MNT/l)
  - Color: fuel type
- **Description EN**: Weekly fuel prices in Ulaanbaatar, including petrol (A-80, A-92) and diesel.
- **Description MN**: Улаанбаатар хотын Аи-80, Аи-92 автобензин, дизелийн түлшний долоо хоног тутмын үнэ.

## Content Generation

### Key Findings Template

For each split, auto-extract:
- Latest price (most recent week)
- Price range over time
- Highest and lowest values
- Price change vs previous week/month/year

### Common Tags

EN: mongolia, prices, weekly, ulaanbaatar, capital
MN: монгол, үнэ, долоо хоног, улаанбаатар, нийслэл

### Excerpt Templates

**weekly-meat-prices-ulaanbaatar**:
- EN: "Meat prices in Ulaanbaatar as of {latest_date}: mutton {mutton_price} MNT/kg, beef {beef_price} MNT/kg, with prices tracked weekly since 2021."
- MN: "{latest_date}-д Улаанбаатарт хонины мах {mutton_price} төг/кг, үхрийн мах {beef_price} төг/кг байсан бөгөөд 2021 оноос долоо хоног бүр бүртгэгдсэн."

## Notes

- This dataset provides **Ulaanbaatar-only** data to complement the aimag-level data in `nso-weekly-prices-aimags`
- Longer time series (2021-2025) compared to aimag data (2024-2025)
- More products (31 vs 11) than aimag data
- A-80 petrol data available but may have gaps as it's being phased out
- **Parent dataset**: This dataset (`nso-weekly-prices-ulaanbaatar`) stores the raw data; only the splits are published to data.mn
