#!/usr/bin/env python3
"""Download station history from agaar.gov.mn into monthly CSVs.

Usage:
    # Backfill everything the site serves (from 2025-02) -> today
    python3 fetch_data.py --output ../../../tools/sources/agaar/raw

    # Routine update: re-fetch only the most recent months (default 3)
    python3 fetch_data.py --output ../../../tools/sources/agaar/raw --update

    # Narrow it down (testing)
    python3 fetch_data.py --output /tmp/agaar --from 2026-01 --to 2026-01 \
        --stations 12401,10101 --freq daily

Outputs in --output:
    hourly/agaar-hourly-YYYY-MM.csv  one row per station-hour
    daily/agaar-daily-YYYY-MM.csv    one row per station-day (site's daily means)
    agaar-stations.csv               station catalog (code, names, aimag, lat/lon)
    agaar-pulls.json                 manifest: per month+freq rows, completeness

How the endpoint behaves (verified 2026-10-03; see SKILL.md):
  * History starts 2025-02-19 (one station); UB stations from 2025-09.
  * Validated rows (LASTDATA=Y, blue on the site) come back only for the
    calendar month the query starts in, so we always query one calendar
    month per request. Validated rows win over real-time ones.
  * Hours are hour-ending 01..24 in local time (UTC+8); we also emit
    `datetime` = start of the hour window.
  * PM25_YN=N means the site withholds PM2.5 for that row; we blank it too
    and set pm25_withheld=1.

Stdlib only.
"""
import argparse
import calendar
import csv
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone

from agaar_client import ITEMS, AgaarClient, FetchError, ServerError, log

HERE = os.path.dirname(os.path.abspath(__file__))
CATALOG = os.path.join(HERE, "stations.json")
FIRST_MONTH = (2025, 2)  # earliest data the site served on 2026-10-03 (one station, 2025-02-19)

POLLUTANTS = [ITEMS[c]["key"] for c in ITEMS]  # pm10 pm25 o3 no2 co so2
HOURLY_COLS = (["station_code", "datetime", "date", "hour", "validated"] + POLLUTANTS
               + ["pm10_24h", "pm25_24h", "concentrations_source",
                  "aqi", "aqi_pollutant", "aqi_grade", "pm25_withheld"])
DAILY_COLS = (["station_code", "date", "validated"] + POLLUTANTS
              + ["concentrations_source", "pm25_withheld"])
# A past month with no validated rows yet keeps being re-fetched until it is
# this many months old, in case NAMEM validates late.
VALIDATION_WAIT_MONTHS = 12
STATION_COLS = ["station_code", "name_mn", "address_mn", "aimag_code", "aimag_mn",
                "aimag_en", "lat", "lon", "mang_code", "listed"]


def num(v):
    if v in (None, "", "-"):
        return ""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return ""
    return int(f) if f.is_integer() else round(f, 3)


def parse_hourly(code, r):
    d, _, h = (r.get("DATA_TIME2") or "").partition(":")
    if not d or not h.isdigit():
        return None
    hour = int(h)
    start = datetime.strptime(d, "%Y-%m-%d") + timedelta(hours=hour - 1)
    row = {"station_code": code, "datetime": start.strftime("%Y-%m-%d %H:00"),
           "date": d, "hour": hour, "validated": 1 if r.get("LASTDATA") == "Y" else 0}
    for item, meta in ITEMS.items():
        row[meta["key"]] = num(r.get("VALUE_" + item))
    row["pm10_24h"] = num(r.get("VALUE_24AVG_10007"))
    row["pm25_24h"] = num(r.get("VALUE_24AVG_10008"))
    row["aqi"] = num(r.get("KHAI_VALUE"))
    row["aqi_pollutant"] = ITEMS.get(str(r.get("KHAI_ITEM_CODE")), {}).get("key", "")
    row["aqi_grade"] = num(r.get("KHAI_GRADE"))
    withheld = r.get("PM25_YN") == "N"
    if withheld:
        row["pm25"] = row["pm25_24h"] = ""
    row["pm25_withheld"] = 1 if withheld else 0
    return row


def parse_daily(code, r):
    d = r.get("DATA_TIME") or ""
    if len(d) != 10:
        return None
    row = {"station_code": code, "date": d, "validated": 1 if r.get("LASTDATA") == "Y" else 0}
    for item, meta in ITEMS.items():
        row[meta["key"]] = num(r.get("VALUE_" + item))
    withheld = r.get("PM25_YN") == "N"
    if withheld:
        row["pm25"] = ""
    row["pm25_withheld"] = 1 if withheld else 0
    return row


def empty(v):
    return v in ("", None)


def has_values(row, cols):
    return any(not empty(row.get(c)) for c in cols)


def as_int(v):
    return 0 if empty(v) else int(float(v))


def conc_source(row, conc_cols):
    """Where a row's concentrations came from: validated / realtime / mixed / "".

    Rows parsed from the site get it from their own LASTDATA flag. Archive
    rows written before this column existed are inferred the same way, which
    is exact: back then a row's values always came from one site row.
    """
    if not has_values(row, conc_cols):
        return ""
    if not empty(row.get("concentrations_source")):
        return row["concentrations_source"]
    return "validated" if as_int(row.get("validated")) else "realtime"


def merge_rows(older, newer, conc_cols):
    """Merge two rows for the same key, field by field.

    `validated`, AQI and pm25_withheld come from the validated row (the newer
    one on a tie). Each concentration takes the first non-empty value from:
    a validated source, the newer row, the older row. So an AQI-only
    validated row never erases concentrations already in the archive, which
    the site stops serving once it validates a month.
    """
    auth, other = ((newer, older) if as_int(newer.get("validated")) >= as_int(older.get("validated"))
                   else (older, newer))
    out = dict(auth)
    for k, v in other.items():  # fill status fields the authoritative row lacks
        if k not in conc_cols and k != "concentrations_source" and empty(out.get(k)):
            out[k] = v
    ranked = sorted([(newer, conc_source(newer, conc_cols)), (older, conc_source(older, conc_cols))],
                    key=lambda rs: rs[1] != "validated")  # stable: validated, then newer, then older
    used = set()
    for c in conc_cols:
        out[c] = ""
        for row, src in ranked:
            if not empty(row.get(c)):
                out[c] = row[c]
                used.add(src)
                break
    if as_int(out.get("pm25_withheld")):  # the site withholds PM2.5 for this row
        for c in ("pm25", "pm25_24h"):
            if c in out:
                out[c] = ""
    out["concentrations_source"] = ""
    if has_values(out, conc_cols):
        out["concentrations_source"] = used.pop() if len(used) == 1 else "mixed"
    return out


def merge_all(rows, key_cols, conc_cols, keep_cols):
    """Fold rows into one per key, in order (later rows count as newer).

    Rows with nothing in keep_cols (offline hours) are dropped.
    """
    out = {}
    for r in rows:
        if r is None or not has_values(r, keep_cols):
            continue
        r = dict(r)
        r["concentrations_source"] = conc_source(r, conc_cols)
        k = tuple(str(r[c]) for c in key_cols)
        out[k] = merge_rows(out[k], r, conc_cols) if k in out else r
    return [out[k] for k in sorted(out)]


FREQS = {
    "hourly": {"div": "1", "cols": HOURLY_COLS, "parse": parse_hourly,
               "key": ["station_code", "datetime"],
               "conc": POLLUTANTS + ["pm10_24h", "pm25_24h"],
               "values": POLLUTANTS + ["aqi"]},
    "daily": {"div": "2", "cols": DAILY_COLS, "parse": parse_daily,
              "key": ["station_code", "date"],
              "conc": POLLUTANTS, "values": POLLUTANTS},
}


def month_range(a, b):
    y, m = a
    while (y, m) <= b:
        yield y, m
        m += 1
        if m > 12:
            y, m = y + 1, 1


def ym(s):
    y, m = s.split("-")
    return int(y), int(m)


def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, cols, rows):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        # LF like the committed archive; csv's default CRLF would make every
        # re-fetched file look fully rewritten in git.
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, path)


def write_stations(path, catalog):
    rows = []
    for s in catalog["stations"]:
        rows.append({"station_code": s["code"], "name_mn": s.get("name_mn", ""),
                     "address_mn": s.get("address_mn", ""), "aimag_code": s.get("aimag_code") or "",
                     "aimag_mn": s.get("aimag_mn", ""), "aimag_en": s.get("aimag_en", ""),
                     "lat": s.get("lat", ""), "lon": s.get("lon", ""),
                     "mang_code": s.get("mang_code", ""),
                     "listed": 1 if s.get("listed", True) else 0})
    write_csv(path, STATION_COLS, rows)


def fetch_split(client, code, div, y, m, d0, d1, bad_days):
    """Fetch days d0..d1 of a month, halving the range around server errors.

    Some station-days make the server fail with an error page every time.
    Splitting isolates them; those single days are recorded in bad_days and
    skipped. Sub-month queries can miss validated rows, so this is a
    fallback, never the first try.
    """
    try:
        return client.history(code, div, f"{y}{m:02d}{d0:02d}00", f"{y}{m:02d}{d1:02d}23")
    except ServerError:
        if d0 == d1:
            bad_days.append(f"{y}-{m:02d}-{d0:02d}")
            return []
    mid = (d0 + d1) // 2
    return (fetch_split(client, code, div, y, m, d0, mid, bad_days)
            + fetch_split(client, code, div, y, m, mid + 1, d1, bad_days))


def fetch_month(client, freq, y, m, codes):
    """Fetch one month for each station. Returns only what the site sent now;
    the caller merges it into the archive (a failed station keeps its old rows)."""
    spec = FREQS[freq]
    last = calendar.monthrange(y, m)[1]
    f, t = f"{y}{m:02d}0100", f"{y}{m:02d}{last:02d}23"
    rows, failed, no_data, per_station = [], [], [], {}
    for i, code in enumerate(codes, 1):
        bad_days = []
        try:
            try:
                raw = client.history(code, spec["div"], f, t)
            except ServerError:
                log(f"  {freq} {y}-{m:02d} {code}: server error on full month; splitting")
                raw = fetch_split(client, code, spec["div"], y, m, 1, last, bad_days)
                log(f"  {freq} {y}-{m:02d} {code}: recovered {len(raw)} rows, "
                    f"unavailable days {bad_days}")
        except FetchError as e:
            log(f"  {freq} {y}-{m:02d} {code}: FAILED ({e}); keeping previous rows")
            failed.append(code)
            continue
        parsed = merge_all([spec["parse"](code, r) for r in raw],
                           spec["key"], spec["conc"], spec["values"])
        # The site can return neighbouring days at the edges; keep this month only.
        parsed = [r for r in parsed if r["date"].startswith(f"{y}-{m:02d}")]
        if not parsed:
            no_data.append(code)
        per_station[code] = {"rows": len(parsed),
                             "validated": sum(r["validated"] for r in parsed)}
        if bad_days:
            per_station[code]["unavailable_days"] = bad_days
        rows.extend(parsed)
        if i % 10 == 0:
            log(f"  {freq} {y}-{m:02d}: {i}/{len(codes)} stations, {len(rows)} rows")
    return rows, failed, no_data, per_station


def months_between(a, b):
    return (b[0] - a[0]) * 12 + (b[1] - a[1])


def is_complete(failed, partial, validated_rows, month, today):
    """A month is done when it is over, fully fetched, and either validated or
    too old to expect validation. Until then it is re-fetched on every run;
    merging means re-fetching never loses archived values."""
    now = (today.year, today.month)
    return (not failed and not partial and month < now
            and (validated_rows > 0 or months_between(month, now) >= VALIDATION_WAIT_MONTHS))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Download agaar.gov.mn station history")
    ap.add_argument("--output", required=True, help="output directory (e.g. tools/sources/agaar/raw)")
    ap.add_argument("--from", dest="from_", help="first month YYYY-MM (default 2025-02)")
    ap.add_argument("--to", help="last month YYYY-MM (default: current month)")
    ap.add_argument("--freq", default="both", choices=["both", "hourly", "daily"])
    ap.add_argument("--stations", help="comma-separated station codes (default: whole catalog)")
    ap.add_argument("--update", action="store_true",
                    help="routine archive run: the last --refresh-months months plus any "
                         "month not yet validated (up to 12 months back)")
    ap.add_argument("--refresh-months", type=int, default=3,
                    help="months always re-fetched to pick up validation (default 3)")
    ap.add_argument("--force", action="store_true", help="re-fetch months already complete")
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between requests (default 1.0)")
    args = ap.parse_args(argv)

    with open(CATALOG, encoding="utf-8") as fh:
        catalog = json.load(fh)
    codes = ([c.strip() for c in args.stations.split(",") if c.strip()] if args.stations
             else [s["code"] for s in catalog["stations"]])
    today = date.today()
    end = ym(args.to) if args.to else (today.year, today.month)
    months = list(month_range(ym(args.from_) if args.from_ else FIRST_MONTH, end))
    recent = set(months[-args.refresh_months:]) if args.refresh_months > 0 else set()
    freqs = ["hourly", "daily"] if args.freq == "both" else [args.freq]

    os.makedirs(args.output, exist_ok=True)
    manifest_path = os.path.join(args.output, "agaar-pulls.json")
    manifest = {}
    if os.path.exists(manifest_path):
        with open(manifest_path, encoding="utf-8") as fh:
            manifest = json.load(fh)

    def settled(freq, month):
        entry = manifest.get(freq, {}).get(f"{month[0]}-{month[1]:02d}")
        # Re-check from the stored counts, so manifests written by older
        # versions (complete without validation) are picked up again.
        return bool(entry) and is_complete(entry.get("stations_failed"), False,
                                           entry.get("validated_rows", 0), month, today)

    if args.update:  # recent months + anything still waiting for validation
        months = [mo for mo in months
                  if mo in recent or not all(settled(fq, mo) for fq in freqs)]
    write_stations(os.path.join(args.output, "agaar-stations.csv"), catalog)

    client = AgaarClient(delay=args.delay)
    exit_code = 0
    try:
        for freq in freqs:
            os.makedirs(os.path.join(args.output, freq), exist_ok=True)
            for y, m in months:
                label = f"{y}-{m:02d}"
                entry = manifest.get(freq, {}).get(label)
                partial = args.stations is not None
                if (settled(freq, (y, m)) and (y, m) not in recent
                        and not args.force and not partial):
                    log(f"{freq} {label}: complete, skipping (use --force to re-fetch)")
                    continue
                spec = FREQS[freq]
                path = os.path.join(args.output, freq, f"agaar-{freq}-{label}.csv")
                old = read_csv(path)
                log(f"{freq} {label}: fetching {len(codes)} stations")
                new, failed, no_data, per_station = fetch_month(client, freq, y, m, codes)
                # Archive first, fresh fetch second: the merge keeps every key and
                # never replaces a stored concentration with a blank.
                rows = merge_all(old + new, spec["key"], spec["conc"], spec["values"])
                write_csv(path, spec["cols"], rows)
                prev_stations = (entry or {}).get("stations", {}) if partial else {}
                validated_rows = sum(as_int(r["validated"]) for r in rows)
                manifest.setdefault(freq, {})[label] = {
                    "rows": len(rows),
                    "validated_rows": validated_rows,
                    # validated hourly rows carry AQI only; archived values survive (see SKILL.md)
                    "rows_with_concentrations": sum(has_values(r, spec["conc"]) for r in rows),
                    "stations_with_data": len({r["station_code"] for r in rows}),
                    "stations_empty": no_data,
                    "stations_failed": failed,
                    "stations": prev_stations | per_station,
                    "complete": is_complete(failed, partial, validated_rows, (y, m), today),
                    "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                }
                with open(manifest_path, "w", encoding="utf-8") as fh:
                    json.dump(manifest, fh, ensure_ascii=False, indent=1, sort_keys=True)
                log(f"{freq} {label}: {len(rows)} rows "
                    f"({validated_rows} validated), "
                    f"{len(no_data)} with no data, {len(failed)} failed -> {path}")
                if failed:
                    exit_code = 1
    except KeyboardInterrupt:
        log("interrupted; finished months are saved, re-run to continue")
        return 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
