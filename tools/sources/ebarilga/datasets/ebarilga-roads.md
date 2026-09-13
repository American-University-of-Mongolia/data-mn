# Dataset: Roads

## Identification

- **ID**: `ebarilga-roads`
- **Source**: `ebarilga`
- **Category**: Infrastructure
- **Tags**: [ebarilga, admin, ulaanbaatar]
- **Parent**: yes — build splits from this; never publish directly

## Source Reference

- **Layer code**: `map_road`
- **Host**: `ebarilga`
- **Geometry**: Polygon
- **Features**: 5362 (counts 2026-09-13)
- **Attributes**: rich
- **Raw files**: `tools/sources/ebarilga/raw/ebarilga-map_road.{geojson,csv,meta.json}`
- **Note**: raw GeoJSON is over 5 MB and stays on this server (see source.md Large-file policy).

## Title

- **EN**: Roads — Ulaanbaatar (eBarilga geoportal)
- **MN**: Авто зам — Улаанбаатар (eBarilga геопортал)

## Description

Roads in Ulaanbaatar from the eBarilga geoportal
(5362 Polygon features). Rich Mongolian-only attributes per feature (names, addresses, permit numbers, years — varies by layer; see CSV headers).
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
python3 query_api.py --layer map_road          # live count vs catalog
python3 fetch_data.py --layer map_road --output ../../tools/sources/ebarilga/raw --with-attributes
```

Then re-run `.venv/bin/python tools/sources/ebarilga/derive.py` to refresh
the per-unit counts. See the `datamn-source-ebarilga` skill for paging and
rate-limit notes.

## Notes

- Name, class, from/to in sample
