# Dataset: Tech park roads

## Identification

- **ID**: `ebarilga-tech-park-roads`
- **Source**: `ebarilga`
- **Category**: Infrastructure
- **Tags**: [ebarilga, zones, ulaanbaatar]
- **Parent**: yes — build splits from this; never publish directly

## Source Reference

- **Layer code**: `technological_park_planning_road`
- **Host**: `ebarilga`
- **Geometry**: Polygon
- **Features**: 10 (counts 2026-09-13)
- **Attributes**: unprobed
- **Raw files**: `tools/sources/ebarilga/raw/ebarilga-technological_park_planning_road.{geojson,csv,meta.json}`

## Title

- **EN**: Tech park roads — Ulaanbaatar (eBarilga geoportal)
- **MN**: Үйлдвэр технологийн паркийн зам — Улаанбаатар (eBarilga геопортал)

## Description

Tech park roads in Ulaanbaatar from the eBarilga geoportal
(10 Polygon features). Attribute richness not yet surveyed; check the CSV headers.
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
python3 query_api.py --layer technological_park_planning_road          # live count vs catalog
python3 fetch_data.py --layer technological_park_planning_road --output ../../tools/sources/ebarilga/raw --with-attributes
```

Then re-run `.venv/bin/python tools/sources/ebarilga/derive.py` to refresh
the per-unit counts. See the `datamn-source-ebarilga` skill for paging and
rate-limit notes.

## Notes

- None
