# Dataset: Ulaanbaatar Khoroos

## Identification

- **ID**: `ebarilga-khoroos`
- **Source**: `ebarilga`
- **Category**: Infrastructure
- **Tags**: [ebarilga, ulaanbaatar, khoroo, districts, boundaries]
- **Parent**: `ebarilga-khoroo-borders` (raw geometries)
- **Split type**: reference table (boundary list + parent districts)

## Contents

One row per khoroo (204): unit code, khoroo name, parent district code
and name, area in km², true-centroid lon/lat. Parent districts are
assigned by true-centroid lookup against district polygons (authoritative;
khoroo code prefixes are NOT reliable — prefix 15 spans two districts).
Khoroo names repeat across districts; codes are the unique join key.

## Build

```bash
.venv/bin/python tools/sources/ebarilga/build_shapes.py
python tools/scripts/rebuild_downloads.py --dataset ebarilga-khoroos --apply
```

Outputs: `data.mn/public/datasets/ebarilga-khoroos-{en,mn}.csv`,
`ebarilga-khoroos.xlsx`, `data.mn/public/charts/ebarilga-khoroos-{en,mn}.json`,
`data.mn/public/maps/ulaanbaatar-khoroos.json`, MDX pages.

## Update Instructions

Re-pull `khoroo_border` + `district_border` (see parent definition),
re-run the build, re-validate. No schedule; re-check counts monthly.

## Notes

- Areas use the equirectangular approximation (~1% accuracy).
- Geometries are authoritative for UB planning but informal for legal use.
- Reference tables are exempt from the single-value rule; see
  `docs/principles/download-standards.md` clause 5.
