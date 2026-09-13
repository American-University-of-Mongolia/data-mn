# Dataset: Disaster assembly points (legacy 192)

## Identification

- **ID**: `ebarilga-disaster-assembly-points-legacy-192`
- **Source**: `ebarilga`
- **Category**: Infrastructure
- **Tags**: [ebarilga, emergency, ulaanbaatar]
- **Parent**: yes — build splits from this; never publish directly

## Source Reference

- **Layer code**: `data_gam_turtsuglarah_old_192sh`
- **Host**: `ebarilga`
- **Geometry**: Polygon
- **Features**: 190 (counts 2026-09-13)
- **Attributes**: unprobed
- **Raw files**: `tools/sources/ebarilga/raw/ebarilga-data_gam_turtsuglarah_old_192sh.{geojson,csv,meta.json}`

## Title

- **EN**: Disaster assembly points (legacy 192) — Ulaanbaatar (eBarilga geoportal)
- **MN**: Гамшгийн үед цуглах талбай_192 байршил — Улаанбаатар (eBarilga геопортал)

## Description

Disaster assembly points (legacy 192) in Ulaanbaatar from the eBarilga geoportal
(190 Polygon features). Attribute richness not yet surveyed; check the CSV headers.
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
python3 query_api.py --layer data_gam_turtsuglarah_old_192sh          # live count vs catalog
python3 fetch_data.py --layer data_gam_turtsuglarah_old_192sh --output ../../tools/sources/ebarilga/raw --with-attributes
```

Then re-run `.venv/bin/python tools/sources/ebarilga/derive.py` to refresh
the per-unit counts. See the `datamn-source-ebarilga` skill for paging and
rate-limit notes.

## Notes

- None
