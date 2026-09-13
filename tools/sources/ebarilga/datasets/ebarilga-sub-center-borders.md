# Dataset: Sub-center borders

## Identification

- **ID**: `ebarilga-sub-center-borders`
- **Source**: `ebarilga`
- **Category**: Infrastructure
- **Tags**: [ebarilga, zones, ulaanbaatar]
- **Parent**: yes — build splits from this; never publish directly

## Source Reference

- **Layer code**: `sub_center_border`
- **Host**: `ebarilga`
- **Geometry**: Polygon
- **Features**: 12 (counts 2026-09-13)
- **Attributes**: unprobed
- **Raw files**: `tools/sources/ebarilga/raw/ebarilga-sub_center_border.{geojson,csv,meta.json}`

## Title

- **EN**: Sub-center borders — Ulaanbaatar (eBarilga geoportal)
- **MN**: Дэд төвийн хил хязгаар — Улаанбаатар (eBarilga геопортал)

## Description

Sub-center borders in Ulaanbaatar from the eBarilga geoportal
(12 Polygon features). Attribute richness not yet surveyed; check the CSV headers.
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
python3 query_api.py --layer sub_center_border          # live count vs catalog
python3 fetch_data.py --layer sub_center_border --output ../../tools/sources/ebarilga/raw --with-attributes
```

Then re-run `.venv/bin/python tools/sources/ebarilga/derive.py` to refresh
the per-unit counts. See the `datamn-source-ebarilga` skill for paging and
rate-limit notes.

## Notes

- None
