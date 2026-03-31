#!/usr/bin/env python3
"""
Download MRPAM monthly statistical report PDFs.

URLs are NOT predictable — this script scrapes each year's page to find
actual download links, then caches PDFs locally.

Usage:
    python3 fetch_report.py --year 2025 --list
    python3 fetch_report.py --year 2025
    python3 fetch_report.py --year 2025 --month 1
    python3 fetch_report.py --all-years
    python3 fetch_report.py --check-update --year 2025
"""

import argparse
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# ─── Constants ────────────────────────────────────────────────────────────────

BASE_URL = "https://mrpam.gov.mn"

# Each year's reports are on a separate page
YEAR_PAGE_IDS = {
    2021: 169,
    2022: 177,
    2023: 196,
    2024: 202,
    2025: 714,
    2026: 732,
}

# Cache directory (relative to repo root)
CACHE_DIR = Path(__file__).resolve().parents[4] / "tools" / "temp" / "mrpam-pdfs"

MONTH_NAMES_MN = {
    1: "1 сар", 2: "2 сар", 3: "3 сар", 4: "4 сар",
    5: "5 сар", 6: "6 сар", 7: "7 сар", 8: "8 сар",
    9: "9 сар", 10: "10 сар", 11: "11 сар", 12: "12 сар",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# ─── Helpers ──────────────────────────────────────────────────────────────────


def get_page(url: str) -> BeautifulSoup:
    """Fetch a page and return a BeautifulSoup object."""
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.content, "html.parser")


def scrape_report_links(year: int) -> list[dict]:
    """
    Scrape a year's page and return a list of report dicts:
      {month: int, url: str, filename: str, date_str: str}

    PDF filenames are NOT predictable — must scrape actual links.
    Pattern observed: {year}.{month}.stat.report.mon.pdf (but varies)
    """
    page_id = YEAR_PAGE_IDS.get(year)
    if not page_id:
        raise ValueError(f"No page ID configured for year {year}")

    page_url = f"{BASE_URL}/page/{page_id}"
    print(f"Scraping {page_url} ...")
    soup = get_page(page_url)

    reports = []

    # Find all <a> tags that link to PDFs
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not href.lower().endswith(".pdf"):
            continue

        full_url = href if href.startswith("http") else urljoin(BASE_URL, href)
        filename = full_url.split("/")[-1]

        # Try to extract month from filename or surrounding text
        month = _guess_month(filename, a, year)

        # Extract date string from nearby table cell
        date_str = _extract_date_near(a)

        reports.append({
            "month": month,
            "url": full_url,
            "filename": filename,
            "date_str": date_str,
        })

    # Sort by month (None last)
    reports.sort(key=lambda r: (r["month"] is None, r["month"] or 0))
    return reports


def _guess_month(filename: str, anchor, year: int) -> int | None:
    """Guess the report month from filename and surrounding HTML."""
    # Pattern: 2025.1.stat... or 2025.10.stat...
    m = re.search(rf"{year}\.(\d{{1,2}})\.", filename)
    if m:
        return int(m.group(1))

    # Try link text or parent row text
    text = anchor.get_text(" ", strip=True)
    parent = anchor.find_parent("tr")
    row_text = parent.get_text(" ", strip=True) if parent else ""
    combined = f"{text} {row_text}"

    # Mongolian month names
    mn_months = {
        "1 сар": 1, "нэгдүгээр сар": 1,
        "2 сар": 2, "хоёрдугаар сар": 2,
        "3 сар": 3, "гуравдугаар сар": 3,
        "4 сар": 4, "дөрөвдүгээр сар": 4,
        "5 сар": 5, "тавдугаар сар": 5,
        "6 сар": 6, "зургадугаар сар": 6,
        "7 сар": 7, "долдугаар сар": 7,
        "8 сар": 8, "наймдугаар сар": 8,
        "9 сар": 9, "есдүгээр сар": 9,
        "10 сар": 10, "аравдугаар сар": 10,
        "11 сар": 11, "арван нэгдүгээр сар": 11,
        "12 сар": 12, "арван хоёрдугаар сар": 12,
    }
    combined_lower = combined.lower()
    for name, num in mn_months.items():
        if name in combined_lower:
            return num

    # Try digit pattern like "2025-01" or "01/2025"
    m2 = re.search(r"(\d{1,2})[/\-]\d{4}|\d{4}[/\-](\d{1,2})", combined)
    if m2:
        val = int(m2.group(1) or m2.group(2))
        if 1 <= val <= 12:
            return val

    return None


def _extract_date_near(anchor) -> str:
    """Extract date string from the table row containing the link."""
    parent = anchor.find_parent("tr")
    if not parent:
        return ""
    cells = parent.find_all("td")
    for cell in cells:
        text = cell.get_text(strip=True)
        # Look for date patterns: 2025.01.15 or 2025-01-15
        if re.search(r"\d{4}[.\-]\d{1,2}[.\-]\d{1,2}", text):
            return text
    return ""


def cache_path(year: int, filename: str) -> Path:
    return CACHE_DIR / str(year) / filename


def download_pdf(url: str, dest: Path) -> Path:
    """Download a PDF to dest, skipping if already cached."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        print(f"  Cached: {dest.name}")
        return dest

    print(f"  Downloading {url} ...")
    resp = requests.get(url, headers=HEADERS, timeout=60, stream=True)
    resp.raise_for_status()

    with open(dest, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    size_kb = dest.stat().st_size // 1024
    print(f"  Saved: {dest.name} ({size_kb} KB)")
    time.sleep(0.5)  # be polite
    return dest


# ─── CLI ──────────────────────────────────────────────────────────────────────


def cmd_list(year: int):
    reports = scrape_report_links(year)
    if not reports:
        print(f"No PDF reports found for {year}.")
        return
    print(f"\n{'Month':<8} {'Filename':<45} {'Date':<15} URL")
    print("-" * 100)
    for r in reports:
        month = str(r["month"]) if r["month"] else "?"
        print(f"{month:<8} {r['filename']:<45} {r['date_str']:<15} {r['url']}")
    print(f"\nTotal: {len(reports)} reports")


def cmd_download(year: int, month: int | None = None):
    reports = scrape_report_links(year)
    if not reports:
        print(f"No PDF reports found for {year}.")
        return

    if month is not None:
        reports = [r for r in reports if r["month"] == month]
        if not reports:
            print(f"No report found for {year}/{month}.")
            return

    print(f"\nDownloading {len(reports)} report(s) for {year} ...")
    downloaded = []
    for r in reports:
        dest = cache_path(year, r["filename"])
        path = download_pdf(r["url"], dest)
        downloaded.append(path)

    print(f"\nDone. {len(downloaded)} file(s) saved to {CACHE_DIR}/{year}/")
    return downloaded


def cmd_check_update(year: int):
    """Check what's the latest report available for a year."""
    reports = scrape_report_links(year)
    if not reports:
        print(f"UPDATE_STATUS: no_reports_found year={year}")
        return

    known_months = [r["month"] for r in reports if r["month"]]
    latest = max(known_months) if known_months else None
    print(f"UPDATE_STATUS: latest_month={latest} year={year} total={len(reports)}")

    # Check which months are already cached
    cached = []
    for r in reports:
        dest = cache_path(year, r["filename"])
        if dest.exists():
            cached.append(r["month"])

    missing = [m for m in known_months if m not in cached]
    if missing:
        print(f"NOT_CACHED: months={sorted(missing)}")
    else:
        print("ALL_CACHED: all available reports are downloaded")


def main():
    parser = argparse.ArgumentParser(description="Download MRPAM monthly report PDFs")
    parser.add_argument("--year", type=int, help="Year to fetch (e.g. 2025)")
    parser.add_argument("--month", type=int, help="Specific month (1-12)")
    parser.add_argument("--all-years", action="store_true", help="Download all years")
    parser.add_argument("--list", action="store_true", help="List available reports (no download)")
    parser.add_argument("--check-update", action="store_true", help="Check for new reports")
    parser.add_argument(
        "--cache-dir", type=Path, default=CACHE_DIR,
        help=f"PDF cache directory (default: {CACHE_DIR})"
    )
    args = parser.parse_args()

    if args.cache_dir != CACHE_DIR:
        globals()["CACHE_DIR"] = args.cache_dir

    if args.all_years:
        for yr in sorted(YEAR_PAGE_IDS.keys()):
            print(f"\n{'='*50}")
            print(f"Year: {yr}")
            print(f"{'='*50}")
            cmd_download(yr)
        return

    if not args.year:
        parser.error("--year is required (unless using --all-years)")

    if args.check_update:
        cmd_check_update(args.year)
    elif args.list:
        cmd_list(args.year)
    else:
        cmd_download(args.year, args.month)


if __name__ == "__main__":
    main()
