# MRPAM - Mineral Resources and Petroleum Authority of Mongolia

## Source Information

- **ID**: `mrpam`
- **Name**: Mineral Resources and Petroleum Authority of Mongolia
- **Name (MN)**: Ашигт малтмал, газрын тосны газар
- **URL**: https://mrpam.gov.mn
- **Type**: PDF Reports
- **Update Frequency**: Monthly

## Navigation Instructions

### Finding Monthly Statistical Reports

The monthly statistical reports are published at:
```
https://mrpam.gov.mn/page/714
```

This page ("Статистикийн мэдээлэл" - Statistical Information) contains:

1. A header section with key statistics displayed as cards
2. A table listing monthly reports with download links

### Page Structure

The reports table typically has these columns:
- **№** (Number) - Row number
- **Нэр** (Name) - Report name/description
- **Огноо** (Date) - Publication date
- **Татах** (Download) - PDF download link

### Report Naming Convention

Reports follow this pattern:
```
2025.[month].stat.report.mon.pdf
```

Examples:
- `2025.1.stat.report.mon.pdf` (January 2025)
- `2025.10.stat.report.mon.pdf` (October 2025)

### Finding the Latest Report

1. Navigate to https://mrpam.gov.mn/page/714
2. Look for a table or list of reports
3. The latest report is typically at the top
4. The row contains a date and a download link (PDF icon or text)
5. Extract the date from the row
6. Click the download link to get the PDF

## Checking for Updates

To determine if new data is available:

1. **Navigate** to https://mrpam.gov.mn/page/714
2. **Take snapshot** of the page
3. **Find the reports table**:
   - Look for a table element
   - Look for rows containing PDF download links
   - Look for dates in format like "2025.10.15" or "2025-10-15"
4. **Extract the latest date** from the first row (or most recent entry)
5. **Compare** with the dataset's `last_fetched_at` in the registry
6. **Return**: `{has_update: true/false, source_date: "2025-10-15"}`

## Data Extraction

### PDF Structure

The monthly statistical report PDF typically contains these sections:

#### Page 1-2: Mining Permits Summary
- Header: "Тусгай зөвшөөрөл" (Special Permits)
- Table with permit types and counts
- Columns: Permit Type, Count, Licensed Area (hectares)

**Data to extract:**
```json
{
  "permits": {
    "exploration": {"count": N, "area_ha": N},
    "extraction": {"count": N, "area_ha": N},
    "total": {"count": N, "area_ha": N}
  }
}
```

#### Page 3-4: Coal Statistics
- Header: "Нүүрс" (Coal)
- Monthly production, export, and domestic sales figures
- Units: thousand tons (мян.тн)

**Data to extract:**
```json
{
  "coal": {
    "production_kt": N,
    "export_kt": N,
    "domestic_kt": N,
    "comparison_previous_month": N  // percentage change
  }
}
```

#### Page 5: Petroleum Statistics
- Header: "Газрын тос" (Petroleum)
- Daily production and export in barrels

**Data to extract:**
```json
{
  "petroleum": {
    "daily_production_barrels": N,
    "daily_export_barrels": N
  }
}
```

#### Other Sections (varies by report)
- Global commodity prices (gold, copper, coal)
- State budget revenue from mineral resources
- Exploration investment statistics

## Handling Page Changes

If the page structure has changed:

1. **URL change**:
   - Check the main menu for "Статистик" or "Мэдээлэл" sections
   - Search the site for "stat report" or "статистик тайлан"

2. **Table structure change**:
   - Look for PDF download links anywhere on the page
   - PDFs usually have distinctive icons or file extensions
   - Dates may be in different formats: "2025.10", "October 2025", "2025-10-15"

3. **Report format change**:
   - The PDF internal structure may change
   - Look for section headers in Mongolian
   - Tables can move between pages
   - Use header keywords to find the right tables

## Key Mongolian Terms

- Тусгай зөвшөөрөл = Special permit / License
- Хайгуулын = Exploration
- Ашиглалтын = Extraction / Mining
- Нүүрс = Coal
- Газрын тос = Petroleum / Oil
- Олборлолт = Production / Extraction
- Экспорт = Export
- Дотоодын хэрэглээ = Domestic consumption
- Баррель = Barrel
- мян.тн = thousand tons

## Language Support

**Source Language**: Mongolian
**Translation Required**: Yes

MRPAM reports are published in Mongolian only. The data.mn platform requires bilingual CSVs, so English versions must be created through translation.

### Translation Process

1. Extract data from Mongolian PDF (results in Mongolian CSV)
2. Identify categorical columns requiring translation
3. Apply standard translations using `tools/scripts/translate_csv.py`:
   ```bash
   python3 tools/scripts/translate_csv.py mrpam-coal-production-mn.csv --from mn --to en -o mrpam-coal-production-en.csv
   ```
4. Validate that both CSVs have matching structure
5. Save both versions to `public/datasets/`

### Translation Mappings

**Column Names**:
- огноо → date
- олборлолт → production
- экспорт → export
- дотоод_хэрэглээ → domestic_consumption
- тусгай_зөвшөөрөл → permit
- хайгуулын → exploration
- ашиглалтын → extraction
- талбай → area
- нүүрс → coal
- газрын_тос → petroleum

**Common Values**:
- Нүүрс → Coal
- Газрын тос → Petroleum
- Хайгуулын → Exploration
- Ашиглалтын → Extraction
- Тусгай зөвшөөрөл → Special Permit
- мян.тн → kt (thousand tons)
- баррель → barrel

## Technical Notes

- The website may have slow loading times
- PDFs are typically 5-15 MB
- Report language is Mongolian
- Some pages use JavaScript for loading content
- Playwright MCP is recommended for navigation
- All datasets must be translated to English after extraction
