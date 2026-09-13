#!/usr/bin/env python3
"""Browse the ebarilga.ub.gov.mn geoportal layer catalog.

Usage:
    python3 query_api.py [search terms]      search layers by keyword (EN/MN/code)
    python3 query_api.py --list              list all layers
    python3 query_api.py --list --group poi  list one group
    python3 query_api.py --groups             list layer groups
    python3 query_api.py --layer CODE         describe one layer (live count)
    python3 query_api.py --refresh            re-scrape /map and recount all layers
    python3 query_api.py --json ...           machine-readable output

Stdlib only. Cached catalog lives in layers.json next to this script.
"""
import argparse
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date

HERE = __file__.rsplit("/", 1)[0] or "."
CATALOG = f"{HERE}/layers.json"
MAP_URL = "https://ebarilga.ub.gov.mn/map"
WFS_URL = "https://ebarilga.ub.gov.mn/api/geoserver/wfs"

TAG_RE = re.compile(
    r'<div id="map-selecter-([^"]+)" class="map-selector"'
    r' data-iscache="([^"]*)" data-layertypecode="([^"]+)"'
    r' data-isexternal="([^"]*)" data-externalcode="([^"]*)"'
    r' data-externalurl="([^"]*)">.*?<div class="sub-selector-name">([^<]+)</div>',
    re.S,
)


def load_catalog():
    with open(CATALOG, encoding="utf-8") as f:
        return json.load(f)


def save_catalog(cat):
    with open(CATALOG, "w", encoding="utf-8") as f:
        json.dump(cat, f, ensure_ascii=False, indent=1)
        f.write("\n")


def http_get(url, params=None, timeout=60):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "datamn-ebarilga/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def live_count(code):
    """Return (count, geometry) from WFS, or (None, None) on failure."""
    try:
        raw = http_get(WFS_URL, {
            "service": "WFS", "version": "1.1.0", "request": "GetFeature",
            "typename": "urban:layer_data_map", "outputFormat": "application/json",
            "srsname": "EPSG:4326", "viewparams": f"layertypecode:{code}",
            "maxFeatures": "1",
        })
        d = json.loads(raw)
        feats = d.get("features") or []
        geom = feats[0].get("geometry", {}).get("type", "") if feats else ""
        return d.get("totalFeatures", d.get("numberMatched")), geom
    except Exception as e:
        print(f"warning: count failed for {code}: {e}", file=sys.stderr)
        return None, None


def cmd_list(cat, group=None, as_json=False):
    layers = cat["layers"]
    if group:
        layers = [l for l in layers if l["group"] == group]
        if not layers:
            print(f"unknown group: {group}", file=sys.stderr)
            return 1
    if as_json:
        print(json.dumps(layers, ensure_ascii=False, indent=1))
        return 0
    total = sum(l["count"] or 0 for l in layers)
    print(f"{len(layers)} layers, {total:,} features (counts as of {cat['count_date']})")
    for l in layers:
        n = f"{l['count']:,}" if l["count"] is not None else "?"
        print(f"  {n:>8}  {l['code']:<34} {l['name_en']}")
    return 0


def cmd_search(cat, terms, as_json=False):
    terms = [t.lower() for t in terms]
    hits = [l for l in cat["layers"]
            if all(t in f"{l['code']} {l['name_en']} {l['name_mn']} {l['group']}".lower()
                   for t in terms)]
    if as_json:
        print(json.dumps(hits, ensure_ascii=False, indent=1))
        return 0
    if not hits:
        print("no matching layers")
        return 0
    for l in hits:
        n = f"{l['count']:,}" if l["count"] is not None else "?"
        print(f"{l['code']}  [{l['group']}]  {n} x {l['geometry'] or '?'}  attrs={l['attrs']}")
        print(f"    EN: {l['name_en']}")
        print(f"    MN: {l['name_mn']}")
        if l.get("notes"):
            print(f"    note: {l['notes']}")
    return 0


def cmd_layer(cat, code, as_json=False):
    known = {l["code"]: l for l in cat["layers"]}
    if code not in known:
        print(f"unknown layer code: {code} (see --list)", file=sys.stderr)
        return 1
    info = dict(known[code])
    if info["host"] == "ebarilga":
        count, geom = live_count(code)
        info["live_count"] = count
        if geom:
            info["live_geometry"] = geom
    else:
        info["live_count"] = "(external host; use fetch_data.py)"
    if as_json:
        print(json.dumps(info, ensure_ascii=False, indent=1))
        return 0
    print(f"code:     {info['code']}")
    print(f"EN:       {info['name_en']}")
    print(f"MN:       {info['name_mn']}")
    print(f"group:    {info['group']}   host: {info['host']}")
    print(f"catalog:  {info['count']} x {info['geometry']} ({cat['count_date']})")
    print(f"live:     {info['live_count']}" +
          (f" x {info['live_geometry']}" if info.get("live_geometry") else ""))
    print(f"attrs:    {info['attrs']}")
    if info.get("notes"):
        print(f"notes:    {info['notes']}")
    return 0


def cmd_refresh(cat):
    print("scraping layer list from /map ...")
    page = http_get(MAP_URL).decode("utf-8", "replace")
    found = {}
    for m in TAG_RE.finditer(page):
        _sel, iscache, code, isext, extcode, exturl, name = m.groups()
        if code in cat.get("ui_only_codes", []):
            continue
        found[code] = {
            "name_mn": html.unescape(name.strip()),
            "external": bool(isext),
        }
    print(f"found {len(found)} data layers on /map")
    known = {l["code"]: l for l in cat["layers"]}
    for code in sorted(set(known) - set(found)):
        print(f"  layer disappeared from map UI: {code} (kept in catalog)")
    for code in sorted(set(found) - set(known)):
        print(f"  new layer: {code} ({found[code]['name_mn']})")
        known[code] = {"code": code, "name_en": "", "group": "uncategorized",
                       "count": None, "geometry": "", "host": "ebarilga",
                       "attrs": "unprobed", "notes": "auto-added by --refresh"}
    for code, entry in known.items():
        if code in found:
            entry["name_mn"] = found[code]["name_mn"]
            if found[code]["external"]:
                entry["host"] = "transco"
        if entry["host"] != "ebarilga":
            print(f"  skip count (external): {code}")
            continue
        count, geom = live_count(code)
        if count is not None:
            if entry["count"] != count:
                print(f"  {code}: {entry['count']} -> {count}")
            entry["count"] = count
            entry["geometry"] = geom or entry["geometry"]
        time.sleep(0.4)  # be polite: ~80 requests
    cat["layers"] = [known[c] for c in
                     sorted(known, key=lambda c: (known[c]["group"], c))]
    cat["count_date"] = date.today().isoformat()
    save_catalog(cat)
    print(f"catalog saved ({len(cat['layers'])} layers)")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Browse the ebarilga geoportal catalog")
    ap.add_argument("terms", nargs="*", help="search keywords")
    ap.add_argument("--list", action="store_true", help="list all layers")
    ap.add_argument("--group", help="filter --list by group")
    ap.add_argument("--groups", action="store_true", help="list layer groups")
    ap.add_argument("--layer", help="describe one layer code (with live count)")
    ap.add_argument("--refresh", action="store_true", help="re-scrape /map, recount, save")
    ap.add_argument("--json", action="store_true", help="JSON output")
    args = ap.parse_args(argv)
    cat = load_catalog()
    if args.groups:
        groups = sorted({l["group"] for l in cat["layers"]})
        if args.json:
            print(json.dumps(groups, ensure_ascii=False))
        else:
            for g in groups:
                n = sum(1 for l in cat["layers"] if l["group"] == g)
                print(f"{g} ({n})")
        return 0
    if args.refresh:
        return cmd_refresh(cat)
    if args.layer:
        return cmd_layer(cat, args.layer, args.json)
    if args.list or not args.terms:
        return cmd_list(cat, args.group, args.json)
    return cmd_search(cat, args.terms, args.json)


if __name__ == "__main__":
    sys.exit(main())
