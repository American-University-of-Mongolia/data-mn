#!/usr/bin/env python3
"""Derive intern-ready CSVs from ebarilga raw pulls (no server calls).

Joins every countable layer against district/khoroo/ZIP boundaries and writes
one wide CSV per admin level: rows = units, columns = per-layer counts plus
total building footprint area. Polygons/lines join on true centroid.

Usage:
    .venv/bin/python tools/sources/ebarilga/derive.py
    .venv/bin/python tools/sources/ebarilga/derive.py --layer built_building

Outputs (committed to git, all small):
    tools/sources/ebarilga/derived/ebarilga-counts-by-{district,khoroo,zip}.csv

Method notes (documented for dataset pages):
- Counts assign each feature to exactly one unit (first match on overlaps)
  or to the _unmatched row (features outside all boundaries).
- Areas use an equirectangular approximation at each polygon's own latitude
  (good to ~1% at Ulaanbaatar's latitude; fine for statistics, not surveying).
"""
import argparse
import csv
import glob
import json
import math
import os
import sys

from shapely.geometry import shape
from shapely.strtree import STRtree

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = f"{HERE}/raw"
OUT = f"{HERE}/derived"
ADMINS = [("district", "district_border"),
          ("khoroo", "khoroo_border"),
          ("zip", "zippolygons")]
SKIP_AS_LAYER = {"district_border", "city_border", "khoroo_border", "zippolygons"}


def load_admin(code):
    with open(f"{RAW}/ebarilga-{code}.geojson", encoding="utf-8") as f:
        gj = json.load(f)
    units = []
    for feat in gj["features"]:
        p = feat["properties"]
        ucode = str(p.get("object_no") or p.get("object_name") or p["id"])
        uname = str(p.get("object_name") or ucode)
        units.append({"code": ucode, "name": uname,
                      "geom": shape(feat["geometry"])})
    return units


def area_m2(geom, lat):
    kx = 111320 * math.cos(math.radians(lat))
    return geom.area * kx * 110540


def main(argv=None):
    ap = argparse.ArgumentParser(description="Derive ebarilga count CSVs")
    ap.add_argument("--layer", help="only process one layer code")
    args = ap.parse_args(argv)

    admin_units = {}
    admin_trees = {}
    for name, code in ADMINS:
        units = load_admin(code)
        admin_units[name] = units
        admin_trees[name] = STRtree([u["geom"] for u in units])
        print(f"{name}: {len(units)} units "
              f"e.g. {units[0]['code']}={units[0]['name']}")

    metas = {}
    for m in glob.glob(f"{RAW}/ebarilga-*.meta.json"):
        d = json.load(open(m, encoding="utf-8"))
        metas[d["layer"]] = d.get("features", 0)
    layers = sorted(c for c, n in metas.items()
                    if n > 0 and c not in SKIP_AS_LAYER)
    if args.layer:
        layers = [args.layer] if args.layer in layers else sys.exit(
            f"unknown/empty layer: {args.layer}")

    # counts[admin][unit_idx][layer], areas for built
    counts = {a: [[0] * len(layers) for _ in admin_units[a]] for a in admin_units}
    unmatched = {a: [0] * len(layers) for a in admin_units}
    multi = {a: 0 for a in admin_units}
    built_area = {a: [0.0] * len(u) for a, u in admin_units.items()}

    for li, code in enumerate(layers):
        with open(f"{RAW}/ebarilga-{code}.geojson", encoding="utf-8") as f:
            feats = json.load(f)["features"]
        for feat in feats:
            g = shape(feat["geometry"]) if feat.get("geometry") else None
            pt = None
            if g is not None and not g.is_empty:
                pt = g if g.geom_type == "Point" else g.centroid
            for a in admin_units:
                idx = None
                if pt is not None:
                    hits = admin_trees[a].query(pt, predicate="intersects")
                    if len(hits):
                        idx = int(sorted(hits)[0])
                        if len(hits) > 1:
                            multi[a] += 1
                if idx is None:
                    unmatched[a][li] += 1
                else:
                    counts[a][idx][li] += 1
                    if code == "built_building" and g.geom_type != "Point":
                        built_area[a][idx] += area_m2(g, pt.y)
        done = sum(counts["district"][i][li] for i in range(len(counts["district"])))
        assert done + unmatched["district"][li] == metas[code], code
        print(f"{code}: {metas[code]} feats "
              f"({unmatched['district'][li]} unmatched)")

    os.makedirs(OUT, exist_ok=True)
    for a, units in admin_units.items():
        path = f"{OUT}/ebarilga-counts-by-{a}.csv"
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["unit_code", "unit_name", *layers, "built_area_m2"])
            for i, u in enumerate(units):
                w.writerow([u["code"], u["name"],
                            *[counts[a][i][li] for li in range(len(layers))],
                            round(built_area[a][i])])
            w.writerow(["_unmatched", "Outside all boundaries",
                        *[unmatched[a][li] for li in range(len(layers))], 0])
        print(f"wrote {path} ({os.path.getsize(path)} bytes, "
              f"{multi[a]} multi-matches)")


if __name__ == "__main__":
    main()
