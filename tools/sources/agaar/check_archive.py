#!/usr/bin/env python3
"""Safety check for an archive run: nothing in the raw archive may be lost.

Compares every raw CSV that differs between a base git ref (default
origin/main) and the working tree:

  rows lost    a (station_code, datetime) hourly or (station_code, date) daily
               key in the base file is missing now
  values lost  a pollutant value that was filled in the base file is empty now

Changed values (the site revising real-time numbers) are counted but are not
an error. New files are listed as new. Exit 1 if any row or value was lost.
The raw files are only read, never changed.

Usage (from the repo root):
    python3 tools/sources/agaar/check_archive.py               # vs origin/main
    python3 tools/sources/agaar/check_archive.py --base main
"""
import argparse
import csv
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RAW_REL = "tools/sources/agaar/raw"
KEYS = {"hourly": ["station_code", "datetime"], "daily": ["station_code", "date"]}
VALUES = ["pm10", "pm25", "o3", "no2", "co", "so2", "pm10_24h", "pm25_24h", "aqi"]


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True, encoding="utf-8", check=True).stdout


def rows(text, keys):
    out = {}
    for r in csv.DictReader(io.StringIO(text)):
        out[tuple(r[k] for k in keys)] = r
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--base", default="origin/main", help="git ref to compare against")
    args = ap.parse_args()

    names = git("diff", "--name-only", args.base, "--", RAW_REL).split()
    names += git("ls-files", "--others", "--exclude-standard", "--", RAW_REL).split()
    lost_any = False
    for name in sorted(set(names)):
        freq = name.split("/")[-2]
        if freq not in KEYS or not name.endswith(".csv"):
            continue
        with open(os.path.join(ROOT, name), encoding="utf-8", newline="") as f:
            new = rows(f.read(), KEYS[freq])
        try:
            old = rows(git("show", f"{args.base}:{name}"), KEYS[freq])
        except subprocess.CalledProcessError:
            print(f"{name}: new file, {len(new)} rows")
            continue
        lost_rows = [k for k in old if k not in new]
        lost_vals = changed = 0
        for k, o in old.items():
            n = new.get(k)
            if n is None:
                continue
            for c in VALUES:
                ov, nv = o.get(c, "").strip(), n.get(c, "").strip()
                if ov and not nv:
                    lost_vals += 1
                elif ov and nv != ov:
                    changed += 1
        lost_any |= bool(lost_rows or lost_vals)
        print(f"{name}: rows {len(old)} -> {len(new)}, rows lost {len(lost_rows)}, "
              f"values lost {lost_vals}, values changed {changed}")
        for k in lost_rows[:10]:
            print(f"  lost row {k}")
    print("FAIL: data lost" if lost_any else "OK: 0 rows lost, 0 values lost")
    sys.exit(1 if lost_any else 0)


if __name__ == "__main__":
    main()
