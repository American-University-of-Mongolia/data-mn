#!/usr/bin/env python3
"""Browse the agaar.gov.mn station catalog and live readings.

Usage:
    python3 query_api.py --list                 # all stations (from stations.json)
    python3 query_api.py --list --aimag 11      # one aimag (11 = Ulaanbaatar)
    python3 query_api.py хороолол               # search name/address/code/aimag
    python3 query_api.py --station 12401        # describe + last 24 hours (live)
    python3 query_api.py --latest pm25          # latest hour, every station (live)
    python3 query_api.py --refresh              # re-scrape catalog -> stations.json
    python3 query_api.py --earliest 12401       # first month with history (live)

Append --json for machine-readable output. Stdlib only.
"""
import argparse
import json
import os
import sys
from datetime import date, datetime, timezone

from agaar_client import ITEMS, ITEM_BY_KEY, AgaarClient, FetchError, log

HERE = os.path.dirname(os.path.abspath(__file__))
CATALOG = os.path.join(HERE, "stations.json")

# Aimag names as the site spells them -> English. Codes come from the site.
AIMAG_EN = {
    "Улаанбаатар": "Ulaanbaatar", "Архангай": "Arkhangai", "Дархан-Уул": "Darkhan-Uul",
    "Хэнтий": "Khentii", "Хөвсгөл": "Khuvsgul", "Орхон": "Orkhon", "Увс": "Uvs",
    "Завхан": "Zavkhan", "Баянхонгор": "Bayankhongor", "Баян-Өлгий": "Bayan-Ulgii",
    "Булган": "Bulgan", "Говьсүмбэр": "Govisumber", "Дорнод": "Dornod",
    "Дорноговь": "Dornogovi", "Дундговь": "Dundgovi", "Говь-Алтай": "Govi-Altai",
    "Ховд": "Khovd", "Өмнөговь": "Umnugovi", "Сэлэнгэ": "Selenge",
    "Сүхбаатар": "Sukhbaatar", "Төв": "Tuv", "Өвөрхангай": "Uvurkhangai",
}


def load_catalog():
    if not os.path.exists(CATALOG):
        log("stations.json missing; run: python3 query_api.py --refresh")
        sys.exit(1)
    with open(CATALOG, encoding="utf-8") as f:
        return json.load(f)


def refresh(client):
    """Rebuild stations.json: search-page list + coordinates from live data."""
    stations, aimags = client.scrape_catalog()
    by_code = {s["code"]: s for s in stations}
    for item in ITEMS:
        for r in client.latest_by_station(item):
            code = str(r.get("STATION_CODE"))
            s = by_code.setdefault(code, {"code": code, "name_mn": r.get("STATION_NAME") or "",
                                          "address_mn": "", "search_page": False})
            s.setdefault("items_live", [])
            if r.get("VALUE") not in (None, "", "-") and ITEMS[item]["key"] not in s["items_live"]:
                s["items_live"].append(ITEMS[item]["key"])
            for src, dst in (("DM_Y", "lat"), ("DM_X", "lon")):
                if r.get(src) is not None and s.get(dst) is None:
                    s[dst] = round(float(r[src]), 6)
            if r.get("DISTRICT_NUM"):
                s["aimag_code"] = str(r["DISTRICT_NUM"])
            if r.get("MANG_CODE"):
                s["mang_code"] = str(r["MANG_CODE"])
    old = {}
    if os.path.exists(CATALOG):
        old = {s["code"]: s for s in json.load(open(CATALOG, encoding="utf-8"))["stations"]}
    out = []
    for code in sorted(by_code):
        s = by_code[code]
        s.setdefault("search_page", True)
        s.setdefault("items_live", [])
        s["items_live"] = sorted(s["items_live"], key=lambda k: list(ITEM_BY_KEY).index(k))
        ac = s.get("aimag_code") or ("11" if code.startswith("12") else None)
        s["aimag_code"] = ac
        s["aimag_mn"] = aimags.get(ac, "")
        s["aimag_en"] = AIMAG_EN.get(s["aimag_mn"], "")
        # keep fields a human added (name_en, notes) across refreshes
        for k in ("name_en", "notes", "first_month"):
            if k in old.get(code, {}):
                s[k] = old[code][k]
        out.append(s)
    added = sorted(set(by_code) - set(old)) if old else []
    gone = sorted(set(old) - set(by_code)) if old else []
    if added:
        log(f"new stations: {added}")
    if gone:
        log(f"stations no longer listed (kept out of catalog; history may remain): {gone}")
        for code in gone:
            s = dict(old[code])
            s["listed"] = False
            out.append(s)
    cat = {"refreshed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "aimags": {c: {"mn": n, "en": AIMAG_EN.get(n, "")} for c, n in aimags.items()},
           "items": ITEMS, "stations": sorted(out, key=lambda s: s["code"])}
    with open(CATALOG, "w", encoding="utf-8") as f:
        json.dump(cat, f, ensure_ascii=False, indent=1)
    log(f"wrote {len(out)} stations -> {CATALOG}")
    return cat


def earliest_month(client, code, start=(2015, 1)):
    """First month with any daily data, scanning forward by month."""
    y, m = start
    today = date.today()
    while (y, m) <= (today.year, today.month):
        rows = client.history(code, "2", f"{y}{m:02d}0100", f"{y}{m:02d}2823")
        if rows:
            return f"{y}-{m:02d}"
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return None


def fmt_station(s):
    loc = f"{s['lat']:.4f},{s['lon']:.4f}" if s.get("lat") is not None else "no coords"
    flag = "" if s.get("listed", True) else "  [unlisted]"
    return (f"{s['code']}  {s['name_mn']:<26} {s.get('aimag_en') or '?':<13} "
            f"{loc:<20} {','.join(s.get('items_live', []))}{flag}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="agaar.gov.mn station catalog")
    ap.add_argument("terms", nargs="*", help="search terms (MN/EN/code)")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--aimag", help="aimag code filter (11 = Ulaanbaatar)")
    ap.add_argument("--station", help="describe one station + live last 24h")
    ap.add_argument("--latest", metavar="ITEM", help="latest hour for all stations: pm25 pm10 o3 no2 co so2")
    ap.add_argument("--earliest", metavar="CODE", help="first month with history for a station")
    ap.add_argument("--refresh", action="store_true", help="re-scrape catalog into stations.json")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    client = AgaarClient(delay=0.5)
    try:
        if args.refresh:
            refresh(client)
            return 0
        if args.latest:
            item = ITEM_BY_KEY.get(args.latest.lower())
            if not item:
                log(f"unknown item {args.latest}; use one of {sorted(ITEM_BY_KEY)}")
                return 1
            rows = client.latest_by_station(item)
            if args.json:
                print(json.dumps(rows, ensure_ascii=False, indent=1))
            else:
                for r in rows:
                    print(f"{r['DATA_TIME']}:00  {r['STATION_CODE']}  {r['STATION_NAME']:<26} "
                          f"{args.latest}={r['VALUE']}  grade={r['GRADE']}")
            return 0
        if args.earliest:
            print(earliest_month(client, args.earliest))
            return 0
    except FetchError as e:
        log(f"error: {e}")
        return 1

    cat = load_catalog()
    stations = cat["stations"]
    if args.station:
        s = next((s for s in stations if s["code"] == args.station), None)
        if not s:
            log(f"unknown station {args.station}")
            return 1
        try:
            rows = client.last_24h(args.station)
        except FetchError as e:
            log(f"live fetch failed: {e}")
            rows = []
        if args.json:
            print(json.dumps({"station": s, "last_24h": rows}, ensure_ascii=False, indent=1))
            return 0
        print(json.dumps(s, ensure_ascii=False, indent=1))
        print("\nlast 24h (hour-ending, local time):")
        print("time            " + "  ".join(f"{ITEMS[i]['key']:>5}" for i in ITEMS))
        for r in rows:
            vals = "  ".join(f"{(r.get('VALUE_' + i) or '-'):>5}" for i in ITEMS)
            print(f"{r.get('DATA_TIME2', ''):<16}{vals}")
        return 0

    if args.aimag:
        stations = [s for s in stations if s.get("aimag_code") == args.aimag]
    if args.terms:
        terms = [t.lower() for t in args.terms]
        def hay(s):
            return " ".join(str(s.get(k, "")) for k in
                            ("code", "name_mn", "name_en", "address_mn", "aimag_mn", "aimag_en")).lower()
        stations = [s for s in stations if all(t in hay(s) for t in terms)]
    elif not args.list and not args.aimag:
        ap.print_help()
        return 0
    if args.json:
        print(json.dumps(stations, ensure_ascii=False, indent=1))
    else:
        for s in stations:
            print(fmt_station(s))
        print(f"\n{len(stations)} stations (catalog refreshed {cat['refreshed_at']})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
