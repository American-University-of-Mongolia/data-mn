# Dataset: School Enrollment by Education Level

## Identification

- **ID**: `school-enrollment-by-level`
- **Source**: `nso-1212`
- **Category**: Education
- **Tags**: [education, enrollment, students, schools, university, vocational]

## Source Reference

- **Table ID**: `DT_NSO_2002_069V2.px`
- **Sector**: `Education, health`
- **Subsector**: `General indicators for Education`

## Title

- **EN**: School Enrollment by Education Level in Mongolia (2010-2025)
- **MN**: Монгол Улсын сургуулийн элсэлт боловсролын түвшнээр (2010-2025)

## Description

Number of students enrolled in educational institutions in Mongolia, broken down by four main education levels: early childhood education, general education (primary/secondary/high school), technical and vocational education, and higher education. Data spans from 2010 to 2025.

## Variables

### Classification (Ангилал)
Source table has 21 hierarchical classifications. This dataset uses 4 top-level categories:
- `Total number of children in early childhood education` / `Сургуулийн өмнөх боловсролд хамрагдагчид`
- `Total number of pupils studying in general educational schools` / `Ерөнхий боловсролын сургуульд өдрөөр суралцагчид`
- `Technical and vocational educational institutions` / `Мэргэжлийн боловсролын сургалтын байгууллагад суралцагчид`
- `Total number of students studying in Higher educational institutions` / `Дээд боловсролын сургалтын байгууллагад суралцагчид`

### Year (Он)
16 years: 2010-2025

## Update Instructions

### Check for Updates

Query the API for table `DT_NSO_2002_069V2.px` and compare `updated` field with registry.

### Fetch Data

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_2002_069V2.px --output ./output
```

Then filter for the 4 main education levels and multiply values by 1000 (source provides data in thousands).

## Notes

- Source values are in thousands (e.g., 819.9 = 819,900 students)
- Dataset converts to actual numbers for clarity
- General education includes primary, secondary, and high school levels combined
- A small number of students studying abroad (~2,000) are excluded from this breakdown
