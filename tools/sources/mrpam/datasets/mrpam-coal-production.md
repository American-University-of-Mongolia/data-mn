# mrpam-coal-production

Monthly coal production, sales, and export data from MRPAM.

## Dataset Info

| Field | Value |
|-------|-------|
| **Dataset ID** | `mrpam-coal-production` |
| **Source** | `mrpam` |
| **Source Tables** | 3.16, 3.17 (numbering varies by report edition) |
| **Update Frequency** | Monthly |
| **Units** | Thousand tons (мян.тн) |

## Description

Monthly coal production, sales, and export volumes for Mongolia. The series
uses the three-measure monthly row in the MRPAM statistical report. When a
month's own PDF is not extractable, the same monthly row is recovered from a
later report's historical table.

## CSV Schema

### English (`mrpam-coal-production-en.csv`)
```
year,month,production_kt,sales_kt,export_kt
2026,6,13036.0,11221.5,10367.4
```

### Mongolian (`mrpam-coal-production-mn.csv`)
```
он,сар,олборлолт_мян_тн,борлуулалт_мян_тн,экспорт_мян_тн
2026,6,13036.0,11221.5,10367.4
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

- Values in the dataset are the monthly rows, not annual or year-to-date totals.
- The source table's measures are production, sales, and exports, all in
  thousand tonnes.
- The May–November 2021 and March 2022 rows are recovered from later
  same-year reports because those months' individual PDFs do not yield the
  table reliably. No values are estimated.
