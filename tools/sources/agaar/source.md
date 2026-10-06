# agaar.gov.mn - National Air Quality Portal (NAMEM)

## Source Information

- **ID**: `agaar`
- **Name**: Air Quality Portal (National Agency for Meteorology and Environmental Monitoring)
- **Name (MN)**: Агаарын чанарын нэгдсэн систем (Цаг уур, орчны шинжилгээний газар)
- **URL**: https://agaar.gov.mn
- **Type**: API (undocumented JSON endpoints behind the website)
- **Update Frequency**: hourly
- **Language**: Mongolian only (station names/addresses need translation)

## Start here (works in any harness)

1. Station catalog: `.claude/skills/datamn-source-agaar/stations.json`, or
   `raw/agaar-stations.csv`.
2. Data: `raw/hourly/agaar-hourly-YYYY-MM.csv` and
   `raw/daily/agaar-daily-YYYY-MM.csv`, joined to stations on `station_code`.
3. What each month contains (rows, validated share, empty stations):
   `raw/agaar-pulls.json`. Pull history: `pulls.md`.
4. Build splits as new datasets; raw pulls are not registry datasets.

## Tooling

All extraction goes through the `datamn-source-agaar` skill
(`.claude/skills/datamn-source-agaar/`). Do not hand-roll requests: the
history endpoint needs a session key + cookie, and validated rows appear only
in single-calendar-month queries (see the skill docs).

```bash
cd .claude/skills/datamn-source-agaar
python3 query_api.py --list
python3 fetch_data.py --output ../../../tools/sources/agaar/raw --update
```

## Archive (IMPORTANT)

The site's history starts in 2025 (earliest row 2025-02-19; UB stations from
2025-09), and nothing guarantees it keeps old data. Once a month is
validated, the site also drops that month's hourly concentrations (AQI stays).
**This folder is the only long-term copy of those.** Run `--update` at least
monthly.

`fetch_data.py --update` runs as a scheduled task (monthly is enough). Each run
merges into the existing CSVs and never overwrites archived values (see
"The archive is merged, never overwritten" in the skill). Months still
awaiting validation are re-checked for up to 12 months.

### Size policy

Monthly hourly files are ~2–3 MB each (~30 MB/year), daily files ~100 KB.
All are committed (no Git LFS), the same as the eBarilga raw CSVs. Revisit
if the archive passes ~100 MB.

## Older data

PDF annual reports (2021–2025) and monthly reports (2025 onward) are listed at
https://agaar.gov.mn/web/detailViewDown?pMENU_SN=125. MinIO also holds
`agaar/agaar_air_quality.parquet` from an earlier scrape (see the
`datamn-minio` skill); its coverage has not been checked against this archive.

## Notes

- Units: µg/m³ for everything except CO (mg/m³).
- Hours are hour-ending (01–24) local time, UTC+8.
- `validated=1` rows are final; `0` are real-time and may be revised.
- PM2.5 is blanked where the site withholds it (`pm25_withheld=1`).
