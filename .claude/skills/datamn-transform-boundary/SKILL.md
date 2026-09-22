---
name: datamn-transform-boundary
description: Process admin-boundary pulls into publishable /maps shapes and boundary reference-table datasets. Use when adding or refreshing district/khoroo/ZIP (or future aimag) boundaries, parent-unit cross data, or code-keyed choropleth wiring.
dependencies:
  - python3
  - shapely
---

# Boundary Shapes & Reference Tables Skill

Turn raw admin-boundary pulls into two products: stripped `/maps/*.json`
shapes for choropleths, and bilingual reference-table datasets (codes,
names, parents, areas). Established precedent: the three Ulaanbaatar
boundary datasets built by `tools/sources/ebarilga/build_shapes.py`.

## Concepts

| Product | Location | Purpose |
|---------|----------|---------|
| Boundary shapes | `data.mn/public/maps/ulaanbaatar-*.json` | Chart geometries + shape downloads |
| Reference tables | `data.mn/public/datasets/{id}-{en,mn}.csv` + `{id}.xlsx` | Join keys, names, parents, areas |
| Dataset pages | `data.mn/src/data/data/{en,mn}/{id}.mdx` | One page per admin level |

**Join on code, never on name.** Khoroo names repeat across districts and
19 ZIP zones share a name. Codes (`object_no`) are the unique keys in the
maps properties, the CSVs, and every choropleth lookup.

**Reference tables are multi-attribute** (codes, names, parents, areas,
coordinates), so the single-value-column rule cannot apply. They live in
`REFERENCE_TABLES` in `tools/scripts/rebuild_downloads.py` (reason each;
validator shares the list) with sheets staying long. See Standard 2 clause
5 in `docs/principles/download-standards.md`.

## Processing Recipe (new boundaries)

1. **Strip properties** to `code`, `name`, `name_mn`, `area_km2` (+ parent
   fields). Raw ebarilga features carry ~21 styling keys.
2. **Round coordinates to 3 decimals** (aimag precedent; ~100 m — plenty
   for choropleths; raw/ keeps full precision).
3. **Orient exterior rings clockwise.** Vega/d3 fills counter-clockwise
   rings inverted. Raw winding varies by layer (ebarilga districts are CW,
   khoroos/ZIPs CCW) — normalize with
   `shapely.ops.orient(geom, sign=-1.0)` and verify visually.
4. **Assign parents by true-centroid spatial join** (STRtree, first match).
   Never parse code prefixes: khoroo prefix 15 spans two districts.
   Record unmatched units (centroid outside all parents) with empty
   parent cells + a documented caveat, never a guessed parent.
5. **Areas** via the equirectangular approximation at each polygon's
   latitude (~1%; statistics-grade, not surveying).
6. **Transliterate names** per the table below; keep `TRANSLIT_EXCEPTIONS`
   for English-origin names that need translation instead.
7. **Strip whitespace** on all names (source data has trailing spaces).
8. **Document** the file in `data.mn/public/maps/README.md` (source,
   license, processing, property contract).

## Transliteration (data.mn house style)

ASCII, no diacritics (Sukhbaatar, Khuvsgul, Umnugovi, Tuv). Capitals mirror
(`Х→Kh`, `Ш→Sh`, `Ч→Ch`, `Ө→U`).

| а a | б b | в v | г g | д d | е e | ё yo | ж j | з z | и i |
| й i | к k | л l | м m | н n | о o | ө u | п p | р r | с s |
| т t | у u | ү u | ф f | х kh | ц ts | ч ch | ш sh | щ shch | ъ — |
| ы y | ь i | э e | ю yu | я ya | | | | | |

## Choropleth Wiring

Same `geoshape` + `lookup` pattern as `datamn-chart-vega` §6, except the
lookup key is the numeric `code` (not a name):

```json
"transform": [{
  "lookup": "properties.code",
  "from": {
    "data": {"url": "/datasets/{id}-en.csv", "format": {"type": "csv"}},
    "key": "code",
    "fields": ["district", "khoroos", "area_km2"]
  }
}]
```

CSV codes must stay numeric to match the JSON properties. A failed join
renders uniform gray — always confirm value variation in visual QA.

## Validation Checklist

- [ ] `validate_vega.py` on new specs + `vl2png` visual QA (fills correct,
      joins returning values, geography sane incl. exclaves)
- [ ] `rebuild_downloads.py --dataset {id} --apply` routes `auto`
- [ ] `validate_dataset.py --all {id}` shows `Valid: 15, Invalid: 0`
- [ ] `validate_mdx_datafiles.py` green
- [ ] Definition file at `tools/sources/{source}/datasets/{id}.md`
- [ ] `tools/versions/{id}/v1/` snapshot committed
- [ ] Registry row + v1 version + `registry publish`
- [ ] Maps README entry for new/changed shapes
