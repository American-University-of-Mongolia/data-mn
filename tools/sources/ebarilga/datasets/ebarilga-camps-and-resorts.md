# Dataset: Camps and resorts

## Identification

- **ID**: `ebarilga-camps-and-resorts`
- **Source**: `ebarilga`
- **Category**: Infrastructure
- **Tags**: [ebarilga, poi, ulaanbaatar]
- **Parent**: yes — build splits from this; never publish directly

## Source Reference

- **Layer code**: `data_pub_camp_resorts`
- **Host**: `ebarilga`
- **Geometry**: Point
- **Features**: 114 (counts 2026-09-13)
- **Attributes**: unprobed
- **Raw files**: `tools/sources/ebarilga/raw/ebarilga-data_pub_camp_resorts.{geojson,csv,meta.json}`

## Title

- **EN**: Camps and resorts — Ulaanbaatar (eBarilga geoportal)
- **MN**: Амралтын газар — Улаанбаатар (eBarilga геопортал)

## Description

Camps and resorts in Ulaanbaatar from the eBarilga geoportal
(114 Point features). Attribute richness not yet surveyed; check the CSV headers.
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
python3 query_api.py --layer data_pub_camp_resorts          # live count vs catalog
python3 fetch_data.py --layer data_pub_camp_resorts --output ../../tools/sources/ebarilga/raw --with-attributes
```

Then re-run `.venv/bin/python tools/sources/ebarilga/derive.py` to refresh
the per-unit counts. See the `datamn-source-ebarilga` skill for paging and
rate-limit notes.

## Notes

- 1 poison feature(s) skipped during pull (unfetchable server-side): [6536].
