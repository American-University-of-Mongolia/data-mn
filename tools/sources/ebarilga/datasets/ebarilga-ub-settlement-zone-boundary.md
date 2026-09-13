# Dataset: UB settlement zone boundary

## Identification

- **ID**: `ebarilga-ub-settlement-zone-boundary`
- **Source**: `ebarilga`
- **Category**: Infrastructure
- **Tags**: [ebarilga, redevelopment, ulaanbaatar]
- **Parent**: yes — build splits from this; never publish directly

## Source Reference

- **Layer code**: `ddp_build_bound`
- **Host**: `ebarilga`
- **Geometry**: Polygon
- **Features**: 1 (counts 2026-09-13)
- **Attributes**: unprobed
- **Raw files**: `tools/sources/ebarilga/raw/ebarilga-ddp_build_bound.{geojson,csv,meta.json}`

## Title

- **EN**: UB settlement zone boundary — Ulaanbaatar (eBarilga geoportal)
- **MN**: Улаанбаатар хотын суурьшлын бүсийн хязгаар — Улаанбаатар (eBarilga геопортал)

## Description

UB settlement zone boundary in Ulaanbaatar from the eBarilga geoportal
(1 Polygon features). Attribute richness not yet surveyed; check the CSV headers.
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
python3 query_api.py --layer ddp_build_bound          # live count vs catalog
python3 fetch_data.py --layer ddp_build_bound --output ../../tools/sources/ebarilga/raw --with-attributes
```

Then re-run `.venv/bin/python tools/sources/ebarilga/derive.py` to refresh
the per-unit counts. See the `datamn-source-ebarilga` skill for paging and
rate-limit notes.

## Notes

- None
