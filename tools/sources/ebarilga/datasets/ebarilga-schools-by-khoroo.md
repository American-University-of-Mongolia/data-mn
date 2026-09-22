# Dataset: Secondary Schools by Khoroo

## Identification

- **ID**: `ebarilga-schools-by-khoroo`
- **Source**: `ebarilga`
- **Category**: Education
- **Tags**: [ebarilga, ulaanbaatar, schools, education, khoroo]
- **Parent**: `ebarilga-secondary-schools` (raw features)
- **Split type**: count table (reference-table pipeline)

## Contents

One row per khoroo (204, zeros included): unit code, khoroo and parent
district (code + name), school count. Counts come from
`derived/ebarilga-counts-by-khoroo.csv` (`data_edu_school` column);
names from the published khoroo boundary table. All 323 schools fall
inside khoroo boundaries (unmatched: 0).

## Build

```bash
.venv/bin/python tools/sources/ebarilga/build_counts.py --dataset ebarilga-schools-by-khoroo
python tools/scripts/rebuild_downloads.py --dataset ebarilga-schools-by-khoroo --apply
```

Outputs: `data.mn/public/datasets/ebarilga-schools-by-khoroo-{en,mn}.csv`,
`ebarilga-schools-by-khoroo.xlsx`,
`data.mn/public/charts/ebarilga-schools-by-khoroo-{en,mn}.json`, MDX pages.

## Update Instructions

Re-pull `data_edu_school` (see parent definition), re-run `derive.py`,
re-run the build, re-validate. No schedule; re-check counts monthly.

## Notes

- Founded/commissioned years exist but are incomplete and irregularly
  formatted; excluded from v1 by design.
