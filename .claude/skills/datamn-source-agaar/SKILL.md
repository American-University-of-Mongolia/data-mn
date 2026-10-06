---
name: datamn-source-agaar
description: "Download Mongolian air quality data (PM2.5, PM10, SO2, NO2, CO, O3, AQI) from agaar.gov.mn, the NAMEM air quality portal: ~46 monitoring stations in Ulaanbaatar and every aimag centre, hourly and daily since 2025, no auth. Use when adding or refreshing air pollution / smog / AQI datasets, or running the archive job that preserves hourly detail the site drops after validation."
dependencies:
  - python3
---

# agaar.gov.mn Air Quality Data Source Skill

This skill pulls station measurements from `https://agaar.gov.mn`, the
national air quality portal run by NAMEM (Цаг уур, орчны шинжилгээний газар).
The site has no published API; these scripts call the same JSON endpoints its
pages use.

When saving data never put it inside the skills/datamn-source-agaar folder.
The archive lives in `tools/sources/agaar/raw/` (see `tools/sources/agaar/source.md`).

## Overview

| Field | Value |
|-------|-------|
| Source ID | `agaar` |
| Organization | Цаг уур, орчны шинжилгээний газар (NAMEM) |
| Website | https://agaar.gov.mn |
| Data Type | api (undocumented form-POST JSON endpoints) |
| Update Frequency | hourly |
| Language | mn (station names/addresses Mongolian only; translation required) |

## ⚠️ Archive it: the site loses detail

- **History starts in 2025** (checked 2026-10-03): the earliest row is
  2025-02-19 (station 10501, daily only; hourly starts 2025-06). Coverage
  grows through 2025, and the Ulaanbaatar stations begin in September 2025. This looks like the start of the
  current system, not a rolling window, but nothing guarantees the site
  keeps old data. Older years exist only as PDF reports (see "Older data").
- **Hourly concentrations disappear once a month is validated** (verified:
  validated hourly rows carry AQI only). The archive in
  `tools/sources/agaar/raw/` is the only place they survive.

Run `fetch_data.py --update` at least monthly.

## Authentication

None. The history endpoint does need a **session key**: a UUID embedded in the
`/web/realSearch` page, valid only with the session cookie it was issued with.
`agaar_client.py` handles this (cookie jar + key scrape + one automatic re-issue
when the server answers `{}`).

## Available Data

- **Stations**: 46 in the catalog (`stations.json`): 22 in Ulaanbaatar (codes
  123xx–129xx), the rest in aimag centres (one each, three in Orkhon and two in Khentii). Each has lat/lon and aimag.
  Not every station measures every pollutant; some report nothing for months.
- **Pollutants**: PM10, PM2.5, O3, NO2, SO2 in µg/m³; **CO in mg/m³**.
- **Hourly**: per-station values plus AQI, the AQI's main pollutant and
  grade, and 24-hour running means for PM10/PM2.5.
- **Daily**: per-station daily means as published by the site.

## Browsing the Catalog

```bash
cd .claude/skills/datamn-source-agaar

python3 query_api.py --list                 # all stations
python3 query_api.py --list --aimag 11      # Ulaanbaatar only
python3 query_api.py хороолол               # search name/address/aimag/code
python3 query_api.py --station 12401        # details + live last 24 hours
python3 query_api.py --latest pm25          # latest hour, every station
python3 query_api.py --refresh              # re-scrape catalog -> stations.json
```

`--refresh` keeps hand-added fields (`name_en`, `notes`) and flags stations that
appeared or vanished; vanished stations stay in the catalog with `listed: false`
so their archived history still joins. `items_live` lists only the pollutants
reporting at refresh time, so treat it as a hint, not the station's full spec.

## Data Fetching

```bash
# Full backfill (everything the site serves, from 2025-02) -> ~1,800 requests, ~1.5 h
python3 fetch_data.py --output ../../../tools/sources/agaar/raw

# Routine archive run: re-fetch the last 3 months (catches late validation)
python3 fetch_data.py --output ../../../tools/sources/agaar/raw --update

# Testing / one-offs
python3 fetch_data.py --output /tmp/agaar --from 2026-01 --to 2026-01 \
    --stations 12401,10101 --freq daily
```

Options: `--freq hourly|daily|both`, `--from/--to YYYY-MM`, `--stations`,
`--refresh-months N` (default 3), `--force`, `--delay` (default 1.0 s).
Completed past months are skipped on re-runs; the last N months are always
re-fetched. Interrupting is safe: every finished month is already on disk.

### How the endpoint behaves (read before changing the fetcher)

`POST /web/pollution/getRealChart` with `dateDiv` (1 = hourly, 2 = daily),
`stationCode`, `from_date`/`to_date` as `YYYYMMDDHH`, `key`, `token=""`.

- **Query one calendar month at a time.** Validated rows (`LASTDATA=Y`, shown
  in blue on the site) come back only for the month the range *starts* in;
  a year-long query returns mostly real-time rows. The site's 60-day limit
  is enforced only in the browser, so this is a data-quality rule, not a cap.
- **Daily** returns a real-time row and, once checked, a validated row for the
  same day; the fetcher keeps the validated one (`validated=1`).
- **Hourly validated rows carry AQI only, with no concentrations.** Once a
  month has been validated, its hourly pollutant values come back null (the
  site's own table and its Excel export show the same blanks). For those
  months the concentrations exist only as validated **daily** means. Hourly
  concentrations for a month exist only until it is validated, which is
  another reason to archive often. `agaar-pulls.json` records
  `rows_with_concentrations` per month so this is visible.
- Hours are **hour-ending 01–24**, local time (UTC+8). `hour=24` is the hour
  ending at midnight. The fetcher adds `datetime` = start of the hour window.
- `PM25_YN=N` means the site withholds PM2.5 for that row. The fetcher blanks
  it as well and sets `pm25_withheld=1`.
- `{}` = session key rejected; `{"charts": []}` = genuinely no data.
- **Server error page on some station-days.** The site's PM2.5-visibility
  SQL fails for certain station+day combinations (seen in daily queries, 1–2
  days per affected station-month), and the same range fails every time.
  The fetcher then halves the range until it isolates the bad days, skips
  them, and lists them as `unavailable_days` in `agaar-pulls.json`.
  Sub-month queries sometimes return fewer validated rows than a full-month
  query, so recovered station-months may be marked real-time where validated
  data exists.
- Rows with every value empty are dropped (stations offline).

## Output Format

```
tools/sources/agaar/raw/
├── hourly/agaar-hourly-YYYY-MM.csv
├── daily/agaar-daily-YYYY-MM.csv
├── agaar-stations.csv
└── agaar-pulls.json      # per freq+month: rows, validated rows, empty/failed stations
```

```csv
# hourly
station_code,datetime,date,hour,validated,pm10,pm25,o3,no2,co,so2,pm10_24h,pm25_24h,aqi,aqi_pollutant,aqi_grade,pm25_withheld
12401,2025-12-15 20:00,2025-12-15,21,0,76,72,,83.8,,54.2,107,82,117,pm25,3,0
# daily
station_code,date,validated,pm10,pm25,o3,no2,co,so2,pm25_withheld
10101,2026-01-01,1,,133.8,,19.4,,18.6,0
```

AQI grades: 1 цэвэр (clean), 2 хэвийн (normal), 3 бага бохирдолтой (lightly
polluted), 4 бохирдолтой (polluted), 5 их бохирдолтой (heavily polluted),
6 маш их бохирдолтой (very heavily polluted).

## Older data (before the API window)

`/web/detailViewDown?pMENU_SN=125` lists PDF reports downloadable from
`/jfile/readDownloadFile.do?fileId=<id>&fileSeq=1`: annual reports 2021–2025
and monthly reports from 2025 onward (some months missing). Use
`datamn-extract-pdf` for their summary tables; they do not contain hourly data.

## Language Support

**Source Language**: Mongolian. **Translation Required**: Yes, for station
names and addresses only; codes, dates and values are language-neutral.
Translate `agaar-stations.csv` with `tools/scripts/translate_csv.py` (or add
`name_en` in `stations.json`), then join on `station_code`.

## Dataset ID Convention

`agaar-<topic>`: `agaar-ub-pm25-daily`, `agaar-aimag-centre-pm25-monthly`,
`agaar-stations`, ...

## Source Registration

```python
from registry import Registry
reg = Registry()
reg.add_source(source_id="agaar",
               name_en="Air Quality Portal (NAMEM)",
               name_mn="Агаарын чанарын нэгдсэн систем (ЦУОШГ)",
               type="api", base_url="https://agaar.gov.mn",
               update_frequency="hourly", enabled=True)
```

## Other endpoints (for debugging)

All `POST`, form-encoded, no key needed:

- `/web/mRealAirInfoAjax` `itemCode=<code>`: latest hour, all stations, lat/lon
- `/web/mMainSidoAirInfoAjax` `itemCode=<code>`: latest hour per aimag (`AREA_n`)
- `/web/vicinityStationTimeAjax` `item_code`, `station_code`: last 24 hours
- `/web/mItemAreaForecastAjax` `quality`, `increaseDay` (0–2), `forecastTime`: forecast

Item codes: 10007 PM10, 10008 PM2.5, 10003 O3, 10006 NO2, 10002 CO, 10001 SO2.

## Common Issues

1. **Every response is `{}`**: key/cookie mismatch. Use `AgaarClient`, never
   reuse a key across sessions.
2. **Hourly month with AQI but no concentrations**: expected for validated
   months (see above); use the daily files for concentrations.
3. **Station with no rows**: offline or decommissioned; the manifest lists it
   under `stations_empty`.
4. **Station catalog changed**: run `query_api.py --refresh`, review the diff
   in `stations.json`, commit it.

## Notes

- Be polite: a small government server. Keep `--delay` ≥ 1 s and never
  parallelize.
- Data is preliminary until validated; say so on dataset pages and show the
  `validated` share.
