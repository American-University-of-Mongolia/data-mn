# Dataset: Registered Vehicles by Province

## Identification

- **ID**: `registered-vehicles-by-province`
- **Source**: `nso-1212`
- **Category**: Infrastructure
- **Tags**: [vehicles, transport, infrastructure, province, aimag, regional]

## Source Reference

- **Table ID**: `DT_NSO_1200_013V4.px`
- **Sector**: `Industry, service`
- **Subsector**: `Transportation`

## Title

- **EN**: Mongolia Registered Vehicles by Province (2012–2025)
- **MN**: Монгол Улсад бүртгэлтэй тээврийн хэрэгсэл аймаг, нийслэлээр (2012–2025)

## Description

Annual number of registered vehicles in Mongolia broken down by province (21 aimags + Ulaanbaatar), from 2012 to 2025. Source table DT_NSO_1200_013V4.px contains 3 dimensions: Age × Region × Year. This dataset filters to Age="Total" (all vehicle ages summed) and keeps only the 22 individual provinces (excludes national total and 4 macro-region aggregates).

## Variables

### Age (Насжилт)
Vehicle age group. This dataset uses only "Total" / "Бүгд".

Available age groups (for future splits):
- 0-3 years
- 4-6 years
- 7-9 years
- 10 or more years

### Region (Бүс)
Source table has 28 entries. This dataset keeps 22 individual provinces:
- 21 aimags (Arkhangai, Bayan-Ulgii, Bayankhongor, Bulgan, Darkhan-Uul, Dornod, Dornogovi, Dundgovi, Govi-Altai, Govisumber, Khentii, Khovd, Khuvsgul, Orkhon, Selenge, Sukhbaatar, Tuv, Umnugovi, Uvs, Uvurkhangai, Zavkhan)
- Ulaanbaatar (capital city)

Excluded: Total (national), Western region, Khangai region, Central region, Eastern region (macro-region aggregates).

**Note**: Ulaanbaatar appears with both 1-space and 2-space prefix in the source CSV — these are identical values. Only one is kept after deduplication.

### Year (Он)
14 years: 2012–2025.

## Output Columns

| Column | Type | Description |
|--------|------|-------------|
| year | integer | Reference year |
| province | string | Province name (EN or MN) |
| count | integer | Number of registered vehicles |

## Update Instructions

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_1200_013V4.px --output /tmp/nso_v4_province
```

Filter: Age="Total" / "Бүгд", exclude macro-regions and national total, deduplicate Ulaanbaatar rows.

## Notes

- Ulaanbaatar dominates with ~60% of all registered vehicles nationally (795,756 in 2025)
- Umnugovi ranks second (74,860 in 2025), driven by mining sector growth
- 308 rows total (22 provinces × 14 years)
- Data as of 2025 (latest year in source)
