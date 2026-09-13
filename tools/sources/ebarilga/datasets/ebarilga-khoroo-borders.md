# Dataset: Khoroo borders

## Identification

- **ID**: `ebarilga-khoroo-borders`
- **Source**: `ebarilga`
- **Category**: Infrastructure
- **Tags**: [ebarilga, admin, ulaanbaatar]
- **Parent**: yes — build splits from this; never publish directly

## Source Reference

- **Layer code**: `khoroo_border`
- **Host**: `ebarilga`
- **Geometry**: Polygon
- **Features**: 204 (counts 2026-09-13)
- **Attributes**: medium
- **Raw files**: `tools/sources/ebarilga/raw/ebarilga-khoroo_border.{geojson,csv,meta.json}`

## Title

- **EN**: Khoroo borders — Ulaanbaatar (eBarilga geoportal)
- **MN**: Хорооны зааг — Улаанбаатар (eBarilga геопортал)

## Description

Khoroo borders in Ulaanbaatar from the eBarilga geoportal
(204 Polygon features). Basic Mongolian-only attributes (usually name and/or address; see CSV headers).
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
python3 query_api.py --layer khoroo_border          # live count vs catalog
python3 fetch_data.py --layer khoroo_border --output ../../tools/sources/ebarilga/raw --with-attributes
```

Then re-run `.venv/bin/python tools/sources/ebarilga/derive.py` to refresh
the per-unit counts. See the `datamn-source-ebarilga` skill for paging and
rate-limit notes.

## Notes

- Code + name present in WFS properties
