# Dataset: Sub-center roads

## Identification

- **ID**: `ebarilga-sub-center-roads`
- **Source**: `ebarilga`
- **Category**: Infrastructure
- **Tags**: [ebarilga, zones, ulaanbaatar]
- **Parent**: yes — build splits from this; never publish directly

## Source Reference

- **Layer code**: `plannig_road`
- **Host**: `ebarilga`
- **Geometry**: Polygon
- **Features**: 30 (counts 2026-09-13)
- **Attributes**: unprobed
- **Raw files**: `tools/sources/ebarilga/raw/ebarilga-plannig_road.{geojson,csv,meta.json}`

## Title

- **EN**: Sub-center roads — Ulaanbaatar (eBarilga geoportal)
- **MN**: Дэд төвийн авто зам — Улаанбаатар (eBarilga геопортал)

## Description

Sub-center roads in Ulaanbaatar from the eBarilga geoportal
(30 Polygon features). Attribute richness not yet surveyed; check the CSV headers.
All names, addresses, and attribute values are Mongolian-only; splits need
the standard MN→EN translation pass.

## Variables

Base columns (present in every ebarilga CSV):

- `id`
- `object_no`
- `object_name`
- `geom_type`
- `lon`
- `lat`

- `lon`/`lat` is the point coordinate, or the bbox center for lines/polygons
  (approximation — use the GeoJSON for exact shapes).
- Attribute columns (Mongolian headers) follow; see the CSV header row.

## Update Instructions

```bash
cd .claude/skills/datamn-source-ebarilga
python3 query_api.py --layer plannig_road          # live count vs catalog
python3 fetch_data.py --layer plannig_road --output ../../tools/sources/ebarilga/raw --with-attributes
```

Then re-run `.venv/bin/python tools/sources/ebarilga/derive.py` to refresh
the per-unit counts. See the `datamn-source-ebarilga` skill for paging and
rate-limit notes.

## Notes

- Note: code misspelled on server (plannig)
