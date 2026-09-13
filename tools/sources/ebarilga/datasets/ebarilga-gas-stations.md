# Dataset: Gas stations

## Identification

- **ID**: `ebarilga-gas-stations`
- **Source**: `ebarilga`
- **Category**: Infrastructure
- **Tags**: [ebarilga, poi, ulaanbaatar]
- **Parent**: yes — build splits from this; never publish directly

## Source Reference

- **Layer code**: `data_auto_shts`
- **Host**: `ebarilga`
- **Geometry**: Point
- **Features**: 192 (counts 2026-09-13)
- **Attributes**: unprobed
- **Raw files**: `tools/sources/ebarilga/raw/ebarilga-data_auto_shts.{geojson,csv,meta.json}`

## Title

- **EN**: Gas stations — Ulaanbaatar (eBarilga geoportal)
- **MN**: ШТС — Улаанбаатар (eBarilga геопортал)

## Description

Gas stations in Ulaanbaatar from the eBarilga geoportal
(192 Point features). Attribute richness not yet surveyed; check the CSV headers.
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
python3 query_api.py --layer data_auto_shts          # live count vs catalog
python3 fetch_data.py --layer data_auto_shts --output ../../tools/sources/ebarilga/raw --with-attributes
```

Then re-run `.venv/bin/python tools/sources/ebarilga/derive.py` to refresh
the per-unit counts. See the `datamn-source-ebarilga` skill for paging and
rate-limit notes.

## Notes

- None
