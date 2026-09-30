#!/usr/bin/env python3
"""
Check that year ranges in dataset page text match the data.

Page titles, excerpts and chart titles carry the span of the data, e.g.
"(2010-2025)", "from 2009 to 2025", "January 2016 to July 2026",
"Q1 2000 to Q4 2025" or "2016 оны 1-р сараас 2026 оны 7-р сар". When a
dataset is refreshed with newer data these go stale ("2021-2025" on a page
with 2026 data). This compares every span in the MDX title, excerpt,
VegaChart titles and the linked chart JSON titles against the first and
last period in the page's CSV. Month and quarter end points are compared
at month/quarter precision when the data has them.

Usage:
    python3 tools/scripts/validate_title_years.py            # report
    python3 tools/scripts/validate_title_years.py --fix      # rewrite spans
    python3 tools/scripts/validate_title_years.py path/to/page.mdx

A span is only rewritten when its start year matches the data's first
year or its end year is within 2 years of the data's last year; anything
else (e.g. a span describing a sub-period in prose) is reported for a
human to review, never auto-edited. Body prose is never touched.
"""

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "data.mn"
CONTENT = SITE / "src/data/data"
TIME_COLUMNS = re.compile(r"^(year|date|month|period|quarter|он|огноо|сар|хугацаа|үе|улирал)$", re.I)

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
Y = r"((?:19|20)\d{2})"
QUAL = r"(?:(Q[1-4]|" + "|".join(MONTHS) + r")\s+)?"
SPANS = [
    # 2010-2025, 2010–2025
    re.compile(rf"(?<!\d){Y}\s*[-–]\s*{Y}(?!\d)"),
    # 2021-25
    re.compile(rf"(?<!\d){Y}\s*[-–]\s*(\d{{2}})(?![\d-])"),
    # [Q1|January] 2010 to|through|until [Q4|July] 2025
    re.compile(rf"(?<![\w-]){QUAL}{Y}\s+(?:to|through|until)\s+{QUAL}{Y}(?!\d)"),
    # 2016 оны 1-р сараас 2026 оны 7-р сар / 2016 оноос 2026 оны 7-р сар /
    # 2000 оны 1-р улирлаас 2025 оны 4-р улирал
    re.compile(rf"(?<!\d){Y}\s+(?:оны\s+\d{{1,2}}(?:-р| дүгээр| дугаар)?\s+(?:сараас|улирлаас)|оноос)"
               rf"\s+{Y}(?:\s+оны\s+(\d{{1,2}})(?=(?:-р| дүгээр| дугаар)?\s+(сар|улирал)))?"),
]


def data_period(frontmatter: dict):
    """(first_year, last_year, last_month) of the page's CSV, or None.

    last_month is None when the time column has no month component.
    """
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
    parts = df[col].str.extract(r"((?:19|20)\d{2})(?:[-/.](\d{1,2})(?!\d)|\s*-?Q([1-4]))?")
    years = pd.to_numeric(parts[0], errors="coerce")
    months = pd.to_numeric(parts[1], errors="coerce")
    months = months.fillna(pd.to_numeric(parts[2], errors="coerce") * 3)
    valid = years.notna()
    if not valid.any():
        return None
    periods = (years * 100 + months.fillna(0))[valid]
    last = int(periods.max())
    has_month = months[valid].notna().all()
    return int(years[valid].min()), last // 100, (last % 100 if has_month else None)


def data_years(frontmatter: dict, page: Path = None):
    """(first, last) year in the page's CSV, or None if it has no time axis."""
    period = data_period(frontmatter)
    return period[:2] if period else None


def spans(value: str):
    """Yield (match, start_year, end_year, end_qualifier, end_month, end_text) per span."""
    seen = set()
    for i, pattern in enumerate(SPANS):
        for m in pattern.finditer(value):
            if any(a < m.end() and m.start() < b for a, b in seen):
                continue
            seen.add((m.start(), m.end()))
            if i == 0:
                yield m, int(m.group(1)), int(m.group(2)), None, None, m.group(2)
            elif i == 1:
                end = int(m.group(1)[:2] + m.group(2))
                if end > int(m.group(1)):
                    yield m, int(m.group(1)), end, None, None, m.group(2)
            elif i == 2:
                qual = m.group(3)
                month = (MONTHS.index(qual) + 1) if qual in MONTHS else (int(qual[1]) * 3 if qual else None)
                end_text = f"{qual} {m.group(4)}" if qual else m.group(4)
                yield m, int(m.group(2)), int(m.group(4)), qual, month, end_text
            else:
                quarter = m.group(4) == "улирал"
                month = (int(m.group(3)) * (3 if quarter else 1)) if m.group(3) else None
                end_text = m.group(0)[m.start(2) - m.start():]
                yield m, int(m.group(1)), int(m.group(2)), ("mnq" if quarter else "mn") if month else None, month, end_text


def new_end(qual, last_year, last_month, end_text):
    """Replacement for a stale end point, keeping its style."""
    if qual is None:
        return str(last_year)[-len(end_text):] if len(end_text) == 2 else str(last_year)
    if qual in ("mn", "mnq"):
        n = (last_month + 2) // 3 if qual == "mnq" else last_month
        return re.sub(r"^\d{4}(\s+оны\s+)\d{1,2}", rf"{last_year}\g<1>{n}", end_text)
    if qual.startswith("Q"):
        return f"Q{(last_month + 2) // 3} {last_year}"
    return f"{MONTHS[last_month - 1]} {last_year}"


def texts(page_text: str, frontmatter: dict):
    """(label, text) pairs for the page title, excerpt and chart titles."""
    for key in ("title", "excerpt"):
        if frontmatter.get(key):
            yield key, str(frontmatter[key])
    for m in re.finditer(r'<VegaChart[^>]*?\btitle="([^"]*)"', page_text, re.S):
        yield "chart title", m.group(1)


def chart_files(page_text: str):
    for m in re.finditer(r'\bspec="(/charts/[^"]+\.json)"', page_text):
        path = SITE / "public" / m.group(1).lstrip("/")
        if path.exists():
            yield path


def chart_title_texts(spec):
    """Title and subtitle strings of a Vega-Lite spec."""
    title = spec.get("title") if isinstance(spec, dict) else None
    if isinstance(title, str):
        yield title
    elif isinstance(title, dict):
        for key in ("text", "subtitle"):
            value = title.get(key)
            for v in (value if isinstance(value, list) else [value]):
                if isinstance(v, str):
                    yield v


def find(label, value, period, findings, replacements):
    first, last_year, last_month = period
    for m, start, end, qual, month, end_text in spans(value):
        if qual and last_month is None:
            continue  # "July 2025" against annual data: can't judge the month
        end_key = end * 100 + (month or 0)
        quarterly = qual in ("mnq",) or (qual or "").startswith("Q")
        # Quarter spans compare at quarter precision (Q2 may be dated April or June).
        last_cmp = ((last_month + 2) // 3 * 3) if quarterly else last_month
        last_key = last_year * 100 + (last_cmp if qual else 0)
        if start == first and end_key == last_key:
            continue
        if start >= first and end_key == last_key:
            continue  # sub-period that ends at the latest data
        covers_whole_series = start == first or 0 <= last_year - end <= 2
        if covers_whole_series and end_key < last_key:
            new_text = new_end(qual, last_year, last_month, end_text)
            new = m.group(0)[:len(m.group(0)) - len(end_text)] + new_text
            findings.append((label, m.group(0), new))
            replacements[m.group(0)] = new
        else:
            findings.append((label, m.group(0), None))


def check_page(page: Path, fix: bool):
    """Return list of (label, old_span, new_span_or_None) findings."""
    text = page.read_text()
    parts = text.split("---", 2)
    if len(parts) < 3:
        return []
    fm = yaml.safe_load(parts[1]) or {}
    period = data_period(fm)
    if not period:
        return []
    findings, replacements = [], {}
    for label, value in texts(text, fm):
        find(label, value, period, findings, replacements)
    chart_replacements = {}
    for chart in chart_files(text):
        spec = json.loads(chart.read_text())
        chart_replacements[chart] = {}
        for value in chart_title_texts(spec):
            find(f"chart json {chart.name}", value, period, findings, chart_replacements[chart])

    if fix:
        # Rewrite only the title/excerpt lines and VegaChart titles, never
        # body prose; in chart JSON only the "title"/"subtitle" strings.
        def sub_line(line, reps):
            for old, new in reps.items():
                line = line.replace(old, new)
            return line
        if replacements:
            lines = text.split("\n")
            for i, line in enumerate(lines):
                if re.match(r"^(title|excerpt):", line) or re.match(r'^\s*title="', line):
                    lines[i] = sub_line(line, replacements)
            page.write_text("\n".join(lines))
        for chart, reps in chart_replacements.items():
            if reps:
                raw = chart.read_text()
                raw = re.sub(r'("(?:title|text|subtitle)"\s*:\s*)"((?:[^"\\]|\\.)*)"',
                             lambda m: m.group(1) + '"' + sub_line(m.group(2), reps) + '"', raw)
                chart.write_text(raw)
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pages", nargs="*", help="MDX files (default: all data pages)")
    parser.add_argument("--fix", action="store_true", help="rewrite stale spans that clearly cover the series")
    args = parser.parse_args()

    pages = [Path(p) for p in args.pages] or sorted(CONTENT.glob("*/*.mdx"))
    stale = review = 0
    for page in pages:
        for label, old, new in check_page(page, args.fix):
            rel = page.resolve().relative_to(ROOT)
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
