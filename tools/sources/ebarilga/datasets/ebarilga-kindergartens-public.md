# Dataset: Kindergartens (public)

## Identification

- **ID**: `ebarilga-kindergartens-public`
- **Source**: `ebarilga`
- **Category**: Education
- **Tags**: [ebarilga, education, ulaanbaatar]
- **Parent**: yes — build splits from this; never publish directly

## Source Reference

- **Layer code**: `data_edu_kindergarten`
- **Host**: `ebarilga`
- **Geometry**: Point
- **Features**: 296 (counts 2026-09-13)
- **Attributes**: rich
- **Raw files**: `tools/sources/ebarilga/raw/ebarilga-data_edu_kindergarten.{geojson,csv,meta.json}`

## Title

- **EN**: Kindergartens (public) — Ulaanbaatar (eBarilga geoportal)
- **MN**: Цэцэрлэг — Улаанбаатар (eBarilga геопортал)

## Description

Kindergartens (public) in Ulaanbaatar from the eBarilga geoportal
(296 Point features). Rich Mongolian-only attributes per feature (names, addresses, permit numbers, years — varies by layer; see CSV headers).
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
python3 query_api.py --layer data_edu_kindergarten          # live count vs catalog
python3 fetch_data.py --layer data_edu_kindergarten --output ../../tools/sources/ebarilga/raw --with-attributes
```

Then re-run `.venv/bin/python tools/sources/ebarilga/derive.py` to refresh
the per-unit counts. See the `datamn-source-ebarilga` skill for paging and
rate-limit notes.

## Notes

- Name, founded year, building/classroom numbers, category
