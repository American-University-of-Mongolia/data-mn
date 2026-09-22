#!/usr/bin/env python3
"""Build ebarilga directory datasets (full feature lists, no server calls).

Merges one raw layer CSV with its admin join (see join_admin.py) plus
district/khoroo names from the published boundary tables, transliterates
names/addresses to the house ASCII style, and writes bilingual directory
CSVs. Only complete columns are published (no sparse year/number fields).

Usage:
    .venv/bin/python tools/sources/ebarilga/build_directories.py --dataset ebarilga-schools
    .venv/bin/python tools/sources/ebarilga/build_directories.py --all
"""
import argparse
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_shapes import transliterate  # noqa: E402  (one mapping, reused)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
RAW = f"{HERE}/raw"
JOIN = f"{HERE}/derived/admin-join"
DATASETS = f"{ROOT}/data.mn/public/datasets"

# dataset id -> raw layer, name column, extra (raw col, EN header, MN header)
DIRECTORIES = {
    "ebarilga-schools": {
        "layer": "data_edu_school",
        "name": ("Нэр", "school", "сургууль"),
        "attrs": [("Хаяг", "address", "хаяг")],
    },
}


def read_csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build(dsid):
    cfg = DIRECTORIES[dsid]
    raw = {r["id"]: r for r in read_csv(f"{RAW}/ebarilga-{cfg['layer']}.csv")}
    join = {r["id"]: r for r in read_csv(f"{JOIN}/{cfg['layer']}.csv")}
    assert set(raw) == set(join), "raw/join id mismatch"
    districts = {r["code"]: (r["district"], None) for r in read_csv(
        f"{DATASETS}/ebarilga-districts-en.csv")}
    districts_mn = {r["код"]: r["дүүрэг"] for r in read_csv(
        f"{DATASETS}/ebarilga-districts-mn.csv")}
    khoroos = {r["code"]: r["khoroo"] for r in read_csv(
        f"{DATASETS}/ebarilga-khoroos-en.csv")}
    khoroos_mn = {r["код"]: r["хороо"] for r in read_csv(
        f"{DATASETS}/ebarilga-khoroos-mn.csv")}

    name_col, name_en, name_mn = cfg["name"]
    head_en = ["id", name_en, *[a[1] for a in cfg["attrs"]],
               "district_code", "district", "khoroo_code", "khoroo",
               "lon", "lat"]
    head_mn = ["id", name_mn, *[a[2] for a in cfg["attrs"]],
               "дүүргийн_код", "дүүрэг", "хорооны_код", "хороо",
               "lon", "lat"]
    rows_en, rows_mn = [], []
    for fid in sorted(raw, key=int):
        r, j = raw[fid], join[fid]
        dc, kc = j["district_code"], j["khoroo_code"]
        base = [int(fid), transliterate((r[name_col] or "").strip())]
        base_mn = [int(fid), (r[name_col] or "").strip()]
        for col, _, _ in cfg["attrs"]:
            v = (r[col] or "").strip()
            base.append(transliterate(v))
            base_mn.append(v)
        base += [int(dc) if dc else "", districts.get(dc, ("",))[0] if dc else "",
                 int(kc) if kc else "", khoroos.get(kc, "") if kc else "",
                 r["lon"], r["lat"]]
        base_mn += [int(dc) if dc else "", districts_mn.get(dc, "") if dc else "",
                    int(kc) if kc else "", khoroos_mn.get(kc, "") if kc else "",
                    r["lon"], r["lat"]]
        rows_en.append(base)
        rows_mn.append(base_mn)
    by_admin = lambda r: (r[3] == "", r[3], r[5] == "", r[5], r[0])
    rows_en.sort(key=by_admin)
    rows_mn.sort(key=by_admin)

    for lang, head, rows in (("en", head_en, rows_en),
                             ("mn", head_mn, rows_mn)):
        path = f"{DATASETS}/{dsid}-{lang}.csv"
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(head)
            w.writerows(rows)
    print(f"wrote {dsid} ({len(rows_en)} rows)")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build ebarilga directories")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dataset", choices=sorted(DIRECTORIES))
    g.add_argument("--all", action="store_true")
    args = ap.parse_args(argv)
    for dsid in sorted(DIRECTORIES) if args.all else [args.dataset]:
        build(dsid)


if __name__ == "__main__":
    main()
