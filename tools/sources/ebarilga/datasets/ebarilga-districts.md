# Dataset: Ulaanbaatar Districts

## Identification

- **ID**: `ebarilga-districts`
- **Source**: `ebarilga`
- **Category**: Infrastructure
- **Tags**: [ebarilga, ulaanbaatar, districts, boundaries]
- **Parent**: `ebarilga-district-borders` (raw geometries)
- **Split type**: reference table (boundary list + khoroo counts)

## Contents

One row per district (9): unit code, district name (EN transliterated /
MN original), khoroo count, area in km², true-centroid lon/lat.
Khoroo counts come from the centroid spatial join in `build_shapes.py`
(all 204 khoroos match exactly one district).

## Build

```bash
.venv/bin/python tools/sources/ebarilga/build_shapes.py
python tools/scripts/rebuild_downloads.py --dataset ebarilga-districts --apply
```

Outputs: `data.mn/public/datasets/ebarilga-districts-{en,mn}.csv`,
`ebarilga-districts.xlsx`, `data.mn/public/charts/ebarilga-districts-{en,mn}.json`,
`data.mn/public/maps/ulaanbaatar-districts.json`, MDX pages.

## Update Instructions

Re-pull `district_border` + `khoroo_border` (see parent definition),
re-run the build, re-validate. No schedule; re-check counts monthly.

## Notes

- Areas use the equirectangular approximation (~1% accuracy).
- Geometries are authoritative for UB planning but informal for legal use.
- Reference tables are exempt from the single-value rule; see
  `docs/principles/download-standards.md` clause 5.
