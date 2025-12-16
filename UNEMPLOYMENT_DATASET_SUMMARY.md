# Unemployment Rate Dataset Addition - Summary

## Task Completed
Added comprehensive unemployment rate datasets to data.mn from NSO 1212.mn API (Table ID: DT_NSO_0400_049V1.px)

## Datasets Created

### Parent Dataset
- **nso-unemployment-rate** - Complete raw dataset with all categories (240 rows)
  - Source: NSO 1212.mn
  - Table: "8.5.2 UNEMPLOYMENT RATE, by sex, age group, persons with disabilities, and by year"
  - Categories: Total, Male, Female, Urban, Rural, Age groups, Regions, Disability status

### Split Datasets (6 user-friendly datasets)

1. **unemployment-rate-total**
   - Overall unemployment rate in Mongolia (2009-2024)
   - 16 data points
   - Published URL: `/en/data/unemployment-rate-total` and `/mn/data/unemployment-rate-total`

2. **unemployment-rate-by-sex**
   - Unemployment rate by sex (Male vs Female)
   - 32 data points
   - Published URL: `/en/data/unemployment-rate-by-sex` and `/mn/data/unemployment-rate-by-sex`

3. **unemployment-rate-youth**
   - Youth unemployment rate (ages 15-24)
   - 16 data points
   - Published URL: `/en/data/unemployment-rate-youth` and `/mn/data/unemployment-rate-youth`

4. **unemployment-rate-by-age**
   - Unemployment rate by age group (15-24, 25-64, 65+)
   - 48 data points
   - Published URL: `/en/data/unemployment-rate-by-age` and `/mn/data/unemployment-rate-by-age`

5. **unemployment-rate-by-location**
   - Unemployment rate by location (Urban, Rural, Ulaanbaatar)
   - 48 data points
   - Published URL: `/en/data/unemployment-rate-by-location` and `/mn/data/unemployment-rate-by-location`

6. **unemployment-rate-by-region**
   - Unemployment rate by region (Central, Western, Khangai, Eastern)
   - 64 data points
   - Published URL: `/en/data/unemployment-rate-by-region` and `/mn/data/unemployment-rate-by-region`

## Files Generated

### CSV Files (14 total)
- 7 English CSVs: `*-en.csv`
- 7 Mongolian CSVs: `*-mn.csv`
- Location: `data.mn/public/datasets/`

### XLSX Files (7 total)
- Each with bilingual sheets (English + Mongolian)
- Location: `data.mn/public/datasets/`

### Chart Specifications (14 total)
- 7 English charts: `*-en.json`
- 7 Mongolian charts: `*-mn.json`
- Location: `data.mn/public/charts/`
- All charts validated with Vega-Lite validator

### MDX Pages (14 total)
- 7 English pages: `src/data/data/en/*.mdx`
- 7 Mongolian pages: `src/data/data/mn/*.mdx`
- All pages validated with proper frontmatter format

## Registry Status

- **Parent dataset**: `nso-unemployment-rate` (registered)
- **Split datasets**: All 6 splits registered and published
- **Category**: Economy / Labor Market
- **Source**: nso-1212
- **Auto-update**: Enabled
- **Auto-publish**: Enabled

## Technical Details

### Data Source
- **API**: NSO 1212.mn
- **Table ID**: DT_NSO_0400_049V1.px
- **Coverage**: 2009-2024 (16 years)
- **Update frequency**: Annual

### Category Translation Mapping
Created mapping for English-Mongolian category values:
- Total → Бүгд
- Male → Эрэгтэй
- Female → Эмэгтэй
- Urban → Хот
- Rural → Хөдөө
- Age groups: 15-24 насны, 25-64 насны, 65 болон түүнээс дээш насны
- Regions: Төвийн бүс, Баруун бүс, Хангайн бүс, Зүүн бүс
- Disability: Хөгжлийн бэрхшээлтэй, Хөгжлийн бэрхшээлгүй

### Chart Types
- Single line charts: Total, Youth
- Multi-line charts: By Sex, By Age, By Location, By Region
- All charts include:
  - Quantitative year axis
  - Formatted percentage axis
  - Proper bilingual labels
  - CSV format specification

## Validation Results
✅ All 9 file types validated per dataset:
- MDX pages (EN + MN)
- CSV files (EN + MN)
- XLSX files
- Chart JSON (EN + MN)
- Chart-CSV cross-validation

## Scripts Created

1. **create_unemployment_datasets.py** - Initial comprehensive creation script
2. **fix_unemployment_charts_and_mdx.py** - Fixed bilingual chart creation
3. **recreate_unemployment_csvs.py** - Fixed bilingual CSV generation with proper category mapping

## Known Issues Resolved

1. ✅ Mongolian CSV files initially empty - Fixed with proper category translation
2. ✅ Charts missing bilingual versions - Created `-en.json` and `-mn.json` versions
3. ✅ MDX pages using old format - Regenerated with `generate_mdx.py` script
4. ✅ File size calculation - Auto-calculated from actual files

## Next Steps

1. Test locally: `cd data.mn && npm run dev`
2. View datasets at:
   - http://localhost:4321/en/data/unemployment-rate-total
   - http://localhost:4321/mn/data/unemployment-rate-total
   - (and other split URLs)
3. Deploy when ready: `kamal deploy`

## URLs (Production)
Once deployed, datasets will be available at:
- English: `https://data.mn/en/data/unemployment-rate-*`
- Mongolian: `https://data.mn/mn/data/unemployment-rate-*`

All URLs are permanent (URL stability guaranteed via registry publish system).

---
Generated: 2025-12-07
