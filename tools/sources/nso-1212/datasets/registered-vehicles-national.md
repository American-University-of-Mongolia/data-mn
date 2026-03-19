# Dataset: Registered Vehicles National

## Identification

- **ID**: `registered-vehicles-national`
- **Source**: `nso-1212`
- **Category**: Infrastructure
- **Tags**: [vehicles, transportation, infrastructure, registered-vehicles, automobile]

## Source Reference

- **Table ID**: `DT_NSO_1200_013V3.px`
- **Sector**: `Industry, service`
- **Subsector**: `Transportation`

## Title

- **EN**: Mongolia Registered Vehicles, National Total (1940-2024)
- **MN**: Монгол Улсын бүртгэлтэй тээврийн хэрэгслийн тоо (1940-2024)

## Description

Annual number of registered vehicles in Mongolia, aggregated national total. Source table contains breakdowns by vehicle type (8 types: car, truck, bus, motorcycle, trailer, mechanisms, special purpose) and region (21 aimags + Ulaanbaatar + regional aggregates). This dataset filters to Types="Total" and Region="Total" for the national aggregate.

## Variables

### Types (Төрөл)
Source table has 8 vehicle types. This dataset uses only "Total" / "Бүгд" (all types summed).

Available types (for future splits):
- Passenger automobile / Суудлын автомашин
- Truck / Ачааны автомашин
- Bus / Автобус
- Trailer / Чиргүүл
- Motorcycle / Мотоцикл
- Mechanisms / Механизм
- Special purpose vehicle / Тусгай зориулалтын автомашин

### Region (Бүс)
Source table has 28 regions. This dataset uses only "Total" / "Улсын дүн" (national aggregate).

### Year (Он)
31 years: 1940-1957 (historical), 2012-2024 (modern). Gap between 1957 and 2012.

## Update Instructions

Query the API for table `DT_NSO_1200_013V3.px` and compare `updated` field with registry.

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_1200_013V3.px --output ./output
```

Filter: Types="Total", Region="Total" for national aggregate.

## Notes

- National total only — no type or region splits in this dataset
- Data has a gap from 1958-2011 (no records in source table)
- Latest data: 1,339,005 vehicles in 2024
- Rapid growth from 608,274 (2012) to 1,339,005 (2024) — more than doubled in 12 years
- Decline in 2023 (1,192,520) before recovery in 2024 may indicate reclassification or deregistration
