#!/usr/bin/env python3
"""
Screenshot data.mn charts as they render on the real site, at desktop and
phone widths, for visual QA.

`vl2png` renders a spec at a fixed size, so it cannot show problems that
only appear inside the site: VegaChart's responsive height, legend layout,
category-label wrapping and explorer controls. This script loads the actual
page in headless Chromium and captures each chart container.

Usage (start `npm run dev` in data.mn first):
    python3 tools/scripts/screenshot_charts.py registered-vehicles-by-age salary-by-sector-2024
    python3 tools/scripts/screenshot_charts.py --lang en --base https://data.mn gdp-growth-rate

Arguments are dataset slugs (the /{lang}/data/{slug} page). The chart whose
spec is /charts/{slug}-{lang}.json is captured, falling back to the first
chart on the page. Output: {out}/{slug}-{lang}-{desk|mob}.png
"""

import argparse
import glob
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

VIEWPORTS = [(1280, "desk"), (390, "mob")]


def launch(p):
    try:
        return p.chromium.launch()
    except Exception:
        # The pip package may expect a newer browser build than is cached;
        # any cached Chromium is fine for screenshots.
        cached = sorted(glob.glob(os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome")))
        if not cached:
            raise
        return p.chromium.launch(executable_path=cached[-1])


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("slugs", nargs="+")
    parser.add_argument("--base", default="http://localhost:4321", help="site origin (default: astro dev)")
    parser.add_argument("--lang", default="mn", choices=["mn", "en"])
    parser.add_argument("--out", default="/tmp/datamn-chart-shots")
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    failed = False
    with sync_playwright() as p:
        browser = launch(p)
        for width, tag in VIEWPORTS:
            page = browser.new_page(viewport={"width": width, "height": 900})
            page.on("console", lambda m: m.type == "error" and print(f"  console error: {m.text}"))
            for slug in args.slugs:
                page.goto(f"{args.base}/{args.lang}/data/{slug}", wait_until="networkidle", timeout=120000)
                selector = f'.vega-chart-container:has([data-spec$="/{slug}-{args.lang}.json"])'
                container = page.query_selector(selector) or page.query_selector(".vega-chart-container")
                if not container:
                    print(f"✗ {slug} ({tag}): no chart on page")
                    failed = True
                    continue
                container.scroll_into_view_if_needed()
                try:
                    container.wait_for_selector(".vega-chart[data-rendered=true] svg", timeout=30000)
                except Exception:
                    print(f"✗ {slug} ({tag}): chart did not render")
                    failed = True
                page.wait_for_timeout(800)
                path = out / f"{slug}-{args.lang}-{tag}.png"
                container.screenshot(path=str(path))
                print(f"✓ {path}")
        browser.close()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
