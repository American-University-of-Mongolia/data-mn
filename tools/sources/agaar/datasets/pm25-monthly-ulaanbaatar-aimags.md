# Dataset: PM2.5 in Ulaanbaatar and Aimag Centres by Month

## Identification
- **ID**: pm25-monthly-ulaanbaatar-aimags
- **Parent**: agaar-daily-station-means (split #1, see `agaar-daily-station-means.md`)
- **Category**: Environment / Байгаль орчин
- **Source**: agaar.gov.mn (NAMEM), see `tools/sources/agaar/source.md`

## Build
- **Table**: `tools/sources/agaar/derived/pm25-monthly-ulaanbaatar-aimags.csv`
  (month, area_en, area_mn, pm25, stations, station_days), written by `build_daily_means.py`
- **Aggregation**: monthly mean of cleaned station-day PM2.5 (µg/m³), Ulaanbaatar vs aimag centres, from 2025-10, complete months only
- **Downloads**: `-all-{en,mn}.csv` (month, area, pm25) and bilingual wide `.xlsx`
- **Chart CSVs**: `-{en,mn}.csv` also carry stations and station_days (used in tooltips)

## Update Instructions
1. Rebuild the derived table, then regenerate the CSVs/XLSX from it (month as first-of-month date).
2. Update titles, excerpt peaks and the dropped-count sentence on both pages.
