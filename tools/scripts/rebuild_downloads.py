#!/usr/bin/env python3
"""Rebuild download files to the 2-file bilingual standard (Standard 1 + 2).

Per dataset this script:
  1. Resolves the canonical long CSV per language (`-all-` if present, else plain)
     and asserts it is LONG form (fails closed -> manual queue otherwise).
  2. Pivots EN + MN long data to wide form and writes ONE bilingual XLSX
     (sheets "English" first, "Монгол" second; freeze top row, auto-width).
  3. Rewrites MDX `dataFiles` to exactly 2 entries (CSV + XLSX).
  4. Asserts content equivalence (pivot totals match CSV totals, EN<->MN aligned).

Nothing is written unless --apply is passed. Any failed assert routes the
dataset to the manual queue instead of writing. This script is the ONLY writer
of download files during the standards rollout (Wave 1 workers run it).

Usage:
    python tools/scripts/rebuild_downloads.py --dataset {id} [--apply]
    python tools/scripts/rebuild_downloads.py --all [--apply] [--report PATH]
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path

import pandas as pd
import yaml
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[2]
DATASETS = ROOT / "data.mn" / "public" / "datasets"
CHARTS = ROOT / "data.mn" / "public" / "charts"
MDX_EN = ROOT / "data.mn" / "src" / "data" / "data" / "en"
MDX_MN = ROOT / "data.mn" / "src" / "data" / "data" / "mn"

EN_SHEET = "English"
MN_SHEET = "Монгол"

TIME_NAMES_EN = {
    "year", "years", "month", "months", "date", "dates", "day", "days",
    "time", "week", "weeks", "quarter", "quarters",
}
TIME_NAMES_MN = {"он", "жил", "сар", "улирал", "өдөр", "огноо", "долоо хоног", "цаг"}
TIME_NAMES = TIME_NAMES_EN | TIME_NAMES_MN

# Timeless datasets exempt from the wide-XLSX rule (still get bilingual sheets).
EXEMPT_WIDE = {
    "gdp-by-sector",
    "health-facilities-by-aimag",
    "health-facilities-by-type",
    "hospital-beds-by-type",
    "population-pyramid-mongolia",
    "salary-by-sector-2024",
}

EXEMPT_WIDE_REASONS = {
    "gdp-by-sector": "single-year snapshot, no time dimension to pivot",
    "health-facilities-by-aimag": "cross-sectional count by aimag, no time dimension",
    "health-facilities-by-type": "cross-sectional count by facility type, no time dimension",
    "hospital-beds-by-type": "cross-sectional count by bed type, no time dimension",
    "population-pyramid-mongolia": "single-year age/sex pyramid, no time dimension",
    "salary-by-sector-2024": "single-year snapshot, no time dimension to pivot",
}

# Reference tables (boundary lists, codebooks): timeless by definition and
# multi-attribute by nature (codes, names, parents, areas, coordinates), so
# the single-value-column long-form rule cannot apply. Sheets stay long;
# structural = text columns only (numeric headers such as lon/lat are
# conventionally Latin in both languages). Adding a new id requires a
# reason string here; the validator shares the same list.
REFERENCE_TABLES = {
    "ebarilga-districts",
    "ebarilga-khoroos",
    "ebarilga-zip-zones",
}

REFERENCE_TABLES_REASONS = {
    "ebarilga-districts": "boundary reference table: codes, names, khoroo counts, areas",
    "ebarilga-khoroos": "boundary reference table: codes, names, parent districts, areas",
    "ebarilga-zip-zones": "boundary reference table: codes, names, parent districts, areas",
}

CYRILLIC = re.compile(r"[\u0400-\u04FF]")


def has_cyrillic(text):
    return bool(CYRILLIC.search(str(text)))


def drop_constant_dims(df):
    """Drop degenerate dimensions: constant object columns (e.g. a unit or
    product column with a single value). Never drops the time column or
    numeric columns. Returns (frame, dropped_names)."""
    const_cols = [c for c in df.columns
                  if df[c].dtype == object and df[c].nunique() <= 1
                  and str(c).strip().lower() not in TIME_NAMES]
    if const_cols:
        return df.drop(columns=const_cols), const_cols
    return df, []


def detect_roles(df, dataset_id=None):
    """Return (time_col, category_col, value_col, problem).

    problem is None when the frame is usable long form (or single series /
    cross-sectional / reference table); otherwise a human-readable reason
    for manual review.
    """
    cols = list(df.columns)
    if dataset_id in REFERENCE_TABLES:
        named_time = [c for c in cols if str(c).strip().lower() in TIME_NAMES]
        if named_time:
            return None, None, None, (
                f"reference table must not have a time column: {named_time}")
        objects = [c for c in cols
                   if not pd.api.types.is_numeric_dtype(df[c])]
        numerics = [c for c in cols
                    if pd.api.types.is_numeric_dtype(df[c])]
        if not objects:
            return None, None, None, "reference table has no text columns"
        if not numerics:
            return None, None, None, "no numeric value column"
        return None, None, numerics[0], None
    named_time = [c for c in cols if str(c).strip().lower() in TIME_NAMES]
    if len(named_time) > 1:
        return None, None, None, f"multiple time dimensions: {named_time}"
    time = named_time[0] if named_time else None
    if time is None:
        # Content fallback: int column in year range, or mostly-parseable
        # dates. Never steal the sole numeric column (that is the value).
        numeric_all = [c for c in cols if pd.api.types.is_numeric_dtype(df[c])]
        ranged = []
        for c in cols:
            s = df[c].dropna()
            if len(s) == 0 or (c in numeric_all and len(numeric_all) == 1):
                continue
            if pd.api.types.is_integer_dtype(s) and s.between(1900, 2100).all():
                ranged.append(c)
                continue
            if s.dtype == object:
                try:
                    parsed = pd.to_datetime(s, format="mixed", errors="coerce")
                except Exception:
                    continue
                if parsed.notna().mean() > 0.9:
                    time = c
                    break
        if time is None and ranged:
            # Years repeat (fewer uniques) while values vary.
            time = min(ranged, key=lambda c: df[c].nunique())
    # The time column is a dimension, never a value column.
    numeric = [c for c in cols
               if c != time and pd.api.types.is_numeric_dtype(df[c])]
    if len(numeric) == 0:
        return None, None, None, "no numeric value column"
    if len(numeric) > 1:
        if time is not None and df[time].nunique() == len(df):
            return None, None, None, (
                f"wide-form CSV: unique time column + {len(numeric)} value columns"
            )
        return None, None, None, f"multiple numeric columns: {numeric}"
    value = numeric[0]
    rest = [c for c in cols if c != time and c != value]
    if time is None:
        if len(numeric) == 1 and 1 <= len(rest) <= 2:
            # Cross-sectional (exempt ids only; caller enforces): sheets stay
            # long, so multiple object dimensions are fine.
            return None, rest[0] if len(rest) == 1 else None, value, None
        return None, None, None, "no time column and not cross-sectional"
    if len(rest) == 0:
        return time, None, value, None  # single series
    if len(rest) == 1:
        return time, rest[0], value, None
    return None, None, None, f"multiple category columns: {rest}"


def pivot_long(df, time, cat, value):
    """Pivot long data to wide (time rows x category columns)."""
    wide = df.pivot_table(index=time, columns=cat, values=value, aggfunc="first")
    wide = wide.reset_index()
    wide.columns.name = None
    return wide


def allows_timeless(dataset_id):
    """True when a timeless frame is a known kind (exempt or reference)."""
    return dataset_id in EXEMPT_WIDE or dataset_id in REFERENCE_TABLES


def structural_cols(df, roles, dataset_id):
    """Columns whose headers must be in the page language.

    Single home for the per-kind rule (imported by the validator, so a
    new kind changes this file only): time-series frames check the time
    (+ category) headers; cross-sectional frames check every non-value
    column; reference tables check text columns only.
    """
    time, cat, value = roles
    if time is None and dataset_id in REFERENCE_TABLES:
        return [c for c in df.columns
                if not pd.api.types.is_numeric_dtype(df[c])]
    if time is None:
        return [c for c in df.columns if c != value]
    return [c for c in (time, cat) if c is not None]


def check_structural_language(struct_cols, lang):
    """Structural headers must be in the page language.

    Value headers may carry unit codes, so only structural headers are
    checked. For timeless frames this is every non-value column.
    Returns a problem string or None.
    """
    if lang == "mn":
        bad = [c for c in struct_cols if not has_cyrillic(c)]
        if bad:
            return f"MN structural headers not Mongolian: {bad}"
    else:
        bad = [c for c in struct_cols if has_cyrillic(c)]
        if bad:
            return f"EN structural headers not English: {bad}"
    return None


def value_total(df, time_col):
    """Sum of numeric value columns, excluding the time dimension."""
    nums = [df[c].sum(skipna=True) for c in df.columns
            if c != time_col and pd.api.types.is_numeric_dtype(df[c])]
    return sum(float(v) for v in nums)


def fuzzy_value_total(df):
    """Value total for a frame of unknown orientation (current XLSX).

    Skips numeric columns named like time dimensions, plus a year-ranged
    integer first column (unnamed time). Headers are never summed, so
    transposed layouts (years across the top) compare correctly.
    """
    total = 0.0
    cols = list(df.columns)
    for i, c in enumerate(cols):
        if not pd.api.types.is_numeric_dtype(df[c]):
            continue
        if str(c).strip().lower() in TIME_NAMES:
            continue
        s = df[c].dropna()
        if (i == 0 and len(s)
                and pd.api.types.is_integer_dtype(s)
                and s.between(1900, 2100).all()):
            continue
        total += float(df[c].sum(skipna=True))
    return total


def read_current_xlsx(path):
    """Read the current XLSX (first sheet) for content comparison."""
    try:
        return pd.read_excel(path, sheet_name=0)
    except Exception:
        return None


def compare_xlsx_content(current, csv_total_en):
    """Orientation-agnostic content check: numeric total must match the CSV.

    Returns a problem string or None. Totals are invariant under transpose /
    pivot, so this catches content drift regardless of the current layout.
    """
    if current is None:
        return "current XLSX unreadable"
    xlsx_total = fuzzy_value_total(current)
    if not math.isclose(xlsx_total, csv_total_en, rel_tol=1e-6, abs_tol=1e-6):
        return (f"XLSX content mismatch: xlsx total {xlsx_total:.4g} != "
                f"CSV total {csv_total_en:.4g}")
    return None


def write_bilingual_xlsx(path, en_sheet, mn_sheet):
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        en_sheet.to_excel(writer, index=False, sheet_name=EN_SHEET)
        mn_sheet.to_excel(writer, index=False, sheet_name=MN_SHEET)
        for sheet_name, sheet_df in ((EN_SHEET, en_sheet), (MN_SHEET, mn_sheet)):
            ws = writer.sheets[sheet_name]
            ws.freeze_panes = "A2"
            for idx, col in enumerate(sheet_df.columns):
                # fillna AFTER astype(str): pandas 3 keeps NaN as missing
                # through astype(str), and len() would crash on it.
                str_vals = sheet_df[col].astype(str).fillna("")
                longest = str_vals.map(len).max()
                width = max(longest if pd.notna(longest) else 0,
                            len(str(col))) + 2
                ws.column_dimensions[get_column_letter(idx + 1)].width = min(
                    width, 30)


def kb_size(path):
    return max(1, path.stat().st_size // 1024)


def rewrite_mdx_datafiles(mdx_path, csv_name, xlsx_name, lang):
    """Replace ONLY the dataFiles block; returns True if the text changed."""
    text = mdx_path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        raise ValueError(f"{mdx_path}: frontmatter not found")
    frontmatter, body = m.group(1), m.group(2)
    meta = yaml.safe_load(frontmatter) or {}
    old_files = meta.get("dataFiles") or []
    xlsx_desc = next((f.get("description") for f in old_files
                      if str(f.get("format", "")).lower() in ("xlsx", "xls")
                      and f.get("description")), None)
    if xlsx_desc is None:
        xlsx_desc = "Open in Excel" if lang == "en" else "Excel-д нээх"
    csv_desc = "Download as CSV" if lang == "en" else "CSV татах"
    new_block = (
        "dataFiles:\n"
        f"  - path: \"/datasets/{csv_name}\"\n"
        "    format: \"csv\"\n"
        f"    size: \"{kb_size(DATASETS / csv_name)} KB\"\n"
        f"    description: \"{csv_desc}\"\n"
        f"  - path: \"/datasets/{xlsx_name}\"\n"
        "    format: \"xlsx\"\n"
        f"    size: \"{kb_size(DATASETS / xlsx_name)} KB\"\n"
        f"    description: \"{xlsx_desc}\"\n"
    )
    lines = frontmatter.split("\n")
    try:
        start = next(i for i, line in enumerate(lines)
                     if line.startswith("dataFiles:"))
    except StopIteration:
        raise ValueError(f"{mdx_path}: no dataFiles block")
    def is_list_item(line):
        return (line.startswith("- ") or line.startswith("-\t")
                or line.strip() == "-")

    end = start + 1
    # Consume indented lines AND column-0 list items: some files author
    # sequences unindented (`dataFiles:\n- path: ...`), which is valid YAML.
    # The next mapping key never starts with "- ", so this cannot overrun.
    while end < len(lines) and (lines[end].startswith((" ", "\t"))
                                or lines[end].strip() == ""
                                or is_list_item(lines[end])):
        end += 1
    new_frontmatter = "\n".join(lines[:start] + [new_block.rstrip("\n")]
                                + lines[end:])
    new_text = f"---\n{new_frontmatter}\n---\n{body}"
    if new_text != text:
        mdx_path.write_text(new_text)
        return True
    return False


def spec_uses_file(dataset_id, filename):
    """True if any chart spec for the dataset references the file."""
    for spec in CHARTS.glob(f"{dataset_id}-*.json"):
        try:
            text = spec.read_text()
        except OSError:
            continue
        if filename in text:
            return True
    return False


def canonical_csv(dataset_id, lang):
    """The download CSV: `-all-` when present, else plain."""
    all_name = f"{dataset_id}-all-{lang}.csv"
    if (DATASETS / all_name).exists():
        return all_name
    return f"{dataset_id}-{lang}.csv"


def process_dataset(dataset_id, apply=False):
    """Dry-run (or apply) the rebuild for one dataset. Returns a report dict."""
    report = {"id": dataset_id, "queue": "auto", "reasons": [],
              "actions": [], "deletes": []}

    def manual(reason):
        report["queue"] = "manual"
        report["reasons"].append(reason)

    mdx = {"en": MDX_EN / f"{dataset_id}.mdx", "mn": MDX_MN / f"{dataset_id}.mdx"}
    for lang, path in mdx.items():
        if not path.exists():
            manual(f"missing {lang.upper()} MDX page")
    csv_name = {lang: canonical_csv(dataset_id, lang) for lang in ("en", "mn")}
    dfs, roles = {}, {}
    for lang in ("en", "mn"):
        path = DATASETS / csv_name[lang]
        if not path.exists():
            manual(f"missing CSV file {csv_name[lang]}")
            continue
        try:
            dfs[lang] = pd.read_csv(path, encoding="utf-8-sig")
        except Exception as e:
            manual(f"unreadable CSV {csv_name[lang]}: {e}")
            continue
        dfs[lang].columns = [str(c).replace("\ufeff", "") for c in dfs[lang].columns]
        df, const_cols = drop_constant_dims(dfs[lang])
        if const_cols:
            report["actions"].append(
                f"{csv_name[lang]}: ignoring constant column(s) {const_cols} "
                f"for the XLSX pivot (CSV file itself unchanged)")
            dfs[lang] = df
        time, cat, value, problem = detect_roles(df, dataset_id)
        roles[lang] = (time, cat, value)
        if problem:
            manual(f"{csv_name[lang]}: {problem}")
            continue
        if time is None and not allows_timeless(dataset_id):
            manual(f"{csv_name[lang]}: no time dimension "
                   f"(exempt-worthy? not on the exempt list)")
            continue
        struct = structural_cols(df, (time, cat, value), dataset_id)
        lang_problem = check_structural_language(struct, lang)
        if lang_problem:
            manual(f"{csv_name[lang]}: {lang_problem}")
    if report["queue"] == "manual":
        return report

    # Pivot (or keep long sheets when there is no category dimension).
    sheets = {}
    for lang in ("en", "mn"):
        time, cat, value = roles[lang]
        df = dfs[lang]
        if time is None or cat is None:
            # Cross-sectional (exempt) or single series: sheets stay long.
            sheets[lang] = df.copy()
        else:
            if df.duplicated(subset=[time, cat]).any():
                manual(f"{csv_name[lang]}: duplicate time x category rows")
                return report
            wide = pivot_long(df, time, cat, value)
            if not math.isclose(value_total(wide, time), value_total(df, time),
                                rel_tol=1e-9, abs_tol=1e-9):
                manual(f"{csv_name[lang]}: pivot total mismatch")
                return report
            sheets[lang] = wide
    en_shape, mn_shape = sheets["en"].shape, sheets["mn"].shape
    if en_shape != mn_shape:
        manual(f"EN/MN shape mismatch: EN {en_shape} vs MN {mn_shape}")
        return report
    if not math.isclose(value_total(sheets["en"], roles["en"][0]),
                        value_total(sheets["mn"], roles["mn"][0]),
                        rel_tol=1e-9, abs_tol=1e-9):
        manual("EN/MN numeric totals differ")
        return report
    time_en = roles["en"][0]
    if time_en is not None:
        years_en = sheets["en"].iloc[:, 0].astype(str).tolist()
        years_mn = sheets["mn"].iloc[:, 0].astype(str).tolist()
        if years_en != years_mn:
            manual("EN/MN time vectors differ")
            return report

    xlsx_name = f"{dataset_id}.xlsx"
    xlsx_path = DATASETS / xlsx_name
    if xlsx_path.exists():
        current = read_current_xlsx(xlsx_path)
        mismatch = compare_xlsx_content(
            current, value_total(dfs["en"], roles["en"][0]))
        if mismatch:
            # Maybe the XLSX was built from the plain (subset) CSV while the
            # canonical download is -all-: verify, then auto-rebuild from -all-.
            plain_name = f"{dataset_id}-en.csv"
            if csv_name["en"] != plain_name and (DATASETS / plain_name).exists():
                try:
                    plain_df = pd.read_csv(DATASETS / plain_name,
                                           encoding="utf-8-sig")
                    plain_df.columns = [str(c).replace("\ufeff", "")
                                        for c in plain_df.columns]
                    ptime = next((c for c in plain_df.columns
                                  if str(c).strip().lower() in TIME_NAMES),
                                 None)
                    if math.isclose(fuzzy_value_total(current),
                                    value_total(plain_df, ptime),
                                    rel_tol=1e-6, abs_tol=1e-6):
                        mismatch = None
                        report["actions"].append(
                            f"{xlsx_name} was subset-built from {plain_name}; "
                            f"rebuilding from {csv_name['en']}")
                except Exception:
                    pass
        if mismatch:
            manual(f"{xlsx_name}: {mismatch}")
            return report
    else:
        report["actions"].append(f"create {xlsx_name} (missing today)")

    # Deletion candidates: plain CSV superseded by -all- and unreferenced.
    for lang in ("en", "mn"):
        plain = f"{dataset_id}-{lang}.csv"
        if (csv_name[lang] != plain and (DATASETS / plain).exists()
                and not spec_uses_file(dataset_id, plain)):
            report["deletes"].append(plain)

    if report["queue"] == "manual":
        return report
    report["actions"].append(
        f"rebuild {xlsx_name} ({EN_SHEET} + {MN_SHEET} sheets, "
        f"{sheets['en'].shape[0]} rows x {sheets['en'].shape[1]} cols)")
    for lang in ("en", "mn"):
        report["actions"].append(
            f"rewrite {mdx[lang].name} dataFiles -> "
            f"{csv_name[lang]} + {xlsx_name}")
    if apply:
        write_bilingual_xlsx(xlsx_path, sheets["en"], sheets["mn"])
        for lang in ("en", "mn"):
            rewrite_mdx_datafiles(mdx[lang], csv_name[lang], xlsx_name, lang)
    return report


def discover_datasets():
    return sorted(p.stem for p in MDX_EN.glob("*.mdx"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dataset", help="single dataset id")
    group.add_argument("--all", action="store_true", help="all datasets")
    parser.add_argument("--apply", action="store_true",
                        help="write files (default is dry-run)")
    parser.add_argument("--report", help="write JSON report to PATH")
    args = parser.parse_args()

    ids = [args.dataset] if args.dataset else discover_datasets()
    reports = [process_dataset(i, apply=args.apply) for i in ids]
    summary = {
        "mode": "apply" if args.apply else "dry-run",
        "total": len(reports),
        "auto": sum(1 for r in reports if r["queue"] == "auto"),
        "manual": sum(1 for r in reports if r["queue"] == "manual"),
        "reports": reports,
    }
    out = json.dumps(summary, indent=2, ensure_ascii=False)
    if args.report:
        Path(args.report).write_text(out)
    else:
        print(out)
    if args.apply and summary["manual"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

