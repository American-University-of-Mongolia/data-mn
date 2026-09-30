#!/usr/bin/env python3
"""
Check that year ranges in dataset page text match the data.

Page titles, excerpts and chart titles often carry a range like
"(2010-2025)". When a dataset is refreshed with newer data the range goes
stale ("2021-2025" on a page with 2026 data). This compares every
"YYYY-YYYY" range (hyphen or en dash) in the MDX title, excerpt and
VegaChart titles against the first and last year in the page's CSV.

Usage:
    python3 tools/scripts/validate_title_years.py            # report
    python3 tools/scripts/validate_title_years.py --fix      # rewrite ranges
    python3 tools/scripts/validate_title_years.py path/to/page.mdx

A range is only rewritten when its start year matches the data's first
year or its end year is within 2 years of the data's last year; anything
else (e.g. a range describing a sub-period in prose) is reported for a
human to review, never auto-edited.
"""

import argparse
import re
import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "data.mn"
CONTENT = SITE / "src/data/data"
RANGE = re.compile(r"(?<!\d)((?:19|20)\d{2})\s*([-–])\s*((?:19|20)\d{2})(?!\d)")
TIME_COLUMNS = re.compile(r"^(year|date|month|period|quarter|он|огноо|сар|хугацаа|үе|улирал)$", re.I)


def data_years(frontmatter: dict, page: Path):
    """(first, last) year in the page's CSV, or None if it has no time axis."""
    csvs = [f["path"] for f in frontmatter.get("dataFiles") or [] if str(f.get("path", "")).endswith(".csv")]
    if not csvs:
        return None
    path = SITE / "public" / csvs[0].lstrip("/")
    if not path.exists():
        return None
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig")
    col = next((c for c in df.columns if TIME_COLUMNS.match(c.strip())), None)
    if col is None:
        return None
    years = pd.to_numeric(df[col].str.extract(r"((?:19|20)\d{2})")[0], errors="coerce").dropna()
    return (int(years.min()), int(years.max())) if len(years) else None


def texts(page_text: str, frontmatter: dict):
    """(label, text) pairs for the page title, excerpt and chart titles."""
    for key in ("title", "excerpt"):
        if frontmatter.get(key):
            yield key, str(frontmatter[key])
    for m in re.finditer(r'<VegaChart[^>]*?\btitle="([^"]*)"', page_text, re.S):
        yield "chart title", m.group(1)


def check_page(page: Path, fix: bool):
    """Return list of (label, old_range, new_range_or_None) findings."""
    text = page.read_text()
    parts = text.split("---", 2)
    if len(parts) < 3:
        return []
    fm = yaml.safe_load(parts[1]) or {}
    span = data_years(fm, page)
    if not span:
        return []
    first, last = span
    findings, replacements = [], {}
    for label, value in texts(text, fm):
        for m in RANGE.finditer(value):
            start, dash, end = int(m.group(1)), m.group(2), int(m.group(3))
            if (start, end) == (first, last):
                continue
            covers_whole_series = start == first or 0 < last - end <= 2
            if covers_whole_series and end < last:
                new = f"{first}{dash}{last}"
                findings.append((label, m.group(0), new))
                replacements[m.group(0)] = new
            else:
                findings.append((label, m.group(0), None))
    if fix and replacements:
        # Rewrite only inside the title/excerpt lines and VegaChart titles,
        # never body prose.
        def sub_line(line):
            for old, new in replacements.items():
                line = line.replace(old, new)
            return line
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if re.match(r"^(title|excerpt):", line) or re.match(r'^\s*title="', line):
                lines[i] = sub_line(line)
        page.write_text("\n".join(lines))
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pages", nargs="*", help="MDX files (default: all data pages)")
    parser.add_argument("--fix", action="store_true", help="rewrite stale ranges that clearly span the series")
    args = parser.parse_args()

    pages = [Path(p) for p in args.pages] or sorted(CONTENT.glob("*/*.mdx"))
    stale = review = 0
    for page in pages:
        for label, old, new in check_page(page, args.fix):
            rel = page.relative_to(ROOT) if page.is_absolute() else page
            if new:
                stale += 1
                print(f"{'FIXED' if args.fix else 'STALE'}  {rel}  {label}: {old} -> {new}")
            else:
                review += 1
                print(f"REVIEW {rel}  {label}: {old} (data does not span this range)")
    print(f"\n{stale} stale range(s){' fixed' if args.fix else ''}, {review} to review")
    return 1 if stale and not args.fix else 0


if __name__ == "__main__":
    sys.exit(main())
