# Dataset: Built buildings

## Identification

- **ID**: `ebarilga-built-buildings`
- **Source**: `ebarilga`
- **Category**: Infrastructure
- **Tags**: [ebarilga, buildings, ulaanbaatar]
- **Parent**: yes — build splits from this; never publish directly

## Source Reference

- **Layer code**: `built_building`
- **Host**: `ebarilga`
- **Geometry**: Polygon
- **Features**: 325072 (counts 2026-09-13)
- **Attributes**: thin
- **Raw files**: `tools/sources/ebarilga/raw/ebarilga-built_building.{geojson,csv,meta.json}`
- **Note**: raw GeoJSON is over 5 MB and stays on this server (see source.md Large-file policy).

## Title

- **EN**: Built buildings — Ulaanbaatar (eBarilga geoportal)
- **MN**: Баригдсан барилга — Улаанбаатар (eBarilga геопортал)

## Description

Built buildings in Ulaanbaatar from the eBarilga geoportal
(325072 Polygon features). Geometry only — attribute records carry no useful fields.
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
python3 query_api.py --layer built_building          # live count vs catalog
python3 fetch_data.py --layer built_building --output ../../tools/sources/ebarilga/raw
```

Then re-run `.venv/bin/python tools/sources/ebarilga/derive.py` to refresh
the per-unit counts. See the `datamn-source-ebarilga` skill for paging and
rate-limit notes.

## Notes

- Only ~12% have object_name; rest geometry-only
- Plan for spatial joins against khoroo/ZIP polygons, not attribute analysis.
