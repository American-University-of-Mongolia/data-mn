#!/usr/bin/env python3
"""
Fetch official daily exchange rates from the Bank of Mongolia.

Source: https://www.mongolbank.mn/mn/currency-rates
Output: Bilingual CSVs (EN + MN) ready for data.mn ingestion.

Usage:
    python3 fetch_exchange_rates.py --output ./output
    python3 fetch_exchange_rates.py --currencies USD EUR CNY --start 2020-01-01 --output ./output
    python3 fetch_exchange_rates.py --check-update --last-date 2025-01-10
"""

import argparse
import sys
import time
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup

# ─── Constants ────────────────────────────────────────────────────────────────

BASE_URL = "https://www.mongolbank.mn"
EXCHANGE_RATE_URL = f"{BASE_URL}/mn/currency-rates"

# Currencies to include by default (major currencies for Mongolia)
DEFAULT_CURRENCIES = ["USD", "EUR", "CNY", "RUB", "JPY", "KRW"]

# Mongolian → English currency name map
CURRENCY_NAME_MAP_MN_TO_EN = {
    "Америк доллар": "US Dollar",
    "Евро": "Euro",
    "Хятад юань": "Chinese Yuan",
    "Оросын рубль": "Russian Ruble",
    "Японы иен": "Japanese Yen",
    "Солонгосын вон": "South Korean Won",
    "Их Британийн фунт": "British Pound",
    "Австралийн доллар": "Australian Dollar",
    "Казахстаны тенге": "Kazakhstani Tenge",
    "Сингапурын доллар": "Singapore Dollar",
    "Гонконгийн доллар": "Hong Kong Dollar",
    "Канадын доллар": "Canadian Dollar",
    "Швейцарийн франк": "Swiss Franc",
    "Турк лир": "Turkish Lira",
}

# ─── HTTP helpers ─────────────────────────────────────────────────────────────

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "mn,en;q=0.9",
    "Referer": BASE_URL,
})


def _get(url: str, params: dict = None, timeout: int = 30) -> Optional[requests.Response]:
    """GET with retry."""
    for attempt in range(3):
        try:
            resp = SESSION.get(url, params=params, timeout=timeout)
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            if attempt == 2:
                print(f"  Error fetching {url}: {e}", file=sys.stderr)
                return None
            time.sleep(2 ** attempt)
    return None


# ─── Data fetching ────────────────────────────────────────────────────────────

def fetch_rates_page_html(target_date: Optional[date] = None) -> Optional[str]:
    """
    Fetch the exchange rates page HTML.
    If target_date is provided, try to get rates for that specific date.

    The page is JavaScript-rendered. This function fetches the raw HTML;
    if the data isn't present (JS-only), it falls back to Playwright.
    """
    params = {}
    if target_date:
        params["date"] = target_date.strftime("%Y-%m-%d")

    resp = _get(EXCHANGE_RATE_URL, params=params)
    if resp is None:
        return None
    return resp.text


def parse_rates_from_html(html: str, target_date: date) -> Optional[pd.DataFrame]:
    """
    Parse exchange rate table from HTML.
    Returns DataFrame with columns: date, currency_code, currency_name_mn, rate_mnt, unit
    """
    soup = BeautifulSoup(html, "lxml")

    # Look for exchange rate table
    tables = soup.find_all("table")
    rate_table = None
    for table in tables:
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        # Look for table that has currency-like headers
        if any(h in headers for h in ["Валют", "Код", "Ханш", "Code", "Rate"]):
            rate_table = table
            break

    if rate_table is None:
        return None

    rows = []
    for tr in rate_table.find_all("tr")[1:]:  # skip header
        cells = [td.get_text(strip=True) for td in tr.find_all("td")]
        if len(cells) >= 3:
            rows.append(cells)

    if not rows:
        return None

    # Build DataFrame — column order varies; detect by header
    headers = [th.get_text(strip=True) for th in rate_table.find_all("th")]
    df = pd.DataFrame(rows, columns=headers[:len(rows[0])])
    df["date"] = target_date.isoformat()
    return df


def fetch_rates_playwright(target_date: Optional[date] = None) -> Optional[pd.DataFrame]:
    """
    Fallback: use Playwright to render the JS page and extract rates.
    Requires: playwright install chromium
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  Playwright not installed. Run: pip install playwright && playwright install chromium",
              file=sys.stderr)
        return None

    url = EXCHANGE_RATE_URL
    if target_date:
        url += f"?date={target_date.strftime('%Y-%m-%d')}"

    print(f"  Using Playwright to render: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)

        # Wait for table to appear
        try:
            page.wait_for_selector("table", timeout=10000)
        except Exception:
            print("  No table found after page load", file=sys.stderr)
            browser.close()
            return None

        html = page.content()
        browser.close()

    if target_date is None:
        target_date = date.today()

    return parse_rates_from_html(html, target_date)


def fetch_rates_for_date(target_date: date) -> Optional[pd.DataFrame]:
    """Fetch exchange rates for a single date. Tries HTML first, then Playwright."""
    html = fetch_rates_page_html(target_date)
    if html:
        df = parse_rates_from_html(html, target_date)
        if df is not None and not df.empty:
            return df

    # Fallback to Playwright
    print(f"  HTML parse failed for {target_date}, trying Playwright...")
    return fetch_rates_playwright(target_date)


def fetch_historical_rates(
    start: date,
    end: date,
    currencies: list[str],
    sleep_seconds: float = 0.5,
) -> pd.DataFrame:
    """
    Fetch exchange rates for a date range.
    Skips weekends (mongolbank publishes on business days only).
    """
    all_rows = []
    current = start

    total_days = (end - start).days + 1
    processed = 0

    while current <= end:
        # Skip weekends
        if current.weekday() < 5:  # Mon=0 ... Fri=4
            df = fetch_rates_for_date(current)
            if df is not None and not df.empty:
                # Filter to requested currencies if column exists
                if "currency_code" in df.columns or "Код" in df.columns:
                    code_col = "currency_code" if "currency_code" in df.columns else "Код"
                    df = df[df[code_col].isin(currencies)]
                all_rows.append(df)

            processed += 1
            if processed % 10 == 0:
                pct = processed / total_days * 100
                print(f"  Progress: {processed}/{total_days} days ({pct:.0f}%)")

            time.sleep(sleep_seconds)

        current += timedelta(days=1)

    if not all_rows:
        return pd.DataFrame()

    return pd.concat(all_rows, ignore_index=True)


# ─── Output formatting ────────────────────────────────────────────────────────

def format_en(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize raw DataFrame to EN output format:
    date, currency_code, currency_name, rate_mnt
    """
    # Map Mongolian currency names to English
    if "currency_name_mn" in df.columns:
        df["currency_name"] = df["currency_name_mn"].map(CURRENCY_NAME_MAP_MN_TO_EN).fillna(df["currency_name_mn"])
    elif "Нэр" in df.columns:
        df["currency_name"] = df["Нэр"].map(CURRENCY_NAME_MAP_MN_TO_EN).fillna(df["Нэр"])

    # Normalize rate column (strip commas)
    rate_col = next((c for c in df.columns if c in ["Ханш", "rate_mnt", "Rate"]), None)
    if rate_col:
        df["rate_mnt"] = pd.to_numeric(
            df[rate_col].astype(str).str.replace(",", ""), errors="coerce"
        )

    # Normalize code column
    code_col = next((c for c in df.columns if c in ["Код", "currency_code", "Code"]), None)
    if code_col:
        df["currency_code"] = df[code_col]

    out = df[["date", "currency_code", "currency_name", "rate_mnt"]].copy()
    out["rate_mnt"] = out["rate_mnt"].round(4)
    return out.dropna(subset=["currency_code", "rate_mnt"])


def format_mn(df_en: pd.DataFrame, df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Build MN output from EN + raw data.
    MN columns: огноо, валютын_код, валютын_нэр, ханш_төгрөг
    """
    name_col = next((c for c in df_raw.columns if c in ["Нэр", "currency_name_mn"]), None)

    df_mn = df_en.copy()
    df_mn = df_mn.rename(columns={
        "date": "огноо",
        "currency_code": "валютын_код",
        "currency_name": "валютын_нэр",
        "rate_mnt": "ханш_төгрөг",
    })

    # Replace EN currency names with MN names
    if name_col:
        reverse_map = {v: k for k, v in CURRENCY_NAME_MAP_MN_TO_EN.items()}
        df_mn["валютын_нэр"] = df_mn["валютын_нэр"].map(reverse_map).fillna(df_mn["валютын_нэр"])

    return df_mn


# ─── Update detection ─────────────────────────────────────────────────────────

def check_update(last_date_str: str) -> str:
    """
    Compare last saved date with today's date.
    Returns 'UPDATE_AVAILABLE' or 'UP_TO_DATE'.
    """
    try:
        last_date = date.fromisoformat(last_date_str)
    except ValueError:
        return "UPDATE_AVAILABLE"

    today = date.today()
    # MongolBank publishes on business days
    if today.weekday() >= 5:
        today = today - timedelta(days=today.weekday() - 4)  # most recent Friday

    if last_date >= today:
        print(f"  UP_TO_DATE (last: {last_date}, latest: {today})")
        return "UP_TO_DATE"
    else:
        print(f"  UPDATE_AVAILABLE (last: {last_date}, latest: {today})")
        return "UPDATE_AVAILABLE"


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Fetch Bank of Mongolia official daily exchange rates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch today's rates for default currencies
  python3 fetch_exchange_rates.py --output ./output

  # Fetch historical data for specific currencies
  python3 fetch_exchange_rates.py --currencies USD EUR CNY --start 2020-01-01 --output ./output

  # Check if update is available
  python3 fetch_exchange_rates.py --check-update --last-date 2025-01-10
        """,
    )
    parser.add_argument("--output", "-o", type=Path, default=Path("."),
                        help="Output directory")
    parser.add_argument("--currencies", nargs="+", default=DEFAULT_CURRENCIES,
                        help=f"Currency codes to include (default: {DEFAULT_CURRENCIES})")
    parser.add_argument("--start", type=str, default=None,
                        help="Start date YYYY-MM-DD (default: today)")
    parser.add_argument("--end", type=str, default=None,
                        help="End date YYYY-MM-DD (default: today)")
    parser.add_argument("--check-update", action="store_true",
                        help="Check if new data is available")
    parser.add_argument("--last-date", type=str, default=None,
                        help="Last saved date (for --check-update)")
    parser.add_argument("--use-playwright", action="store_true",
                        help="Force Playwright (skip HTML parse attempt)")
    args = parser.parse_args()

    # Update check mode
    if args.check_update:
        if not args.last_date:
            print("UPDATE_AVAILABLE")
            sys.exit(0)
        result = check_update(args.last_date)
        print(result)
        sys.exit(0 if result == "UP_TO_DATE" else 1)

    # Determine date range
    end_date = date.fromisoformat(args.end) if args.end else date.today()
    start_date = date.fromisoformat(args.start) if args.start else end_date

    print(f"Fetching exchange rates: {start_date} to {end_date}")
    print(f"Currencies: {args.currencies}")
    print(f"Output: {args.output.absolute()}")
    print("=" * 50)

    # Fetch data
    if start_date == end_date:
        df_raw = fetch_rates_playwright(start_date) if args.use_playwright else fetch_rates_for_date(start_date)
    else:
        df_raw = fetch_historical_rates(start_date, end_date, args.currencies)

    if df_raw is None or df_raw.empty:
        print("ERROR: No data retrieved.", file=sys.stderr)
        sys.exit(1)

    # Format outputs
    df_en = format_en(df_raw)
    df_mn = format_mn(df_en, df_raw)

    # Save
    args.output.mkdir(parents=True, exist_ok=True)
    en_path = args.output / "mongolbank-exchange-rates-daily-en.csv"
    mn_path = args.output / "mongolbank-exchange-rates-daily-mn.csv"

    df_en.to_csv(en_path, index=False)
    df_mn.to_csv(mn_path, index=False)

    print(f"\nSaved:")
    print(f"  EN: {en_path} ({len(df_en)} rows)")
    print(f"  MN: {mn_path} ({len(df_mn)} rows)")
    print(f"  Currencies: {sorted(df_en['currency_code'].unique().tolist())}")
    print(f"  Date range: {df_en['date'].min()} to {df_en['date'].max()}")


if __name__ == "__main__":
    main()
