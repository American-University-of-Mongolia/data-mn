# Dataset: Substation protection zones

## Identification

- **ID**: `ebarilga-substation-protection-zones`
- **Source**: `ebarilga`
- **Category**: Infrastructure
- **Tags**: [ebarilga, protection, ulaanbaatar]
- **Parent**: yes — build splits from this; never publish directly

## Source Reference

- **Layer code**: `pz_city_substation`
- **Host**: `transco`
- **Geometry**: Polygon
- **Features**: 39 (counts 2026-09-13)
- **Attributes**: unprobed
- **Raw files**: `tools/sources/ebarilga/raw/ebarilga-pz_city_substation.{geojson,csv,meta.json}`

## Title

- **EN**: Substation protection zones — Ulaanbaatar (eBarilga geoportal)
- **MN**: Дамжуулах сүлжээний дэд станц хамгаалалтын зурвас — Улаанбаатар (eBarilga геопортал)

## Description

Substation protection zones in Ulaanbaatar from the eBarilga geoportal
(39 Polygon features). Attribute richness not yet surveyed; check the CSV headers.
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
python3 query_api.py --layer pz_city_substation          # live count vs catalog
python3 fetch_data.py --layer pz_city_substation --output ../../tools/sources/ebarilga/raw --with-attributes --insecure-tls
```

Then re-run `.venv/bin/python tools/sources/ebarilga/derive.py` to refresh
the per-unit counts. See the `datamn-source-ebarilga` skill for paging and
rate-limit notes.

## Notes

- External host grid.transco.mn; TLS cert invalid, needs --insecure-tls
- Lives on grid.transco.mn (external host, invalid TLS certificate — fetch requires --insecure-tls).
