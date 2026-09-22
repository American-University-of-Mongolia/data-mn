#!/usr/bin/env python3
"""Validate MapChart Leaflet wiring (regression test for the swap bug).

Bug: loadLeaflet() injected the Leaflet CSS <link> at runtime but returned
early when window.L already existed. Astro ClientRouter swaps drop
runtime-injected head elements, so after navigating between map pages the
JS (heap-persisted window.L) kept working while the CSS was gone:
polygons rendered but all CSS-positioned UI (zoom controls, legend,
Reset) collapsed unstyled below the map.

Contract asserted here:
1. Leaflet is vendored locally (no CDN dependency at runtime).
2. MapChart.astro emits a STATIC stylesheet <link> in its SSR HTML, so the
   stylesheet ships with every swapped page body.
3. loadLeaflet() ensures the CSS link BEFORE the window.L early-return
   (fallback if head diffing ever drops the static link).
4. No Leaflet CDN references remain in MapChart.astro.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMPONENT = ROOT / "data.mn/src/components/ui/MapChart.astro"
VENDOR = ROOT / "data.mn/public/vendor/leaflet"

CHECKS = []


def check(name):
    def wrap(fn):
        CHECKS.append((name, fn))
        return fn

    return wrap


@check("Leaflet vendored locally")
def check_vendored():
    js = VENDOR / "leaflet.js"
    css = VENDOR / "leaflet.css"
    want = ["layers.png", "layers-2x.png", "marker-icon.png", "marker-icon-2x.png"]
    missing = [p.name for p in [js, css] if not p.is_file()]
    missing += [n for n in want if not (VENDOR / "images" / n).is_file()]
    if missing:
        return False, "missing: " + ", ".join(missing)
    if js.stat().st_size < 100_000 or css.stat().st_size < 10_000:
        return False, "vendored files suspiciously small"
    return True, f"leaflet.js + leaflet.css + {len(want)} images"


@check("Static stylesheet link in component HTML")
def check_static_link():
    src = COMPONENT.read_text(encoding="utf-8")
    template = src.split("<script", 1)[0]
    if "<link" not in template or "data-leaflet-css" not in template:
        return False, "no static <link data-leaflet-css> outside <script>"
    if "/vendor/leaflet/leaflet.css" not in template:
        return False, "static link does not point at /vendor/leaflet/leaflet.css"
    return True, "SSR <link> survives Astro swaps"


@check("CSS ensured before window.L early-return")
def check_css_first():
    src = COMPONENT.read_text(encoding="utf-8")
    css_pos = src.find("link[data-leaflet-css]")
    l_pos = src.find("if (window.L)")
    if css_pos == -1:
        return False, "no CSS link check in loadLeaflet"
    if l_pos == -1:
        return False, "no window.L guard in loadLeaflet"
    if css_pos > l_pos:
        return False, "window.L early-return runs before CSS check (swap bug)"
    return True, "CSS check precedes early-return"


@check("No Leaflet CDN references")
def check_no_cdn():
    src = COMPONENT.read_text(encoding="utf-8").lower()
    for cdn in ("cdn.jsdelivr.net", "unpkg.com", "cdnjs.cloudflare.com"):
        if cdn in src and "leaflet" in src:
            return False, f"found {cdn} reference"
    return True, "fully self-hosted"


def main():
    failed = 0
    for name, fn in CHECKS:
        try:
            ok, detail = fn()
        except Exception as exc:  # noqa: BLE001 - report as failure
            ok, detail = False, f"{type(exc).__name__}: {exc}"
        print(("PASS " if ok else "FAIL ") + name + f" ({detail})")
        failed += not ok
    print(f"\n{len(CHECKS) - failed}/{len(CHECKS)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
