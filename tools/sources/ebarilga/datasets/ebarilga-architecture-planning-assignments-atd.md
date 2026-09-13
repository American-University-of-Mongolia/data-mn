# Dataset: Architecture planning assignments (ATD)

## Identification

- **ID**: `ebarilga-architecture-planning-assignments-atd`
- **Source**: `ebarilga`
- **Category**: Infrastructure
- **Tags**: [ebarilga, buildings, ulaanbaatar]
- **Parent**: yes — build splits from this; never publish directly

## Source Reference

- **Layer code**: `planning_area`
- **Host**: `ebarilga`
- **Geometry**: Polygon
- **Features**: 7007 (counts 2026-09-13)
- **Attributes**: rich
- **Raw files**: `tools/sources/ebarilga/raw/ebarilga-planning_area.{geojson,csv,meta.json}`
- **Note**: raw GeoJSON is over 5 MB and stays on this server (see source.md Large-file policy).

## Title

- **EN**: Architecture planning assignments (ATD) — Ulaanbaatar (eBarilga geoportal)
- **MN**: Архитектур төлөвлөлтийн даалгавар — Улаанбаатар (eBarilga геопортал)

## Description

Architecture planning assignments (ATD) in Ulaanbaatar from the eBarilga geoportal
(7007 Polygon features). Rich Mongolian-only attributes per feature (names, addresses, permit numbers, years — varies by layer; see CSV headers).
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
python3 query_api.py --layer planning_area          # live count vs catalog
python3 fetch_data.py --layer planning_area --output ../../tools/sources/ebarilga/raw --with-attributes
```

Then re-run `.venv/bin/python tools/sources/ebarilga/derive.py` to refresh
the per-unit counts. See the `datamn-source-ebarilga` skill for paging and
rate-limit notes.

## Notes

- Permit number, purpose, floors, district/khoroo/address zone
