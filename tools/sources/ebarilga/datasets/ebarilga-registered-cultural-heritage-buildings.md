# Dataset: Registered cultural heritage buildings

## Identification

- **ID**: `ebarilga-registered-cultural-heritage-buildings`
- **Source**: `ebarilga`
- **Category**: Infrastructure
- **Tags**: [ebarilga, culture, ulaanbaatar]
- **Parent**: yes — build splits from this; never publish directly

## Source Reference

- **Layer code**: `Cultural_heritage_building`
- **Host**: `ebarilga`
- **Geometry**: Polygon
- **Features**: 39 (counts 2026-09-13)
- **Attributes**: rich
- **Raw files**: `tools/sources/ebarilga/raw/ebarilga-Cultural_heritage_building.{geojson,csv,meta.json}`

## Title

- **EN**: Registered cultural heritage buildings — Ulaanbaatar (eBarilga geoportal)
- **MN**: Соёлын өвд бүртгэлтэй дурсгалт барилга — Улаанбаатар (eBarilga геопортал)

## Description

Registered cultural heritage buildings in Ulaanbaatar from the eBarilga geoportal
(39 Polygon features). Rich Mongolian-only attributes per feature (names, addresses, permit numbers, years — varies by layer; see CSV headers).
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
python3 query_api.py --layer Cultural_heritage_building          # live count vs catalog
python3 fetch_data.py --layer Cultural_heritage_building --output ../../tools/sources/ebarilga/raw --with-attributes
```

Then re-run `.venv/bin/python tools/sources/ebarilga/derive.py` to refresh
the per-unit counts. See the `datamn-source-ebarilga` skill for paging and
rate-limit notes.

## Notes

- Purpose, district/khoroo/address zone; designation in object_name
