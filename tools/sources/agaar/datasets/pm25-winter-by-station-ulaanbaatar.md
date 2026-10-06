# Dataset: Winter PM2.5 by Monitoring Station in Ulaanbaatar

## Identification
- **ID**: pm25-winter-by-station-ulaanbaatar (split of `agaar-daily-station-means`)
- **Source**: agaar.gov.mn (NAMEM), see `tools/sources/agaar/source.md`
- **Category**: Environment / Байгаль орчин

## Definition
Parent, cleaning rules, split filter and content guidance are in
`agaar-daily-station-means.md` (split #4). Table:
`tools/sources/agaar/derived/pm25-winter-by-station-ulaanbaatar.csv`, built by
`tools/sources/agaar/build_daily_means.py`. Season: December 2025 to
February 2026; bars need 60+ valid station-days.

## Update Instructions
Changes only when a new winter is added: update `WINTER` in the build script,
rebuild, then regenerate the CSVs, XLSX and charts
(`rebuild_downloads.py --dataset pm25-winter-by-station-ulaanbaatar --apply`) and refresh the title, excerpt
numbers and the dropped count.
