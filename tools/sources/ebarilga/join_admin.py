#!/usr/bin/env python3
"""Per-feature admin join for ebarilga layers (no server calls).

Assigns every feature of one raw layer to its district + khoroo by the
same rule as derive.py (points as-is, polygons/lines on true centroid;
first match on overlaps). Split builders merge this onto raw CSVs by id.

Usage:
    .venv/bin/python tools/sources/ebarilga/join_admin.py --layer data_edu_school

Outputs (committed to git, all small):
    tools/sources/ebarilga/derived/admin-join/{code}.csv
    columns: id, district_code, khoroo_code (empty when outside all boundaries)
"""
import argparse
import csv
import json
import os
import sys

from shapely.geometry import shape
from shapely.strtree import STRtree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from derive import load_admin  # noqa: E402  (same unit rules as counts)

RAW = f"{HERE}/raw"
OUT = f"{HERE}/derived/admin-join"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Per-feature admin join")
    ap.add_argument("--layer", required=True, help="ebarilga layer code")
    args = ap.parse_args(argv)

    units, trees = {}, {}
    for name, code in (("district", "district_border"),
                       ("khoroo", "khoroo_border")):
        units[name] = load_admin(code)
        trees[name] = STRtree([u["geom"] for u in units[name]])

    with open(f"{RAW}/ebarilga-{args.layer}.geojson",
              encoding="utf-8") as f:
        feats = json.load(f)["features"]

    rows, unmatched = [], 0
    for feat in feats:
        g = shape(feat["geometry"]) if feat.get("geometry") else None
        pt = None
        if g is not None and not g.is_empty:
            pt = g if g.geom_type == "Point" else g.centroid
        codes = {}
        for a in ("district", "khoroo"):
            idx = None
            if pt is not None:
                hits = trees[a].query(pt, predicate="intersects")
                if len(hits):
                    idx = int(sorted(hits)[0])
            codes[a] = units[a][idx]["code"] if idx is not None else ""
        if not codes["district"] and not codes["khoroo"]:
            unmatched += 1
        rows.append((str(feat["properties"].get("id")),
                     codes["district"], codes["khoroo"]))

    os.makedirs(OUT, exist_ok=True)
    path = f"{OUT}/{args.layer}.csv"
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "district_code", "khoroo_code"])
        w.writerows(rows)
    print(f"wrote {path} ({len(rows)} rows, {unmatched} unmatched)")


if __name__ == "__main__":
    main()
