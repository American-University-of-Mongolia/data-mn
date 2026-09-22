# Dataset: Ulaanbaatar ZIP Zones

## Identification

- **ID**: `ebarilga-zip-zones`
- **Source**: `ebarilga`
- **Category**: Infrastructure
- **Tags**: [ebarilga, ulaanbaatar, zip, boundaries]
- **Parent**: `ebarilga-zip-code-zones` (raw geometries)
- **Split type**: reference table (boundary list + centroid districts)

## Contents

One row per ZIP address zone (513): unit code, zone name, centroid
district code and name, area in km², true-centroid lon/lat. ZIP zones
need not nest inside districts, so the district column is the district
containing each zone's centroid (informative, not authoritative).
Zone 12001 (Kherlen golyn khuvuu-1) lies outside all districts and has
empty district cells.

## Build

```bash
.venv/bin/python tools/sources/ebarilga/build_shapes.py
python tools/scripts/rebuild_downloads.py --dataset ebarilga-zip-zones --apply
```

Outputs: `data.mn/public/datasets/ebarilga-zip-zones-{en,mn}.csv`,
`ebarilga-zip-zones.xlsx`, `data.mn/public/charts/ebarilga-zip-zones-{en,mn}.json`,
`data.mn/public/maps/ulaanbaatar-zip-zones.json`, MDX pages.

## Update Instructions

Re-pull `zippolygons` + `district_border` (see parent definition),
re-run the build, re-validate. No schedule; re-check counts monthly.

## Notes

- Areas use the equirectangular approximation (~1% accuracy).
- Geometries are authoritative for UB planning but informal for legal use.
- Reference tables are exempt from the single-value rule; see
  `docs/principles/download-standards.md` clause 5.
