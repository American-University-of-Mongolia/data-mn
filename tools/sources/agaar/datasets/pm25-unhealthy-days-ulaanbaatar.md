# Dataset: Days Above Mongolia's PM2.5 Limit in Ulaanbaatar by Month

## Identification
- **ID**: pm25-unhealthy-days-ulaanbaatar (split of `agaar-daily-station-means`)
- **Source**: agaar.gov.mn (NAMEM), see `tools/sources/agaar/source.md`
- **Category**: Environment / Байгаль орчин

## Definition
Parent, cleaning rules, split filter and content guidance are in
`agaar-daily-station-means.md` (split #2). Table:
`tools/sources/agaar/derived/pm25-unhealthy-days-ulaanbaatar.csv`
(month, days_with_data, days_above_limit, max_city_mean), built by
`tools/sources/agaar/build_daily_means.py`.

A day counts when the mean of all reporting Ulaanbaatar stations (at least 8)
is above 50 µg/m³, the 24-hour PM2.5 limit in MNS 4585:2016.

## Update Instructions
Rebuild the derived table, then regenerate the CSVs, XLSX and charts
(`rebuild_downloads.py --dataset pm25-unhealthy-days-ulaanbaatar --apply`) and
refresh title spans, excerpt numbers and the dropped count.
