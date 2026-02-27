#!/usr/bin/env python3
"""
Fetch indicator data from Bank of Mongolia statistics bulletins and portal.

Supports two source types:
  1. Statistics portal page (HTML table) — preferred when available
  2. PDF bulletin — fallback for Mongolian-only sources

Output: Bilingual CSVs ready for data.mn ingestion.

Usage:
    python3 fetch_bulletin_table.py --indicator policy-rate --output ./output
    python3 fetch_bulletin_table.py --indicator money-supply-m2 --output ./output
    python3 fetch_bulletin_table.py --list-indicators
    python3 fetch_bulletin_table.py --indicator policy-rate --check-update --last-date 2024-12
"""

import argparse
import re
import sys
import time
from datetime import datetime, date
from pathlib import Path
from typing import Optional
from io import BytesIO

import pandas as pd
import requests
from bs4 import BeautifulSoup

# ─── Indicator Registry ───────────────────────────────────────────────────────
# Maps indicator slug → source config
# Add new indicators here as MongolBank datasets are added to data.mn

INDICATORS = {
    "policy-rate": {
        "title_en": "Bank of Mongolia Policy Rate",
        "title_mn": "Монголбанкны бодлогын хүү",
        "source_type": "portal",  # 'portal' or 'bulletin'
        "portal_url": "https://www.mongolbank.mn/mn/p/monetary-policy-rate",
        "bulletin_section": "Бодлогын хүү",  # keyword to find in PDF
        "output_id": "mongolbank-policy-rate",
        "frequency": "event",  # changes when policy changes, not regular monthly
        "columns_mn": ["огноо", "бодлогын_хүү_хувь"],
        "columns_en": ["date", "policy_rate_pct"],
        "unit": "percent",
        "language": "mn-only",  # requires translation
    },
    "money-supply-m2": {
        "title_en": "Mongolia Money Supply (M2)",
        "title_mn": "Монгол Улсын мөнгөний нийлүүлэлт (М2)",
        "source_type": "portal",
        "portal_url": "https://www.mongolbank.mn/mn/p/monetary-statistics",
        "bulletin_section": "Мөнгөний нийлүүлэлт",
        "output_id": "mongolbank-money-supply-m2",
        "frequency": "monthly",
        "columns_mn": ["огноо", "м2_тэрбум_төгрөг"],
        "columns_en": ["date", "m2_billion_mnt"],
        "unit": "billion MNT",
        "language": "mn-only",
    },
    "lending-rate": {
        "title_en": "Mongolia Weighted Average Lending Rate",
        "title_mn": "Зээлийн жигнэсэн дундаж хүү",
        "source_type": "portal",
        "portal_url": "https://www.mongolbank.mn/mn/p/interest-rate-statistics",
        "bulletin_section": "Зээлийн хүү",
        "output_id": "mongolbank-lending-rate",
        "frequency": "monthly",
        "columns_mn": ["огноо", "зээлийн_хүү_хувь"],
        "columns_en": ["date", "lending_rate_pct"],
        "unit": "percent",
        "language": "mn-only",
    },
    "deposit-rate": {
        "title_en": "Mongolia Weighted Average Deposit Rate",
        "title_mn": "Хадгаламжийн жигнэсэн дундаж хүү",
        "source_type": "portal",
        "portal_url": "https://www.mongolbank.mn/mn/p/interest-rate-statistics",
        "bulletin_section": "Хадгаламжийн хүү",
        "output_id": "mongolbank-deposit-rate",
        "frequency": "monthly",
        "columns_mn": ["огноо", "хадгаламжийн_хүү_хувь"],
        "columns_en": ["date", "deposit_rate_pct"],
        "unit": "percent",
        "language": "mn-only",
    },
}

# ─── HTTP helpers ─────────────────────────────────────────────────────────────

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.9",
    "Accept-Language": "mn,en;q=0.9",
})


def _get(url: str, timeout: int = 30) -> Optional[requests.Response]:
    for attempt in range(3):
        try:
            resp = SESSION.get(url, timeout=timeout)
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            if attempt == 2:
                print(f"  Error: {e}", file=sys.stderr)
                return None
            time.sleep(2 ** attempt)
    return None


# ─── Portal (HTML) fetching ───────────────────────────────────────────────────

def fetch_from_portal(indicator: dict) -> Optional[pd.DataFrame]:
    """
    Fetch indicator data from MongolBank statistics portal page.
    Tries direct HTML parse first, then Playwright if JS-rendered.
    """
    url = indicator["portal_url"]
    print(f"  Fetching from portal: {url}")

    resp = _get(url)
    if resp is None:
        return None

    df = _parse_html_table(resp.text, indicator)
    if df is not None and not df.empty:
        return df

    print("  HTML parse returned no data — trying Playwright...")
    return _fetch_playwright(url, indicator)


def _parse_html_table(html: str, indicator: dict) -> Optional[pd.DataFrame]:
    """Parse a statistics table from HTML."""
    soup = BeautifulSoup(html, "lxml")
    tables = soup.find_all("table")

    if not tables:
        return None

    # Try each table, pick the one with date-like first column
    for table in tables:
        rows = table.find_all("tr")
        if len(rows) < 2:
            continue

        headers = [th.get_text(strip=True) for th in rows[0].find_all(["th", "td"])]
        data_rows = []
        for tr in rows[1:]:
            cells = [td.get_text(strip=True) for td in tr.find_all("td")]
            if cells:
                data_rows.append(cells)

        if not data_rows:
            continue

        df = pd.DataFrame(data_rows, columns=headers[:len(data_rows[0])])

        # Check if first column looks like a date
        first_col = df.iloc[:, 0].astype(str)
        if first_col.str.match(r"\d{4}").any():
            return df

    return None


def _fetch_playwright(url: str, indicator: dict) -> Optional[pd.DataFrame]:
    """Use Playwright to render JS page and extract table."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  Install Playwright: pip install playwright && playwright install chromium",
              file=sys.stderr)
        return None

    print(f"  Using Playwright: {url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        try:
            page.wait_for_selector("table", timeout=10000)
        except Exception:
            print("  No table found after JS render", file=sys.stderr)
            browser.close()
            return None
        html = page.content()
        browser.close()

    return _parse_html_table(html, indicator)


# ─── Bulletin (PDF) fetching ──────────────────────────────────────────────────

BULLETIN_LIST_URL = "https://www.mongolbank.mn/mn/category/statistics"


def get_latest_bulletin_url() -> Optional[str]:
    """Find the URL of the latest statistical bulletin PDF."""
    resp = _get(BULLETIN_LIST_URL)
    if resp is None:
        return None

    soup = BeautifulSoup(resp.text, "lxml")

    # Look for PDF links
    pdf_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        if ".pdf" in href.lower() or "bulletin" in text.lower() or "статистик" in text.lower():
            if not href.startswith("http"):
                href = f"https://www.mongolbank.mn{href}"
            pdf_links.append((text, href))

    if not pdf_links:
        return None

    # Return most recent (first in list, assuming newest first)
    print(f"  Found bulletin: {pdf_links[0][0]}")
    return pdf_links[0][1]


def fetch_from_bulletin(indicator: dict) -> Optional[pd.DataFrame]:
    """
    Fetch indicator from PDF bulletin.
    Requires pdfplumber.
    """
    try:
        import pdfplumber
    except ImportError:
        print("  Install pdfplumber: pip install pdfplumber", file=sys.stderr)
        return None

    pdf_url = get_latest_bulletin_url()
    if not pdf_url:
        print("  Could not find bulletin PDF", file=sys.stderr)
        return None

    print(f"  Downloading PDF: {pdf_url}")
    resp = _get(pdf_url, timeout=60)
    if not resp:
        return None

    keyword = indicator.get("bulletin_section", "")
    tables_found = []

    with pdfplumber.open(BytesIO(resp.content)) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            if keyword.lower() in text.lower():
                tables = page.extract_tables()
                for t in tables:
                    if t and len(t) > 1:
                        df = pd.DataFrame(t[1:], columns=t[0])
                        tables_found.append(df)
                        print(f"  Found table on page {page_num + 1}: {list(df.columns)[:4]}")

    if not tables_found:
        print(f"  No tables found with keyword '{keyword}'", file=sys.stderr)
        return None

    return tables_found[0]


# ─── Post-processing & translation ───────────────────────────────────────────

def normalize_date_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect and normalize the date column to ISO format YYYY-MM-DD.
    Handles: YYYY-MM, YYYY.MM, YYYY оны MM сар, etc.
    """
    date_col = df.columns[0]  # assume first column is date

    def parse_mn_date(s: str) -> Optional[str]:
        s = str(s).strip()
        # YYYY-MM-DD
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
        if m:
            return s[:10]
        # YYYY-MM
        m = re.match(r"(\d{4})-(\d{2})$", s)
        if m:
            return f"{m.group(1)}-{m.group(2)}-01"
        # YYYY.MM
        m = re.match(r"(\d{4})\.(\d{2})", s)
        if m:
            return f"{m.group(1)}-{m.group(2)}-01"
        # YYYY оны MM сар
        m = re.match(r"(\d{4})\s*оны?\s*(\d{1,2})", s)
        if m:
            return f"{m.group(1)}-{int(m.group(2)):02d}-01"
        # Just YYYY
        m = re.match(r"^(\d{4})$", s)
        if m:
            return f"{m.group(1)}-01-01"
        return None

    df["date_parsed"] = df[date_col].apply(parse_mn_date)
    df = df.dropna(subset=["date_parsed"])
    df[date_col] = df["date_parsed"]
    df = df.drop(columns=["date_parsed"])
    return df


def clean_numeric(series: pd.Series) -> pd.Series:
    """Strip commas, spaces, % signs; convert to float."""
    return pd.to_numeric(
        series.astype(str).str.replace(",", "").str.replace("%", "").str.strip(),
        errors="coerce"
    )


def build_output_csvs(df_raw: pd.DataFrame, indicator: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Build EN and MN CSVs from raw (Mongolian) DataFrame.
    Returns (df_en, df_mn).
    """
    # Normalize date
    df = normalize_date_column(df_raw.copy())

    date_col = df.columns[0]
    value_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]

    # Clean value
    df[value_col] = clean_numeric(df[value_col])
    df = df.dropna(subset=[value_col])

    cols_mn = indicator["columns_mn"]
    cols_en = indicator["columns_en"]

    # MN CSV
    df_mn = df[[date_col, value_col]].copy()
    df_mn.columns = cols_mn

    # EN CSV — same data, English column names (translation happens at column level)
    df_en = df_mn.copy()
    df_en.columns = cols_en

    return df_en, df_mn


# ─── Update detection ─────────────────────────────────────────────────────────

def check_update(indicator: dict, last_date_str: str) -> str:
    """
    Check if new data is available.
    Returns 'UPDATE_AVAILABLE' or 'UP_TO_DATE'.
    """
    print(f"  Checking for updates (last saved: {last_date_str})...")
    resp = _get(indicator["portal_url"])
    if resp is None:
        print("  Could not reach portal — assuming UPDATE_AVAILABLE")
        return "UPDATE_AVAILABLE"

    soup = BeautifulSoup(resp.text, "lxml")
    text = soup.get_text()

    # Find most recent date in page
    dates = re.findall(r"(\d{4})[-./](\d{2})", text)
    if not dates:
        return "UPDATE_AVAILABLE"

    latest = max(f"{y}-{m}" for y, m in dates)
    last = last_date_str[:7]  # compare YYYY-MM

    if latest > last:
        print(f"  UPDATE_AVAILABLE (latest: {latest}, last saved: {last})")
        return "UPDATE_AVAILABLE"
    else:
        print(f"  UP_TO_DATE (latest: {latest})")
        return "UP_TO_DATE"


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Fetch Bank of Mongolia statistics bulletin tables",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch policy rate
  python3 fetch_bulletin_table.py --indicator policy-rate --output ./output

  # Check for updates
  python3 fetch_bulletin_table.py --indicator policy-rate --check-update --last-date 2024-12

  # List available indicators
  python3 fetch_bulletin_table.py --list-indicators
        """,
    )
    parser.add_argument("--indicator", "-i", choices=list(INDICATORS.keys()),
                        help="Which indicator to fetch")
    parser.add_argument("--output", "-o", type=Path, default=Path("."),
                        help="Output directory")
    parser.add_argument("--list-indicators", action="store_true",
                        help="List available indicators")
    parser.add_argument("--check-update", action="store_true",
                        help="Check if new data is available")
    parser.add_argument("--last-date", type=str, default=None,
                        help="Last saved date YYYY-MM (for --check-update)")
    parser.add_argument("--force-bulletin", action="store_true",
                        help="Force PDF bulletin fetch (skip portal)")
    args = parser.parse_args()

    if args.list_indicators:
        print("Available indicators:")
        for slug, cfg in INDICATORS.items():
            print(f"  {slug:30s} — {cfg['title_en']}")
            print(f"  {'':30s}   Source: {cfg['portal_url']}")
        return

    if not args.indicator:
        parser.error("--indicator is required")

    indicator = INDICATORS[args.indicator]

    # Update check mode
    if args.check_update:
        last = args.last_date or "2000-01"
        result = check_update(indicator, last)
        print(result)
        sys.exit(0 if result == "UP_TO_DATE" else 1)

    print(f"Fetching: {indicator['title_en']}")
    print(f"Output: {args.output.absolute()}")
    print("=" * 50)

    # Fetch data
    df_raw = None

    if not args.force_bulletin and indicator["source_type"] == "portal":
        df_raw = fetch_from_portal(indicator)

    if df_raw is None or df_raw.empty:
        print("  Portal fetch failed — trying PDF bulletin...")
        df_raw = fetch_from_bulletin(indicator)

    if df_raw is None or df_raw.empty:
        print("ERROR: Could not retrieve data from any source.", file=sys.stderr)
        print("Try: --force-bulletin or check the portal URL in INDICATORS", file=sys.stderr)
        sys.exit(1)

    print(f"  Retrieved {len(df_raw)} rows from source")

    # Build bilingual output
    df_en, df_mn = build_output_csvs(df_raw, indicator)

    if df_en.empty:
        print("ERROR: No valid rows after cleaning.", file=sys.stderr)
        sys.exit(1)

    # Save
    args.output.mkdir(parents=True, exist_ok=True)
    out_id = indicator["output_id"]
    en_path = args.output / f"{out_id}-en.csv"
    mn_path = args.output / f"{out_id}-mn.csv"

    df_en.to_csv(en_path, index=False)
    df_mn.to_csv(mn_path, index=False)

    print(f"\nSaved:")
    print(f"  EN: {en_path} ({len(df_en)} rows)")
    print(f"  MN: {mn_path} ({len(df_mn)} rows)")
    print(f"  Date range: {df_en.iloc[:, 0].min()} to {df_en.iloc[:, 0].max()}")
    print()
    print("Next: translate MN-only data if needed:")
    print(f"  conda run -n datamn python3 tools/scripts/translate_csv.py {mn_path} --from mn --to en -o {en_path}")


if __name__ == "__main__":
    main()
