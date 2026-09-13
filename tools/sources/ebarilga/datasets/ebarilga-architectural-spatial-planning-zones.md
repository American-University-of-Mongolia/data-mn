# Dataset: Architectural spatial planning zones

## Identification

- **ID**: `ebarilga-architectural-spatial-planning-zones`
- **Source**: `ebarilga`
- **Category**: Infrastructure
- **Tags**: [ebarilga, zones, ulaanbaatar]
- **Parent**: yes — build splits from this; never publish directly

## Source Reference

- **Layer code**: `ddt_aoz_tuluvlult_2030`
- **Host**: `ebarilga`
- **Geometry**: Polygon
- **Features**: 5390 (counts 2026-09-13)
- **Attributes**: medium
- **Raw files**: `tools/sources/ebarilga/raw/ebarilga-ddt_aoz_tuluvlult_2030.{geojson,csv,meta.json}`
- **Note**: raw GeoJSON is over 5 MB and stays on this server (see source.md Large-file policy).

## Title

- **EN**: Architectural spatial planning zones — Ulaanbaatar (eBarilga geoportal)
- **MN**: Архитектур орон зайн төлөвлөлтийн бүсчлэл — Улаанбаатар (eBarilga геопортал)

## Description

Architectural spatial planning zones in Ulaanbaatar from the eBarilga geoportal
(5390 Polygon features). Basic Mongolian-only attributes (usually name and/or address; see CSV headers).
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
python3 query_api.py --layer ddt_aoz_tuluvlult_2030          # live count vs catalog
python3 fetch_data.py --layer ddt_aoz_tuluvlult_2030 --output ../../tools/sources/ebarilga/raw --with-attributes
```

Then re-run `.venv/bin/python tools/sources/ebarilga/derive.py` to refresh
the per-unit counts. See the `datamn-source-ebarilga` skill for paging and
rate-limit notes.

## Notes

- Zone + name in sample
- 1 poison feature(s) skipped during pull (unfetchable server-side): [76803].
