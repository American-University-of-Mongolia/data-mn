#!/usr/bin/env python3
"""Register ebarilga layers as parent datasets (idempotent, re-runnable).

Reads layers.json + raw/*.meta.json, writes datasets/*.md definitions, and
inserts one parent row per pulled layer into the registry (skips IDs already
present, so re-running after a refresh only adds new layers).

Usage:
    cd /home/ritz/projects/data/tools
    ../.venv/bin/python sources/ebarilga/register_parents.py   # (or system python3)

Conventions (see source.md):
- IDs: ebarilga-<slugified English name>, asserted unique.
- Status active (raw data present), is_parent=1 (never publishable).
- data_file/source_path point at the raw CSV (no versions/ duplication).
"""
import json
import os
import re
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, TOOLS)
from registry import Dataset, Registry  # noqa: E402

OUTDIR = f"{HERE}/datasets"
CATS = {"education": ("Education", "Боловсрол"),
        "health": ("Health", "Эрүүл мэнд")}
DEFAULT_CAT = ("Infrastructure", "Дэд бүтэц")
GEOM_MN = {"Point": "цэг", "LineString": "шугам", "Polygon": "полигон",
           "MultiPolygon": "полигон"}
BASE_COLS = ["id", "object_no", "object_name", "geom_type", "lon", "lat"]
ATTRS_TXT = {
    "rich": "Rich Mongolian-only attributes per feature (names, addresses, "
            "permit numbers, years — varies by layer; see CSV headers).",
    "medium": "Basic Mongolian-only attributes (usually name and/or address; "
              "see CSV headers).",
    "thin": "Geometry only — attribute records carry no useful fields.",
    "unprobed": "Attribute richness not yet surveyed; check the CSV headers.",
    "empty": "No features.",
}


def slugify(name_en):
    s = re.sub(r"[()]", " ", name_en.lower())
    return "ebarilga-" + re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def load_meta(code):
    try:
        with open(f"{HERE}/raw/ebarilga-{code}.meta.json", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def layer_markdown(code, info, ds_id, cat_en):
    meta = load_meta(code)
    n = meta.get("features", info["count"])
    skipped = meta.get("skipped_ids", [])
    geom = info["geometry"] or "n/a"
    group = info["group"]
    tags = f"[ebarilga, {group}, ulaanbaatar]"
    tls = " --insecure-tls" if info["host"] == "transco" else ""
    attr_flag = ("--with-attributes"
                 if info["attrs"] in ("rich", "medium", "unprobed") else "")
    notes = []
    if info.get("notes"):
        notes.append(info["notes"])
    if skipped:
        notes.append(f"{len(skipped)} poison feature(s) skipped during pull "
                     f"(unfetchable server-side): {skipped}.")
    if info["host"] == "transco":
        notes.append("Lives on grid.transco.mn (external host, invalid TLS "
                     "certificate — fetch requires --insecure-tls).")
    if info["attrs"] == "thin":
        notes.append("Plan for spatial joins against khoroo/ZIP polygons, "
                     "not attribute analysis.")
    notes_txt = "\n".join(f"- {x}" for x in notes) if notes else "- None"
    gj = f"{HERE}/raw/ebarilga-{code}.geojson"
    bignote = ("- **Note**: raw GeoJSON is over 5 MB and stays on this server "
               "(see source.md Large-file policy).\n"
               if os.path.exists(gj) and os.path.getsize(gj) >= 5e6 else "")
    return f"""# Dataset: {info['name_en']}

## Identification

- **ID**: `{ds_id}`
- **Source**: `ebarilga`
- **Category**: {cat_en}
- **Tags**: {tags}
- **Parent**: yes — build splits from this; never publish directly

## Source Reference

- **Layer code**: `{code}`
- **Host**: `{info['host']}`
- **Geometry**: {geom}
- **Features**: {n if n is not None else '?'} (counts {meta.get('fetched_at', '?')[:10]})
- **Attributes**: {info['attrs']}
- **Raw files**: `tools/sources/ebarilga/raw/ebarilga-{code}.{{geojson,csv,meta.json}}`
{bignote}
## Title

- **EN**: {info['name_en']} — Ulaanbaatar (eBarilga geoportal)
- **MN**: {info['name_mn']} — Улаанбаатар (eBarilga геопортал)

## Description

{info['name_en']} in Ulaanbaatar from the eBarilga geoportal
({n if n is not None else '?'} {geom} features). {ATTRS_TXT[info['attrs']]}
All names, addresses, and attribute values are Mongolian-only; splits need
the standard MN→EN translation pass.

## Variables

Base columns (present in every ebarilga CSV):

{chr(10).join('- `' + c + '`' for c in BASE_COLS)}

- `lon`/`lat` is the point coordinate, or the bbox center for lines/polygons
  (approximation — use the GeoJSON for exact shapes).
- Attribute columns (Mongolian headers) follow; see the CSV header row.

## Update Instructions

```bash
cd .claude/skills/datamn-source-ebarilga
python3 query_api.py --layer {code}          # live count vs catalog
python3 fetch_data.py --layer {code} --output ../../tools/sources/ebarilga/raw{(' ' + attr_flag) if attr_flag else ''}{tls}
```

Then re-run `.venv/bin/python tools/sources/ebarilga/derive.py` to refresh
the per-unit counts. See the `datamn-source-ebarilga` skill for paging and
rate-limit notes.

## Notes

{notes_txt}
"""


DERIVED_MD = """# Dataset: eBarilga Admin-Unit Counts

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
"""


def main():
    layers_path = os.path.join(HERE, "..", "..", "..", ".claude", "skills",
                               "datamn-source-ebarilga", "layers.json")
    layers = json.load(open(layers_path, encoding="utf-8"))["layers"]
    os.makedirs(OUTDIR, exist_ok=True)
    reg = Registry()
    ids = {}
    for info in layers:
        if (info["count"] or 0) == 0 or info["attrs"] == "empty":
            continue
        ds_id = slugify(info["name_en"])
        assert ds_id not in ids, f"duplicate slug: {ds_id}"
        ids[ds_id] = info
    assert "ebarilga-admin-counts" not in ids
    for ds_id in list(ids) + ["ebarilga-admin-counts"]:
        row = reg.get_dataset(ds_id)
        if row is not None and row.source_id != "ebarilga":
            raise SystemExit(f"ID collision with {row.source_id} dataset: {ds_id}")

    added = 0
    for ds_id, info in sorted(ids.items()):
        code = info["code"]
        cat_en, cat_mn = CATS.get(info["group"], DEFAULT_CAT)
        md = layer_markdown(code, info, ds_id, cat_en)
        with open(f"{OUTDIR}/{ds_id}.md", "w", encoding="utf-8") as f:
            f.write(md)
        csv_path = f"sources/ebarilga/raw/ebarilga-{code}.csv"
        if reg.get_dataset(ds_id) is None:
            n = load_meta(code).get("features", info["count"])
            reg.add_dataset(Dataset(
                id=ds_id, source_id="ebarilga", name_en=info["name_en"],
                name_mn=info["name_mn"],
                description_en=f"{info['name_en']} in Ulaanbaatar from the "
                               f"eBarilga geoportal ({n} {info['geometry']} "
                               f"features).",
                description_mn=f"{info['name_mn']} — Улаанбаатар, eBarilga "
                               f"геопортал ({n} "
                               f"{GEOM_MN.get(info['geometry'], 'объект')}).",
                category_en=cat_en, category_mn=cat_mn,
                tags=["ebarilga", info["group"], "ulaanbaatar"],
                keywords_en=[info["name_en"]], keywords_mn=[info["name_mn"]],
                source_ref=code,
                source_path=csv_path,
                definition_path=f"sources/ebarilga/datasets/{ds_id}.md",
                source_metadata={"geometry": info["geometry"], "count": n,
                                 "attrs": info["attrs"], "host": info["host"]},
                status="active", is_parent=True,
                auto_update=True, auto_publish=True))
            added += 1
        # add_dataset doesn't persist data_file; set it explicitly (idempotent)
        reg.update_dataset(ds_id, data_file=csv_path)
    with open(f"{OUTDIR}/ebarilga-admin-counts.md", "w", encoding="utf-8") as f:
        f.write(DERIVED_MD)
    if reg.get_dataset("ebarilga-admin-counts") is None:
        reg.add_dataset(Dataset(
            id="ebarilga-admin-counts", source_id="ebarilga",
            name_en="eBarilga Feature Counts by Admin Unit",
            name_mn="eBarilga давхаргуудын тоо (админ нэгжээр)",
            description_en="Per-district/khoroo/ZIP counts for all ebarilga "
                           "layers plus building footprint area.",
            description_mn="eBarilga давхаргуудын дүүрэг/хороо/зип бүсээрх тоо "
                           "+ барилгын талбай.",
            category_en="Infrastructure", category_mn="Дэд бүтэц",
            tags=["ebarilga", "admin", "ulaanbaatar", "derived"],
            keywords_en=["counts by district", "khoroo"],
            keywords_mn=["дүүрэг", "хороо"],
            source_ref="derive.py",
            source_path="sources/ebarilga/derived/",
            definition_path="sources/ebarilga/datasets/ebarilga-admin-counts.md",
            status="active", is_parent=True,
            auto_update=True, auto_publish=True))
        added += 1
    reg.update_dataset(
        "ebarilga-admin-counts",
        data_file="sources/ebarilga/derived/ebarilga-counts-by-khoroo.csv")
    print(f"wrote {len(ids) + 1} .md files, added {added} registry rows")


if __name__ == "__main__":
    main()
