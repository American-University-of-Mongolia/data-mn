# Dataset: Population Pyramid of Mongolia

## Identification

- **ID**: `population-pyramid-mongolia`
- **Source**: `nso-1212`
- **Category**: Demographics
- **Tags**: [mongolia, population, age, pyramid, demographics]

## Source Reference

- **Table ID**: `DT_NSO_0300_003V1.px`
- **Sector**: `Population, household`
- **Subsector**: `1_Population, household`
- **API Path**: `/en/NSO/Population, household/1_Population, household/DT_NSO_0300_003V1.px`

## Title

- **EN**: Population Pyramid of Mongolia
- **MN**: Монгол Улсын хүн амын пирамид

## Description

Population distribution by age group and sex for Mongolia in 2024, from age 0 to 100+. Mongolia's 2024 population pyramid shows a relatively young population with the largest cohorts in the 30-44 age groups, reflecting birth patterns from the late 20th century.

## Variables

### Sex (Хүйс)
- `Male` / `Эрэгтэй`
- `Female` / `Эмэгтэй`

### Age Group (Насны бүлэг)
15 five-year age groups: 0-4, 5-9, 10-14, 15-19, 20-24, 25-29, 30-34, 35-39,
40-44, 45-49, 50-54, 55-59, 60-64, 65-69, 70+

### Value (Утга)
- **Unit**: Person count (2024)
- **Columns EN**: `sex`, `age_group`, `value`
- **Columns MN**: `хүйс`, `насны_бүлэг`, `утга`
- **Rows**: 30 (15 age groups x 2 sexes)

## Update Instructions

### Check for Updates

1. Query the table listing endpoint:
   ```
   GET https://data.1212.mn/api/v1/en/NSO/Population, household/1_Population, household/
   ```

2. Find `DT_NSO_0300_003V1.px` in the response

3. Compare the `updated` field with `source_updated_at` in registry

4. If API's `updated` is newer, dataset needs updating

### Fetch Data

Use the `datamn-source-nso` skill for bilingual data fetching:

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_0300_003V1.px --output ./output
```

### Data Transformation

Split filter applied to the parent table (same source as
`tools/sources/nso-1212/datasets/population-by-age-sex.md`):

1. **Filter to latest year, exclude totals**:
   - Year: latest (2024)
   - Sex: NOT Total (Male, Female only)
   - Age Group: NOT Total (all 15 age groups)

2. **Clean column names**:
   - EN: `sex`, `age_group`, `value`
   - MN: `хүйс`, `насны_бүлэг`, `утга`
   - Strip whitespace from all string columns

3. **Export files**:
   - Chart CSV: `population-pyramid-mongolia-en.csv` and `population-pyramid-mongolia-mn.csv`
   - Excel XLSX: `population-pyramid-mongolia.xlsx` (with English and Mongolian sheets)

### Validation

- All population values should be positive integers
- 30 rows expected (15 age groups x 2 sexes)
- Male + Female per age group should match the parent table's Total
- EN/MN row counts and totals must match

## Chart Configuration

### Chart Type
Population pyramid (mirrored horizontal bars)

### Visual Encoding

- **Y-axis**: age_group
- **X-axis**: population, signed by sex (negative for male, positive for female)
- **Color**: sex (Male=#3b82f6, Female=#ec4899)

### Tooltip

Display for each bar:
- Age group
- Sex
- Population count

## Content Generation

### Key Findings Template

Auto-extract for MDX page:
- Largest age group
- Working-age proportion (15-64)
- Sex ratio
- Total population (3,544,835 in 2024)

### Common Tags
- mongolia
- population
- demographics
- age
- pyramid
- census
- nso

### Keywords (EN)
- Mongolia population pyramid
- age distribution
- demographic structure

### Keywords (MN)
- Монгол хүн амын пирамид
- насны бүтэц
- хүн ам зүйн бүтэц

### Excerpt Templates

**EN**: "Population distribution by age group and sex for Mongolia in 2024, from age 0 to 100+."

**MN**: "Монгол Улсын хүн амын тархалт насны бүлэг болон хүйсээр 2024 онд, 0-өөс 100+ нас хүртэл."

## Notes

- Cross-sectional snapshot (2024 only); exempt from the wide-XLSX rule
  (see `EXEMPT_WIDE` in `tools/scripts/rebuild_downloads.py`)
- Parent table also feeds `population-by-age-sex` splits
- Early years of the parent table are census years with irregular intervals;
  this split uses the latest year only
