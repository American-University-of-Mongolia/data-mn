# Dataset: Mongolia Imported Vehicles by Type

## Identification

- **ID**: `imported-vehicles-by-type`
- **Source**: `nso-1212`
- **Parent**: `imported-vehicles-total`
- **Category**: Trade
- **Tags**: [mongolia, vehicles, imports, trade, transport, passenger cars, freight]

## Source Reference

- **Table ID**: `DT_NSO_1200_013V5.px`
- **Sector**: `Foreign Trade`
- **API Path**: `/en/NSO/Foreign Trade/DT_NSO_1200_013V5.px` (resolve sector/subsector via catalog cache)

## Title

- **EN**: Mongolia Imported Vehicles by Type (2007–2025)
- **MN**: Монгол Улсад импортолсон тээврийн хэрэгсэл төрлөөр (2007–2025)

## Description

Annual breakdown of motor vehicles imported into Mongolia by vehicle type — passenger cars, freight vehicles, and buses/large vehicles — from 2007 to 2025.

## Variables

### Type (Төрөл)
Filtered to `Country == Total` / `Улс == Бүгд` rows only, mapped to short labels:
- `Motor vehicles for the transport of ten or more persons...` → `Buses & Large Vehicles` / `Автобус, том тээврийн хэрэгсэл`
- `Motor vehicles for the transport of goods` → `Freight Vehicles` / `Ачааны тээврийн хэрэгсэл`
- `Motor cars and other motor vehicles principally designed...` → `Passenger Cars` / `Суудлын автомашин`

### Year (Он)
Annual data from 2007 to 2025. Drop rows with missing values (partial-year cells).

### Value
- **Unit**: vehicle count (integer)
- **Range**: Positive values only

## Update Instructions

Updated together with parent `imported-vehicles-total`; see the parent definition for fetch and transform steps. Output columns are `year,vehicle_type,count` (EN) / `он,төрөл,тоо` (MN), ascending by year. The MN CSV must use translated headers and the MN chart must reference those field names.

### Validation

- `validate_vega.py --data` for both charts; `validate_dataset.py --all imported-vehicles-by-type`.
- Chart color domain must match the three short labels in each language.

## Chart Configuration

### Chart Type
Stacked multi-series area chart with nearest-point hover (Template 2, stacked).

### Visual Encoding

- **X-axis**: year (quantitative)
- **Y-axis**: count, stacked (quantitative)
- **Color Scale**:
  - Passenger Cars / Суудлын автомашин: `#4c78a8`
  - Freight Vehicles / Ачааны тээврийн хэрэгсэл: `#f58518`
  - Buses & Large Vehicles / Автобус, том тээврийн хэрэгсэл: `#72b7b2`
- **Legend**: Top horizontal

## Content Generation

### Keywords (EN)
- Mongolia vehicle imports
- imported vehicles Mongolia
- passenger car imports
- freight vehicle imports
- Mongolia trade statistics

### Keywords (MN)
- монгол тээврийн хэрэгсэл импорт
- импортолсон тээврийн хэрэгсэл
- суудлын автомашин импорт
- ачааны машин импорт
- монгол худалдааны статистик

## Notes

- 2025 is a partial year in the NSO table and is revised in subsequent releases.
- Chart data equals the full download data (only three categories, no subsetting needed).
