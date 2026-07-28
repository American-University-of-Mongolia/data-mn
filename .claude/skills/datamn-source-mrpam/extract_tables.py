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
from urllib.parse import unquote

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

_PROVINCE_MN_EN = {
    "Архангай": "Arkhangai", "Баян-Өлгий": "Bayan-Ulgii",
    "Баянхонгор": "Bayankhongor", "Булган": "Bulgan",
    "Говь-Алтай": "Govi-Altai", "Говьсүмбэр": "Govisumber",
    "Дархан-Уул": "Darkhan-Uul", "Дорноговь": "Dornogovi",
    "Дорнод": "Dornod", "Дундговь": "Dundgovi", "Завхан": "Zavkhan",
    "Орхон": "Orkhon", "Өвөрхангай": "Uvurkhangai",
    "Өмнөговь": "Umnugovi", "Сүхбаатар": "Sukhbaatar",
    "Сэлэнгэ": "Selenge", "Төв": "Tuv", "Увс": "Uvs",
    "Улаанбаатар": "Ulaanbaatar", "Улсын дундаж": "National average",
    "Ховд": "Khovd", "Хөвсгөл": "Khuvsgul", "Хэнтий": "Khentii",
}

_PROVINCE_EN_MN = {name_en: name_mn for name_mn, name_en in _PROVINCE_MN_EN.items()}
_PROVINCE_EN_MN.update({
    "Darkhan Uul": "Дархан-Уул",
    "Zavhan": "Завхан",
})

_COMMODITY_MN_EN = {
    "Алт": "Gold", "Мөнгө": "Silver", "Зэс": "Copper", "Цайр": "Zinc",
    "Хар тугалга": "Lead", "Цагаан тугалга": "Tin",
    "Молибдени": "Molybdenum", "Манган, 36%": "Manganese, 36%",
    "Гянтболд, 99%": "Tungsten, 99%", "Гянтболд, 65%": "Tungsten, 65%",
    "Төмөр, 56% хүдэр": "Iron ore, 56%",
    "Төмөр, 60% баяжмал": "Iron concentrate, 60%",
    "Жонш, баяжмал ФФ-97": "Fluorspar concentrate FF-97",
    "Жонш, хүдэр ФК-85": "Fluorspar ore FK-85", "Уран": "Uranium",
}

_COMMODITY_ALIASES_MN = {
    **{name: name for name in _COMMODITY_MN_EN},
    **{name_en: name_mn for name_mn, name_en in _COMMODITY_MN_EN.items()},
    # The August 2023 report is available only in English and uses these
    # source-specific labels.
    "Blue lead": "Хар тугалга",
    "Manganese 36%": "Манган, 36%",
    "Iron ore 56%": "Төмөр, 56% хүдэр",
    "Iron ore 60% concentrate": "Төмөр, 60% баяжмал",
    "Fluorite concentrate AG-97": "Жонш, баяжмал ФФ-97",
    "Fluorite ore MG-85": "Жонш, хүдэр ФК-85",
}

_UNIT_ALIASES_MN = {
    "ам.долл/унци": "ам.долл/унци",
    "$/ounce": "ам.долл/унци",
    "USD/troy oz": "ам.долл/унци",
    "ам.долл/тн": "ам.долл/тн",
    "$/tons": "ам.долл/тн",
    "USD/tonne": "ам.долл/тн",
    "ам.долл/кг": "ам.долл/кг",
    "$/kg": "ам.долл/кг",
    "USD/kg": "ам.долл/кг",
}

_PRODUCT_MN_EN = {
    "Нийт": "Total",
    "Автобензин А-80": "Gasoline A-80",
    "Автобензин АИ-92": "Gasoline AI-92",
    "АИ-92 /Евро-5/": "Gasoline AI-92 Euro-5",
    "Автобензин АИ-95": "Gasoline AI-95",
    "Автобензин АИ-98": "Gasoline AI-98",
    "Дизелийн түлш": "Diesel fuel", "Дизель /Евро-5/": "Diesel Euro-5",
    "Онгоцны түлш ТС-1": "Jet fuel TS-1",
    "Шингэрүүлсэн шатдаг хий": "Liquefied petroleum gas", "Бусад": "Other",
}

_REVENUE_MN_EN = {
    "БҮГД": "Total",
    "Ашигт малтмалын тусгай зөвшөөрлийн төлбөр": "Mineral licence fees",
    "Улсын төсвийн хөрөнгөөр хайгуул хийсэн ордын нөхөн төлбөр":
        "Reimbursement for state-funded exploration",
    "Газрын тосны экспорт": "Petroleum exports",
    "Бусад орлого": "Other revenue",
    "Сонгон шалгаруулалт": "Tender revenue",
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


def _normalize_province(value: str) -> str:
    """Return the canonical Mongolian province label used by data.mn."""
    value = re.sub(r"\s+\d[\d,.\s%]*$", "", clean_cell(value) or "")
    # The 2026 PDFs inconsistently substitute Latin A for Cyrillic А.
    value = value.replace("Говь-Aлтай", "Говь-Алтай")
    return value


def _row_words(page, prefix: str) -> list[dict] | None:
    """Return words on the same visual row as *prefix*.

    Coordinate extraction retains empty PDF table cells, unlike extract_text,
    and also captures values wrapped a few pixels below their logical row.
    """
    words = page.extract_words()
    for word in words:
        if word["text"] == prefix:
            top = word["top"]
            return [w for w in words if abs(w["top"] - top) <= 7]
    return None


def _value_in_x_band(words: list[dict], left: float, right: float) -> float | None:
    candidates = [w for w in words if left <= w["x0"] < right]
    if not candidates:
        return None
    # Wrapped values can share a band with a percentage. Prefer a plain number.
    for word in sorted(candidates, key=lambda w: abs(w["x0"] - (left + right) / 2)):
        if "%" not in word["text"]:
            return to_float(word["text"])
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
        # Other pages containing "нүүрс" can have the same year/month prefix
        # followed by additional commodity-price or stripping-volume values.
        # Table 3.16/3.17's monthly coal row has exactly three measures.
        if len(nums) == 3:
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
    pages = find_pages_with_keyword(
        pdf,
        [
            "газрын тосны олборлолт",
            "баррель",
            "petroleum production and export",
            "barrel",
        ],
    )
    roman = INT_TO_ROMAN[month]
    target = f"{year}.{roman}"

    for pg_idx in pages:
        text = pdf.pages[pg_idx].extract_text() or ""
        line = _find_roman_line(text, year, month)
        if not line:
            continue
        rest = line[len(target):].strip()
        nums = extract_price_nums(rest)
        if nums:
            return pd.DataFrame([{
                "year": year, "month": month,
                "production_barrels": nums[0],
                # Early-2022 reports use "-" while petroleum exports were
                # suspended. Preserve that source null instead of dropping the
                # otherwise valid production observation.
                "export_barrels": nums[1] if len(nums) >= 2 else None,
            }])
    return None


def extract_mining_permits(pdf, year: int, month: int) -> pd.DataFrame | None:
    """
    Extract mining permits by province (Table 1.1).

    The source reports area in thousand hectares (мян.га), not hectares.

    Returns DataFrame: year, month, province, total_count, total_area_kha,
                       extraction_count, extraction_area_kha,
                       exploration_count, exploration_area_kha
    """
    pages = find_pages_with_keyword(pdf, ["тусгай зөвшөөрөл", "1.1", "хайгуулын"])
    if not pages:
        # The August 2023 report is only available in English.
        pages = find_pages_with_keyword(
            pdf, ["valid licenses", "1.1", "exploration"]
        )
    if not pages:
        return None

    for pg_idx in pages:
        text = pdf.pages[pg_idx].extract_text() or ""
        rows_out = []
        for line in text.splitlines():
            stripped = line.strip()
            is_mongolian = any(stripped.startswith(p) for p in _PROV_PREFIXES)
            english_name = next(
                (
                    name
                    for name in sorted(_PROVINCE_EN_MN, key=len, reverse=True)
                    if stripped.startswith(f"{name} ")
                ),
                None,
            )
            if not is_mongolian and english_name is None:
                continue
            province_match = re.match(r"^(.+?)\s+(?=\d)", stripped)
            if not province_match:
                continue
            province = (
                _PROVINCE_EN_MN[english_name]
                if english_name is not None
                else _normalize_province(province_match.group(1))
            )
            if province not in _PROVINCE_MN_EN or province == "Улсын дундаж":
                continue
            nums = extract_price_nums(stripped[province_match.end():])
            # Percentages are skipped, leaving count/area for total, mining,
            # and exploration in source order.
            if len(nums) < 6:
                continue
            rows_out.append({
                "year": year,
                "month": month,
                "province": province,
                "total_count": int(nums[0]),
                "total_area_kha": nums[1],
                "extraction_count": int(nums[2]),
                "extraction_area_kha": nums[3],
                "exploration_count": int(nums[4]),
                "exploration_area_kha": nums[5],
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

            # The final cell before the percentage columns is the current
            # report-month price. Keep missing values as missing instead of
            # accidentally falling back to the preceding month's price.
            price_tokens = []
            for token in stripped[unit_match.end():].split():
                if "%" in token:
                    break
                price_tokens.append(token)
            if not price_tokens:
                continue
            current_price = to_float(price_tokens[-1])
            if current_price is None:
                continue

            # Commodity name = text before the unit token
            commodity = _COMMODITY_ALIASES_MN.get(
                stripped[: unit_match.start()].strip()
            )
            unit = _UNIT_ALIASES_MN.get(unit_match.group(0))
            if not commodity or not unit:
                continue

            rows_out.append({
                "year": year,
                "month": month,
                "commodity": commodity,
                "price": current_price,
                "unit": unit,
            })

        if rows_out:
            return pd.DataFrame(rows_out)

    return None


def extract_fuel_prices(pdf, year: int, month: int) -> pd.DataFrame | None:
    """
    Extract retail fuel prices by province (Table 4.6).

    Table 4.6 has five product groups with prior price, current price, and
    change. Coordinate bands preserve missing values represented by '-'.

    Returns current prices for AI-92, AI-92 Euro-5, AI-95, diesel, and diesel
    Euro-5 in MNT/litre.
    """
    pages = find_pages_with_keyword(
        pdf, ["4.6. ГАЗРЫН ТОСНЫ БҮТЭЭГДЭХҮҮНИЙ ЖИЖИГЛЭН"]
    )
    if not pages:
        return None

    for pg_idx in pages:
        page = pdf.pages[pg_idx]
        text = page.extract_text() or ""
        if "4.6." not in text:
            continue
        rows_out = []
        for province in _PROVINCE_MN_EN:
            if province == "Улсын дундаж":
                continue
            lookup = "Говь-Aлтай" if province == "Говь-Алтай" else province
            words = _row_words(page, lookup)
            if not words:
                continue
            rows_out.append({
                "year": year, "month": month, "province": province,
                "ai92_price": _value_in_x_band(words, 130, 165),
                "ai92_euro5_price": _value_in_x_band(words, 220, 255),
                "ai95_price": _value_in_x_band(words, 310, 340),
                "diesel_price": _value_in_x_band(words, 400, 430),
                "diesel_euro5_price": _value_in_x_band(words, 495, 530),
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
    The source schema changed twice:
      * through 2024: total, A-80, AI-92, AI-95, AI-98, diesel, jet, LPG, other
      * 2025 through 2026-01: the same schema without AI-98
      * from 2026-02: total, AI-92, AI-92 Euro-5, AI-95, diesel,
        diesel Euro-5, jet, LPG, other

    Values are read from fixed x-coordinate bands so a blank or dash remains a
    null in its product position instead of shifting every later product.

    Returns DataFrame: year, month, product, volume_t
    """
    roman = INT_TO_ROMAN[month]
    target = f"{year}.{roman}"

    pages = find_pages_with_keyword(
        pdf,
        ["газрын тосны бүтээгдэхүүний импорт", "petroleum products importing"],
    )
    if not pages:
        return None

    for pg_idx in pages:
        text = pdf.pages[pg_idx].extract_text() or ""
        page = pdf.pages[pg_idx]
        if "Евро-5" in text:
            products = [
                "Нийт", "Автобензин АИ-92", "АИ-92 /Евро-5/",
                "Автобензин АИ-95", "Дизелийн түлш", "Дизель /Евро-5/",
                "Онгоцны түлш ТС-1", "Шингэрүүлсэн шатдаг хий", "Бусад",
            ]
            bands = [
                (65, 125), (125, 185), (185, 240), (240, 300), (300, 360),
                (360, 420), (420, 480), (480, 525), (525, 580),
            ]
        elif not any("98" in line for line in text.splitlines()[:8]):
            products = [
                "Нийт", "Автобензин А-80", "Автобензин АИ-92",
                "Автобензин АИ-95", "Дизелийн түлш",
                "Онгоцны түлш ТС-1", "Шингэрүүлсэн шатдаг хий", "Бусад",
            ]
            bands = [
                (75, 135), (135, 195), (195, 250), (250, 310),
                (310, 375), (375, 425), (425, 475), (475, 530),
            ]
        else:
            products = [
                "Нийт", "Автобензин А-80", "Автобензин АИ-92",
                "Автобензин АИ-95", "Автобензин АИ-98",
                "Дизелийн түлш", "Онгоцны түлш ТС-1",
                "Шингэрүүлсэн шатдаг хий", "Бусад",
            ]
            bands = [
                (75, 135), (135, 195), (195, 250), (250, 310), (310, 360),
                (360, 415), (415, 465), (465, 510), (510, 565),
            ]

        # Most reports include an explicit dash for missing values, so the text
        # row is the clearest and most portable representation. The 2026-06
        # report omits its empty AI-95 cell entirely; in that case fall back to
        # coordinates to preserve the empty position.
        row_line = next(
            (
                line.strip()
                for line in text.splitlines()
                if re.match(rf"^{re.escape(target)}\s+", line.strip())
            ),
            None,
        )
        tokens = row_line.split()[1:] if row_line else []
        if len(tokens) == len(products):
            volumes = [to_float(token) for token in tokens]
        else:
            words = _row_words(page, target)
            if not words:
                continue
            volumes = [_value_in_x_band(words, left, right) for left, right in bands]
        rows = [
            {"year": year, "month": month, "product": prod, "volume_t": vol}
            for prod, vol in zip(products, volumes)
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
        "ai92_price": "аи92_үнэ",
        "ai92_euro5_price": "аи92_евро5_үнэ",
        "ai95_price": "аи95_үнэ",
        "diesel_price": "дизель_үнэ",
        "diesel_euro5_price": "дизель_евро5_үнэ",
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

CATEGORY_TRANSLATIONS = {
    "mrpam-mining-permits": {"province": _PROVINCE_MN_EN},
    "mrpam-commodity-prices": {
        "commodity": _COMMODITY_MN_EN,
        "unit": {
            "ам.долл/унци": "USD/troy oz", "ам.долл/тн": "USD/tonne",
            "ам.долл/кг": "USD/kg",
        },
    },
    "mrpam-fuel-prices": {"province": _PROVINCE_MN_EN},
    "mrpam-petroleum-imports": {"product": _PRODUCT_MN_EN},
    "mrpam-budget-revenue": {"revenue_type": _REVENUE_MN_EN},
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
    filename = unquote(filename)
    m = re.search(r"(?<!\d)(\d{4})[.\-_ ](\d{1,2})(?!\d)", filename)
    if m:
        year, month = int(m.group(1)), int(m.group(2))
        if 1 <= month <= 12:
            return year, month
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
    """Return one cached PDF per report month, sorted chronologically."""
    year_dir = (cache_dir or CACHE_DIR) / str(year)
    if not year_dir.exists():
        return []
    by_month: dict[int, Path] = {}
    for path in sorted(year_dir.glob("*.pdf")):
        parsed = parse_year_month_from_filename(path.name)
        if parsed and parsed[0] == year:
            # Prefer decoded local names when both legacy URL-encoded and
            # normalized cache entries exist.
            current = by_month.get(parsed[1])
            if current is None or ("%" in current.name and "%" not in path.name):
                by_month[parsed[1]] = path
    return [by_month[month] for month in sorted(by_month)]


def save_bilingual(df_en: pd.DataFrame, dataset_id: str, output_dir: Path):
    """Save bilingual CSVs, translating categorical values for English."""
    output_dir.mkdir(parents=True, exist_ok=True)

    col_map = MN_COLUMNS.get(dataset_id, {})
    # Extractors retain source-language categories. Preserve them in MN before
    # translating the English copy; numeric cells therefore remain identical.
    df_mn = df_en.rename(columns=col_map).copy()
    df_en = df_en.copy()
    for column, translations in CATEGORY_TRANSLATIONS.get(dataset_id, {}).items():
        if column in df_en:
            df_en[column] = df_en[column].map(
                lambda value: translations.get(value, value)
            )

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
