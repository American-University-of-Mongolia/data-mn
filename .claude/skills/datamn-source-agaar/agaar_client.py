"""Shared HTTP client for agaar.gov.mn (NAMEM air quality portal).

The site has no published API. Its pages call form-encoded POST endpoints
that return JSON. The history endpoint (/web/pollution/getRealChart) needs a
per-session `key` scraped from the realSearch page AND the session cookie it
was issued with; without both it returns `{}`. This module keeps one cookie
jar per client and re-issues the key once if a response comes back empty.

Stdlib only.
"""
import html
import http.cookiejar
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://agaar.gov.mn"
SEARCH_PAGE = "/web/realSearch?pMENU_SN=97"
UA = "datamn-agaar/1.0 (+https://data.mn)"

# Pollutant item codes used throughout the site.
ITEMS = {
    "10007": {"key": "pm10", "name": "PM10", "unit": "µg/m³"},
    "10008": {"key": "pm25", "name": "PM2.5", "unit": "µg/m³"},
    "10003": {"key": "o3", "name": "O3", "unit": "µg/m³"},
    "10006": {"key": "no2", "name": "NO2", "unit": "µg/m³"},
    "10002": {"key": "co", "name": "CO", "unit": "mg/m³"},
    "10001": {"key": "so2", "name": "SO2", "unit": "µg/m³"},
}
ITEM_BY_KEY = {v["key"]: k for k, v in ITEMS.items()}

KEY_RE = re.compile(r"var key = '([0-9a-f-]{36})'")
STATION_RE = re.compile(r'name="stationCode"\s+value="([^"]+)"')
AIMAG_SELECT_RE = re.compile(r'<select[^>]*name="districtnum"[^>]*>(.*?)</select>', re.S)
OPTION_RE = re.compile(r'<option[^>]*value="(\d+)"[^>]*>([^<]+)</option>')


def log(msg):
    print(msg, file=sys.stderr, flush=True)


class FetchError(Exception):
    pass


class ServerError(FetchError):
    """The server answered with its HTML error page instead of JSON.

    Deterministic for some station-day combinations (an SQL error in the
    site's PM2.5-visibility subquery), so retrying the same range is useless;
    callers split the range instead.
    """


class AgaarClient:
    def __init__(self, delay=1.0, timeout=180, tries=4):
        self.delay = delay
        self.timeout = timeout
        self.tries = tries
        self.key = None
        self.search_html = None
        self._last = 0.0
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    # ---- low level ----
    def _throttle(self):
        nap = self.delay - (time.time() - self._last)
        if nap > 0:
            time.sleep(nap)
        self._last = time.time()

    def _request(self, path, data=None):
        url = BASE + path
        body = urllib.parse.urlencode(data).encode() if data is not None else None
        wait = 5
        for attempt in range(1, self.tries + 1):
            self._throttle()
            req = urllib.request.Request(url, data=body, headers={
                "User-Agent": UA,
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
            })
            try:
                with self.opener.open(req, timeout=self.timeout) as r:
                    return r.read().decode("utf-8", "replace")
            except urllib.error.HTTPError as e:
                if attempt < self.tries and (e.code == 429 or e.code >= 500):
                    log(f"  HTTP {e.code} on {path}; retry in {wait}s ({attempt}/{self.tries})")
                    time.sleep(wait)
                    wait *= 2
                    continue
                raise FetchError(f"HTTP {e.code} on {path}")
            except (TimeoutError, ConnectionError, OSError) as e:
                if attempt < self.tries:
                    log(f"  network error {e}; retry in {wait}s ({attempt}/{self.tries})")
                    time.sleep(wait)
                    wait *= 2
                    continue
                raise FetchError(f"network error on {path}: {e}")
        raise FetchError("unreachable")

    def post_json(self, path, data):
        text = self._request(path, data)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            raise ServerError(f"error page instead of JSON from {path} ({len(text)} bytes)")

    # ---- session key ----
    def refresh_key(self):
        self.search_html = self._request(SEARCH_PAGE)
        m = KEY_RE.search(self.search_html)
        if not m:
            raise FetchError("session key not found on realSearch page (site changed?)")
        self.key = m.group(1)
        return self.key

    # ---- endpoints ----
    def history(self, station_code, date_div, from_ymdh, to_ymdh):
        """Rows from /web/pollution/getRealChart.

        date_div: "1" hourly, "2" daily means. from/to: YYYYMMDDHH strings.
        An empty `{}` reply means the session key was rejected; the key is
        re-issued once before giving up. `{"charts": []}` is a real "no data".
        """
        for attempt in (1, 2):
            if self.key is None:
                self.refresh_key()
            d = self.post_json("/web/pollution/getRealChart", {
                "dateDiv": date_div, "stationCode": station_code,
                "from_date": from_ymdh, "to_date": to_ymdh,
                "key": self.key, "token": ""})
            if "charts" in d:
                return d["charts"] or []
            log("  empty reply (session key rejected); re-issuing key")
            self.key = None
        raise FetchError(f"key rejected twice for station {station_code}")

    def latest_by_station(self, item_code):
        return self.post_json("/web/mRealAirInfoAjax", {"itemCode": item_code}).get("list") or []

    def last_24h(self, station_code, item_code="10008"):
        d = self.post_json("/web/vicinityStationTimeAjax",
                           {"item_code": item_code, "station_code": station_code})
        return d.get("vicinityStationChart2") or []

    # ---- catalog scraping ----
    def scrape_catalog(self):
        """Stations listed on the search page plus aimag code names."""
        if self.search_html is None:
            self.refresh_key()
        h = self.search_html
        stations = []
        for raw in STATION_RE.findall(h):
            parts = html.unescape(raw).split("_", 2)
            if len(parts) < 2 or not parts[0].isdigit():
                continue
            stations.append({"code": parts[0], "name_mn": parts[1].strip(),
                             "address_mn": (parts[2] if len(parts) > 2 else "").strip()})
        aimags = {}
        m = AIMAG_SELECT_RE.search(h)
        if m:
            for code, name in OPTION_RE.findall(m.group(1)):
                aimags[code] = html.unescape(name).strip()
        return stations, aimags
