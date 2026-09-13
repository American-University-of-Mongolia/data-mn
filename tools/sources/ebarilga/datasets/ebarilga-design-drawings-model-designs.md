# Dataset: Design drawings (model designs)

## Identification

- **ID**: `ebarilga-design-drawings-model-designs`
- **Source**: `ebarilga`
- **Category**: Infrastructure
- **Tags**: [ebarilga, buildings, ulaanbaatar]
- **Parent**: yes — build splits from this; never publish directly

## Source Reference

- **Layer code**: `plan_building`
- **Host**: `ebarilga`
- **Geometry**: Polygon
- **Features**: 25174 (counts 2026-09-13)
- **Attributes**: rich
- **Raw files**: `tools/sources/ebarilga/raw/ebarilga-plan_building.{geojson,csv,meta.json}`
- **Note**: raw GeoJSON is over 5 MB and stays on this server (see source.md Large-file policy).

## Title

- **EN**: Design drawings (model designs) — Ulaanbaatar (eBarilga geoportal)
- **MN**: Загвар зураг — Улаанбаатар (eBarilga геопортал)

## Description

Design drawings (model designs) in Ulaanbaatar from the eBarilga geoportal
(25174 Polygon features). Rich Mongolian-only attributes per feature (names, addresses, permit numbers, years — varies by layer; see CSV headers).
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
python3 query_api.py --layer plan_building          # live count vs catalog
python3 fetch_data.py --layer plan_building --output ../../tools/sources/ebarilga/raw --with-attributes
```

Then re-run `.venv/bin/python tools/sources/ebarilga/derive.py` to refresh
the per-unit counts. See the `datamn-source-ebarilga` skill for paging and
rate-limit notes.

## Notes

- Company, floors, district/khoroo/ZIP on 8/8 sampled; some have ATD + construction-permit numbers
