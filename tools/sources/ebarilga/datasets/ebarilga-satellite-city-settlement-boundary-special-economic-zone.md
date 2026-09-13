# Dataset: Satellite city settlement boundary, special economic zone

## Identification

- **ID**: `ebarilga-satellite-city-settlement-boundary-special-economic-zone`
- **Source**: `ebarilga`
- **Category**: Infrastructure
- **Tags**: [ebarilga, redevelopment, ulaanbaatar]
- **Parent**: yes — build splits from this; never publish directly

## Source Reference

- **Layer code**: `ddp_daguul_haya_hot`
- **Host**: `ebarilga`
- **Geometry**: Polygon
- **Features**: 14 (counts 2026-09-13)
- **Attributes**: unprobed
- **Raw files**: `tools/sources/ebarilga/raw/ebarilga-ddp_daguul_haya_hot.{geojson,csv,meta.json}`

## Title

- **EN**: Satellite city settlement boundary, special economic zone — Ulaanbaatar (eBarilga geoportal)
- **MN**: Дагуул хаяа хотын суурьшлын бүсийн хязгаар, Эдийн засгийн тусгай бүс — Улаанбаатар (eBarilga геопортал)

## Description

Satellite city settlement boundary, special economic zone in Ulaanbaatar from the eBarilga geoportal
(14 Polygon features). Attribute richness not yet surveyed; check the CSV headers.
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
python3 query_api.py --layer ddp_daguul_haya_hot          # live count vs catalog
python3 fetch_data.py --layer ddp_daguul_haya_hot --output ../../tools/sources/ebarilga/raw --with-attributes
```

Then re-run `.venv/bin/python tools/sources/ebarilga/derive.py` to refresh
the per-unit counts. See the `datamn-source-ebarilga` skill for paging and
rate-limit notes.

## Notes

- None
