# Dataset: General Educational School Pupils in Mongolia (2010-2025)

## Identification

- **ID**: `school-pupils`
- **Source**: `nso-1212`
- **Category**: Education
- **Tags**: [mongolia, education, schools, pupils, primary, secondary, students]

## Source Reference

- **Table ID**: `DT_NSO_2001_018V1.px`
- **Sector**: `Education, health`
- **Subsector**: `General indicators for Education`
- **Last Updated**: 2026-02-01

## Title

- **EN**: General Educational School Pupils in Mongolia (2010-2025)
- **MN**: Ерөнхий боловсролын сургуулийн сурагчдын тоо (2010-2025)

## Description

Total number of pupils studying in general educational schools in Mongolia
by education level, ownership type, and sex from 2010 to 2025.

## Variables

### Indicator (Үзүүлэлт)
7 indicators: `Total`, `Primary`, `Secondary`, `High`, `Public`, `Private`,
`Of which: Female`.

### Year (Он)
16 years: 2010-2025 (continuous, no gaps)

### Pupils (Сурагч)
Number of pupils. 2025 national total: 819,907.

## Update Instructions

Query the API for table `DT_NSO_2001_018V1.px` and compare `updated` field with registry.

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_2001_018V1.px --output ./output
```

Raw columns EN: `Indicator, Year, value`.
Strip leading whitespace from indicator names (source pads sub-category
names), rename to `indicator, year, pupils`, and sort by indicator, year
ascending.

## Files

- `data.mn/public/datasets/school-pupils-en.csv`
- `data.mn/public/datasets/school-pupils-mn.csv`
- `data.mn/public/datasets/school-pupils.xlsx`
- `data.mn/public/charts/school-pupils-en.json`
- `data.mn/public/charts/school-pupils-mn.json`
- `data.mn/src/data/data/en/school-pupils.mdx`
- `data.mn/src/data/data/mn/school-pupils.mdx`

## Chart

Multi-series line chart. The chart shows the three education levels
(Primary, Secondary, High) via a Vega-Lite transform filter; the
downloadable files contain all 7 indicators.

## Notes

- Raw NSO fetch archived at `tools/versions/nso-school-pupils/v1/raw/`
- 112 rows (7 indicators x 16 years) per language
- Related dataset `school-enrollment-by-level` (table DT_NSO_2002_069V2.px)
  covers enrollment across all education levels including higher education
