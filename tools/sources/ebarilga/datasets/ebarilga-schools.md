# Dataset: Secondary Schools Directory

## Identification

- **ID**: `ebarilga-schools`
- **Source**: `ebarilga`
- **Category**: Education
- **Tags**: [ebarilga, ulaanbaatar, schools, education, directory]
- **Parent**: `ebarilga-secondary-schools` (raw features)
- **Split type**: directory (reference-table pipeline)

## Contents

One row per school (323): feature id, transliterated name and address,
parent district + khoroo (code + name, centroid spatial join via
`derived/admin-join/data_edu_school.csv`), lon/lat. Only complete
columns are published; founded/commissioned years and building numbers
are excluded (incomplete). English names follow the house ASCII
transliteration (see `datamn-transform-boundary`); English-origin names
(Galaxy, Saint Paul, Singapore School of Mongolia, ...) are translated
via `TRANSLIT_EXCEPTIONS` in `build_shapes.py`.

The page chart is the counts choropleth from `ebarilga-schools-by-khoroo`
(same map, own spec file); the downloads hold the full directory.

## Build

```bash
.venv/bin/python tools/sources/ebarilga/join_admin.py --layer data_edu_school
.venv/bin/python tools/sources/ebarilga/build_directories.py --dataset ebarilga-schools
python tools/scripts/rebuild_downloads.py --dataset ebarilga-schools --apply
```

Outputs: `data.mn/public/datasets/ebarilga-schools-{en,mn}.csv`,
`ebarilga-schools.xlsx`,
`data.mn/public/charts/ebarilga-schools-{en,mn}.json`, MDX pages.

## Update Instructions

Re-pull `data_edu_school` (see parent definition), re-run the join and
the build, re-validate. No schedule; re-check counts monthly.

## Notes

- Source typo preserved verbatim: `140-р бага сургуль` (missing у).
  Transliteration is faithful to source; only `TRANSLIT_EXCEPTIONS`
  entries are normalized.
