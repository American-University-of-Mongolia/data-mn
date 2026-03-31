# mrpam-coal-production

Monthly coal production, export, and domestic consumption data from MRPAM.

## Dataset Info

| Field | Value |
|-------|-------|
| **Dataset ID** | `mrpam-coal-production` |
| **Source** | `mrpam` |
| **Source Tables** | 3.16, 3.17 |
| **Update Frequency** | Monthly |
| **Units** | Thousand tons (мян.тн) |

## Description

Monthly breakdown of coal production, export volume, and domestic consumption in Mongolia. Sourced from Tables 3.16 and 3.17 of the MRPAM monthly statistical report.

## CSV Schema

### English (`mrpam-coal-production-en.csv`)
```
year,month,production_kt,export_kt,domestic_kt
2025,1,4250.5,3100.2,350.1
```

### Mongolian (`mrpam-coal-production-mn.csv`)
```
он,сар,олборлолт_мян_тн,экспорт_мян_тн,дотоод_мян_тн
2025,1,4250.5,3100.2,350.1
```

## Extraction

```bash
cd .claude/skills/datamn-source-mrpam

# Download 2025 reports
conda run -n datamn python3 fetch_report.py --year 2025

# Extract coal production from all 2025 PDFs
conda run -n datamn python3 extract_tables.py --dataset mrpam-coal-production --year 2025

# Translate to English
conda run -n datamn python3 tools/scripts/translate_csv.py \
  tools/temp/mrpam-extracted/mrpam-coal-production-mn.csv \
  --from mn --to en \
  -o tools/temp/mrpam-extracted/mrpam-coal-production-en.csv
```

## Section Keywords

Search for pages containing: `нүүрс`, `3.16`, `3.17`

## Notes

- Values are cumulative year-to-date in some report versions; verify row labels
- `domestic_kt` = дотоодын хэрэглээ (domestic consumption)
- Some early reports (2021) may combine production and export in a single table
