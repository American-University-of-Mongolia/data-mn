# Dataset: Daily PM2.5 by Monitoring Station (cleaned)

## Identification
- **ID**: agaar-daily-station-means (parent, no page of its own)
- **Category**: Environment / Байгаль орчин
- **Tags**: air quality, PM2.5, pollution, ulaanbaatar, aimag

## Source Reference
- **Source**: agaar.gov.mn (NAMEM), see `tools/sources/agaar/source.md`
- **Raw archive**: `tools/sources/agaar/raw/daily/agaar-daily-YYYY-MM.csv`
- **Built file**: `tools/sources/agaar/derived/agaar-daily-station-means.csv`
  (+ `.meta.json` with coverage and dropped counts)
- **Build**: `python3 tools/sources/agaar/build_daily_means.py`. It also writes the
  four page tables `tools/sources/agaar/derived/pm25-*.csv`;
  `build_page_downloads.py` turns those into the pages' CSV/XLSX downloads.

## Variables

One row per station-day: `station_code`, `station_en`, `name_mn`, `aimag_en`,
`aimag_mn`, `ulaanbaatar` (1/0), `date`, `validated`, `pm25` (cleaned, blank when
dropped), `pm25_raw`, `pm10`, `dropped_reason`.

Units: µg/m³. Daily values are the site's own daily means; `validated=1` rows
are NAMEM-checked, the rest are real-time.

## Cleaning rules

The raw archive keeps what the site served (source.md, "Raw values are kept as
served"). This build drops a PM2.5 station-day for the first rule it meets:

| Rule | Condition |
|------|-----------|
| `negative` | PM2.5 < 0 |
| `above_pm10` | PM2.5 > 1.1 × same-day PM10 and > 50 (PM2.5 is part of PM10) |
| `spike` | PM2.5 > 5 × that day's median across all stations and > 150 |
| `flat` | Same value on 5+ consecutive days at one station (stuck sensor) |

As of the first build (data to 2026-10-06): 163 of 16,115 station-days dropped
(2 negative, 90 above PM10, 42 spike, 29 flat).
As of the 2026-11 refresh (data to 2026-11-02): 173 of 17,191 dropped
(8 negative, 94 above PM10, 42 spike, 29 flat). Every page states the rules and
the current count from `agaar-daily-station-means.meta.json`.

Pages use data from 2025-10 (first full month with Ulaanbaatar stations), and
complete months only.

Reference levels: Mongolian standard MNS 4585:2016, 24-hour PM2.5 limit
50 µg/m³; WHO 2021 guideline, 24-hour PM2.5 15 µg/m³.

## Update Instructions

Run every command from the repo root unless it says `cd`. With the conda
`datamn` environment, `python3` is enough; with the repo venv on Windows use
`.venv/Scripts/python.exe` and set `PYTHONUTF8=1` (Cyrillic output).

1. **Archive run.** The scheduled job refreshes `raw/` monthly
   (`tools/scheduled/agaar-archive/`). Never edit the raw files,
   `fetch_data.py` or `stations.json`.

2. **Check the archive run.**

   ```bash
   cd .claude/skills/datamn-source-agaar && python3 -m unittest discover -s tests && cd -
   python3 tools/sources/agaar/check_archive.py          # vs origin/main
   ```

   The tests must all pass, and `check_archive.py` must print
   `OK: 0 rows lost, 0 values lost`. If it doesn't, stop and report it.
   "Values changed" are the site revising real-time numbers and are fine.

3. **Rebuild the parent and the page tables, refresh the registry.**

   ```bash
   python3 tools/sources/agaar/build_daily_means.py
   python3 tools/sources/agaar/register.py
   ```

   Note `last_full_month`, `station_days` and `dropped_total` from the printed
   meta (also in `derived/agaar-daily-station-means.meta.json`).

4. **Write the download files.**

   ```bash
   python3 tools/sources/agaar/build_page_downloads.py
   ```

   This writes the 16 split CSVs in `data.mn/public/datasets/` from
   `derived/pm25-*.csv`, then rebuilds the XLSX and MDX `dataFiles` sizes for
   every split that changed. `--check` only reports.

5. **Update the page text by hand** (EN and MN, in frontmatter and body):
   - every page: `dataDate` = meta `last_date`, and the cleaning clause with
     the new counts: "Implausible readings (173 of 17,191 station-days) were
     removed before averaging." / "Дундажийг тооцохдоо бодит бус утгатай 173
     станц-өдрийг (нийт 17,191-ээс) хассан."
   - monthly and unhealthy-days pages: the span in the title, excerpt,
     `<VegaChart title>` and the chart JSON `description` ends at
     `last_full_month`; add the newest month's figures to the excerpt from the
     page CSV.
   - winter pages: data changes only when a new winter is added (update
     `WINTER` in `build_daily_means.py`); otherwise only the clause above.
   - Incomplete months are never shown (the build cuts at `last_full_month`).

6. **Validate.** All must pass.

   ```bash
   for id in pm25-monthly-ulaanbaatar-aimags pm25-unhealthy-days-ulaanbaatar pm25-winter-by-aimag-centre pm25-winter-by-station-ulaanbaatar; do
     python3 tools/scripts/validate_dataset.py --all $id --base-dir data.mn
   done
   python3 tools/scripts/validate_title_years.py
   python3 tools/scripts/validate_claims.py
   cd data.mn && python3 ../tools/scripts/validate_vega.py --all && cd -
   ```

7. **Look at the charts at phone width.** Start `npm run dev` in `data.mn`
   (add `-- --host` to open it on a phone on the same Wi-Fi at
   `http://<PC IP>:4321/en/data/<id>`), then:

   ```bash
   python3 tools/scripts/screenshot_charts.py pm25-monthly-ulaanbaatar-aimags pm25-unhealthy-days-ulaanbaatar pm25-winter-by-aimag-centre pm25-winter-by-station-ulaanbaatar
   ```

   (needs `pip install playwright && python3 -m playwright install chromium`).

## Splits

All splits are aggregations of the cleaned parent. Each split's
`split_filter` names its derived table.

### 1. pm25-monthly-ulaanbaatar-aimags
- **Table**: `derived/pm25-monthly-ulaanbaatar-aimags.csv`
- **Title EN**: PM2.5 in Ulaanbaatar and Aimag Centres by Month (October 2025 to October 2026)
- **Title MN**: Улаанбаатар болон аймгийн төвүүдийн PM2.5, сараар (2025 оны 10-р сараас 2026 оны 10-р сар)
- **Aggregation**: mean of cleaned station-day values per month, UB stations vs aimag-centre stations
- **Chart**: 2-line chart (month temporal x, pm25 y), dashed reference rules at 50 (MNS) and 15 (WHO)
- **split_filter**: `{"table": "pm25-monthly-ulaanbaatar-aimags", "from": "2025-10", "aggregate": "monthly mean by area"}`

### 2. pm25-unhealthy-days-ulaanbaatar
- **Table**: `derived/pm25-unhealthy-days-ulaanbaatar.csv`
- **Title EN**: Days Above Mongolia's PM2.5 Limit in Ulaanbaatar by Month (October 2025 to October 2026)
- **Title MN**: Улаанбаатарт PM2.5-ын зөвшөөрөгдөх хэмжээг давсан өдрийн тоо, сараар (2025 оны 10-р сараас 2026 оны 10-р сар)
- **Aggregation**: city daily mean = mean of UB stations (day counts only with 8+ stations); count days > 50 µg/m³
- **Chart**: bar chart, days_above_limit per month (temporal x)
- **split_filter**: `{"table": "pm25-unhealthy-days-ulaanbaatar", "from": "2025-10", "limit": 50, "min_stations": 8}`

### 3. pm25-winter-by-aimag-centre
- **Table**: `derived/pm25-winter-by-aimag-centre.csv`
- **Title EN**: Winter PM2.5 by Aimag Centre (December 2025 to February 2026)
- **Title MN**: Аймгийн төвүүдийн өвлийн PM2.5 (2025 оны 12-р сараас 2026 оны 2-р сар)
- **Aggregation**: mean of cleaned station-days, Dec 2025–Feb 2026, per aimag (Ulaanbaatar included for reference); 60+ station-days required
- **Chart**: horizontal bar chart sorted descending, Ulaanbaatar highlighted, rule at 50
- **split_filter**: `{"table": "pm25-winter-by-aimag-centre", "season": "2025-12/2026-02", "min_station_days": 60}`

### 4. pm25-winter-by-station-ulaanbaatar
- **Table**: `derived/pm25-winter-by-station-ulaanbaatar.csv`
- **Title EN**: Winter PM2.5 by Monitoring Station in Ulaanbaatar (December 2025 to February 2026)
- **Title MN**: Улаанбаатарын агаар хяналтын станцуудын өвлийн PM2.5 (2025 оны 12-р сараас 2026 оны 2-р сар)
- **Aggregation**: mean of cleaned station-days per UB station, Dec 2025–Feb 2026; 60+ days required
- **Chart**: horizontal bar chart sorted descending, rule at 50
- **split_filter**: `{"table": "pm25-winter-by-station-ulaanbaatar", "season": "2025-12/2026-02", "min_days": 60}`

## Content Generation

Minimal pages like every data page: frontmatter, the excerpt, the chart. The
page template hides body text, so the cleaning disclosure is the excerpt's last
clause: "Implausible readings (173 of 17,191 station-days) were removed before
averaging." Update the counts from `agaar-daily-station-means.meta.json` on
each refresh. The full rules live in this file and in source.md.
Related: `air-pollution-concentration` (NSO SO₂, 2002–2026), whose page notes
NSO stopped publishing PM2.5/PM10; these pages fill that gap.
