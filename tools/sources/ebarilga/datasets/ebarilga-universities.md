# Dataset: Universities

## Identification

- **ID**: `ebarilga-universities`
- **Source**: `ebarilga`
- **Category**: Education
- **Tags**: [ebarilga, education, ulaanbaatar]
- **Parent**: yes — build splits from this; never publish directly

## Source Reference

- **Layer code**: `data_edu_university`
- **Host**: `ebarilga`
- **Geometry**: Point
- **Features**: 112 (counts 2026-09-13)
- **Attributes**: unprobed
- **Raw files**: `tools/sources/ebarilga/raw/ebarilga-data_edu_university.{geojson,csv,meta.json}`

## Title

- **EN**: Universities — Ulaanbaatar (eBarilga geoportal)
- **MN**: Их сургууль — Улаанбаатар (eBarilga геопортал)

## Description

Universities in Ulaanbaatar from the eBarilga geoportal
(112 Point features). Attribute richness not yet surveyed; check the CSV headers.
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
python3 query_api.py --layer data_edu_university          # live count vs catalog
python3 fetch_data.py --layer data_edu_university --output ../../tools/sources/ebarilga/raw --with-attributes
```

Then re-run `.venv/bin/python tools/sources/ebarilga/derive.py` to refresh
the per-unit counts. See the `datamn-source-ebarilga` skill for paging and
rate-limit notes.

## Notes

- None
