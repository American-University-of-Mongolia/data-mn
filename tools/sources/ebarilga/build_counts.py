#!/usr/bin/env python3
"""Build ebarilga count-by-admin datasets from derived counts (no server calls).

Reads tools/sources/ebarilga/derived/ebarilga-counts-by-{khoroo,district}.csv,
joins unit + parent names from the published boundary tables (so names and
transliteration stay consistent everywhere), and writes bilingual download
CSVs. The _unmatched row is dropped from published tables; its counts are
printed for captions.

Usage:
    .venv/bin/python tools/sources/ebarilga/build_counts.py --dataset ebarilga-schools-by-khoroo
    .venv/bin/python tools/sources/ebarilga/build_counts.py --all
"""
import argparse
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DERIVED = f"{HERE}/derived"
DATASETS = f"{ROOT}/data.mn/public/datasets"

# dataset id -> level, [(layer code, EN header, MN header)], optional total + area
DATASETS_CONFIG = {
    "ebarilga-schools-by-khoroo": {
        "level": "khoroo",
        "layers": [("data_edu_school", "schools", "сургуулийн_тоо")],
    },
    "ebarilga-kindergartens-by-khoroo": {
        "level": "khoroo",
        "layers": [("data_edu_kindergarten", "public", "улсын"),
                   ("data_edu_private_kinder", "private", "хувийн")],
        "total": ("total", "нийт"),
    },
    "ebarilga-pharmacies-by-khoroo": {
        "level": "khoroo",
        "layers": [("data_clinic_pharmacy", "pharmacies", "эмийн_сангийн_тоо")],
    },
    "ebarilga-supermarkets-by-khoroo": {
        "level": "khoroo",
        "layers": [("data_pub_supermarket", "supermarkets",
                    "супермаркетийн_тоо")],
    },
    "ebarilga-bus-stops-by-khoroo": {
        "level": "khoroo",
        "layers": [("data_trans_bus_station", "bus_stops",
                    "автобусны_буудлын_тоо")],
    },
    "ebarilga-buildings-by-khoroo": {
        "level": "khoroo",
        "layers": [("built_building", "buildings", "барилгын_тоо")],
        "area": ("area_km2", "талбай_км2"),
    },
    "ebarilga-universities-by-district": {
        "level": "district",
        "layers": [("data_edu_university", "universities",
                    "их_сургуулийн_тоо")],
    },
    "ebarilga-hospitals-by-district": {
        "level": "district",
        "layers": [("data_clinic_gov", "hospitals", "эмнэлгийн_тоо")],
    },
}

BOUNDARY = {"khoroo": "ebarilga-khoroos", "district": "ebarilga-districts"}


def read_csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build(dsid):
    cfg = DATASETS_CONFIG[dsid]
    level = cfg["level"]
    counts = {r["unit_code"]: r for r in read_csv(
        f"{DERIVED}/ebarilga-counts-by-{level}.csv")}
    base = BOUNDARY[level]
    units_en = read_csv(f"{DATASETS}/{base}-en.csv")
    units_mn = {r["код"]: r for r in read_csv(f"{DATASETS}/{base}-mn.csv")}

    value_en = [v for _, v, _ in cfg["layers"]]
    value_mn = [v for _, _, v in cfg["layers"]]
    if cfg.get("total"):
        value_en.append(cfg["total"][0])
        value_mn.append(cfg["total"][1])
    if cfg.get("area"):
        value_en.append(cfg["area"][0])
        value_mn.append(cfg["area"][1])

    if level == "khoroo":
        head_en = ["code", "khoroo", "district_code", "district", *value_en]
        head_mn = ["код", "хороо", "дүүргийн_код", "дүүрэг", *value_mn]
    else:
        head_en = ["code", "district", *value_en]
        head_mn = ["код", "дүүрэг", *value_mn]

    rows_en, rows_mn, unmatched = [], [], {}
    for u in units_en:
        code = u["code"]
        c = counts[code]
        vals = [int(c[layer]) for layer, _, _ in cfg["layers"]]
        if cfg.get("total"):
            vals.append(sum(vals))
        if cfg.get("area"):
            vals.append(round(float(c["built_area_m2"]) / 1e6, 3))
        if level == "khoroo":
            rows_en.append([int(code), u["khoroo"], int(u["district_code"]),
                            u["district"], *vals])
            m = units_mn[code]
            rows_mn.append([int(code), m["хороо"], int(m["дүүргийн_код"]),
                            m["дүүрэг"], *vals])
        else:
            rows_en.append([int(code), u["district"], *vals])
            rows_mn.append([int(code), units_mn[code]["дүүрэг"], *vals])
    for layer, _, _ in cfg["layers"]:
        unmatched[layer] = counts["_unmatched"][layer]

    for lang, head, rows in (("en", head_en, rows_en),
                             ("mn", head_mn, rows_mn)):
        path = f"{DATASETS}/{dsid}-{lang}.csv"
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(head)
            w.writerows(rows)
    print(f"wrote {dsid} ({len(rows_en)} rows); unmatched: {unmatched}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build ebarilga count datasets")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dataset", choices=sorted(DATASETS_CONFIG))
    g.add_argument("--all", action="store_true")
    args = ap.parse_args(argv)
    ids = sorted(DATASETS_CONFIG) if args.all else [args.dataset]
    for dsid in ids:
        build(dsid)


if __name__ == "__main__":
    main()
