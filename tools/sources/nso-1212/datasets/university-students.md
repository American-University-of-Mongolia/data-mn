# Dataset: University Students in Mongolia by Sex (2010-2025)

## Identification

- **ID**: `university-students`
- **Source**: `nso-1212`
- **Category**: Education
- **Tags**: [mongolia, education, university, students, higher-education, gender]

## Source Reference

- **Table ID**: `DT_NSO_2001_013V1.px`
- **Sector**: `Education, health` (verify via NSO catalog; same 2001 family as school-pupils)
- **Subsector**: higher-education indicators (verify exact NSO subsector name)

## Title

- **EN**: University Students in Mongolia by Sex (2010-2025)
- **MN**: Их, дээд сургууль, коллежид суралцагчдын тоо, хүйсээр (2010-2025)

## Description

Students enrolled in universities, institutes, and colleges in Mongolia
by sex and region from 2010 to 2025.

## Variables

### Sex (Хүйс)
`Female`, `Male`. Female students outnumber males in every year shown.

### Region (Бүс нутаг)
All 21 aimags, Ulaanbaatar, and 5 regional aggregates (28 series).

### Year (Он)
16 years: 2010-2025 (continuous, no gaps)

### Students (Оюутан)
Enrolled student count. 2025 national totals: Female 99,483, Male 62,408.

## File Shapes

- Download CSV (`-all-`): long form with composite categories `Sex — Region`
  (e.g. `Female — Arkhangai`), 28 categories x 16 years.
- Chart CSV (plain): long form, national totals by sex only (2 x 16 rows).
- XLSX: wide form, bilingual `English` + `Монгол` sheets.

## Update Instructions

Re-fetch table `DT_NSO_2001_013V1.px` from the 1212.mn API, rebuild the
long CSVs (verify totals match the API), pivot the bilingual XLSX, and
re-validate with `validate_dataset.py --all university-students`.
