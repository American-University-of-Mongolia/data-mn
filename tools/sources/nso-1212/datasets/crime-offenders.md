# Dataset: Crime Offenders in Mongolia by Type (2010-2024)

## Identification

- **ID**: `crime-offenders`
- **Source**: `nso-1212`
- **Category**: Society
- **Tags**: [mongolia, crime, offenders, justice, law, statistics]

## Source Reference

- **Table ID**: `DT_NSO_2300_038V1.px`
- **Sector**: `Regional development`
- **Subsector**: `Justice and crime`
- **Last Updated**: 2026-02-01

## Title

- **EN**: Crime Offenders in Mongolia by Type (2010-2024)
- **MN**: Гэмт хэргийн төрлөөр гэмт этгээдийн тоо (2010-2024)

## Description

Number of crime offenders in Mongolia by classification of crimes from 2010 to 2024, covering 20 crime classifications (19 crime types plus the national total row).

## Variables

### Crime Type (Гэмт хэргийн төрөл)
20 classifications: `Total` plus 19 crime types (Corruption, Crimes against
administration of justice, Crimes against children, Crimes against
environment, Crimes against health, Crimes against human heath immunity,
Crimes against human immunity and freedom, Crimes against human privacy,
political right and liberty, Crimes against human right to be live, Crimes
against human sexual freedom and immunity, Crimes against humanity safety
and peace, Crimes against military service, Crimes against national
security, Crimes against ownership right, Crimes against public safety and
interests, Crimes against public service interest, Crimes against security
of computer data, Crimes against traffic safety and regulation of vehicle
use, Economic crimes).

### Year (Он)
15 years: 2010-2024 (continuous, no gaps)

### Offenders (Гэмт этгээд)
Number of offenders. 2024 national total: 25,291.

## Update Instructions

Query the API for table `DT_NSO_2300_038V1.px` and compare `updated` field with registry.

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_2300_038V1.px --output ./output
```

Raw columns EN: `Classification of crimes, Year, value`.
Rename to `crime_type, year, offenders` and sort by crime type, year ascending.

## Files

- `data.mn/public/datasets/crime-offenders-en.csv`
- `data.mn/public/datasets/crime-offenders-mn.csv`
- `data.mn/public/datasets/crime-offenders.xlsx`
- `data.mn/public/charts/crime-offenders-en.json`
- `data.mn/public/charts/crime-offenders-mn.json`
- `data.mn/src/data/data/en/crime-offenders.mdx`
- `data.mn/src/data/data/mn/crime-offenders.mdx`

## Chart

Multi-series line chart. The chart shows a readable 4-type subset
(ownership, health, traffic safety, environment) via a Vega-Lite transform
filter; the downloadable files contain all 20 classifications.

## Notes

- Raw NSO fetch archived at `tools/versions/nso-crime-offenders/v1/raw/`
- 300 rows (20 classifications x 15 years) per language
- Related dataset `recorded-crimes-national` (table DT_NSO_2300_003V_1.px)
  covers recorded crime counts; this dataset covers offenders by crime type
