# eBarilga Geoportal - UB Urban Development Agency

## Source Information

- **ID**: `ebarilga`
- **Name**: eBarilga Geoportal (UB Urban Development and Standard Agency)
- **Name (MN)**: eBarilga Геопортал (Хот байгуулалт, хотын стандартын газар)
- **URL**: https://ebarilga.ub.gov.mn/map
- **Type**: API (OGC WFS + attribute API)
- **Update Frequency**: irregular (no published schedule)
- **Language**: Mongolian only (translation required for all datasets)

## Intern start here (works in any harness)

1. List what's available: `cd tools && python -m registry list --source ebarilga`
   (76 parent datasets: 75 raw layers + 1 derived bundle).
2. Read one definition: `tools/sources/ebarilga/datasets/<id>.md` — contents,
   file paths, fetch commands, translation notes.
3. Work from the raw CSVs in `tools/sources/ebarilga/raw/` or the
   `derived/ebarilga-counts-by-{district,khoroo,zip}.csv` joins. Build splits
   as new datasets; never publish a parent (the registry blocks it anyway).

## Tooling

All extraction goes through the `datamn-source-ebarilga` skill
(`.claude/skills/datamn-source-ebarilga/`). Do not hand-roll WFS requests;
the proxy has paging quirks (keyset pagination required, see skill docs).
Skill or no skill, the same commands work from any checkout — see any
dataset `.md` under `datasets/` for copy-pasteable examples.

```bash
cd .claude/skills/datamn-source-ebarilga
python3 query_api.py --list              # 80-layer catalog
python3 fetch_data.py --layer <code> --output ../../tools/sources/ebarilga/raw/
```

## Raw pulls

Staging area: `tools/sources/ebarilga/raw/`. One
`ebarilga-<code>.{geojson,csv,meta.json}` triple per layer, plus
`.attrs.jsonl` attribute caches. Pull status is tracked in `pulls.md`.
Raw pulls are NOT registry datasets; datasets get registered only when
built into bilingual MDX + CSV deliverables (see `datamn-page-mdx`).

### Large-file policy (no Git LFS)

- **Committed to git** (~46 MB): all `raw/*.csv`, `raw/*.meta.json`,
  `raw/*.geojson` under 5 MB, and `derived/`. Biggest file ~21 MB.
- **Local-only** (this server is authoritative): the 12 `raw/*.geojson`
  at/over 5 MB (280 MB footprints, 62 MB HET roads, ...) and all
  `raw/*.attrs.jsonl` caches. Listed in `.gitignore`.
- To reproduce a big file: `fetch_data.py --layer <code> --output
  tools/sources/ebarilga/raw/` (footprints take ~1h; the fetcher adapts
  page sizes automatically, see skill docs).

## Derived products

`derive.py` joins every layer against district/khoroo/ZIP boundaries
(representative points; true centroids for polygons) and writes
`derived/ebarilga-counts-by-{district,khoroo,zip}.csv`: per-unit counts
for all 71 countable layers plus total building footprint area in m².
Run: `.venv/bin/python tools/sources/ebarilga/derive.py` (~40s).
Unmatched features (outside all boundaries) go in the `_unmatched` row.

## Endpoints

- WFS GetFeature: `https://ebarilga.ub.gov.mn/api/geoserver/wfs`
  (`typename=urban:layer_data_map`, `viewparams=layertypecode:<code>`)
- Attributes: `https://ebarilga.ub.gov.mn/api/layer/data/attribute?layer_id=<id>`
- Search: `https://ebarilga.ub.gov.mn/search?search_value=<text>`
- External host: `https://grid.transco.mn/api/geoserver/wfs`
  (`typename=grid:layer_data_map_p`, TLS cert invalid)

## Notes

- Coverage is Ulaanbaatar only.
- Attribute API is rate-limited (~1 req/s safe); geometries are fast.
- `built_building` (325k) and `town_2023` are geometry-only; skip attributes.
- 5 layers are empty: `emergency_alarm`, `data_clinic_family`, `post`,
  `Public_land`, `no_construction_GEOPORTAL_empty`.
- `plannig_road` is misspelled on the server; use as-is.
