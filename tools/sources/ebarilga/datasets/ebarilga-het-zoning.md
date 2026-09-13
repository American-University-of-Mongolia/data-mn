# Dataset: HET zoning

## Identification

- **ID**: `ebarilga-het-zoning`
- **Source**: `ebarilga`
- **Category**: Infrastructure
- **Tags**: [ebarilga, redevelopment, ulaanbaatar]
- **Parent**: yes — build splits from this; never publish directly

## Source Reference

- **Layer code**: `ddp_het_buschlel`
- **Host**: `ebarilga`
- **Geometry**: Polygon
- **Features**: 5306 (counts 2026-09-13)
- **Attributes**: unprobed
- **Raw files**: `tools/sources/ebarilga/raw/ebarilga-ddp_het_buschlel.{geojson,csv,meta.json}`
- **Note**: raw GeoJSON is over 5 MB and stays on this server (see source.md Large-file policy).

## Title

- **EN**: HET zoning — Ulaanbaatar (eBarilga geoportal)
- **MN**: ХЕТ-ний бүсчлэл — Улаанбаатар (eBarilga геопортал)

## Description

HET zoning in Ulaanbaatar from the eBarilga geoportal
(5306 Polygon features). Attribute richness not yet surveyed; check the CSV headers.
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
python3 query_api.py --layer ddp_het_buschlel          # live count vs catalog
python3 fetch_data.py --layer ddp_het_buschlel --output ../../tools/sources/ebarilga/raw --with-attributes
```

Then re-run `.venv/bin/python tools/sources/ebarilga/derive.py` to refresh
the per-unit counts. See the `datamn-source-ebarilga` skill for paging and
rate-limit notes.

## Notes

- 9 poison feature(s) skipped during pull (unfetchable server-side): [548024, 548715, 548716, 548718, 548760, 549248, 549249, 549250, 549251].
