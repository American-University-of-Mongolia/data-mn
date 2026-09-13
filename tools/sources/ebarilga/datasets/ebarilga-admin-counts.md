# Dataset: eBarilga Admin-Unit Counts

## Identification

- **ID**: `ebarilga-admin-counts`
- **Source**: `ebarilga`
- **Category**: Infrastructure
- **Tags**: [ebarilga, admin, ulaanbaatar, derived]
- **Parent**: yes — build splits from this; never publish directly

## Source Reference

- **Derived by**: `tools/sources/ebarilga/derive.py` from the raw pulls
- **Files**: `tools/sources/ebarilga/derived/ebarilga-counts-by-{{district,khoroo,zip}}.csv`
- **Units**: 9 districts, 204 khoroos, 513 ZIP zones (+ `_unmatched` row)

## Title

- **EN**: eBarilga Feature Counts by District, Khoroo, and ZIP Zone — Ulaanbaatar
- **MN**: eBarilga давхаргуудын тоо (дүүрэг, хороо, зип бүсээр) — Улаанбаатар

## Description

Per-admin-unit counts for all 71 countable ebarilga layers plus total
building footprint area in m². One wide CSV per admin level: rows are units
(`unit_code`, `unit_name`), columns are per-layer counts. This is the
starting point for most tabular ebarilga datasets — no GIS work needed.

## Variables

- `unit_code`, `unit_name` — district/khoroo/ZIP code and Mongolian name.
- One count column per layer code (e.g. `data_edu_school`, `plan_building`).
- `built_area_m2` — summed building footprint area (equirectangular
  approximation at each polygon's latitude; statistics-grade, not surveying).
- `_unmatched` row — features falling outside all boundaries.

## Update Instructions

```bash
.venv/bin/python tools/sources/ebarilga/derive.py   # ~40s, reads raw/*.geojson
```

Re-run after any raw re-pull. Joins on true centroids (points as-is);
each feature lands in exactly one unit or `_unmatched`.

## Notes

- Method detail lives in `derive.py`'s docstring — quote it on dataset pages.
- Admin layers join independently; ZIP/khoroo/district borders need not nest.
