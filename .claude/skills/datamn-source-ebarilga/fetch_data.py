#!/usr/bin/env python3
"""Download a full ebarilga.ub.gov.mn geoportal layer.

Usage:
    python3 fetch_data.py --layer data_edu_school --output ./output
    python3 fetch_data.py --layer plan_building --output ./output --with-attributes
    python3 fetch_data.py --layer built_building --output ./output --max 1000
    python3 fetch_data.py --layer pz_city_line --output ./output --insecure-tls
    python3 fetch_data.py --layer plan_building --output ./output --attrs-only

Outputs in --output:
    ebarilga-<code>.geojson   all geometries (EPSG:4326)
    ebarilga-<code>.csv       tabular rows: id, object_no, object_name,
                              geom_type, lon, lat + attribute columns
    ebarilga-<code>.meta.json fetch metadata
    ebarilga-<code>.attrs.jsonl  attribute cache (with --with-attributes)

Paging uses keyset pagination (sortBy=id + CQL id>=cursor) because the
server ignores startIndex (returns HTTP 200 with an empty body).
Stdlib only.
"""
import argparse
import csv
import html
import json
import os
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

HOSTS = {
    "ebarilga": {"wfs": "https://ebarilga.ub.gov.mn/api/geoserver/wfs",
                 "typename": "urban:layer_data_map",
                 "attrs": "https://ebarilga.ub.gov.mn/api/layer/data/attribute",
                 "tls_ok": True},
    "transco": {"wfs": "https://grid.transco.mn/api/geoserver/wfs",
                "typename": "grid:layer_data_map_p",
                "attrs": None,  # no attribute API on the external host
                "tls_ok": False},
}
HERE = __file__.rsplit("/", 1)[0] or "."
ATTR_ROW_RE = re.compile(r"<td[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>", re.S)
TAG_RE = re.compile(r"<[^>]+>")
BASE_COLS = ["id", "object_no", "object_name", "geom_type", "lon", "lat"]


def log(msg):
    print(msg, file=sys.stderr, flush=True)


def clean(s):
    return html.unescape(TAG_RE.sub("", s)).strip()


class FetchError(Exception):
    pass


def http_bytes(url, params=None, timeout=180, ctx=None, tries=5, hard_tries=1):
    """GET with retries. Returns (body, status). Raises FetchError.

    429s and network errors get full `tries` (transient). HTTP 5xx and empty
    bodies get `hard_tries` only: on this proxy they are always deterministic
    (poison feature or oversize page; verified across ~400k requests), and the
    caller splits the page instead of retrying the same doomed request.
    """
    if params:
        url += "?" + urllib.parse.urlencode(params)
    wait = 5
    for attempt in range(1, tries + 1):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "datamn-ebarilga/1.0"})
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                body = r.read()
                if not body:
                    raise FetchError("empty body (HTTP 200)")
                return body, r.status
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < tries:
                retry_after = e.headers.get("Retry-After")
                nap = int(retry_after) if retry_after and retry_after.isdigit() else wait
                log(f"  429 rate-limited; sleeping {nap}s (try {attempt}/{tries})")
                time.sleep(nap)
                wait *= 2
            elif 500 <= e.code < 600 and attempt < hard_tries:
                log(f"  HTTP {e.code}; retry in {wait}s (try {attempt}/{hard_tries})")
                time.sleep(wait)
                wait *= 2
            elif 500 <= e.code < 600:
                raise FetchError(f"HTTP {e.code} (persistent)")
            else:
                raise FetchError(f"HTTP {e.code}: {e.reason}")
        except (TimeoutError, ConnectionError, OSError) as e:
            if attempt < tries:
                log(f"  network error {e}; retry in {wait}s (try {attempt}/{tries})")
                time.sleep(wait)
                wait *= 2
            else:
                raise FetchError(f"network error: {e}")
        except FetchError:
            if attempt < hard_tries:
                log(f"  empty body; retry in {wait}s (try {attempt}/{hard_tries})")
                time.sleep(wait)
                wait *= 2
            else:
                raise
    raise FetchError("unreachable")


def wfs_page(host, code, max_features, cursor=None, timeout=180, ctx=None,
             property_name=None):
    params = {"service": "WFS", "version": "1.1.0", "request": "GetFeature",
              "typename": HOSTS[host]["typename"],
              "outputFormat": "application/json", "srsname": "EPSG:4326",
              "viewparams": f"layertypecode:{code}",
              "maxFeatures": str(max_features), "sortBy": "id"}
    if cursor is not None:
        params["CQL_FILTER"] = f"id>={cursor}"
    if property_name:
        params["propertyName"] = property_name
    body, _ = http_bytes(HOSTS[host]["wfs"], params, timeout=timeout, ctx=ctx)
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        raise FetchError(f"invalid JSON ({len(body)} bytes)")


def probe_next_id(host, code, cursor, ctx=None):
    """Lowest feature id >= cursor via an id-only query (no geometry
    serialization, so it works on poison features). None if none left."""
    d = wfs_page(host, code, 1, cursor, timeout=60, ctx=ctx,
                 property_name="id")
    feats = d.get("features") or []
    return feats[0]["properties"]["id"] if feats else None


def fetch_attributes(layer_id, host, ctx=None):
    base = HOSTS[host]["attrs"]
    if base is None:
        return {}
    body, _ = http_bytes(f"{base}?layer_id={layer_id}", timeout=60, ctx=ctx)
    text = body.decode("utf-8", "replace")
    out = {}
    for k, v in ATTR_ROW_RE.findall(text):
        k, v = clean(k).rstrip(":").rstrip(), clean(v)
        if not k or not v:
            continue
        if k in out and out[k] != v:
            v = out[k] + " | " + v
        out[k] = v
    return out


def iter_coords(geom):
    """Yield (lon, lat) pairs from any GeoJSON geometry."""
    if not geom:
        return
    t, c = geom.get("type"), geom.get("coordinates")
    if c is None:
        return
    if t == "Point":
        yield tuple(c)
    elif t in ("MultiPoint", "LineString"):
        yield from (tuple(p) for p in c)
    elif t in ("MultiLineString", "Polygon"):
        for ring in c:
            yield from (tuple(p) for p in ring)
    elif t == "MultiPolygon":
        for poly in c:
            for ring in poly:
                yield from (tuple(p) for p in ring)


def lonlat(geom):
    """Point coords, else bbox center (rounded to ~1m)."""
    pts = list(iter_coords(geom))
    if not pts:
        return "", ""
    if geom.get("type") == "Point":
        return round(pts[0][0], 6), round(pts[0][1], 6)
    lons = [p[0] for p in pts]
    lats = [p[1] for p in pts]
    return round((min(lons) + max(lons)) / 2, 6), round((min(lats) + max(lats)) / 2, 6)


def load_catalog():
    with open(f"{HERE}/layers.json", encoding="utf-8") as f:
        return json.load(f)


def backfill_attributes(args, stem, csv_path, meta_path, cache_path, host, ctx):
    """Fetch attributes for rows of an existing CSV (no WFS calls)."""
    if not os.path.exists(csv_path):
        log(f"no CSV to backfill: {csv_path} (fetch geometries first)")
        return 1
    with open(csv_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    cache = {}
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    e = json.loads(line)
                    cache[e["id"]] = e["attrs"]
    log(f"backfill: {len(rows)} rows, {len(cache)} cached attrs")
    cache_file = open(cache_path, "a", encoding="utf-8")
    gap = 1.0 / args.attr_rate if args.attr_rate > 0 else 0
    done, t0 = 0, time.time()
    try:
        for i, row in enumerate(rows):
            fid = int(row["id"])
            if fid not in cache:
                if args.max and done >= args.max:
                    break
                t_req = time.time()
                try:
                    cache[fid] = fetch_attributes(fid, host, ctx)
                except FetchError as e:
                    log(f"attrs failed for id {fid}: {e} (saved empty)")
                    cache[fid] = {}
                cache_file.write(json.dumps(
                    {"id": fid, "attrs": cache[fid]}, ensure_ascii=False) + "\n")
                done += 1
                nap = gap - (time.time() - t_req)
                if nap > 0:
                    time.sleep(nap)
            for k, v in cache[fid].items():
                row["attr_" + k if k in BASE_COLS else k] = v
            if (i + 1) % 500 == 0:
                log(f"  {i+1}/{len(rows)} rows ({done} fetched, {time.time()-t0:.0f}s)")
    except KeyboardInterrupt:
        log("interrupted; saving partial backfill")
    cache_file.close()
    cols = list(BASE_COLS)
    for r in rows:
        for k in r:
            if k not in cols:
                cols.append(k)
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    meta = {"layer": args.layer, "host": host,
            "features": len(rows), "with_attributes": True,
            "complete": True, "srs": "EPSG:4326", "attrs_backfilled": True,
            "fetched_at": datetime.now(timezone.utc).isoformat()}
    if os.path.exists(meta_path):
        try:
            old = json.load(open(meta_path, encoding="utf-8"))
            meta["fetched_at"] = old.get("fetched_at", meta["fetched_at"])
        except (json.JSONDecodeError, OSError):
            pass
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    log(f"done: {len(rows)} rows backfilled ({done} fetched) ({time.time()-t0:.0f}s)")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Download a full ebarilga layer")
    ap.add_argument("--layer", required=True, help="layer code (see query_api.py --list)")
    ap.add_argument("--output", required=True, help="output directory")
    ap.add_argument("--with-attributes", action="store_true",
                    help="enrich each feature via the attribute API (slow, rate-limited)")
    ap.add_argument("--attrs-only", action="store_true",
                    help="backfill attributes into an existing CSV (no WFS calls)")
    ap.add_argument("--page-size", type=int, default=2000,
                    help="features per WFS request (default 2000, max tested 10000)")
    ap.add_argument("--max", type=int, default=0, help="stop after N features (testing)")
    ap.add_argument("--format", default="both", choices=["both", "geojson", "csv"])
    ap.add_argument("--wfs-delay", type=float, default=0.3, help="seconds between WFS pages")
    ap.add_argument("--attr-rate", type=float, default=1.0,
                    help="attribute requests per second (default 1.0)")
    ap.add_argument("--resume", action="store_true",
                    help="continue from existing outputs (max id + attribute cache)")
    ap.add_argument("--insecure-tls", action="store_true",
                    help="disable TLS verification (REQUIRED for transco host; cert invalid)")
    args = ap.parse_args(argv)

    cat = {l["code"]: l for l in load_catalog()["layers"]}
    if args.layer not in cat:
        log(f"unknown layer: {args.layer} (see query_api.py --list)")
        return 1
    host = cat[args.layer]["host"]
    if not HOSTS[host]["tls_ok"] and not args.insecure_tls:
        log(f"layer {args.layer} lives on grid.transco.mn whose TLS cert is "
            f"invalid; re-run with --insecure-tls to proceed anyway")
        return 1
    if args.with_attributes and HOSTS[host]["attrs"] is None:
        log(f"no attribute API for host {host}; ignoring --with-attributes")
        args.with_attributes = False
    ctx = ssl._create_unverified_context() if args.insecure_tls else None

    os.makedirs(args.output, exist_ok=True)
    stem = f"{args.output}/ebarilga-{args.layer}"
    gj_path, csv_path = stem + ".geojson", stem + ".csv"
    meta_path, cache_path = stem + ".meta.json", stem + ".attrs.jsonl"

    if args.attrs_only:
        if HOSTS[host]["attrs"] is None:
            log(f"no attribute API for host {host}")
            return 1
        return backfill_attributes(args, stem, csv_path, meta_path,
                                   cache_path, host, ctx)

    # ---- resume state ----
    cursor, seen, rows, attr_cache = None, set(), [], {}
    gj_file, first_feature = None, True
    if args.resume and os.path.exists(gj_path):
        with open(gj_path, encoding="utf-8") as f:
            gj = json.load(f)
        for feat in gj.get("features", []):
            fid = feat["properties"]["id"]
            seen.add(fid)
        if seen:
            cursor = max(seen) + 1
        log(f"resume: {len(seen)} features already saved, cursor id>={cursor}")
    if args.resume and os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    e = json.loads(line)
                    attr_cache[e["id"]] = e["attrs"]
        log(f"resume: {len(attr_cache)} cached attributes")
    if args.resume and os.path.exists(csv_path):
        with open(csv_path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                rows.append(r)
                seen.add(int(r["id"]))
        if seen and cursor is None:
            cursor = max(seen) + 1

    def open_geojson():
        nonlocal gj_file, first_feature
        gj_file = open(gj_path, "w", encoding="utf-8")
        gj_file.write('{"type":"FeatureCollection","features":[')
        first_feature = True

    def write_feature(feat):
        nonlocal first_feature
        if not first_feature:
            gj_file.write(",")
        first_feature = False
        gj_file.write(json.dumps(feat, ensure_ascii=False))

    want_gj = args.format in ("both", "geojson")
    want_csv = args.format in ("both", "csv")
    if want_gj and not (args.resume and seen):
        open_geojson()
    # resume mode re-streams: reload existing features into the new file
    resumed_features = []
    if want_gj and args.resume and seen:
        with open(gj_path, encoding="utf-8") as f:
            resumed_features = json.load(f).get("features", [])
        open_geojson()
        for feat in resumed_features:
            write_feature(feat)

    cache_file = open(cache_path, "a", encoding="utf-8") if args.with_attributes else None
    attr_gap = 1.0 / args.attr_rate if args.attr_rate > 0 else 0
    fetched, t0 = len(seen), time.time()  # --max counts total in output, incl. resumed
    stopped_early = False
    page_size = args.page_size  # adaptive: halve on failure, double on success
    skipped = []

    try:
        while True:
            want = page_size
            if args.max:
                want = min(want, args.max - fetched)
                if want <= 0:
                    break
            try:
                d = wfs_page(host, args.layer, want, cursor, ctx=ctx)
            except FetchError as e:
                if want > 1:
                    # Oversize page or poison feature inside: halve and retry.
                    page_size = max(1, want // 2)
                    log(f"page failed ({e}); halving page size to {page_size}")
                    continue
                # Single-feature page failed: identify the poison id and skip it.
                try:
                    pid = probe_next_id(host, args.layer, cursor, ctx)
                except FetchError as e2:
                    log(f"cannot isolate poison feature: {e2}")
                    stopped_early = True
                    break
                if pid is None:
                    break  # cursor beyond last feature
                log(f"skipping unfetchable feature id={pid}")
                skipped.append(pid)
                cursor = pid + 1
                page_size = args.page_size  # poison is positional; restore size
                continue
            feats = d.get("features") or []
            if not feats:
                break
            if cursor is None:
                log(f"server reports {d.get('numberMatched')} features")
            ids = [f["properties"]["id"] for f in feats]
            new = [f for f in feats if f["properties"]["id"] not in seen]
            for f in new:
                p = f["properties"]
                if want_gj:
                    write_feature(f)
                if want_csv:
                    lon, lat = lonlat(f.get("geometry"))
                    row = {"id": p["id"], "object_no": p.get("object_no") or "",
                           "object_name": p.get("object_name") or "",
                           "geom_type": (f.get("geometry") or {}).get("type") or "",
                           "lon": lon, "lat": lat}
                    rows.append(row)
                seen.add(p["id"])
            fetched += len(new)
            # attributes for the new ids (cached or fetched)
            if args.with_attributes and want_csv:
                id2row = {r["id"]: r for r in rows[-len(new):]} if new else {}
                for f in new:
                    fid = f["properties"]["id"]
                    if fid not in attr_cache:
                        t_req = time.time()
                        try:
                            attr_cache[fid] = fetch_attributes(fid, host, ctx)
                        except FetchError as e:
                            log(f"attrs failed for id {fid}: {e} (saved empty)")
                            attr_cache[fid] = {}
                        cache_file.write(json.dumps(
                            {"id": fid, "attrs": attr_cache[fid]},
                            ensure_ascii=False) + "\n")
                        cache_file.flush()
                        nap = attr_gap - (time.time() - t_req)
                        if nap > 0:
                            time.sleep(nap)
                    for k, v in attr_cache[fid].items():
                        id2row[fid]["attr_" + k if k in BASE_COLS else k] = v
            log(f"  {fetched} features (ids {ids[0]}..{ids[-1]}, "
                f"pg={want}, {time.time()-t0:.0f}s elapsed)")
            if len(feats) < want or (args.max and fetched >= args.max):
                break
            page_size = min(args.page_size, page_size * 2)  # AIMD recovery
            cursor = ids[-1] + 1
            time.sleep(args.wfs_delay)
    except KeyboardInterrupt:
        log("interrupted; saving partial outputs")
        stopped_early = True

    if gj_file:
        gj_file.write("]}")
        gj_file.close()
    if cache_file:
        cache_file.close()
    if want_csv and rows:
        cols = list(BASE_COLS)
        for r in rows:
            for k in r:
                if k not in cols:
                    cols.append(k)
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
    skipped_ids = set(skipped)
    if args.resume and os.path.exists(meta_path):
        try:
            skipped_ids |= set(json.load(open(meta_path, encoding="utf-8"))
                               .get("skipped_ids", []))
        except (json.JSONDecodeError, OSError):
            pass
    meta = {"layer": args.layer, "host": host,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "features": len(seen), "with_attributes": args.with_attributes,
            "complete": not stopped_early and not args.max,
            "skipped_ids": sorted(skipped_ids),
            "srs": "EPSG:4326"}
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    log(f"done: {len(seen)} features"
        + (f" ({len(skipped_ids)} skipped: {sorted(skipped_ids)})"
           if skipped_ids else "")
        + f" -> {stem}.{{geojson,csv,meta.json}} ({time.time()-t0:.0f}s)")
    return 0 if not stopped_early else 1


if __name__ == "__main__":
    sys.exit(main())
