# Dataset: Apartment complexes

## Identification

- **ID**: `ebarilga-apartment-complexes`
- **Source**: `ebarilga`
- **Category**: Infrastructure
- **Tags**: [ebarilga, poi, ulaanbaatar]
- **Parent**: yes — build splits from this; never publish directly

## Source Reference

- **Layer code**: `town_2023`
- **Host**: `ebarilga`
- **Geometry**: MultiPolygon
- **Features**: 327 (counts 2026-09-13)
- **Attributes**: thin
- **Raw files**: `tools/sources/ebarilga/raw/ebarilga-town_2023.{geojson,csv,meta.json}`

## Title

- **EN**: Apartment complexes — Ulaanbaatar (eBarilga geoportal)
- **MN**: Хотхон, хороолол — Улаанбаатар (eBarilga геопортал)

## Description

Apartment complexes in Ulaanbaatar from the eBarilga geoportal
(327 MultiPolygon features). Geometry only — attribute records carry no useful fields.
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
python3 query_api.py --layer town_2023          # live count vs catalog
python3 fetch_data.py --layer town_2023 --output ../../tools/sources/ebarilga/raw
```

Then re-run `.venv/bin/python tools/sources/ebarilga/derive.py` to refresh
the per-unit counts. See the `datamn-source-ebarilga` skill for paging and
rate-limit notes.

## Notes

- Sampled records had layer type only, no names
- Plan for spatial joins against khoroo/ZIP polygons, not attribute analysis.
