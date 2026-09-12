# Dataset: Total Health Facilities in Mongolia

## Identification

- **ID**: `health-facilities-national`
- **Source**: `nso-1212`
- **Category**: Health
- **Tags**: [mongolia, health, hospitals, health-infrastructure]

## Source Reference

- **Table ID**: `DT_NSO_2100_008V3.px`
- **Sector**: `Education, health`
- **Subsector**: `Main indicators for Health sector`
- **API Path**: `/en/NSO/Education, health/Main indicators for Health sector/DT_NSO_2100_008V3.px`

## Title

- **EN**: Total Health Facilities in Mongolia (2015–2024)
- **MN**: Монгол Улсын эрүүл мэндийн байгууллагын нийт тоо (2015–2024)

## Description

Total number of registered health facilities in Mongolia from 2015 to 2024. Mongolia had 4,914 registered health facilities in 2024, up from 3,244 in 2015, reflecting a 52% increase over the decade.

## Variables

### Year (Он)
Annual data from 2015 to 2024 (10 years)

### Facilities Count (Байгууллагын тоо)
- **Unit**: Count of registered health facilities (national total)
- **Columns EN**: `year`, `facilities_count`
- **Columns MN**: `он`, `байгууллагын_тоо`
- **Rows**: 10 annual observations

## Update Instructions

### Check for Updates

1. Query the table listing endpoint:
   ```
   GET https://data.1212.mn/api/v1/en/NSO/Education, health/Main indicators for Health sector/
   ```

2. Find `DT_NSO_2100_008V3.px` in the response

3. Compare the `updated` field with `source_updated_at` in registry

4. If API's `updated` is newer, dataset needs updating

### Fetch Data

Use the `datamn-source-nso` skill for bilingual data fetching:

```bash
cd .claude/skills/datamn-source-nso
python3 fetch_data.py --table DT_NSO_2100_008V3.px --output ./output
```

### Data Transformation

1. **Filter to national total only**:
   - Keep the national aggregate series (exclude regional breakdowns if present)

2. **Clean column names**:
   - EN: `year`, `facilities_count`
   - MN: `он`, `байгууллагын_тоо`
   - Strip whitespace from all string columns

3. **Data validation**:
   - All facility counts should be positive integers
   - Year values should be valid years (2015-2024)

4. **Export files**:
   - Chart CSV: `health-facilities-national-en.csv` and `health-facilities-national-mn.csv`
   - Excel XLSX: `health-facilities-national.xlsx` (with English and Mongolian sheets)

### Validation

- Facility counts should be positive integers
- No missing years in the series
- EN/MN row counts and totals must match

## Chart Configuration

### Chart Type
Single-series line/area chart

### Visual Encoding

- **X-axis**: year (temporal)
- **Y-axis**: facilities count (quantitative)

### Tooltip

Display for each point:
- Year
- Facilities count

## Content Generation

### Key Findings Template

Auto-extract for MDX page:
- Latest year's facility count
- First year's facility count
- Percentage change over the period

### Common Tags
- mongolia
- health
- hospitals
- health-infrastructure
- nso
- annual

### Keywords (EN)
- Mongolia health facilities
- total health institutions
- hospital count Mongolia
- health infrastructure Mongolia

### Keywords (MN)
- Монгол эрүүл мэндийн байгууллага
- нийт эрүүл мэндийн байгууллага
- эмнэлгийн тоо Монгол

### Excerpt Templates

**EN**: "Mongolia had 4,914 registered health facilities in 2024, up from 3,244 in 2015, reflecting a 52% increase over the decade."

**MN**: "2024 онд Монгол Улсад 4,914 эрүүл мэндийн байгууллага бүртгэлтэй байсан бөгөөд 2015 оны 3,244-өөс 52%-иар өссөн байна."

## Notes

- National total only; regional breakdowns are out of scope for this dataset
- Values are counts of registered facilities
- Updated annually by NSO
