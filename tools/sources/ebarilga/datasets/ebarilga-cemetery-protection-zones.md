# Dataset: Cemetery protection zones

## Identification

- **ID**: `ebarilga-cemetery-protection-zones`
- **Source**: `ebarilga`
- **Category**: Infrastructure
- **Tags**: [ebarilga, protection, ulaanbaatar]
- **Parent**: yes — build splits from this; never publish directly

## Source Reference

- **Layer code**: `data_pz_cemetry`
- **Host**: `ebarilga`
- **Geometry**: Polygon
- **Features**: 13 (counts 2026-09-13)
- **Attributes**: unprobed
- **Raw files**: `tools/sources/ebarilga/raw/ebarilga-data_pz_cemetry.{geojson,csv,meta.json}`

## Title

- **EN**: Cemetery protection zones — Ulaanbaatar (eBarilga geoportal)
- **MN**: Оршуулгын газрын хамгаалалтын бүс — Улаанбаатар (eBarilga геопортал)

## Description

Cemetery protection zones in Ulaanbaatar from the eBarilga geoportal
(13 Polygon features). Attribute richness not yet surveyed; check the CSV headers.
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
python3 query_api.py --layer data_pz_cemetry          # live count vs catalog
python3 fetch_data.py --layer data_pz_cemetry --output ../../tools/sources/ebarilga/raw --with-attributes
```

Then re-run `.venv/bin/python tools/sources/ebarilga/derive.py` to refresh
the per-unit counts. See the `datamn-source-ebarilga` skill for paging and
rate-limit notes.

## Notes

- None
