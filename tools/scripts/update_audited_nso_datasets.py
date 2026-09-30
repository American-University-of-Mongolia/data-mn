#!/usr/bin/env python3
"""Regenerate the NSO datasets identified by the July 2026 freshness audit.

The script consumes bilingual raw CSVs produced by datamn-source-nso and
updates the published derivatives, version snapshots, MDX freshness metadata,
and registry records in one repeatable operation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rebuild_downloads import process_dataset
from validate_title_years import check_page


ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "data.mn/public/datasets"
CONTENT = ROOT / "data.mn/src/data/data"
CHARTS = ROOT / "data.mn/public/charts"
VERSIONS = ROOT / "tools/versions"
REGISTRY = ROOT / "tools/registry/data.db"
TODAY = "2026-07-27"

SOURCE_UPDATED = {
    "nso-gdp-by-economic-activity": "2026-04-20T16:32:03",
    "nso-bop-monthly": "2026-07-08T15:25:08",
    "nso-temperature-by-station": "2026-07-22T16:12:00",
    "industrial-production-national": "2026-06-22T11:51:13",
}

GDP_SPLITS = [
    "gdp-nominal",
    "gdp-real",
    "gdp-usd",
    "gdp-growth-rate",
    "gdp-by-sector",
    "gdp-sector-trends",
]
BOP_SPLITS = [
    "bop-current-account",
    "bop-trade-balance",
    "bop-services-balance",
    "bop-fdi-net",
    "bop-reserve-assets",
    "bop-remittances",
]
TEMPERATURE_SPLITS = [
    "temperature-ulaanbaatar",
    "temperature-regional",
    "temperature-extremes-ulaanbaatar",
    "temperature-anomaly",
]


def clean_strings(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    for column in frame.select_dtypes(include=["object"]).columns:
        frame[column] = frame[column].astype(str).str.strip()
    return frame


def write_csv_pair(dataset_id: str, en: pd.DataFrame, mn: pd.DataFrame) -> None:
    en.to_csv(PUBLIC / f"{dataset_id}-en.csv", index=False)
    mn.to_csv(PUBLIC / f"{dataset_id}-mn.csv", index=False)


def rebuild_downloads_for(dataset_ids: list[str]) -> None:
    """Rebuild each dataset's single bilingual wide XLSX (Standard 1+2)."""
    for dataset_id in dataset_ids:
        report = process_dataset(dataset_id, apply=True)
        if report["queue"] != "auto":
            raise ValueError(
                f"{dataset_id}: rebuild_downloads routed to manual queue: "
                f"{report['reasons']}"
            )


def aligned_language_frames(en_path: Path, mn_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    en = clean_strings(pd.read_csv(en_path))
    mn = clean_strings(pd.read_csv(mn_path))
    if len(en) != len(mn):
        raise ValueError(f"Bilingual row mismatch: {en_path} ({len(en)}) vs {mn_path} ({len(mn)})")
    return en, mn


def regenerate_gdp(raw_root: Path) -> None:
    en, mn = aligned_language_frames(
        raw_root / "gdp/nso-0500-001v1-en.csv",
        raw_root / "gdp/nso-0500-001v1-mn.csv",
    )
    en.columns = ["indicator", "division", "year", "value"]
    mn.columns = ["indicator", "division", "year", "value"]

    def simple(indicator: str, dataset_id: str) -> None:
        mask = (en.indicator == indicator) & (en.division == "Total") & en.value.notna()
        out_en = en.loc[mask, ["year", "value"]].sort_values("year")
        out_mn = mn.loc[mask, ["year", "value"]].sort_values("year")
        out_mn.columns = ["он", "утга"]
        write_csv_pair(dataset_id, out_en, out_mn)

    simple("GDP, at current prices", "gdp-nominal")
    simple("GDP, at 2015 constant prices", "gdp-real")
    simple("GDP, at current price, thousand US dollars", "gdp-usd")
    simple("Annual changes, by percent", "gdp-growth-rate")

    current = en.indicator.eq("GDP, at current prices")
    latest_year = int(en.loc[current & en.value.notna(), "year"].astype(int).max())
    sector_mask = current & en.year.astype(int).eq(latest_year) & en.division.ne("Total") & en.value.notna()
    sector_en = en.loc[sector_mask, ["division", "value"]].rename(columns={"division": "sector"})
    sector_mn = mn.loc[sector_mask, ["division", "value"]].rename(
        columns={"division": "салбар", "value": "утга"}
    )
    write_csv_pair("gdp-by-sector", sector_en, sector_mn)

    sectors = {
        "Agriculture, forestry, fishing and hunting": "Agriculture",
        "Mining and quarrying": "Mining",
        "Manufacturing": "Manufacturing",
        "Construction": "Construction",
        "Wholesale and retail trade; repair of motor vehicles and motorcycles": "Trade",
        "Transportation and storage": "Transport",
    }
    trends_mask = current & en.division.isin(sectors) & en.value.notna()
    trends_en = en.loc[trends_mask, ["division", "year", "value"]].copy()
    trends_en["division"] = trends_en["division"].map(sectors)
    trends_en.columns = ["sector", "year", "value"]
    trends_en = trends_en.sort_values(["sector", "year"])
    trends_mn = mn.loc[trends_mask, ["division", "year", "value"]].copy()
    trends_mn.columns = ["салбар", "он", "утга"]
    trends_mn = trends_mn.sort_values(["салбар", "он"])
    write_csv_pair("gdp-sector-trends", trends_en, trends_mn)

    snapshot("nso-gdp-by-economic-activity", 2, en_path=raw_root / "gdp/nso-0500-001v1-en.csv",
             mn_path=raw_root / "gdp/nso-0500-001v1-mn.csv")


def regenerate_bop(raw_root: Path) -> None:
    en, mn = aligned_language_frames(
        raw_root / "bop/nso-0100-001v10-en.csv",
        raw_root / "bop/nso-0100-001v10-mn.csv",
    )
    en.columns = ["indicator", "month", "value"]
    mn.columns = ["indicator", "month", "value"]

    def simple(indicator: str, dataset_id: str) -> None:
        mask = en.indicator.eq(indicator) & en.value.notna()
        out_en = en.loc[mask, ["month", "value"]].sort_values("month")
        out_mn = mn.loc[mask, ["month", "value"]].sort_values("month")
        out_mn.columns = ["сар", "утга"]
        write_csv_pair(dataset_id, out_en, out_mn)

    simple("I. CURRENT ACCOUNT", "bop-current-account")
    simple("2. Services", "bop-services-balance")
    simple("1. Direct investment", "bop-fdi-net")
    simple("V. RESERVE ASSETS", "bop-reserve-assets")
    simple("of which: Personal transfers", "bop-remittances")

    exports = en.loc[en.indicator.eq("1.1 Export FOB (credit)"), ["month", "value"]]
    imports = en.loc[en.indicator.eq("1.2 Import FOB (debit)"), ["month", "value"]]
    trade = exports.merge(imports, on="month", suffixes=("_exports", "_imports")).dropna()
    trade.columns = ["month", "exports", "imports"]
    trade["net"] = trade.exports - trade.imports
    trade = trade.melt(id_vars="month", value_vars=["exports", "imports", "net"],
                       var_name="metric", value_name="value")
    trade["metric"] = trade.metric.map(
        {"exports": "Exports", "imports": "Imports", "net": "Net Balance"})
    trade_en = trade.sort_values(["month", "metric"]).reset_index(drop=True)
    trade_mn = trade_en.copy()
    trade_mn["metric"] = trade_mn.metric.map(
        {"Exports": "Экспорт", "Imports": "Импорт", "Net Balance": "Цэвэр тэнцэл"})
    trade_mn.columns = ["сар", "үзүүлэлт", "утга"]
    write_csv_pair("bop-trade-balance", trade_en, trade_mn)

    snapshot("nso-bop-monthly", 2, en_path=raw_root / "bop/nso-0100-001v10-en.csv",
             mn_path=raw_root / "bop/nso-0100-001v10-mn.csv")


def normalize_month(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, format="%Y-%m").dt.strftime("%Y-%m")


AVERAGE = "Average air temperature"
ANOMALY = "Comparison with multi-year (1981-2010)"


def _zscore(series: pd.Series) -> pd.Series:
    """z-score of each YYYY-MM value against the same calendar month."""
    month = series.index.str[5:7]
    grouped = series.groupby(month)
    return (series - grouped.transform("median")) / grouped.transform("std")


def _local_normal(implied: pd.Series, window: int = 3) -> pd.Series:
    """Baseline normal for each month: the median of ``mean - anomaly`` for
    the same calendar month within +/- ``window`` years, excluding the month
    itself. NSO revises its normal over time (Ulaanbaatar's July normal is
    16.9 C in 2005-2010 and 19.0 C from 2021), so nearby years are used."""
    years = implied.index.str[:4].astype(int)
    months = implied.index.str[5:7]
    out = pd.Series(index=implied.index, dtype=float)
    for key in implied.index:
        y, m = int(key[:4]), key[5:7]
        near = implied[(months == m) & (abs(years - y) <= window) & (implied.index != key)]
        out[key] = near.median()
    return out


def clean_temperature_table(en: pd.DataFrame, mn: pd.DataFrame, tolerance: float = 3.0):
    """Remove and correct known corruption in NSO table DT_NSO_2400_022V2.

    ``en``/``mn`` are row-aligned long frames (indicator, station, month,
    value) with EN indicator/station labels in ``en``. Returns cleaned copies.

    1. Copied months: a month whose values for every station and indicator
       duplicate another month's is dropped (2026-01 is an exact copy of
       2025-03 for all 29 stations). Of the pair, the month whose mean
       temperatures are atypical for its calendar month is the copy.
    2. For each station, the anomaly should equal mean minus the baseline
       normal. Where they disagree by more than ``tolerance`` C, a value is
       only recomputed when the evidence says which one is wrong:
       - anomaly = mean - normal, if the mean is typical for the month and
         the anomaly cell is clearly misplaced: it equals that month's
         minimum or maximum, equals the normal, or is exactly 0.0 (a
         missing value). 2008-11, 2016-03 and 2017-08 for Ulaanbaatar hold
         the minimum temperature or the normal;
       - mean = normal + anomaly, if the anomaly is typical and the station's
         mean is an outlier against the other stations that month, and the
         month is not itself flagged at several stations (2009-07
         Ulaanbaatar 25.1 C while its neighbours read 17-20 C; 2016-12
         Baruun-Urt +15.8 C is a sign error: mean = -(normal + anomaly), fixed
         by flipping the sign). A month flagged at several stations at once
         (e.g. 2022-12 in the west) is ambiguous and left alone;
       - otherwise the values are left unchanged with a warning (e.g. months
         where many stations shift by 3-5 C together, which looks like NSO
         applying a different baseline that month).
    3. Maximum/minimum cells that cannot be right are dropped (they cannot be
       reconstructed): a maximum below the month's mean, a minimum above it,
       or a value equal to the month's anomaly that is atypical for the
       calendar month. 2023-06 holds the anomaly in the maximum column at
       every station; Ulaanbaatar's 2023-07 minimum (-1.1 C) is its anomaly.
    """
    en, mn = en.copy(), mn.copy()
    key = en.station + "|" + en.indicator
    wide = en.assign(key=key).pivot_table(index="month", columns="key", values="value")
    avg_cols = [c for c in wide.columns if c.endswith("|" + AVERAGE)]
    drop = set()
    months = list(wide.index)
    for i, a in enumerate(months):
        for b in months[i + 1:]:
            both = wide.loc[a].notna() & wide.loc[b].notna()
            if both.sum() >= 20 and (wide.loc[a][both] == wide.loc[b][both]).mean() > 0.9:
                z = wide[avg_cols].apply(_zscore).abs()
                copy = a if z.loc[a].mean() > z.loc[b].mean() else b
                drop.add(copy)
                print(f"  temperature {copy}: all stations duplicate {b if copy == a else a}; dropping {copy}")
    keep = ~en.month.isin(drop)
    en, mn = en[keep], mn[keep]

    # Mean temperature z-scores per station, and each month's median across
    # stations, to tell a station-specific outlier from region-wide weather.
    mean_wide = en[en.indicator.eq(AVERAGE)].pivot_table(index="month", columns="station", values="value")
    mean_z = mean_wide.apply(_zscore)
    month_z = mean_z.median(axis=1)
    extremes = {ind: en[en.indicator.eq(ind)].pivot_table(index="month", columns="station", values="value")
                for ind in ("Maximum temperature", "Minimum temperature")}

    # Months where mean and anomaly disagree at several stations at once are
    # ambiguous (region-wide weather or a baseline change), so means in those
    # months are never rewritten.
    flagged = {}
    for station in en.station.unique():
        s = en[en.station.eq(station)]
        avg = s[s.indicator.eq(AVERAGE)].set_index("month").value.dropna()
        anom = s[s.indicator.eq(ANOMALY)].set_index("month").value.dropna()
        common = avg.index.intersection(anom.index)
        if len(common) >= 24:
            gap = ((avg[common] - anom[common]) - _local_normal(avg[common] - anom[common])).abs()
            for month in gap[gap > tolerance].index:
                flagged[month] = flagged.get(month, 0) + 1

    for station in en.station.unique():
        rows = en.station.eq(station)
        avg_rows = en.index[rows & en.indicator.eq(AVERAGE) & en.value.notna()]
        anom_rows = en.index[rows & en.indicator.eq(ANOMALY) & en.value.notna()]
        avg = pd.Series(en.loc[avg_rows, "value"].values, index=en.loc[avg_rows, "month"].values)
        anom = pd.Series(en.loc[anom_rows, "value"].values, index=en.loc[anom_rows, "month"].values)
        common = avg.index.intersection(anom.index)
        if len(common) < 24:
            continue
        avg, anom = avg[common].sort_index(), anom[common].sort_index()
        normal = _local_normal(avg - anom)
        bad = ((avg - anom) - normal).abs() > tolerance
        avg_z, anom_z = _zscore(avg).abs(), _zscore(anom).abs()
        for month in bad[bad].index:
            gap = abs((avg[month] - anom[month]) - normal[month])
            misplaced = (
                any(abs(anom[month] - extremes[ind].at[month, station]) < 0.05
                    for ind in extremes if station in extremes[ind] and month in extremes[ind].index)
                or abs(anom[month] - normal[month]) < 0.15
                or anom[month] == 0.0
            )
            station_outlier = (station in mean_z and month in mean_z.index
                               and abs(mean_z.at[month, station] - month_z[month]) > 2.5
                               and flagged.get(month, 0) < 3)
            sign_flip = abs(avg[month] + normal[month] + anom[month]) < 1.0
            if sign_flip and anom_z[month] < 2.5:
                fixed, which, rows_fix = round(-avg[month], 1), "mean (sign)", avg_rows
            elif avg_z[month] < 2.5 and misplaced:
                fixed, which, rows_fix = round(avg[month] - normal[month], 1), "anomaly", anom_rows
            elif anom_z[month] < 2.5 and station_outlier:
                fixed, which, rows_fix = round(normal[month] + anom[month], 1), "mean", avg_rows
            else:
                print(f"  WARNING temperature {station} {month}: mean {avg[month]} and anomaly "
                      f"{anom[month]} disagree by {gap:.1f} C; cause unclear, left unchanged")
                continue
            idx = [r for r in rows_fix if en.at[r, "month"] == month]
            old = en.loc[idx, "value"].iloc[0]
            en.loc[idx, "value"] = fixed
            mn.loc[idx, "value"] = fixed
            print(f"  temperature {station} {month}: {which} {old} -> {fixed} "
                  f"(normal {normal[month]:.1f})")
    # 3. Impossible or misplaced extremes (after the mean corrections above).
    means = en[en.indicator.eq(AVERAGE)].set_index(["station", "month"]).value
    anoms = en[en.indicator.eq(ANOMALY)].set_index(["station", "month"]).value
    drop_rows = []
    for ind, too_far in (("Maximum temperature", lambda v, m: v < m), ("Minimum temperature", lambda v, m: v > m)):
        ext = en[en.indicator.eq(ind) & en.value.notna()]
        for station, part in ext.groupby("station"):
            series = pd.Series(part.value.values, index=part.month.values)
            z = _zscore(series).abs()
            for idx, month, value in zip(part.index, part.month, part.value):
                mean, anom = means.get((station, month)), anoms.get((station, month))
                impossible = mean is not None and pd.notna(mean) and too_far(value, mean)
                is_anomaly = anom is not None and pd.notna(anom) and abs(value - anom) < 0.05 and z[month] > 2.5
                if impossible or is_anomaly:
                    drop_rows.append(idx)
                    print(f"  temperature {station} {month}: dropping {ind.split()[0].lower()} {value} "
                          f"({'contradicts mean ' + str(mean) if impossible else 'equals the anomaly'})")
    en, mn = en.drop(drop_rows), mn.drop(drop_rows)
    return en, mn


def regenerate_temperature(raw_root: Path) -> None:
    en, mn = aligned_language_frames(
        raw_root / "temperature/nso-2400-022v2-en.csv",
        raw_root / "temperature/nso-2400-022v2-mn.csv",
    )
    en.columns = ["indicator", "station", "month", "value"]
    mn.columns = ["indicator", "station", "month", "value"]
    en["month"] = normalize_month(en.month)
    mn["month"] = normalize_month(mn.month)
    en, mn = clean_temperature_table(en, mn)

    average = en.indicator.eq("Average air temperature")
    ub = en.station.eq("Ulaanbaatar")
    mask = average & ub & en.value.notna()
    out_en = en.loc[mask, ["month", "value"]].rename(columns={"value": "temperature"}).sort_values("month")
    out_mn = mn.loc[mask, ["month", "value"]].rename(
        columns={"month": "сар", "value": "температур"}
    ).sort_values("сар")
    write_csv_pair("temperature-ulaanbaatar", out_en, out_mn)

    stations = ["Ulaanbaatar", "Darkhan", "Dalanzadgad", "Choibalsan", "Khovd"]
    mask = average & en.station.isin(stations) & en.value.notna()
    out_en = en.loc[mask, ["month", "station", "value"]].rename(
        columns={"value": "temperature"}
    ).sort_values(["month", "station"])
    # Same row order as EN (sorting by MN station names would misalign rows).
    out_mn = mn.loc[out_en.index, ["month", "station", "value"]].rename(
        columns={"month": "сар", "station": "станц", "value": "температур"}
    )
    write_csv_pair("temperature-regional", out_en, out_mn)

    labels_en = {
        "Average air temperature": "Average",
        "Maximum temperature": "Maximum",
        "Minimum temperature": "Minimum",
    }
    labels_mn = {"Average": "Дундаж", "Maximum": "Хамгийн их", "Minimum": "Хамгийн бага"}
    mask = en.indicator.isin(labels_en) & ub & en.value.notna()
    out_en = en.loc[mask, ["month", "indicator", "value"]].copy()
    out_en["indicator"] = out_en.indicator.map(labels_en)
    out_en.columns = ["month", "indicator", "temperature"]
    out_en = out_en.sort_values(["month", "indicator"])
    out_mn = out_en.copy()
    out_mn["indicator"] = out_mn.indicator.map(labels_mn)
    out_mn.columns = ["сар", "үзүүлэлт", "температур"]
    write_csv_pair("temperature-extremes-ulaanbaatar", out_en, out_mn)

    anomaly = en.indicator.eq("Comparison with multi-year (1981-2010)")
    mask = anomaly & ub & en.value.notna()
    out_en = en.loc[mask, ["month", "value"]].rename(columns={"value": "anomaly"}).sort_values("month")
    out_mn = mn.loc[mask, ["month", "value"]].rename(
        columns={"month": "сар", "value": "хазайлт"}
    ).sort_values("сар")
    write_csv_pair("temperature-anomaly", out_en, out_mn)

    snapshot("nso-temperature-by-station", 1,
             en_path=raw_root / "temperature/nso-2400-022v2-en.csv",
             mn_path=raw_root / "temperature/nso-2400-022v2-mn.csv")


def regenerate_industrial(raw_root: Path) -> None:
    en, mn = aligned_language_frames(
        raw_root / "industrial/nso-1100-013v1-en.csv",
        raw_root / "industrial/nso-1100-013v1-mn.csv",
    )
    en.columns = ["commodity", "year", "value"]
    mn.columns = ["commodity", "year", "value"]
    selected = {
        "Coal (thous.t)": ("Coal", "Нүүрс", "thousand tonnes", "мян.тонн"),
        "Copper concentrate with 35% /thous.t/": (
            "Copper concentrate (35%)", "Зэсийн баяжмал (35%)", "thousand tonnes", "мян.тонн"
        ),
        "Gold /kg/": ("Gold", "Алт", "kg", "кг"),
        "Electricity /mln.k.W.h/": ("Electricity", "Цахилгаан эрчим хүч", "million kWh", "сая кВт.ц"),
        "Crude oil /thous.barrel/": ("Crude oil", "Газрын тос", "thousand barrels", "мян.баррель"),
        "Iron ore /thous.t/": ("Iron ore", "Төмрийн хүдэр", "thousand tonnes", "мян.тонн"),
        "Molybdenium concentrate with 47 % /t/": (
            "Molybdenum concentrate (47%)", "Молибдений баяжмал (47%)", "tonnes", "тонн"
        ),
    }
    mask = en.commodity.isin(selected) & en.value.notna()
    rows_en = []
    rows_mn = []
    for index in en.index[mask]:
        name_en, name_mn, unit_en, unit_mn = selected[en.at[index, "commodity"]]
        rows_en.append((int(en.at[index, "year"]), f"{name_en} ({unit_en})", en.at[index, "value"]))
        rows_mn.append((int(mn.at[index, "year"]), f"{name_mn} ({unit_mn})", mn.at[index, "value"]))
    order = pd.DataFrame(rows_en, columns=["year", "commodity", "value"])
    rank = order.sort_values(["year", "commodity"]).index
    out_en = order.loc[rank].reset_index(drop=True)
    out_mn = pd.DataFrame(
        rows_mn, columns=["он", "бараа_бүтээгдэхүүн", "утга"]
    ).loc[rank].reset_index(drop=True)
    write_csv_pair("industrial-production-national", out_en, out_mn)
    snapshot("industrial-production-national", 2,
             en_path=raw_root / "industrial/nso-1100-013v1-en.csv",
             mn_path=raw_root / "industrial/nso-1100-013v1-mn.csv")


def snapshot(dataset_id: str, version: int, *, en_path: Path, mn_path: Path) -> None:
    destination = VERSIONS / dataset_id / f"v{version}"
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copy2(en_path, destination / f"{dataset_id}-en.csv")
    shutil.copy2(mn_path, destination / f"{dataset_id}-mn.csv")
    metadata = {
        "dataset_id": dataset_id,
        "version": version,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source_updated_at": SOURCE_UPDATED[dataset_id],
        "source_files": [f"{dataset_id}-en.csv", f"{dataset_id}-mn.csv"],
    }
    (destination / "version.json").write_text(json.dumps(metadata, indent=2) + "\n")


def snapshot_published(dataset_ids: list[str], version: int, source_updated_at: str) -> None:
    for dataset_id in dataset_ids:
        destination = VERSIONS / dataset_id / f"v{version}"
        destination.mkdir(parents=True, exist_ok=True)
        files = [
            PUBLIC / f"{dataset_id}-en.csv",
            PUBLIC / f"{dataset_id}-mn.csv",
            PUBLIC / f"{dataset_id}.xlsx",
        ]
        for source in files:
            shutil.copy2(source, destination / source.name)
        metadata = {
            "dataset_id": dataset_id,
            "version": version,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "source_updated_at": source_updated_at,
            "files": [source.name for source in files],
        }
        (destination / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")


def refresh_mdx_and_charts(dataset_ids: list[str], latest: str, version: int) -> None:
    for dataset_id in dataset_ids:
        for language in ("en", "mn"):
            path = CONTENT / language / f"{dataset_id}.mdx"
            text = path.read_text()
            text = re.sub(r"^dataVersion: \d+$", f"dataVersion: {version}", text, flags=re.MULTILINE)
            text = re.sub(r"^dataDate: .+$", f"dataDate: {latest}", text, flags=re.MULTILINE)
            path.write_text(text)
            # Move title/excerpt/chart-title spans to the new data span.
            check_page(path, fix=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def update_registry() -> None:
    fetched = datetime.now(timezone.utc).isoformat()
    groups = [
        ("nso-gdp-by-economic-activity", GDP_SPLITS, "2025", 2),
        ("nso-bop-monthly", BOP_SPLITS, "2026-05", 2),
        ("nso-temperature-by-station", TEMPERATURE_SPLITS, "2026-06", 1),
        ("industrial-production-national", [], "2025", 2),
    ]
    with sqlite3.connect(REGISTRY) as connection:
        for parent, splits, data_as_of, version in groups:
            ids = [parent, *splits]
            placeholders = ",".join("?" for _ in ids)
            connection.execute(
                f"""UPDATE datasets
                    SET status='active', current_version=?, data_as_of=?,
                        source_updated_at=?, last_checked_at=?, last_fetched_at=?
                    WHERE id IN ({placeholders})""",
                (version, data_as_of, SOURCE_UPDATED[parent], fetched, fetched, *ids),
            )
            data_path = str(VERSIONS / parent / f"v{version}")
            raw_en = Path(data_path) / f"{parent}-en.csv"
            connection.execute(
                "DELETE FROM versions WHERE dataset_id=? AND version=?",
                (parent, version),
            )
            connection.execute(
                """INSERT INTO versions
                   (dataset_id, version, data_hash, data_path, row_count, column_count,
                    change_type, change_summary, source_updated_at, source_raw_files)
                   VALUES (?, ?, ?, ?, ?, ?, 'source_update', ?, ?, ?)""",
                (
                    parent,
                    version,
                    sha256(raw_en),
                    str(Path(data_path).relative_to(ROOT)),
                    len(pd.read_csv(raw_en)),
                    len(pd.read_csv(raw_en, nrows=0).columns),
                    f"Refreshed source data through {data_as_of}",
                    SOURCE_UPDATED[parent],
                    json.dumps([raw_en.name, f"{parent}-mn.csv"]),
                ),
            )
            connection.execute(
                """INSERT INTO activity_log
                   (action, dataset_id, source_id, status, message, triggered_by)
                   VALUES ('update', ?, 'nso-1212', 'success', ?, 'manual')""",
                (parent, f"Updated source data and {len(splits)} derived datasets through {data_as_of}"),
            )

        # The two nested table IDs remain valid; only their API paths were incomplete.
        connection.execute(
            """UPDATE datasets SET source_path=?
               WHERE id='labor-participation-national'""",
            ("Labour, business/Labour/LABOUR FORCE PARTICIPATION RATE, by sex, age group, aimags and the Capital/DT_NSO_0400_018V1_1.px",),
        )
        connection.execute(
            """UPDATE datasets SET source_path=?
               WHERE id='salary-average-national'""",
            ("Labour, business/Wages/MONTHLY AVERAGE NOMINAL WAGES, by division of economic activities/DT_NSO_0400_022V1.px",),
        )
        # V1 was retired; V3 preserves the type/region/year dimensions.
        connection.execute(
            """UPDATE datasets SET source_ref=?, source_path=?, source_updated_at=?
               WHERE id='hospital-beds-national'""",
            (
                "DT_NSO_2100_005V3.px",
                "Education, health/Main indicators for Health sector/DT_NSO_2100_005V3.px",
                "2026-05-06T15:41:29",
            ),
        )

        source_metadata = {
            "household-income-by-location": (
                "DT_NSO_1900_001V1.px", "Society, development/Household income and expenditure",
                "2026-05-29T12:44:23"
            ),
            "household-income-total": (
                "DT_NSO_1900_001V1.px", "Society, development/Household income and expenditure",
                "2026-05-29T12:44:23"
            ),
            "nso-deaths-by-region-monthly": (
                "DT_NSO_2100_027V2.px", "Education, health/Births, deaths",
                "2026-07-09T18:30:38"
            ),
            "nso-deaths-monthly": (
                "DT_NSO_2100_027V2.px", "Education, health/Births, deaths",
                "2026-07-09T18:30:38"
            ),
            "nso-exports-by-country-top": (
                "DT_NSO_1400_006V3.px", "Economy, environment/Foreign Trade",
                "2026-04-14T17:27:45"
            ),
            "nso-foreign-trade-annual": (
                "DT_NSO_1400_001V1_year.px", "Economy, environment/Foreign Trade",
                "2026-04-13T09:30:49"
            ),
            "nso-foreign-trade-monthly": (
                "DT_NSO_1400_003V1.px", "Economy, environment/Foreign Trade",
                "2026-07-09T12:25:28"
            ),
            "nso-imports-by-country-top": (
                "DT_NSO_1400_010V3.px", "Economy, environment/Foreign Trade",
                "2026-04-15T11:02:21"
            ),
            "nso-live-births-by-region-monthly": (
                "DT_NSO_2100_018V5.px", "Education, health/Births, deaths",
                "2026-07-09T18:29:03"
            ),
            "nso-live-births-monthly": (
                "DT_NSO_2100_018V5.px", "Education, health/Births, deaths",
                "2026-07-09T18:29:03"
            ),
            "nso-marriages-divorces-annual": (
                "DT_NSO_0300_018V2.px", "Population, household/2_Regular movement of population",
                "2026-05-05T11:17:03"
            ),
            "nso-population-age-sex": (
                "DT_NSO_0300_003V1.px", "Population, household/1_Population, household",
                "2026-05-01T14:52:02"
            ),
            "trade-exports-imports": (
                "DT_NSO_1400_001V1_year.px", "Economy, environment/Foreign Trade",
                "2026-04-13T09:30:49"
            ),
            "trade-total": (
                "DT_NSO_1400_001V1_year.px", "Economy, environment/Foreign Trade",
                "2026-04-13T09:30:49"
            ),
        }
        for dataset_id, (source_ref, source_path, updated) in source_metadata.items():
            connection.execute(
                """UPDATE datasets
                   SET source_ref=?, source_path=?, source_updated_at=?, last_checked_at=?
                   WHERE id=?""",
                (source_ref, source_path, updated, fetched, dataset_id),
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--raw-root",
        type=Path,
        required=True,
        help="Directory containing gdp/, bop/, temperature/, and industrial/ raw fetches",
    )
    args = parser.parse_args()
    regenerate_gdp(args.raw_root)
    regenerate_bop(args.raw_root)
    regenerate_temperature(args.raw_root)
    regenerate_industrial(args.raw_root)
    refresh_mdx_and_charts(GDP_SPLITS, "2025-12-31", 2)
    refresh_mdx_and_charts(BOP_SPLITS, "2026-05-31", 2)
    refresh_mdx_and_charts(TEMPERATURE_SPLITS, "2026-06-30", 1)
    refresh_mdx_and_charts(["industrial-production-national"], "2025-12-31", 2)
    rebuild_downloads_for([
        *GDP_SPLITS,
        *BOP_SPLITS,
        *TEMPERATURE_SPLITS,
        "industrial-production-national",
    ])
    snapshot_published(GDP_SPLITS, 2, SOURCE_UPDATED["nso-gdp-by-economic-activity"])
    snapshot_published(BOP_SPLITS, 2, SOURCE_UPDATED["nso-bop-monthly"])
    snapshot_published(TEMPERATURE_SPLITS, 1, SOURCE_UPDATED["nso-temperature-by-station"])
    update_registry()


if __name__ == "__main__":
    main()
