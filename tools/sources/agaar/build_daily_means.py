#!/usr/bin/env python3
"""Build the cleaned daily PM2.5 station means (parent dataset).

Reads the raw daily archive (raw/daily/agaar-daily-*.csv) and writes
derived/agaar-daily-station-means.csv: one row per station-day with the raw
PM2.5 value, the cleaned value (blank when dropped) and the reason it was
dropped. Also writes derived/agaar-daily-station-means.meta.json with
coverage and per-rule counts, which the split pages quote.

The raw archive is never modified (see source.md, "Raw values are kept as
served"). Cleaning rules, applied in this order, first match wins:

  negative   PM2.5 below zero.
  above_pm10 PM2.5 more than 10% above the same day's PM10 (and above 50).
             PM2.5 is a subset of PM10, so this can't be real.
  spike      More than 5x that day's median across all reporting stations,
             and above 150.
  flat       The same value on 5 or more consecutive days at one station
             (a stuck sensor).

It also writes the four page tables (derived/pm25-*.csv) from the cleaned
values; see datasets/agaar-daily-station-means.md for what each one is.

Usage:  python3 tools/sources/agaar/build_daily_means.py
"""
import glob
import json
import os
from datetime import datetime, timezone

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OUT_DIR = os.path.join(HERE, "derived")
OUT = os.path.join(OUT_DIR, "agaar-daily-station-means.csv")
META = os.path.join(OUT_DIR, "agaar-daily-station-means.meta.json")

ABOVE_PM10_RATIO = 1.1
ABOVE_PM10_MIN = 50
SPIKE_RATIO = 5
SPIKE_MIN = 150
FLAT_DAYS = 5

PAGE_START = "2025-10"        # first full month with UB stations reporting
WINTER = ("2025-12-01", "2026-02-28")
WINTER_MIN_DAYS = 60          # station-days a bar needs in the winter window
UB_MIN_STATIONS = 8           # stations a UB day needs to count
MNS_LIMIT = 50                # MNS 4585:2016, 24-hour PM2.5 (µg/m³)

# English station names (romanized; the site has Mongolian only).
STATION_EN = {
    "10101": "Bayan-Ulgii-01", "10201": "Ulaangom-01", "10301": "Khovd-01",
    "10401": "Uliastai-01", "10501": "Altai-01", "10602": "Bayankhongor-02",
    "10701": "Undurkhaan-01", "10702": "Undurkhaan-02", "10801": "Choibalsan-01",
    "10901": "Baruun-Urt-01", "11001": "Murun-01", "11101": "Tsetserleg-01",
    "11201": "Arvaikheer-01", "11301": "Bulgan-01", "11403": "Erdenet-03",
    "11404": "Erdenet Kindergarten No. 2", "11405": "Erdenet Mine",
    "11501": "Sukhbaatar-01", "11601": "Darkhan-01", "11701": "Zuunmod-01",
    "11801": "Choir-01", "11902": "Dalanzadgad-01", "12001": "Mandalgovi-01",
    "12101": "Sainshand-01",
    "12301": "Wrestling Palace", "12303": "Urgakh Naran", "12304": "Sharkhad",
    "12305": "Amgalan-3", "12306": "New 100 Ail Center", "12401": "1st Microdistrict",
    "12402": "Tolgoit-1", "12403": "Bayankhoshuu-6", "12404": "5 Shar",
    "12501": "100 Ail", "12503": "5 Buudal", "12504": "Dambadarjaa-5",
    "12601": "Misheel Expo", "12602": "Vitafit Milk", "12603": "Bogd Khan Palace Museum",
    "12604": "Yarmag", "12605": "Nisekh-4", "12701": "Khailaast",
    "12801": "Baruun 4 Zam", "12802": "MUST-2", "12803": "End of 3rd-4th Microdistrict",
    "12901": "Nalaikh",
}


def load():
    daily = pd.concat(
        [pd.read_csv(f, dtype={"station_code": str})
         for f in sorted(glob.glob(os.path.join(RAW, "daily", "agaar-daily-*.csv")))],
        ignore_index=True)
    stations = pd.read_csv(os.path.join(RAW, "agaar-stations.csv"), dtype=str)
    daily = daily[["station_code", "date", "validated", "pm25", "pm10"]]
    daily = daily[daily["pm25"].notna()].copy()
    st = stations[["station_code", "name_mn", "aimag_code", "aimag_mn", "aimag_en"]]
    df = daily.merge(st, on="station_code", how="left")
    df["station_en"] = df["station_code"].map(STATION_EN).fillna(df["name_mn"])
    df["ulaanbaatar"] = (df["aimag_en"] == "Ulaanbaatar").astype(int)
    return df.sort_values(["station_code", "date"]).reset_index(drop=True)


def clean(df):
    pm25, pm10 = df["pm25"], df["pm10"]
    reason = pd.Series("", index=df.index)

    def flag(mask, name):
        reason[(reason == "") & mask] = name

    flag(pm25 < 0, "negative")
    flag(pm10.notna() & (pm25 > pm10 * ABOVE_PM10_RATIO) & (pm25 > ABOVE_PM10_MIN), "above_pm10")
    day_median = df.groupby("date")["pm25"].transform("median")
    flag((pm25 > SPIKE_RATIO * day_median) & (pm25 > SPIKE_MIN), "spike")
    # Runs of identical values on consecutive calendar days, per station.
    d = pd.to_datetime(df["date"])
    new_run = ((df["station_code"] != df["station_code"].shift())
               | (pm25 != pm25.shift())
               | (d - d.shift() != pd.Timedelta(days=1)))
    run_id = new_run.cumsum()
    flag(df.groupby(run_id)["pm25"].transform("size") >= FLAT_DAYS, "flat")

    df["pm25_raw"] = pm25
    df["pm25"] = pm25.where(reason == "")
    df["dropped_reason"] = reason
    return df


def build_pages(df, last_date):
    """The four page tables, from cleaned values from PAGE_START on."""
    c = df[df["pm25"].notna() & (df["date"] >= PAGE_START)].copy()
    c["month"] = c["date"].str[:7]
    # Complete months only: the current month would show a partial mean.
    last = pd.Timestamp(last_date)
    last_full = (last.to_period("M") - (0 if last.is_month_end else 1)).strftime("%Y-%m")
    c_full = c[c["month"] <= last_full]
    tables = {}

    m = (c_full.groupby(["month", "ulaanbaatar"])
         .agg(pm25=("pm25", "mean"), stations=("station_code", "nunique"),
              station_days=("pm25", "size"))
         .reset_index())
    m["area_en"] = m["ulaanbaatar"].map({1: "Ulaanbaatar", 0: "Aimag centres"})
    m["area_mn"] = m["ulaanbaatar"].map({1: "Улаанбаатар", 0: "Аймгийн төвүүд"})
    m["pm25"] = m["pm25"].round(1)
    tables["pm25-monthly-ulaanbaatar-aimags"] = m[
        ["month", "area_en", "area_mn", "pm25", "stations", "station_days"]]

    ub = c_full[c_full["ulaanbaatar"] == 1]
    days = ub.groupby("date").agg(pm25=("pm25", "mean"), stations=("station_code", "nunique"))
    days = days[days["stations"] >= UB_MIN_STATIONS].reset_index()
    days["month"] = days["date"].str[:7]
    u = (days.groupby("month")
         .agg(days_with_data=("pm25", "size"),
              days_above_limit=("pm25", lambda x: int((x > MNS_LIMIT).sum())),
              max_city_mean=("pm25", "max"))
         .reset_index())
    u["max_city_mean"] = u["max_city_mean"].round(1)
    tables["pm25-unhealthy-days-ulaanbaatar"] = u

    w = c[(c["date"] >= WINTER[0]) & (c["date"] <= WINTER[1])]
    a = (w.groupby(["aimag_en", "aimag_mn"])
         .agg(pm25=("pm25", "mean"), stations=("station_code", "nunique"),
              station_days=("pm25", "size"))
         .reset_index())
    a = a[a["station_days"] >= WINTER_MIN_DAYS].sort_values("pm25", ascending=False)
    a["pm25"] = a["pm25"].round(1)
    tables["pm25-winter-by-aimag-centre"] = a

    s_ = (w[w["ulaanbaatar"] == 1].groupby(["station_code", "station_en", "name_mn"])
          .agg(pm25=("pm25", "mean"), days=("pm25", "size"))
          .reset_index())
    s_ = s_[s_["days"] >= WINTER_MIN_DAYS].sort_values("pm25", ascending=False)
    s_["pm25"] = s_["pm25"].round(1)
    tables["pm25-winter-by-station-ulaanbaatar"] = s_

    for name, t in tables.items():
        t.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False, lineterminator="\n")
    return {name: len(t) for name, t in tables.items()}, last_full


def main():
    df = clean(load())
    cols = ["station_code", "station_en", "name_mn", "aimag_code", "aimag_en", "aimag_mn",
            "ulaanbaatar", "date", "validated", "pm25", "pm25_raw", "pm10", "dropped_reason"]
    os.makedirs(OUT_DIR, exist_ok=True)
    df[cols].to_csv(OUT, index=False, lineterminator="\n")
    counts = df["dropped_reason"].value_counts()
    meta = {
        "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "first_date": df["date"].min(),
        "last_date": df["date"].max(),
        "station_days": int(len(df)),
        "station_days_kept": int(df["pm25"].notna().sum()),
        "dropped": {k: int(counts.get(k, 0))
                    for k in ("negative", "above_pm10", "spike", "flat")},
        "rules": {"above_pm10_ratio": ABOVE_PM10_RATIO, "above_pm10_min": ABOVE_PM10_MIN,
                  "spike_ratio": SPIKE_RATIO, "spike_min": SPIKE_MIN, "flat_days": FLAT_DAYS},
        "stations": int(df["station_code"].nunique()),
    }
    meta["dropped_total"] = sum(meta["dropped"].values())
    meta["page_tables"], meta["last_full_month"] = build_pages(df, meta["last_date"])
    with open(META, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
