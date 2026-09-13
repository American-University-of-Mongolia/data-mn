---
name: datamn-source-ebarilga
description: "Browse and download Ulaanbaatar geospatial data from the ebarilga.ub.gov.mn geoportal (City Urban Development Agency). Use when adding UB construction, building, road, transit, school, health-facility, POI, zoning, or admin-boundary datasets: 80 open WFS layers, ~380k features, no auth. Covers layer discovery, full-layer download to GeoJSON/CSV, and attribute enrichment."
dependencies:
  - python3
---

# eBarilga Geoportal Data Source Skill

This skill extracts geospatial data from Ulaanbaatar's eBarilga geoportal
(`https://ebarilga.ub.gov.mn/map`), run by the City Urban Development and
Standard Agency. It is the city's open map of buildings, construction permits,
roads, transit, public facilities, and planning zones.

When saving data never put it inside the skills/datamn-source-ebarilga folder.
Ask the user where to save the data if not specified.

All 75 layers are tracked as parent datasets in the registry
(`registry list --source ebarilga`) with definitions under
`tools/sources/ebarilga/datasets/` — start there for discovery; this skill
is the fetch/refresh tooling behind them.

## Overview

| Field | Value |
|-------|-------|
| Source ID | `ebarilga` |
| Organization | Хот байгуулалт, хотын стандартын газар (UB Urban Development Agency) |
| Website | https://ebarilga.ub.gov.mn/map |
| Data Type | api (OGC WFS + JSON/HTML attribute API) |
| Update Frequency | irregular (no published schedule; re-check counts monthly) |
| Language | mn (Mongolian only; translation required) |

## Authentication

No authentication required. All documented endpoints are openly accessible.

## Available Data

80 layers, ~380k features total (counts 2026-09-13; refresh with
`query_api.py --refresh`). Groups:

| Group | Contents |
|-------|----------|
| `buildings` | Built footprints (325k), design approvals (25k, rich), ATD planning assignments (7k, rich) |
| `admin` | District/khoroo/city borders, ZIP zones (513), roads with names/class |
| `transport` | Bus routes (88, named + geometry), bus stops (607) |
| `education` | Schools (323, founded/commissioned years), kindergartens (296+477), universities (112) |
| `health` | Hospitals (46), pharmacies (1,016) |
| `poi` | Supermarkets (1,581), banks/ATMs, hotels, restaurants, statues (319), apartments (327, unnamed) |
| `culture` | Heritage buildings (39, decree references), public lands (empty) |
| `zones` | 2030 spatial zones (5,391), HET zones, sub-center/tech-park/SEZ boundaries |
| `protection` | Forest, flood works, lake/spring buffers, protected areas, power-grid zones (external host) |
| `redevelopment` | Redevelopment blocks, planned heating lines, settlement boundaries |
| `emergency` | Assembly points (213+190), evacuation sites (32) |

5 layers are listed in the UI but hold zero features (family clinics,
checkpoints, public land, no-construction zones, sirens). `town_2023`
apartment polygons and most `built_building` footprints have geometry only.

Attribute richness per layer is recorded in `layers.json` (`attrs` field:
`rich` / `medium` / `thin` / `empty` / `unprobed`).

## Browsing the Catalog

```bash
cd .claude/skills/datamn-source-ebarilga

python3 query_api.py --list                  # all 80 layers with counts
python3 query_api.py --list --group health   # one group
python3 query_api.py сургууль                # search (MN/EN/code)
python3 query_api.py bus route
python3 query_api.py --layer data_edu_school # describe + live count
python3 query_api.py --refresh               # re-scrape /map, recount all (~1 min)
```

Append `--json` for machine-readable output. `--refresh` preserves English
names/groups/notes and flags new or disappeared layers.

## Data Fetching

```bash
# Full layer -> GeoJSON + CSV + meta
python3 fetch_data.py --layer data_edu_school --output ./output

# ... with per-feature attributes (name, address, years, permit nos, ...)
python3 fetch_data.py --layer plan_building --output ./output --with-attributes

# Quick sample for inspection
python3 fetch_data.py --layer built_building --output /tmp/eb --max 1000

# Resume an interrupted fetch (geometries + attribute cache)
python3 fetch_data.py --layer plan_building --output ./output --with-attributes --resume

# Fast geometries now, slow attributes later (two-pass; same result)
python3 fetch_data.py --layer plan_building --output ./output
python3 fetch_data.py --layer plan_building --output ./output --attrs-only

# Power-grid layers live on grid.transco.mn (broken TLS cert)
python3 fetch_data.py --layer pz_city_line --output ./output --insecure-tls
```

Options: `--page-size N` (default 2000; 10000 verified), `--format
geojson|csv|both`, `--wfs-delay`, `--attr-rate` (default 1 req/s),
`--timeout`.

### How paging works (read before changing it)

- The WFS proxy **ignores `startIndex`** (HTTP 200 + empty body). Paging MUST
  use keyset pagination: `sortBy=id` plus `CQL_FILTER=id>=<last_id+1>`.
  Verified gapless over all 25,174 `plan_building` features.
- Two server quirks force **adaptive page sizes** (implemented in
  `fetch_data.py`; do not "simplify" it to fixed pages):
  - **Poison features**: a few records (e.g. restaurant id 7127) crash
    GeoJSON serialization for ANY response containing them (empty body).
    The fetcher halves down to single-feature pages, identifies the poison
    id with an id-only probe (`propertyName=id`, no geometry), skips it,
    and records it in `meta.json` (`skipped_ids`).
  - **Response-size cap**: layers with heavy polygons (e.g. `ddp_road`:
    11 MB ok, ~22 MB → HTTP 500) need small pages. The fetcher halves on
    failure and doubles on success (AIMD), converging per layer.
- 429s and network errors get full backoff retries; 500s/empty bodies get
  one retry and then trigger a split (they are usually deterministic).

### Rate limits

- The attribute API returns **HTTP 429** under load (observed after tens of
  requests at 3-5 req/s). Default is 1 req/s with backoff on 429/5xx and
  `Retry-After` support. At that rate, 25k enriched records take ~7 hours;
  the `.attrs.jsonl` cache makes re-runs free.
- WFS tolerates large pages (10,000 features / ~10 MB in ~3 s). Keep
  `--page-size <= 10000`.

## Update Detection

The source publishes no timestamps or changelog. Detect change by re-counting:

```bash
python3 query_api.py --layer plan_building   # compare live vs catalog count
python3 query_api.py --refresh               # recount everything, save
```

`fetch_data.py` writes `ebarilga-<code>.meta.json` (`features`, `fetched_at`,
`complete`) with every download; store it next to the dataset for provenance.
Recommended re-check cadence: monthly.

## Output Format

`fetch_data.py` writes three files per layer (plus `.attrs.jsonl` cache):

- `ebarilga-<code>.geojson` — FeatureCollection in EPSG:4326, raw WFS
  properties plus geometry.
- `ebarilga-<code>.csv` — one row per feature. Base columns plus one column
  per attribute key (Mongolian headers; see translation below):

```csv
id,object_no,object_name,geom_type,lon,lat,Нэр,Хаяг,Ашиглалтад орсон он
4989,,,Point,106.917,47.921,2-р сургууль,СБД 7-р хороо ...,1978
```

- `lon`/`lat` is the point coordinate, or the **bbox center** for
  lines/polygons (documented approximation, good enough for mapping and
  district joins; use the GeoJSON for exact shapes).

## Language Support

**Source Language**: Mongolian. **Translation Required**: Yes.

All names, addresses, and attribute keys/values are Mongolian-only. After
fetching, translate with the standard tooling:

```bash
python3 tools/scripts/translate_csv.py ebarilga-<code>.csv --from mn --to en \
  -o ebarilga-<code>-en.csv
# then rename the original to ebarilga-<code>-mn.csv
```

Translate column headers AND categorical values; keep `id`, `object_no`, codes,
years, and coordinates identical in both files. Standard mappings (district
names, etc.) from the template apply; layer-specific terms (АТД numbers,
permit classes, zoning codes) must be added to the dataset's source doc.
Validate per `tools/TRANSLATION_GUIDE.md` (same row count, identical numerics).

## Dataset ID Convention

`ebarilga-<topic>`: `ebarilga-schools`, `ebarilga-bus-routes`,
`ebarilga-design-approvals`, `ebarilga-buildings-by-khoroo`, ...

## Source Registration

After creating datasets, register the source once:

```bash
cd tools && python -m registry sources  # check it is missing first
```

```python
from registry import Registry
reg = Registry()
reg.add_source(source_id="ebarilga",
               name_en="eBarilga Geoportal (UB Urban Development Agency)",
               name_mn="eBarilga Геопортал (Хот байгуулалт, хотын стандартын газар)",
               type="api", base_url="https://ebarilga.ub.gov.mn/map",
               update_frequency="irregular", enabled=True)
```

## API Reference (for debugging)

- `GET /api/geoserver/wfs?service=WFS&version=1.1.0&request=GetFeature
  &typename=urban:layer_data_map&outputFormat=application/json
  &srsname=EPSG:4326&viewparams=layertypecode:<CODE>
  &maxFeatures=N&sortBy=id&CQL_FILTER=id>=X`
- `GET /api/layer/data/attribute?layer_id=<id>` — HTML table of attributes.
- `GET /search?search_value=<text>` — full-text search, JSON + WKT geometry.
- External host: `https://grid.transco.mn/api/geoserver/wfs`,
  `typename=grid:layer_data_map_p` (TLS certificate invalid as of 2026-09).
- Layer codes come from `data-layertypecode` attributes on
  `https://ebarilga.ub.gov.mn/map` (`ui_only_codes` in layers.json are app
  layers, not data).

## Common Issues

1. **Empty 200 response from WFS** — either a paging parameter the proxy
   dislikes (notably `startIndex`: use keyset pagination only) or a poison
   feature / oversize page. `fetch_data.py` splits and skips automatically;
   check `meta.json` (`complete`, `skipped_ids`) after every pull.
2. **HTTP 429 from attribute API** — back off; `--attr-rate` below 1.0 and
   `--resume` are designed for this. Never parallelize attribute fetches.
3. **TLS failure on grid.transco.mn** — expected; pass `--insecure-tls`.
   Public data only; no credentials are ever sent.
4. **Thin layers** (`built_building`, `town_2023`, heating lines) — geometry
   is the product; plan for spatial joins against khoroo/ZIP polygons, not
   attribute analysis.
5. **`plannig_road`** — misspelled on the server; use as-is.
6. **Permit years** — take years from АТД/permit-number fields
   (`МЗХ2022/…`), not from `ТБА…` record numbers (record-creation
   timestamps, unverified).

## Notes

- Be polite: this is a small city-government server. Cache aggressively,
  fetch off-hours for the 325k-footprint layer, never add concurrency.
- Geometries are authoritative for UB planning but informal for legal use;
  say so on dataset pages.
- Coverage is Ulaanbaatar only.
