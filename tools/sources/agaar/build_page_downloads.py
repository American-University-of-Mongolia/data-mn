#!/usr/bin/env python3
"""Write the four PM2.5 pages' download files from the derived page tables.

Run after build_daily_means.py. For each split it writes the four CSVs in
data.mn/public/datasets/ ({id}-en.csv / -mn.csv, used by the charts, and
{id}-all-en.csv / -all-mn.csv, the page downloads) from
derived/{id}.csv. For every split whose CSVs changed it then rebuilds the
bilingual XLSX and the MDX dataFiles sizes with
tools/scripts/rebuild_downloads.py.

rebuild_downloads.py refuses to overwrite an XLSX whose totals differ from
the CSV (a guard against stale hand-edited files). New data always changes the
totals, so the old XLSX is removed first. It is in git if you need it back.

Page text (titles, excerpts, dropped counts) is not touched; see
datasets/agaar-daily-station-means.md, "Update Instructions".

Usage (from the repo root):
    python3 tools/sources/agaar/build_page_downloads.py          # write
    python3 tools/sources/agaar/build_page_downloads.py --check  # report only, exit 1 if stale
"""
import argparse
import io
import os
import subprocess
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DERIVED = os.path.join(HERE, "derived")
DATASETS = os.path.join(ROOT, "data.mn", "public", "datasets")
REBUILD = os.path.join(ROOT, "tools", "scripts", "rebuild_downloads.py")

UNHEALTHY_MEASURES = [
    # derived column, EN label, MN label
    ("days_with_data", "Days with data", "Мэдээлэлтэй өдөр"),
    ("days_above_limit", "Days above 50 µg/m³", "50 мкг/м³-аас дээш өдөр"),
    ("max_city_mean", "Highest city-wide daily mean (µg/m³)",
     "Хотын өдрийн дундажийн дээд (мкг/м³)"),
]


def first_of_month(s):
    return s + "-01"


def monthly(t):
    t = t.assign(month=first_of_month(t["month"])).sort_values(["month", "area_en"])
    en = ["month", "area", "pm25_ug_m3"]
    mn = ["сар", "бүс", "pm25_мкг_м3"]
    return {
        "en": t[["month", "area_en", "pm25", "stations", "station_days"]]
        .set_axis(en + ["stations", "station_days"], axis=1),
        "mn": t[["month", "area_mn", "pm25", "stations", "station_days"]]
        .set_axis(mn + ["станц", "станцын_өдөр"], axis=1),
        "all-en": t[["month", "area_en", "pm25"]].set_axis(en, axis=1),
        "all-mn": t[["month", "area_mn", "pm25"]].set_axis(mn, axis=1),
    }


def unhealthy(t):
    t = t.assign(month=first_of_month(t["month"]))
    wide = t[["month", "days_with_data", "days_above_limit", "max_city_mean"]]
    out = {
        "en": wide.set_axis(["month", "days_with_data", "days_above_limit",
                             "max_city_mean_ug_m3"], axis=1),
        "mn": wide.set_axis(["сар", "мэдээлэлтэй_өдөр", "хэмжээ_давсан_өдөр",
                             "хотын_дээд_дундаж_мкг_м3"], axis=1),
    }
    for lang, cols, i in (("en", ["month", "measure", "value"], 1),
                          ("mn", ["сар", "үзүүлэлт", "утга"], 2)):
        rows = [[r["month"], m[i], float(r[m[0]])]
                for _, r in t.iterrows() for m in UNHEALTHY_MEASURES]
        out[f"all-{lang}"] = pd.DataFrame(rows, columns=cols)
    return out


def winter_aimag(t):
    # The -mn chart CSV keeps English headers: the MN chart spec reads them.
    detail = ["aimag", "pm25", "stations", "station_days"]
    return {
        "en": t[["aimag_en", "pm25", "stations", "station_days"]].set_axis(detail, axis=1),
        "mn": t[["aimag_mn", "pm25", "stations", "station_days"]].set_axis(detail, axis=1),
        "all-en": t[["aimag_en", "pm25"]].set_axis(["aimag", "pm25"], axis=1),
        "all-mn": t[["aimag_mn", "pm25"]].set_axis(["аймаг", "pm25"], axis=1),
    }


def winter_station(t):
    en = t[["station_code", "station_en", "pm25", "days"]].set_axis(
        ["station_code", "station", "pm25_ug_m3", "valid_days"], axis=1)
    mn = t[["station_code", "name_mn", "pm25", "days"]].set_axis(
        ["станцын_код", "станц", "pm25_мкг_м3", "хүчинтэй_өдөр"], axis=1)
    return {"en": en, "mn": mn, "all-en": en, "all-mn": mn}


SPLITS = {
    "pm25-monthly-ulaanbaatar-aimags": monthly,
    "pm25-unhealthy-days-ulaanbaatar": unhealthy,
    "pm25-winter-by-aimag-centre": winter_aimag,
    "pm25-winter-by-station-ulaanbaatar": winter_station,
}


def to_csv(df):
    buf = io.StringIO()
    df.to_csv(buf, index=False, lineterminator="\n")
    return buf.getvalue()


def current(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8", newline="") as f:
        return f.read().replace("\r\n", "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="only report files that would change; exit 1 if any")
    args = ap.parse_args()

    stale = []
    for split, build in SPLITS.items():
        table = pd.read_csv(os.path.join(DERIVED, f"{split}.csv"),
                            dtype={"month": str, "station_code": str})
        changed = []
        for suffix, df in build(table).items():
            name = f"{split}-{suffix}.csv"
            path = os.path.join(DATASETS, name)
            text = to_csv(df)
            if current(path) == text:
                continue
            changed.append(name)
            if not args.check:
                with open(path, "w", encoding="utf-8", newline="") as f:
                    f.write(text)
        print(f"{split}: {', '.join(changed) if changed else 'unchanged'}")
        if not changed:
            continue
        stale.append(split)
        if args.check:
            continue
        xlsx = os.path.join(DATASETS, f"{split}.xlsx")
        if os.path.exists(xlsx):
            os.remove(xlsx)
        r = subprocess.run([sys.executable, REBUILD, "--dataset", split, "--apply"],
                           capture_output=True, text=True, encoding="utf-8")
        if r.returncode != 0 or '"queue": "manual"' in r.stdout:
            print(r.stdout + r.stderr)
            sys.exit(f"rebuild_downloads.py failed for {split}")
        print(f"  rebuilt {split}.xlsx and MDX dataFiles")

    if args.check and stale:
        sys.exit(1)


if __name__ == "__main__":
    main()
