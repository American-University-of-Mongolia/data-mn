# Teachers by Education Level

## Source Table
- **Table ID**: DT_NSO_2002_067V1.px
- **Sector**: Education, health
- **Subsector**: General indicators for Education

## Variables
- **Classification** (10 values): Total, Of which: Female, Kindergartens, Of which: Female, General educational schools, Of which: Female, Technical and vocational educational institutions, Of which: Female, Universities/institutes/colleges, Of which: Female
- **Year** (16 values): 2010-2025

## Notes
- "Of which: Female" appears 5 times (once per level + total), disambiguated by position after parent
- Values are number of full-time teachers
- EN labels have leading whitespace that must be stripped
- "Universities, institutes, colleges" contains comma — needs CSV quoting

## Split Filter
- **teachers-by-level**: Classification in [Kindergartens, General educational schools, Technical and vocational educational institutions, Universities/institutes/colleges]

## Update Instructions
1. Fetch EN data from DT_NSO_2002_067V1.px
2. Strip whitespace from Classification column
3. Disambiguate "Of which: Female" rows by sequential parent tracking
4. Build both language CSVs from single EN source with order index
5. Regenerate XLSX in wide format
