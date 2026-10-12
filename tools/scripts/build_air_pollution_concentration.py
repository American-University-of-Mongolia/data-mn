#!/usr/bin/env python3
"""Build air-pollution-concentration from the NSO monthly air-pollution tables.

Source: data.1212.mn, Economy, environment > Environment >
"CONCENTRATION OF AIR POLLUTION, by location, by month":
  DT_NSO_2400_015V1.px  SO2     (table IDs are reused outside this folder,
  DT_NSO_2400_015V4.px  PM10     so always fetch by full folder path)
  DT_NSO_2400_015V5.px  PM2.5

Method: for each pollutant and month, the unweighted mean of the station
"Average" values of the 17 fixed Ulaanbaatar stations that have data that
month, rounded to 4 dp. Stations without data are skipped; nothing is
interpolated. Stations NSO added in 2026 (Yarmag, Nalaikh, Sharkhad,
5 Buudal) are excluded to keep the station set fixed. PM2.5 months whose
station values all equal PM10 (an NSO publishing error, seen 2026-09) are
dropped.

Usage:
  .venv/bin/python tools/scripts/build_air_pollution_concentration.py --version 3 [--fetch] [--apply]
Then rebuild the XLSX:
  .venv/bin/python tools/scripts/rebuild_downloads.py --dataset air-pollution-concentration --apply
"""
import argparse
import itertools
import json
import re
import shutil
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
SLUG = "air-pollution-concentration"
DATASETS = ROOT / "data.mn/public/datasets"
FOLDER = ("https://data.1212.mn/api/v1/{lang}/NSO/Economy,%20environment/Environment/"
          "CONCENTRATION%20OF%20AIR%20POLLUTION,%20by%20location,%20by%20month/DT_NSO_2400_015V{v}.px")
# (table version, EN label, MN label), in chart/legend order
POLLUTANTS = [(5, "PM2.5", "Тоосонцор PM2.5"), (4, "PM10", "Тоосонцор PM10"), (1, "SO2", "Хүхэрлэг хий SO₂")]
# NSO names as of Oct 2026; matched ignoring case, spaces and punctuation
# (spellings differ between tables, e.g. "khar khorin" vs "kharkhorin").
# Old names: 1st micro district, 32nd Toirog, Kharkhorin market, Dambdarjaa, 248th kindergarten.
UB_STATIONS = [
    "Misheel-Expo center", "West crossroad", "Takhilt, 1st micro district", "13th micro district",
    "100 Ail, 32 Toirog", "Ofitseruudiin ordon", "Tsakhilgaan stants, khar khorin zakh",
    "Urgakh naran micro district", "Dambadarjaa", "Khailaast", "Nisekh", "Tolgoit", "Zuragt",
    "Amgalan", "Bayankhoshuu", "248nd tsetserleg", "Bogd khan palace museum",
]


def key(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


def fetch(v, lang, out):
    """Download a whole table as long CSV (Indicator, Location, Month, value)."""
    url = FOLDER.format(lang=lang, v=v)
    meta = requests.get(url, timeout=60).json()
    query = {"query": [{"code": x["code"], "selection": {"filter": "item", "values": x["values"]}}
                       for x in meta["variables"]], "response": {"format": "json-stat2"}}
    d = requests.post(url, json=query, timeout=120).json()
    cats = []
    for dim in d["id"]:
        c = d["dimension"][dim]["category"]
        order = sorted(c["index"], key=c["index"].get) if isinstance(c["index"], dict) else c["index"]
        cats.append([c["label"][k] for k in order])
    rows = list(itertools.product(*cats))
    vals = d["value"]
    if isinstance(vals, dict):
        vals = [vals.get(str(i)) for i in range(len(rows))]
    df = pd.DataFrame(rows, columns=[d["dimension"][x]["label"] for x in d["id"]])
    df["value"] = vals
    df.to_csv(out, index=False)
    return d.get("updated")


def station_averages(raw_dir, v):
    df = pd.read_csv(raw_dir / f"nso-2400-015v{v}-en.csv.gz")
    df.columns = ["Indicator", "Location", "Month", "value"]
    df = df[df.Indicator.str.strip().str.endswith("Average")].copy()
    df["k"] = df.Location.map(key)
    return df


def build(raw_dir):
    ub = {key(s) for s in UB_STATIONS}
    pm10 = station_averages(raw_dir, 4).dropna(subset=["value"])
    frames, stats = [], {}
    for v, en_label, mn_label in POLLUTANTS:
        a = station_averages(raw_dir, v)
        a = a[a.k.isin(ub)]
        assert a.k.nunique() == len(ub), f"V{v}: matched {a.k.nunique()}/{len(ub)} UB stations"
        dropped = []
        if en_label == "PM2.5":
            m = a.dropna(subset=["value"]).merge(pm10[["k", "Month", "value"]], on=["k", "Month"],
                                                 how="left", suffixes=("", "_10"))
            same = m.groupby("Month").apply(lambda x: len(x) >= 3 and (x.value == x.value_10).all())
            dropped = sorted(same[same].index)
            a = a[~a.Month.isin(dropped)]
        g = a.groupby("Month").value.agg(["mean", "count"]).sort_index()
        reported = g[g["count"] > 0].index
        g = g.loc[reported.min():reported.max()]
        stats[en_label] = {"first": g.index.min(), "last": g.index.max(),
                           "empty_months": list(g[g["count"] == 0].index),
                           "dropped_as_pm10_copies": dropped,
                           "stations_per_month": [int(g["count"].min()), int(g["count"].max())],
                           "peak": round(float(g["mean"].max()), 4), "peak_month": g["mean"].idxmax()}
        frames.append(pd.DataFrame({"month": g.index, "pollutant": en_label, "pollutant_mn": mn_label,
                                    "value": g["mean"].round(4).values}))
    order = {p[1]: i for i, p in enumerate(POLLUTANTS)}
    df = pd.concat(frames)
    df = df.assign(o=df.pollutant.map(order)).sort_values(["month", "o"]).reset_index(drop=True)
    en = df[["month", "pollutant", "value"]].rename(columns={"value": "value_mg_m3"})
    mn = df[["month", "pollutant_mn", "value"]].rename(
        columns={"month": "сар", "pollutant_mn": "бохирдуулагч", "value": "утга_мг_м3"})
    return en, mn, stats


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", type=int, required=True, help="dataset version to build (tools/versions/{slug}/v{N})")
    ap.add_argument("--fetch", action="store_true", help="download the three NSO tables into the version folder")
    ap.add_argument("--apply", action="store_true", help="write public CSVs and version copies")
    args = ap.parse_args()
    vdir = ROOT / f"tools/versions/{SLUG}/v{args.version}"
    vdir.mkdir(parents=True, exist_ok=True)
    if args.fetch:
        for v, label, _ in POLLUTANTS:
            for lang in ("en", "mn"):
                updated = fetch(v, lang, vdir / f"nso-2400-015v{v}-{lang}.csv.gz")
            print(f"fetched V{v} {label} (updated {updated})")
    en, mn, stats = build(vdir)
    print(f"{len(en)} rows")
    print(json.dumps(stats, indent=1))
    if args.apply:
        en.to_csv(DATASETS / f"{SLUG}-en.csv", index=False)
        mn.to_csv(DATASETS / f"{SLUG}-mn.csv", index=False)
        for lang in ("en", "mn"):
            shutil.copy(DATASETS / f"{SLUG}-{lang}.csv", vdir)
        print(f"wrote {SLUG}-en/mn.csv and copies in {vdir.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
