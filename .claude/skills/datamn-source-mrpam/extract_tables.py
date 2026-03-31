#!/usr/bin/env python3
"""
Extract tables from MRPAM monthly statistical report PDFs.

Finds sections by Mongolian heading text (NOT by page number — pages shift
between report months). Handles merged cells and noisy whitespace.

Usage:
    # Extract a specific dataset from all PDFs in a year's cache
    python3 extract_tables.py --dataset mrpam-coal-production --year 2025

    # Extract all datasets from a single PDF
    python3 extract_tables.py --pdf /path/to/report.pdf --all

    # Extract a specific dataset from a single PDF
    python3 extract_tables.py --pdf /path/to/report.pdf --dataset mrpam-coal-production

    # Debug: print all pages and detected tables
    python3 extract_tables.py --pdf /path/to/report.pdf --debug
"""

import argparse
import re
import sys
from pathlib import Path

import pandas as pd
import pdfplumber

# ─── Constants ────────────────────────────────────────────────────────────────

# Resolve from repo root (skill is at .claude/skills/datamn-source-mrpam/)
_REPO_ROOT = Path(__file__).resolve().parents[3]
CACHE_DIR = _REPO_ROOT / "tools" / "temp" / "mrpam-pdfs"
OUTPUT_DIR = _REPO_ROOT / "tools" / "temp" / "mrpam-extracted"

YEAR_PAGE_IDS = {
    2021: 169, 2022: 177, 2023: 196,
    2024: 202, 2025: 714, 2026: 732,
}

# ─── Section Keywords (search for these in page text) ─────────────────────────

SECTION_KEYWORDS = {
    "licenses": ["тусгай зөвшөөрөл", "special permit"],
    "coal": ["нүүрс", "coal"],
    "petroleum_prod": ["газрын тос", "petroleum"],
    "fuel_prices": ["шатахуун", "fuel price", "бензин"],
    "budget": ["улсын төсвийн орлого", "budget revenue"],
    "commodity_prices": ["дэлхийн зах зээл", "world market", "commodity price"],
}

# ─── Cleaning Helpers ─────────────────────────────────────────────────────────


def clean_cell(val) -> str | None:
    """Normalize a cell value: strip whitespace, collapse newlines."""
    if val is None:
        return None
    text = str(val).replace("\n", " ").strip()
    text = re.sub(r"\s+", " ", text)
    return text if text else None


def forward_fill_none(rows: list[list]) -> list[list]:
    """Fill None cells using the last non-None value in the same column."""
    if not rows:
        return rows
    n_cols = max(len(r) for r in rows)
    last = [None] * n_cols
    result = []
    for row in rows:
        new_row = list(row) + [None] * (n_cols - len(row))
        for i, cell in enumerate(new_row):
            if cell is None or (isinstance(cell, str) and not cell.strip()):
                new_row[i] = last[i]
            else:
                last[i] = new_row[i]
        result.append(new_row)
    return result


def to_float(val) -> float | None:
    """Parse a numeric cell that may have spaces/commas as separators."""
    if val is None:
        return None
    s = str(val).replace(" ", "").replace(",", ".").replace("\xa0", "")
    s = re.sub(r"[^\d.\-]", "", s)
    try:
        return float(s) if s else None
    except ValueError:
        return None


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """Drop all-empty rows and columns, strip cell whitespace."""
    df = df.dropna(how="all").dropna(axis=1, how="all")
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].apply(lambda v: clean_cell(v))
    df = df[df.apply(lambda r: any(v is not None for v in r), axis=1)]
    return df.reset_index(drop=True)


# ─── PDF Utilities ────────────────────────────────────────────────────────────


def find_pages_with_keyword(pdf, keywords: list[str]) -> list[int]:
    """Return 0-based page indices that contain any of the keywords (case-insensitive)."""
    matches = []
    for i, page in enumerate(pdf.pages):
        text = (page.extract_text() or "").lower()
        if any(kw.lower() in text for kw in keywords):
            matches.append(i)
    return matches


def extract_table_from_page(page, table_idx: int = 0) -> list[list] | None:
    """Extract the n-th table from a page, with fallback settings."""
    # Try line-based detection first (most accurate for bordered tables)
    for strategy in (
        {"vertical_strategy": "lines", "horizontal_strategy": "lines"},
        {"vertical_strategy": "text", "horizontal_strategy": "lines"},
        {"vertical_strategy": "lines", "horizontal_strategy": "text"},
    ):
        tables = page.extract_tables(strategy)
        if tables and len(tables) > table_idx:
            t = tables[table_idx]
            if t and len(t) > 1:
                return t
    return None


def extract_largest_table(page) -> list[list] | None:
    """Extract the largest table (by cell count) from a page."""
    for strategy in (
        {"vertical_strategy": "lines", "horizontal_strategy": "lines"},
        {"vertical_strategy": "text", "horizontal_strategy": "lines"},
    ):
        tables = page.extract_tables(strategy)
        if tables:
            best = max(tables, key=lambda t: sum(len(r) for r in t) if t else 0)
            if best and len(best) > 1:
                return best
    return None


# ─── Dataset Extractors ───────────────────────────────────────────────────────


def extract_coal_production(pdf, year: int, month: int) -> pd.DataFrame | None:
    """
    Extract coal production/export/domestic data (Tables 3.16, 3.17).
    Looks for pages mentioning 'нүүрс' (coal) with a monthly breakdown.
    Returns DataFrame with columns: year, month, production_kt, export_kt, domestic_kt
    """
    pages = find_pages_with_keyword(pdf, ["нүүрс", "3.16", "3.17"])
    if not pages:
        return None

    all_rows = []
    for pg_idx in pages:
        page = pdf.pages[pg_idx]
        raw = extract_largest_table(page)
        if not raw:
            continue

        raw = forward_fill_none(raw)
        raw = [[clean_cell(c) for c in row] for row in raw]

        # Look for a row that matches our target month (cumulative or monthly)
        for row in raw:
            # Try to find the row for this specific month
            row_text = " ".join(str(c) for c in row if c)
            # Mongolian months in order: 1 сар ... 12 сар
            month_str = str(month)
            if not (re.search(rf"\b{month_str}\b", row_text) or
                    re.search(rf"{month_str}\s*сар", row_text)):
                continue

            nums = [to_float(c) for c in row if to_float(c) is not None]
            if len(nums) >= 2:
                all_rows.append({
                    "year": year,
                    "month": month,
                    "production_kt": nums[0] if len(nums) > 0 else None,
                    "export_kt": nums[1] if len(nums) > 1 else None,
                    "domestic_kt": nums[2] if len(nums) > 2 else None,
                })
                break  # take first match per page

    if not all_rows:
        return None

    return pd.DataFrame(all_rows)


def extract_petroleum_production(pdf, year: int, month: int) -> pd.DataFrame | None:
    """
    Extract petroleum production/export (Tables 4.1, 4.2).
    Returns DataFrame: year, month, production_barrels, export_barrels
    """
    pages = find_pages_with_keyword(pdf, ["газрын тос", "4.1", "4.2", "баррель"])
    if not pages:
        return None

    for pg_idx in pages:
        page = pdf.pages[pg_idx]
        raw = extract_largest_table(page)
        if not raw:
            continue

        raw = forward_fill_none(raw)
        raw = [[clean_cell(c) for c in row] for row in raw]

        for row in raw:
            row_text = " ".join(str(c) for c in row if c)
            if not re.search(rf"\b{month}\b", row_text):
                continue
            nums = [to_float(c) for c in row if to_float(c) is not None]
            if len(nums) >= 1:
                return pd.DataFrame([{
                    "year": year,
                    "month": month,
                    "production_barrels": nums[0] if len(nums) > 0 else None,
                    "export_barrels": nums[1] if len(nums) > 1 else None,
                }])
    return None


def extract_mining_permits(pdf, year: int, month: int) -> pd.DataFrame | None:
    """
    Extract mining permits by province (Table 1.1).

    Province names are in a left-side text column (x≈67) separate from the
    bordered table. We align them to table rows by matching y-coordinates.

    Returns DataFrame: year, month, province, exploration_count, exploration_area_ha,
                       extraction_count, extraction_area_ha
    """
    pages = find_pages_with_keyword(pdf, ["тусгай зөвшөөрөл", "1.1", "хайгуулын"])
    if not pages:
        return None

    for pg_idx in pages:
        page = pdf.pages[pg_idx]

        # --- Step 1: extract province names from left text column ---
        words = page.extract_words()
        # Province names sit at x < 150, below the header (y > 200)
        province_words: dict[float, str] = {}  # y_center → name
        for w in words:
            if w["x0"] < 150 and w["top"] > 200:
                y = round(w["top"])
                # Collect multi-word province names on the same line
                existing = province_words.get(y, "")
                province_words[y] = (existing + " " + w["text"]).strip()

        # Filter out non-province entries (footnotes, headers)
        known_prefixes = (
            "Архангай", "Баян", "Булган", "Говь", "Дархан", "Дорно",
            "Дунд", "Завхан", "Орхон", "Өвөр", "Өмнө", "Сүх", "Сэлэн",
            "Төв", "Увс", "Улаанбаатар", "Ховд", "Хөвс", "Хэнтий",
        )
        province_ys = sorted(
            [(y, name) for y, name in province_words.items()
             if any(name.startswith(p) for p in known_prefixes)],
            key=lambda x: x[0],
        )

        # --- Step 2: extract table rows ---
        raw = extract_largest_table(page)
        if not raw:
            continue

        # Find data rows (rows where first cell looks numeric = permit count)
        data_rows = []
        for row in raw:
            nums = [to_float(c) for c in row if to_float(c) is not None]
            if len(nums) >= 4:
                data_rows.append(nums)

        if not data_rows or not province_ys:
            continue

        # Skip the first data row if it's the national total (highest permit count)
        if len(data_rows) > len(province_ys):
            data_rows = data_rows[len(data_rows) - len(province_ys):]

        rows_out = []
        for (_, province), nums in zip(province_ys, data_rows):
            rows_out.append({
                "year": year,
                "month": month,
                "province": province,
                "total_count": int(nums[0]) if len(nums) > 0 else None,
                "total_area_kha": nums[1] if len(nums) > 1 else None,
                "extraction_count": int(nums[3]) if len(nums) > 3 else None,
                "extraction_area_kha": nums[4] if len(nums) > 4 else None,
                "exploration_count": int(nums[6]) if len(nums) > 6 else None,
                "exploration_area_kha": nums[7] if len(nums) > 7 else None,
            })

        if rows_out:
            return pd.DataFrame(rows_out)
    return None


def extract_commodity_prices(pdf, year: int, month: int) -> pd.DataFrame | None:
    """
    Extract world commodity prices (Table 3.8).
    Returns DataFrame: year, month, commodity, price, unit, source
    """
    pages = find_pages_with_keyword(pdf, ["дэлхийн зах зээл", "3.8", "алт", "зэс"])
    if not pages:
        return None

    for pg_idx in pages:
        page = pdf.pages[pg_idx]
        raw = extract_largest_table(page)
        if not raw:
            continue

        raw = [[clean_cell(c) for c in row] for row in raw]
        rows_out = []
        for row in raw[1:]:
            if not row or not row[0]:
                continue
            commodity = row[0]
            if len(row) >= 2:
                price = to_float(row[-1]) or to_float(row[1])
                unit = row[2] if len(row) > 2 else None
                rows_out.append({
                    "year": year,
                    "month": month,
                    "commodity": commodity,
                    "price": price,
                    "unit": unit,
                })

        if rows_out:
            return pd.DataFrame(rows_out)
    return None


def extract_fuel_prices(pdf, year: int, month: int) -> pd.DataFrame | None:
    """
    Extract retail fuel prices by province (Table 4.6).
    Returns DataFrame: year, month, province, gasoline_price, diesel_price
    """
    pages = find_pages_with_keyword(pdf, ["шатахуун", "4.6", "бензин", "дизель"])
    if not pages:
        return None

    for pg_idx in pages:
        page = pdf.pages[pg_idx]
        raw = extract_largest_table(page)
        if not raw:
            continue

        raw = forward_fill_none(raw)
        raw = [[clean_cell(c) for c in row] for row in raw]

        rows_out = []
        for row in raw[1:]:
            if not row or not row[0]:
                continue
            province = row[0]
            nums = [to_float(c) for c in row[1:] if to_float(c) is not None]
            if len(nums) >= 1:
                rows_out.append({
                    "year": year,
                    "month": month,
                    "province": province,
                    "gasoline_price": nums[0] if len(nums) > 0 else None,
                    "diesel_price": nums[1] if len(nums) > 1 else None,
                })

        if rows_out:
            return pd.DataFrame(rows_out)
    return None


def extract_petroleum_imports(pdf, year: int, month: int) -> pd.DataFrame | None:
    """
    Extract petroleum product imports (Table 4.3).
    Returns DataFrame: year, month, product, volume, unit
    """
    pages = find_pages_with_keyword(pdf, ["импорт", "4.3", "шатахуун импорт"])
    if not pages:
        return None

    for pg_idx in pages:
        page = pdf.pages[pg_idx]
        raw = extract_largest_table(page)
        if not raw:
            continue

        raw = [[clean_cell(c) for c in row] for row in raw]
        rows_out = []
        for row in raw[1:]:
            if not row or not row[0]:
                continue
            product = row[0]
            nums = [to_float(c) for c in row[1:] if to_float(c) is not None]
            if len(nums) >= 1:
                rows_out.append({
                    "year": year,
                    "month": month,
                    "product": product,
                    "volume": nums[0],
                    "unit": row[2] if len(row) > 2 else None,
                })

        if rows_out:
            return pd.DataFrame(rows_out)
    return None


def extract_budget_revenue(pdf, year: int, month: int) -> pd.DataFrame | None:
    """
    Extract state budget revenue from mining (Table 5.1).
    Returns DataFrame: year, month, revenue_type, plan_bln_mnt, actual_bln_mnt, pct_of_plan
    """
    pages = find_pages_with_keyword(pdf, ["улсын төсвийн орлого", "5.1", "төсөв"])
    if not pages:
        return None

    for pg_idx in pages:
        page = pdf.pages[pg_idx]
        raw = extract_largest_table(page)
        if not raw:
            continue

        raw = [[clean_cell(c) for c in row] for row in raw]
        rows_out = []
        for row in raw[1:]:
            if not row or not row[0]:
                continue
            rev_type = row[0]
            nums = [to_float(c) for c in row[1:] if to_float(c) is not None]
            if len(nums) >= 1:
                rows_out.append({
                    "year": year,
                    "month": month,
                    "revenue_type": rev_type,
                    "plan_bln_mnt": nums[0] if len(nums) > 0 else None,
                    "actual_bln_mnt": nums[1] if len(nums) > 1 else None,
                    "pct_of_plan": nums[2] if len(nums) > 2 else None,
                })

        if rows_out:
            return pd.DataFrame(rows_out)
    return None


# ─── Dataset Registry ─────────────────────────────────────────────────────────

DATASET_EXTRACTORS = {
    "mrpam-coal-production": extract_coal_production,
    "mrpam-petroleum-production": extract_petroleum_production,
    "mrpam-mining-permits": extract_mining_permits,
    "mrpam-commodity-prices": extract_commodity_prices,
    "mrpam-fuel-prices": extract_fuel_prices,
    "mrpam-petroleum-imports": extract_petroleum_imports,
    "mrpam-budget-revenue": extract_budget_revenue,
}

# Mongolian column name mappings for each dataset
MN_COLUMNS = {
    "mrpam-coal-production": {
        "year": "он", "month": "сар",
        "production_kt": "олборлолт_мян_тн",
        "export_kt": "экспорт_мян_тн",
        "domestic_kt": "дотоод_мян_тн",
    },
    "mrpam-petroleum-production": {
        "year": "он", "month": "сар",
        "production_barrels": "олборлолт_баррель",
        "export_barrels": "экспорт_баррель",
    },
    "mrpam-mining-permits": {
        "year": "он", "month": "сар", "province": "аймаг",
        "total_count": "нийт_тоо",
        "total_area_kha": "нийт_талбай_мян_га",
        "extraction_count": "ашиглалтын_тоо",
        "extraction_area_kha": "ашиглалтын_талбай_мян_га",
        "exploration_count": "хайгуулын_тоо",
        "exploration_area_kha": "хайгуулын_талбай_мян_га",
    },
    "mrpam-commodity-prices": {
        "year": "он", "month": "сар", "commodity": "бараа",
        "price": "үнэ", "unit": "нэгж",
    },
    "mrpam-fuel-prices": {
        "year": "он", "month": "сар", "province": "аймаг",
        "gasoline_price": "бензин_үнэ", "diesel_price": "дизель_үнэ",
    },
    "mrpam-petroleum-imports": {
        "year": "он", "month": "сар", "product": "бүтээгдэхүүн",
        "volume": "хэмжээ", "unit": "нэгж",
    },
    "mrpam-budget-revenue": {
        "year": "он", "month": "сар", "revenue_type": "орлогын_төрөл",
        "plan_bln_mnt": "төлөвлөгөө_тэрбум", "actual_bln_mnt": "гүйцэтгэл_тэрбум",
        "pct_of_plan": "хувь",
    },
}


# ─── Core Logic ───────────────────────────────────────────────────────────────


def parse_year_month_from_filename(filename: str) -> tuple[int, int] | None:
    """
    Extract year and month from various MRPAM PDF filename patterns:
      2025.1.stat.report.mon.pdf
      2025.01.stat.report.mon.pdf
      2021-01-mon.pdf
      2022-01.pdf
      2021-02-stat-report-mon.pdf
    """
    # Pattern: YYYY.M. or YYYY.MM.
    m = re.search(r"(\d{4})\.(\d{1,2})[.\-]", filename)
    if m:
        return int(m.group(1)), int(m.group(2))
    # Pattern: YYYY-MM
    m = re.search(r"(\d{4})-(\d{1,2})", filename)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None


def extract_dataset_from_pdf(pdf_path: Path, dataset_id: str) -> pd.DataFrame | None:
    """Extract a single dataset from one PDF file."""
    parsed = parse_year_month_from_filename(pdf_path.name)
    if not parsed:
        print(f"  Warning: cannot parse year/month from {pdf_path.name}")
        return None

    year, month = parsed
    extractor = DATASET_EXTRACTORS.get(dataset_id)
    if not extractor:
        raise ValueError(f"Unknown dataset: {dataset_id}")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            return extractor(pdf, year, month)
    except Exception as e:
        print(f"  Error extracting from {pdf_path.name}: {e}")
        return None


def collect_pdfs_for_year(year: int, cache_dir: Path | None = None) -> list[Path]:
    """Return all cached PDFs for a given year, sorted by filename."""
    year_dir = (cache_dir or CACHE_DIR) / str(year)
    if not year_dir.exists():
        return []
    return sorted(year_dir.glob("*.pdf"))


def save_bilingual(df_en: pd.DataFrame, dataset_id: str, output_dir: Path):
    """Save EN and MN CSVs from an English-column DataFrame."""
    output_dir.mkdir(parents=True, exist_ok=True)

    col_map = MN_COLUMNS.get(dataset_id, {})
    df_mn = df_en.rename(columns=col_map)

    en_path = output_dir / f"{dataset_id}-en.csv"
    mn_path = output_dir / f"{dataset_id}-mn.csv"

    df_en.to_csv(en_path, index=False)
    df_mn.to_csv(mn_path, index=False)

    print(f"  Saved: {en_path.name} ({len(df_en)} rows)")
    print(f"  Saved: {mn_path.name} ({len(df_mn)} rows)")


def debug_pdf(pdf_path: Path):
    """Print all pages, detected tables, and raw text for debugging."""
    print(f"\nDebugging: {pdf_path.name}")
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            tables = page.extract_tables()
            print(f"\n--- Page {i+1} ---")
            print(f"  Tables detected: {len(tables)}")
            print(f"  Text snippet: {text[:200].replace(chr(10), ' ')}")
            for j, t in enumerate(tables):
                if t:
                    print(f"  Table {j}: {len(t)} rows × {len(t[0]) if t else 0} cols")


# ─── CLI ──────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Extract tables from MRPAM PDFs")
    parser.add_argument("--pdf", type=Path, help="Single PDF file to process")
    parser.add_argument("--year", type=int, help="Process all cached PDFs for this year")
    parser.add_argument("--dataset", help=f"Dataset to extract: {', '.join(DATASET_EXTRACTORS)}")
    parser.add_argument("--all", action="store_true", help="Extract all datasets")
    parser.add_argument("--debug", action="store_true", help="Debug table detection")
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR, help="Output directory")
    parser.add_argument("--cache-dir", type=Path, default=CACHE_DIR, help="PDF cache directory")
    args = parser.parse_args()

    if args.debug:
        if not args.pdf:
            parser.error("--debug requires --pdf")
        debug_pdf(args.pdf)
        return

    datasets = list(DATASET_EXTRACTORS.keys()) if args.all else [args.dataset]
    if not datasets or datasets == [None]:
        parser.error("Specify --dataset DATASET_ID or --all")

    # Determine which PDFs to process
    if args.pdf:
        pdf_files = [args.pdf]
    elif args.year:
        pdf_files = collect_pdfs_for_year(args.year, args.cache_dir)
        if not pdf_files:
            print(f"No PDFs found in {CACHE_DIR}/{args.year}/")
            print("Run fetch_report.py first.")
            sys.exit(1)
        print(f"Found {len(pdf_files)} PDF(s) for {args.year}")
    else:
        parser.error("Specify --pdf or --year")

    # Extract and accumulate
    for dataset_id in datasets:
        print(f"\nExtracting: {dataset_id}")
        frames = []
        for pdf_path in pdf_files:
            print(f"  Processing {pdf_path.name} ...")
            df = extract_dataset_from_pdf(pdf_path, dataset_id)
            if df is not None and not df.empty:
                frames.append(df)
            else:
                print(f"  No data found for {dataset_id} in {pdf_path.name}")

        if not frames:
            print(f"  No data extracted for {dataset_id}")
            continue

        combined = pd.concat(frames, ignore_index=True)
        combined = combined.sort_values(["year", "month"]).reset_index(drop=True)
        save_bilingual(combined, dataset_id, args.output)

    print(f"\nDone. Output: {args.output}/")


if __name__ == "__main__":
    main()
