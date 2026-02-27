# Dataset: Exports by Category

## Identification

- **ID**: `exports-by-category`
- **Source**: `nso-1212`
- **Category**: Trade
- **Tags**: [exports, trade, commodities, mining]

## Source Reference

- **Table ID**: `DT_NSO_1400_005V1_year.px`
- **Sector**: `Economy, environment`
- **Subsector**: `External trade`

## Title

- **EN**: Mongolia Exports by Category, Thousands USD (1995-2024)
- **MN**: Монгол Улсын экспорт ангиллаар, мянган ам.доллар (1995-2024)

## Description

Mongolia's annual export values by commodity category in thousands of US dollars, from 1995 to 2024. Categories include mineral products, textiles, base metals, food products, live animals, and precious stones/jewellery. Mineral products dominate, accounting for approximately 87% of total exports in 2024.

## Variables

### Category (Ангилал)
6 export categories:
- `Mineral products` / `Эрдэс бүтээгдэхүүн`
- `Textiles & textile articles` / `Нэхмэлийн материал, нэхмэл бүтээгдэхүүн`
- `Base metals & articles thereof` / `Үндсэн төмөрлөг, түүгээр хийсэн зүйлс`
- `Live animals, animals origin products` / `Амьд амьтан, амьтны гаралтай бүтээгдэхүүн`
- `Food products` / `Хүнсний бүтээгдэхүүн`
- `Natural or cultured stones, precious metal, jewellery` / `Байгалийн болон өсгөвөрийн чулуу, үнэт металл, үнэт эдлэл`

### Year (Он)
30 years: 1995-2024

## Update Instructions

Query the API for table `DT_NSO_1400_005V1_year.px` and compare `updated` field with registry.

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_1400_005V1_year.px --output ./output
```

## Notes

- Values are in thousands of US dollars
- Mineral products include coal, copper concentrate, iron ore, crude oil, and other mining outputs
- Mongolia's export composition is highly concentrated in mining/minerals
