# Dataset: Pharmacies

## Identification

- **ID**: `ebarilga-pharmacies`
- **Source**: `ebarilga`
- **Category**: Health
- **Tags**: [ebarilga, health, ulaanbaatar]
- **Parent**: yes — build splits from this; never publish directly

## Source Reference

- **Layer code**: `data_clinic_pharmacy`
- **Host**: `ebarilga`
- **Geometry**: Point
- **Features**: 1016 (counts 2026-09-13)
- **Attributes**: medium
- **Raw files**: `tools/sources/ebarilga/raw/ebarilga-data_clinic_pharmacy.{geojson,csv,meta.json}`

## Title

- **EN**: Pharmacies — Ulaanbaatar (eBarilga geoportal)
- **MN**: Эмийн сан — Улаанбаатар (eBarilga геопортал)

## Description

Pharmacies in Ulaanbaatar from the eBarilga geoportal
(1016 Point features). Basic Mongolian-only attributes (usually name and/or address; see CSV headers).
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
python3 query_api.py --layer data_clinic_pharmacy          # live count vs catalog
python3 fetch_data.py --layer data_clinic_pharmacy --output ../../tools/sources/ebarilga/raw --with-attributes
```

Then re-run `.venv/bin/python tools/sources/ebarilga/derive.py` to refresh
the per-unit counts. See the `datamn-source-ebarilga` skill for paging and
rate-limit notes.

## Notes

- Name + address in sample
