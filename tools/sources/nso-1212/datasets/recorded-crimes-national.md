# Dataset: Recorded Crimes National

## Identification

- **ID**: `recorded-crimes-national`
- **Source**: `nso-1212`
- **Category**: Public Safety
- **Tags**: [crime, public-safety, law-enforcement, recorded-crimes]

## Source Reference

- **Table ID**: `DT_NSO_2300_003V_1.px`
- **Sector**: `Regional development`
- **Subsector**: `Justice and crime`
- **Last Updated**: 2026-01-15

## Title

- **EN**: Mongolia Recorded Crimes, National Total (1989-2024)
- **MN**: Монгол Улсын бүртгэгдсэн гэмт хэргийн тоо (1989-2024)

## Description

Annual number of recorded crimes in Mongolia, national total. Source table contains breakdown by 21 aimags, Ulaanbaatar (with district detail), and regional aggregates. This dataset uses the pre-computed "Total" row for the national aggregate.

## Variables

### Region (Бүс)
Source table has 40 regions including aimags, UB districts, regional aggregates. This dataset uses only "Total" / "Улсын дүн".

### Year (Он)
36 years: 1989-2024 (continuous, no gaps)

## Update Instructions

Query the API for table `DT_NSO_2300_003V_1.px` and compare `updated` field with registry.

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_2300_003V_1.px --output ./output
```

Filter: Region="Total" for national aggregate.

## Notes

- National total only — no aimag or district splits in this dataset
- This is the first dataset in the "Public Safety" category
- Notable trends: sharp rise in 1990s transition, decline 2003-2011, new peak 2024 (44,673)
- Related table DT_NSO_2300_034V1.px has crime rate per 10,000 population (future split)
- Issue reference mentioned DT_NSO_2300_003V1.px but actual table ID is DT_NSO_2300_003V_1.px
