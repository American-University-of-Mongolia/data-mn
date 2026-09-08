# Dataset: Total Imported Vehicles in Mongolia

## Identification

- **ID**: `imported-vehicles-total`
- **Source**: `nso-1212`
- **Category**: Economy
- **Tags**: [mongolia, vehicles, imports, trade, transport, motor-vehicles]
- **Splits**: [`imported-vehicles-by-type`]

## Source Reference

- **Table ID**: `DT_NSO_1200_013V5.px`
- **Sector**: `Foreign Trade`
- **API Path**: `/en/NSO/Foreign Trade/DT_NSO_1200_013V5.px` (resolve sector/subsector via catalog cache)

## Title

- **EN**: Total Imported Vehicles in Mongolia, Count (2007-2025)
- **MN**: Монгол Улсад импортолсон тээврийн хэрэгслийн нийт тоо, ширхэг (2007-2025)

## Description

Annual total number of motor vehicles imported into Mongolia from 2007 to 2025, summed across passenger cars, freight vehicles, and buses/large vehicles. Imports peaked at 154,294 vehicles in 2024.

## Variables

### Type (Төрөл)
Three vehicle types, filtered to `Country == Total` / `Улс == Бүгд` rows only:
- `Motor vehicles for the transport of ten or more persons...` → `Buses & Large Vehicles` / `Автобус, том тээврийн хэрэгсэл`
- `Motor vehicles for the transport of goods` → `Freight Vehicles` / `Ачааны тээврийн хэрэгсэл`
- `Motor cars and other motor vehicles principally designed...` → `Passenger Cars` / `Суудлын автомашин`

### Year (Он)
Annual data from 2007 to 2025. Drop rows with missing values (partial-year cells).

### Value
- **Unit**: vehicle count (integer)
- **Range**: Positive values only

## Update Instructions

### Check for Updates

Compare the catalog `updated_at` for `DT_NSO_1200_013V5.px` (metadata/tables.db) with `source_updated_at` in the registry.

### Fetch Data

```bash
.venv/bin/python .claude/skills/datamn-source-nso/fetch_data.py \
  --table DT_NSO_1200_013V5.px --output /tmp/ivt-fetch
```

### Data Transformation

1. Keep only `Country == Total` (EN) / `Улс == Бүгд` (MN) rows; drop NaN values.
2. Map the three types to short labels (see Variables); strip whitespace.
3. Parent: group by year and sum → `year,value` (EN) / `он,утга` (MN), ascending.
4. Split `imported-vehicles-by-type`: `year,vehicle_type,count` (EN) / `он,төрөл,тоо` (MN).
5. Export files: chart CSVs, `-all-` download CSVs (parent), XLSX workbooks.
6. Save raw NSO CSVs under `tools/versions/<dataset-id>/v<N+1>/`.

### Validation

- Fresh `Country == Total` series must reproduce the previously published by-type values for overlapping years.
- Year values 2007+ with no gaps; all counts positive integers.
- `validate_vega.py --data` for every chart; `validate_dataset.py --all` for both datasets.

## Chart Configuration

### Chart Type
Single-series area chart with nearest-point hover (Template 1).

### Visual Encoding

- **X-axis**: year (quantitative)
- **Y-axis**: value, imported vehicle count (quantitative)
- **Color**: `#4c78a8` (primary)

## Content Generation

### Keywords (EN)
- Mongolia vehicle imports
- total imported vehicles
- Mongolia motor vehicle imports

### Keywords (MN)
- монгол тээврийн хэрэгсэл импорт
- импортолсон тээврийн хэрэгсэл
- нийт импорт

### Excerpt Templates

**EN**: "Total motor vehicles imported into Mongolia each year from 2007 to 2025, peaking at 154,294 vehicles in 2024."

**MN**: "Монгол Улсад жил бүр импортолсон тээврийн хэрэгслийн нийт тоо 2007-2025 онд, 2024 онд 154,294-т хүрч дээд цэгтээ хүрсэн."

## Notes

- 2025 is a partial year in the NSO table and is revised in subsequent releases.
- Sibling standalone dataset `imported-vehicles-cars-by-country` shares this source table but is maintained separately.
