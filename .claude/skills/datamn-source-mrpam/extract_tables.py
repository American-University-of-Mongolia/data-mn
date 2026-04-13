#!/usr/bin/env python3
"""
Extract tables from MRPAM monthly statistical report PDFs.

Uses text-based parsing (page.extract_text()) with year.ROMAN_MONTH matching
instead of pdfplumber table detection — MRPAM PDFs include bar charts that
pdfplumber incorrectly detects as tables, producing garbage data.

Mining permits (Table 1.1) is the exception: it uses word-coordinate alignment
because province names appear outside the bordered table.

Usage:
    python3 extract_tables.py --dataset mrpam-coal-production --year 2025
    python3 extract_tables.py --pdf /path/to/report.pdf --all
    python3 extract_tables.py --pdf /path/to/report.pdf --dataset mrpam-coal-production
    python3 extract_tables.py --pdf /path/to/report.pdf --debug
"""

import argparse
import re
import sys
from pathlib import Path

import pandas as pd
import pdfplumber

# ─── Constants ────────────────────────────────────────────────────────────────

_REPO_ROOT = Path(__file__).resolve().parents[3]
CACHE_DIR = _REPO_ROOT / "tools" / "temp" / "mrpam-pdfs"
OUTPUT_DIR = _REPO_ROOT / "tools" / "temp" / "mrpam-extracted"

INT_TO_ROMAN = {
    1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI",
    7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII",
}

# Province name prefixes used to identify data rows in fuel prices table (4.6)
# Covers all 21 aimags + Ulaanbaatar + national average variants
_PROV_PREFIXES = (
    "Архангай", "Баян", "Булган", "Говь", "Дархан", "Дорно",
    "Дунд", "Завхан", "Орхон", "Өвөр", "Өмнө", "Сүх", "Сэлэн",
    "Төв", "Увс", "Улаанбаатар", "Улсын", "УЛСЫН", "Ховд", "Хөвс", "Хэнтий",
)

# Known revenue types for budget revenue table (5.1)
_BUDGET_REV_TYPES = [
    "Ашигт малтмалын нөөц ашигласны төлбөр",
    "Газрын тосны нөөц ашигласны төлбөр",
    "Аж ахуйн нэгжийн орлогын татвар",
    "Нийт",
]

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
    """Parse a numeric value that may use spaces or commas as thousand separators.

    Commas are stripped (NOT converted to dots) to avoid corrupting numbers
    like '7,987.8' → '7.987.8' which was the root cause of garbage extraction.
    """
    if val is None:
        return None
    s = str(val).replace(" ", "").replace(",", "").replace("\xa0", "")
    s = re.sub(r"[^\d.\-]", "", s)
    if s.count(".") > 1:
        return None  # multiple dots = not a valid number
    try:
        return float(s) if s else None
    except ValueError:
        return None


def extract_price_nums(text: str) -> list[float]:
    """Split text on whitespace, return floats for each token, skip %-containing tokens."""
    result = []
    for token in text.split():
        if "%" in token:
            continue
        v = to_float(token)
        if v is not None:
            result.append(v)
    return result


def extract_pct(text: str) -> float | None:
    """Extract first percentage value from text (e.g., '93.4%' → 93.4)."""
    m = re.search(r"([\d.,]+)%", text)
    if m:
        return to_float(m.group(1))
    return None


# ─── PDF Utilities ────────────────────────────────────────────────────────────


def find_pages_with_keyword(pdf, keywords: list[str]) -> list[int]:
    """Return 0-based page indices containing any of the keywords (case-insensitive)."""
    matches = []
    for i, page in enumerate(pdf.pages):
        text = (page.extract_text() or "").lower()
        if any(kw.lower() in text for kw in keywords):
            matches.append(i)
    return matches


def extract_table_from_page(page, table_idx: int = 0) -> list[list] | None:
    """Extract the n-th table from a page, with fallback settings."""
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


def _find_roman_line(text: str, year: int, month: int) -> str | None:
    """Find the text line starting with '{year}.{ROMAN}' for the given month."""
    roman = INT_TO_ROMAN[month]
    target = f"{year}.{roman}"
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(rf"^{re.escape(target)}\b", stripped):
            return stripped
    return None


# ─── Dataset Extractors ───────────────────────────────────────────────────────


def extract_coal_production(pdf, year: int, month: int) -> pd.DataFrame | None:
    """
    Extract coal production/sales/export data (Table 3.17).

    Text rows: '{year}.{ROMAN}  production_kt  sales_kt  export_kt'
    Example:   '2025.III  7,987.8  4,921.5  3,897.0'

    Returns DataFrame: year, month, production_kt, sales_kt, export_kt
    """
    pages = find_pages_with_keyword(pdf, ["нүүрс", "3.17"])
    roman = INT_TO_ROMAN[month]
    target = f"{year}.{roman}"

    for pg_idx in pages:
        text = pdf.pages[pg_idx].extract_text() or ""
        line = _find_roman_line(text, year, month)
        if not line:
            continue
        # Strip the 'year.ROMAN' prefix before parsing numbers
        rest = line[len(target):].strip()
        nums = extract_price_nums(rest)
        if len(nums) >= 3:
            return pd.DataFrame([{
                "year": year, "month": month,
                "production_kt": nums[0],
                "sales_kt": nums[1],
                "export_kt": nums[2],
            }])
    return None


def extract_petroleum_production(pdf, year: int, month: int) -> pd.DataFrame | None:
    """
    Extract petroleum production/export data (Table 4.2).

    Text rows: '{year}.{ROMAN}  production_barrels  export_barrels'

    Returns DataFrame: year, month, production_barrels, export_barrels
    """
    pages = find_pages_with_keyword(pdf, ["газрын тосны олборлолт", "баррель"])
    roman = INT_TO_ROMAN[month]
    target = f"{year}.{roman}"

    for pg_idx in pages:
        text = pdf.pages[pg_idx].extract_text() or ""
        line = _find_roman_line(text, year, month)
        if not line:
            continue
        rest = line[len(target):].strip()
        nums = extract_price_nums(rest)
        if len(nums) >= 2:
            return pd.DataFrame([{
                "year": year, "month": month,
                "production_barrels": nums[0],
                "export_barrels": nums[1],
            }])
    return None


def extract_mining_permits(pdf, year: int, month: int) -> pd.DataFrame | None:
    """
    Extract mining permits by province (Table 1.1).

    Province names are in a left-side text column (x<150) separate from the
    bordered table. We align them to table rows by matching y-coordinates.

    Returns DataFrame: year, month, province, total_count, total_area_kha,
                       extraction_count, extraction_area_kha,
                       exploration_count, exploration_area_kha
    """
    pages = find_pages_with_keyword(pdf, ["тусгай зөвшөөрөл", "1.1", "хайгуулын"])
    if not pages:
        return None

    for pg_idx in pages:
        page = pdf.pages[pg_idx]

        # --- Step 1: extract province names from left text column ---
        words = page.extract_words()
        province_words: dict[float, str] = {}
        for w in words:
            if w["x0"] < 150 and w["top"] > 200:
                y = round(w["top"])
                existing = province_words.get(y, "")
                province_words[y] = (existing + " " + w["text"]).strip()

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

        data_rows = []
        for row in raw:
            nums = [to_float(c) for c in row if to_float(c) is not None]
            if len(nums) >= 4:
                data_rows.append(nums)

        if not data_rows or not province_ys:
            continue

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

    Text rows: '{commodity}  {unit}  {prev_price}  {curr_price}  {change%}'
    Unit tokens contain 'ам.долл' (USD). Current price = last non-% number.

    Returns DataFrame: year, month, commodity, price, unit
    """
    pages = find_pages_with_keyword(pdf, ["дэлхийн зах зээл", "3.8", "алт", "зэс"])
    if not pages:
        return None

    for pg_idx in pages:
        text = pdf.pages[pg_idx].extract_text() or ""
        rows_out = []

        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue

            # Data rows contain a USD unit token
            unit_match = re.search(r"ам\.долл\S*|\$\/\S+|USD\S*", stripped, re.IGNORECASE)
            if not unit_match:
                continue

            nums = extract_price_nums(stripped)
            if len(nums) < 2:
                continue

            # Commodity name = text before the unit token
            commodity = stripped[: unit_match.start()].strip()
            if not commodity:
                continue

            rows_out.append({
                "year": year,
                "month": month,
                "commodity": commodity,
                "price": nums[-1],  # last number = most recent (current month) price
                "unit": unit_match.group(0),
            })

        if rows_out:
            return pd.DataFrame(rows_out)

    return None


def extract_fuel_prices(pdf, year: int, month: int) -> pd.DataFrame | None:
    """
    Extract retail fuel prices by province (Table 4.6).

    Text rows: '{province}  prev_A80  curr_A80  prev_AI92  curr_AI92  prev_AI95  curr_AI95  prev_diesel  curr_diesel'
    Current prices sit at odd indices [1, 3, 5, 7] of the 8 non-% numbers.

    Some reports split 'УЛСЫН ДУНДАЖ' (national average) across two lines:
    province name on one line, numbers on the next. Handled via lookahead.

    Returns DataFrame: year, month, province, a80_price, ai92_price, ai95_price, diesel_price
    """
    pages = find_pages_with_keyword(pdf, ["шатахуун", "4.6", "бензин", "дизель"])
    if not pages:
        return None

    for pg_idx in pages:
        text = pdf.pages[pg_idx].extract_text() or ""
        rows_out = []
        lines = text.splitlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            starts_prov = any(line.startswith(p) for p in _PROV_PREFIXES)
            if not starts_prov:
                i += 1
                continue

            nums = extract_price_nums(line)

            # Handle split lines: province name only, numbers on next line
            if len(nums) < 6 and (i + 1) < len(lines):
                next_nums = extract_price_nums(lines[i + 1].strip())
                if len(next_nums) >= 6:
                    # Province name is current line (stripped of any trailing text)
                    province = re.sub(r"\s+[\d,.].*", "", line).strip() or line
                    nums = next_nums
                    i += 2
                else:
                    i += 1
                    continue
            elif len(nums) >= 6:
                # Province name + numbers on same line
                m = re.match(r"^([^\d]+)", line)
                province = m.group(1).strip() if m else line
                i += 1
            else:
                i += 1
                continue

            # Normalize national average label; skip region subtotals
            if province.upper().startswith("УЛСЫН"):
                province = "Улсын дундаж"
            if "бүс" in province.lower():
                continue  # skip region subtotals (Баруун бүс, Хангайн бүс, etc.)

            if len(nums) >= 8:
                rows_out.append({
                    "year": year, "month": month,
                    "province": province,
                    "a80_price": nums[1],
                    "ai92_price": nums[3],
                    "ai95_price": nums[5],
                    "diesel_price": nums[7],
                })
            elif len(nums) >= 6:
                # Some reports may lack A80 column
                rows_out.append({
                    "year": year, "month": month,
                    "province": province,
                    "a80_price": None,
                    "ai92_price": nums[1],
                    "ai95_price": nums[3],
                    "diesel_price": nums[5],
                })

        # The province table always has 20+ rows (21 aimags + UB + national avg).
        # Fewer rows means we matched a wrong page — keep searching.
        if len(rows_out) >= 20:
            return pd.DataFrame(rows_out)

    return None


def extract_petroleum_imports(pdf, year: int, month: int) -> pd.DataFrame | None:
    """
    Extract petroleum product imports (Table 4.3).

    Rows use '{year}.{ROMAN}' prefix (same as coal/petroleum production tables).
    2024+ columns: БҮГД, А-80, АИ-92, АИ-95, Дизель, Онгоцны (ТС-1), LPG, Бусад

    Returns DataFrame: year, month, product, volume_t
    """
    roman = INT_TO_ROMAN[month]
    target = f"{year}.{roman}"

    # Product names by position (Mongolian) — 2024+ format (8 cols including total)
    # Note: unit is tonnes (тонн), NOT thousand tonnes
    products_8 = [
        "Нийт", "А-80 бензин", "АИ-92 бензин", "АИ-95 бензин",
        "Дизелийн түлш", "Онгоцны түлш ТС-1", "Шингэрүүлсэн шатдаг хий", "Бусад",
    ]

    pages = find_pages_with_keyword(pdf, ["газрын тосны бүтээгдэхүүний импорт"])
    if not pages:
        return None

    for pg_idx in pages:
        text = pdf.pages[pg_idx].extract_text() or ""
        line = _find_roman_line(text, year, month)
        if not line:
            continue

        rest = line[len(target):].strip()
        nums = extract_price_nums(rest)
        if len(nums) < 2:
            continue

        products = products_8[:len(nums)]
        rows = [
            {"year": year, "month": month, "product": prod, "volume_t": vol}
            for prod, vol in zip(products, nums)
        ]
        return pd.DataFrame(rows)

    return None


def extract_budget_revenue(pdf, year: int, month: int) -> pd.DataFrame | None:
    """
    Extract state budget revenue from the mining sector (Table 5.1).

    Units are million MNT (сая төгрөгөөр), NOT billion.

    Format: revenue type name (may wrap across lines), then plan_mln actual_mln pct%
    Revenue types vary by year; we use generic parsing rather than hard-coded names.

    Returns DataFrame: year, month, revenue_type, plan_mln_mnt, actual_mln_mnt, pct_of_plan
    """
    pages = find_pages_with_keyword(pdf, ["улсын төсвийн орлог", "5.1", "гүйцэтгэл"])
    if not pages:
        return None

    for pg_idx in pages:
        text = pdf.pages[pg_idx].extract_text() or ""

        # Scope the text to just the 5.1 section
        m = re.search(r"5\.1\.", text)
        if not m:
            continue
        section = text[m.start():]
        end = re.search(r"5\.2\.|Эх сурвалж", section[10:])
        if end:
            section = section[: 10 + end.start()]

        lines = section.splitlines()

        # Skip header lines (find where data rows begin — after "Гүйцэтгэл"/"Биелэлт" header)
        data_start = 0
        for j, line in enumerate(lines):
            if "Гүйцэтгэл" in line or "Биелэлт" in line:
                data_start = j + 1
                break

        rows_out = []
        name_parts: list[str] = []
        # PDF layout quirk: when a name wraps, the tail of the name appears
        # AFTER the data numbers (not before). Detect this by checking whether
        # the data line starts with a digit (no inline name prefix).
        expect_tail = False  # True when next text-only line is tail of last row

        for line in lines[data_start:]:
            stripped = line.strip()
            if not stripped:
                continue

            nums = extract_price_nums(stripped)
            pct = extract_pct(stripped)

            if len(nums) >= 2:
                # Check if line has a text prefix (name + data on same line)
                m_prefix = re.match(r"^([^\d,]+)", stripped)
                prefix = m_prefix.group(1).strip() if m_prefix else ""
                # Avoid treating percentage / decimal artifacts as prefix
                if re.match(r"^[\d,.]", stripped):
                    prefix = ""

                if prefix:
                    name_parts.append(prefix)
                    expect_tail = False  # name ended inline, no tail needed
                else:
                    expect_tail = True   # data started with digit → tail follows

                revenue_type = " ".join(p for p in name_parts if p).strip()
                name_parts = []

                if revenue_type:
                    rows_out.append({
                        "year": year,
                        "month": month,
                        "revenue_type": revenue_type,
                        "plan_mln_mnt": nums[0],
                        "actual_mln_mnt": nums[1],
                        "pct_of_plan": pct,
                    })
            else:
                if expect_tail:
                    # This text-only line is the trailing part of the previous row's name
                    if rows_out:
                        rows_out[-1]["revenue_type"] = (
                            rows_out[-1]["revenue_type"] + " " + stripped
                        ).strip()
                    expect_tail = False
                elif stripped and not re.match(r"^[\d.]", stripped):
                    name_parts.append(stripped)

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

# Mongolian column name mappings (applied by save_bilingual to create -mn.csv)
MN_COLUMNS = {
    "mrpam-coal-production": {
        "year": "он", "month": "сар",
        "production_kt": "олборлолт_мян_тн",
        "sales_kt": "борлуулалт_мян_тн",
        "export_kt": "экспорт_мян_тн",
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
        "year": "он", "month": "сар",
        "commodity": "бараа", "price": "үнэ", "unit": "нэгж",
    },
    "mrpam-fuel-prices": {
        "year": "он", "month": "сар", "province": "аймаг",
        "a80_price": "а80_үнэ",
        "ai92_price": "аи92_үнэ",
        "ai95_price": "аи95_үнэ",
        "diesel_price": "дизель_үнэ",
    },
    "mrpam-petroleum-imports": {
        "year": "он", "month": "сар",
        "product": "бүтээгдэхүүн", "volume_t": "хэмжээ_тн",
    },
    "mrpam-budget-revenue": {
        "year": "он", "month": "сар",
        "revenue_type": "орлогын_төрөл",
        "plan_mln_mnt": "төлөвлөгөө_сая_төг",
        "actual_mln_mnt": "гүйцэтгэл_сая_төг",
        "pct_of_plan": "хувь",
    },
}


# ─── Core Logic ───────────────────────────────────────────────────────────────


def parse_year_month_from_filename(filename: str) -> tuple[int, int] | None:
    """
    Extract year and month from MRPAM PDF filename patterns:
      2025.1.stat.report.mon.pdf
      2025.01.stat.report.mon.pdf
      2021-01-mon.pdf
      2022-01.pdf
    """
    m = re.search(r"(\d{4})\.(\d{1,2})[.\-]", filename)
    if m:
        return int(m.group(1)), int(m.group(2))
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
    """Print page text and table counts for debugging."""
    print(f"\nDebugging: {pdf_path.name}")
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            tables = page.extract_tables()
            print(f"\n--- Page {i+1} ---")
            print(f"  Tables detected: {len(tables)}")
            print(f"  Text snippet: {text[:300].replace(chr(10), ' | ')}")
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
