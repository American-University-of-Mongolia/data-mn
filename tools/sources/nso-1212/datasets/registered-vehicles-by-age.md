# Dataset: Registered Vehicles by Age Group

## Identification

- **ID**: `registered-vehicles-by-age`
- **Source**: `nso-1212`
- **Category**: Infrastructure
- **Tags**: [vehicles, transportation, infrastructure, age, fleet]

## Source Reference

- **Table ID**: `DT_NSO_1200_013V4.px`
- **Sector**: `Industry, service`
- **Subsector**: `Transportation`

## Title

- **EN**: Mongolia Registered Vehicles by Age Group (2012–2025)
- **MN**: Монгол Улсад бүртгэлтэй тээврийн хэрэгслийн насны бүтэц (2012–2025)

## Description

Annual breakdown of Mongolia's registered vehicle fleet by age group, showing the national total across 4 age bands. Source table has 3 dimensions: Age × Region × Year. This dataset filters to Region="Total" (Улсын дүн) and excludes the Age="Total" row, yielding the age-group breakdown of the national fleet.

## Variables

### Age (Насжилт)
4 groups used in this dataset:
- `0-3` — New to slightly used (0–3 years old)
- `4-6` — Moderately used (4–6 years old)
- `7-9` — Older used (7–9 years old)
- `10 or more` / `10 ба түүнээс дээш` — Very old (10+ years, dominant category)

### Region (Бүс)
Source table has 28 region values (with spacing variations for sub-regions). This dataset uses only "Total" / "Улсын дүн" (national aggregate).

### Year (Он)
14 years: 2012–2025

## Split Filter

```json
{"Region": "Total", "Age": "!Total"}
```

## Update Instructions

Query the API for table `DT_NSO_1200_013V4.px` and compare `updated` field with registry.

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_1200_013V4.px --output ./output
```

Filter: Region="Total", Age != "Total".

## Notes

- Key insight: In 2025, 81.7% of Mongolia's registered vehicles are 10+ years old
- Fleet is growing rapidly (608K in 2012 → 1.42M in 2025), but age structure remains heavily skewed toward old vehicles
- Reflects Mongolia's heavy reliance on second-hand vehicle imports
- Duplicate Ulaanbaatar entries in source (1-space and 2-space prefix) have identical values — only "Total" row is used
