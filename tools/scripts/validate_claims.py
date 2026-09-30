#!/usr/bin/env python3
"""
Check numeric claims in dataset page text against the data.

Excerpts and page prose quote values tied to a period: "154,294 vehicles
in 2024", "net IIP stood at -45,715 million USD in Q2 2026", "2026 оны 7
сард 5,631 тэрбум төгрөг". After a refresh these go stale (the sentence
still describes 2024 when the data reaches 2025) or wrong (the number no
longer matches the revised data). For every number paired with a period in
the excerpt and body prose this reports:

  STALE     the sentence's latest period is older than the data's latest
            period (within 2 years of it) and it isn't a historical claim
            ("peaked at X in 2024" is fine)
  MISMATCH  the data has rows for that period but no value that rounds to
            the quoted number (unit words and billion/million scaling are
            tried; "over", "nearly", "about" widen the tolerance)

Percentages, ratios ("4-fold") and small unitless counts are not value-
checked: they are usually derived, not in the CSV.

Usage:
    python3 tools/scripts/validate_claims.py                 # all pages
    python3 tools/scripts/validate_claims.py path/to/page.mdx

Exit 1 if any STALE or MISMATCH finding. There is no --fix: rewrite the
sentence from the CSV (see /data-update step 3.1b).
"""

import argparse
import math
import re
import sys
from pathlib import Path

import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_title_years import CONTENT, MONTHS, ROOT, SITE, TIME_COLUMNS, spans  # noqa: E402

UNITS = {
    "thousand": 1e3, "million": 1e6, "billion": 1e9, "trillion": 1e12,
    "мянга": 1e3, "мянган": 1e3, "сая": 1e6, "тэрбум": 1e9, "их наяд": 1e12,
}
NUMBER = re.compile(
    r"(?<![\w.,/-])(-?\d{1,3}(?:,\d{3})+(?:\.\d+)?|-?\d+(?:\.\d+)?)"
    r"(\s*(?:%|-fold|x\b|times\b)|\s+(?:" + "|".join(sorted(UNITS, key=len, reverse=True)) + r")\b)?",
    re.I,
)
YEAR = r"((?:19|20)\d{2})"
PERIODS = [
    # Q2 2026
    (re.compile(rf"\bQ([1-4])\s+{YEAR}\b"), lambda m: (int(m.group(2)), "q", int(m.group(1)))),
    # February 2026
    (re.compile(rf"\b({'|'.join(MONTHS)})\s+{YEAR}\b"),
     lambda m: (int(m.group(2)), "m", MONTHS.index(m.group(1)) + 1)),
    # 2025 оны 3-р улирал / 2026 оны 7 сард
    (re.compile(rf"(?<!\d){YEAR}\s+оны\s+(\d{{1,2}})(?:-р| дүгээр| дугаар)?\s+(улирал|сар)"),
     lambda m: (int(m.group(1)), "q" if m.group(3) == "улирал" else "m", int(m.group(2)))),
    # 2025
    # 2026 оны II улирал (roman numerals)
    (re.compile(rf"(?<!\d){YEAR}\s+оны\s+(I{{1,3}}|IV)\s+улирал"),
     lambda m: (int(m.group(1)), "q", {"I": 1, "II": 2, "III": 3, "IV": 4}[m.group(2)])),
    (re.compile(rf"(?<![\d.,-]){YEAR}(?![\d=-]|'?s\b|\s+оны\s+\d{1,2}(?:-р| дүгээр| дугаар)?\s+(?:улирал|сар))"), lambda m: (int(m.group(1)), "y", None)),
]
# Only series still being published can go stale; archive series (1940-1992)
# end where they end.
LIVE_SINCE = 2023
HISTORICAL = re.compile(
    r"\b(peak\w*|record\w*|high\w*|low\w*|max\w*|min\w*|first|since|until|before|previous\w*|"
    r"pandemic|covid)\b|дээд|оргил|хамгийн|анх|өмнө",
    re.I,
)
WIDE = {
    "over": (1.0, 1.35), "more than": (1.0, 1.35), "above": (1.0, 1.35), "exceed": (1.0, 1.35),
    "nearly": (0.85, 1.0), "almost": (0.85, 1.0), "under": (0.7, 1.0), "below": (0.7, 1.0),
    "about": (0.9, 1.1), "around": (0.9, 1.1), "roughly": (0.9, 1.1), "approximately": (0.9, 1.1),
    "some": (0.9, 1.1), "~": (0.9, 1.1), "орчим": (0.9, 1.1), "гаруй": (1.0, 1.35), "шахам": (0.85, 1.0),
}


def load_data(frontmatter: dict):
    """DataFrame of (year, month, values[]) rows for the page's CSV, or None."""
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
    out = pd.DataFrame({
        "year": pd.to_numeric(parts[0], errors="coerce"),
        "month": pd.to_numeric(parts[1], errors="coerce").fillna(pd.to_numeric(parts[2], errors="coerce") * 3),
    })
    values = df.drop(columns=[col]).apply(lambda s: pd.to_numeric(s.str.replace(",", ""), errors="coerce"))
    out["values"] = [[v for v in row if not math.isnan(v)] for row in values.itertuples(index=False)]
    out = out[out.year.notna()]
    return out if len(out) else None


def period_key(p, has_month):
    year, kind, n = p
    if kind == "q":
        return year * 100 + n * 3
    if kind == "m":
        return year * 100 + n
    return year * 100 + (12 if has_month else 0)


def latest_key(data, has_month):
    year = int(data.year.max())
    if not has_month:
        return year * 100
    month = int(data[data.year == year].month.max())
    return year * 100 + month


def rows_for(data, p):
    year, kind, n = p
    rows = data[data.year == year]
    if kind == "m":
        rows = rows[rows.month == n]
    elif kind == "q":
        # quarter-start (Jan/Apr/...) or quarter-end (Mar/Jun/...) dating
        rows = rows[rows.month.between(n * 3 - 2, n * 3)]
    values = [v for vals in rows["values"] for v in vals]
    # Totals quoted from category-split CSVs: whole-period and per-column sums.
    if len(rows) > 1:
        values.append(sum(values))
        width = max(len(v) for v in rows["values"])
        for j in range(width):
            values.append(sum(v[j] for v in rows["values"] if len(v) > j))
    return values


AFTER = {"орчим": (0.9, 1.1), "гаруй": (1.0, 1.35), "дээш": (1.0, 1.35), "хүрэхгүй": (0.7, 1.0)}


def matches(number: str, unit: str, before: str, values, after_text: str = "") -> bool:
    claim = float(number.replace(",", ""))
    decimals = len(number.split(".")[1]) if "." in number else 0
    lo, hi = next((b for w, b in WIDE.items() if re.search(rf"(?:^|\W){re.escape(w)}\W*$", before, re.I)),
                  (None, None))
    if lo is None:
        tail = re.match(r"[\s-]*(?:аас|ээс)?\s*(орчим|гаруй|дээш|хүрэхгүй)", after_text)
        if tail:
            lo, hi = AFTER[tail.group(1)]
    after = UNITS.get(unit.strip().lower(), 1) if unit else 1
    for v in values:
        for k in range(-12, 13, 3):
            # value expressed in the claim's unit, assuming the CSV is in 10^k units
            x = v * 10 ** k / after
            if lo is not None:
                if claim * lo - 1e-9 <= x <= claim * hi + 1e-9 or claim * lo >= x >= claim * hi:
                    return True
            elif abs(round(x, decimals) - claim) < 10 ** -decimals / 2 + 1e-9:
                return True
            elif decimals == 0 and abs(claim) >= 10 and abs(x - claim) <= max(1, abs(claim) * 0.005):
                return True  # "12 trillion" quoting 12,415 billion
    return False


def prose(text: str, frontmatter: dict):
    """(label, sentence) pairs from the excerpt and body prose lines."""
    body = text.split("---", 2)[2]
    blocks = [("excerpt", str(frontmatter.get("excerpt") or ""))]
    blocks += [("body", line) for line in body.split("\n")
               if line.strip() and not re.match(r"\s*(import |<|/>|[a-zA-Z]+=|\||```|#)", line)]
    for label, block in blocks:
        for sentence in re.split(r"(?<=[.!?])\s+(?=[A-ZА-ЯӨҮЁ\d])", block):
            if sentence.strip():
                yield label, sentence.strip()


def check_sentence(sentence, data, has_month, last):
    """Yield (kind, detail) findings for one sentence."""
    # Blank out data-span phrases ("from 2000 to 2025") so their years aren't claims.
    masked = sentence
    blanks = [(m.start(), m.end()) for m, *_ in spans(sentence)]
    blanks += [m.span() for m in re.finditer(rf"(?<!\d){YEAR}\s+(?:to|until)\s+(?:the\s+)?present|"
                                             rf"(?<!\d){YEAR}\s+оноос\s+(?:өнөөг|одоог)", sentence)]
    blanks += [m.span() for m in re.finditer(r"\bper\s+[\d,]+", sentence)]
    for a, b in blanks:
        masked = masked[:a] + " " * (b - a) + masked[b:]
    periods, taken = [], []
    for pattern, parse in PERIODS:
        for m in pattern.finditer(masked):
            if any(a < m.end() and m.start() < b for a, b in taken):
                continue
            taken.append((m.start(), m.end()))
            periods.append((m.start(), m.end(), parse(m)))
    if not periods:
        return
    numbers = [m for m in NUMBER.finditer(masked) if not any(a <= m.start() < b for a, b in taken)]
    claims = []
    for i, m in enumerate(numbers):
        # English puts the period after the number ("X in 2024"), Mongolian
        # before it ("2024 онд X"). Take the first period on that side, up to
        # the neighbouring number; fall back to the other side.
        lo = numbers[i - 1].end() if i else 0
        hi = numbers[i + 1].start() if i + 1 < len(numbers) else len(masked)
        after = sorted((p for p in periods if m.end() <= p[0] < hi), key=lambda p: p[0])
        before = sorted((p for p in periods if lo <= p[0] and p[1] <= m.start()), key=lambda p: -p[1])
        if not before:
            before = sorted((p for p in periods if p[1] <= m.start()), key=lambda p: -p[1])
        order = (before, after) if re.search("[\u0400-\u04FF]", sentence) else (after, before)
        nearest = next((side[0] for side in order if side), None)
        if nearest is None:
            continue
        claims.append((m, m.group(1), (m.group(2) or "").strip(), nearest))
    if not claims:
        return
    newest = max(period_key(p[2], has_month) for p in periods)
    newest_year = newest // 100
    target = last
    if has_month and any(p[2][1] == "q" for p in periods) and newest_year == last // 100:
        # A quarter quoted from monthly data: the latest *complete* quarter counts.
        target = last - last % 100 + last % 100 // 3 * 3
    live = last // 100 >= LIVE_SINCE
    if live and newest < target and last // 100 - newest_year <= 2 and not HISTORICAL.search(sentence):
        yield "STALE", f"latest period quoted is older than the data ({last // 100}" + \
            (f"-{last % 100:02d})" if has_month else ")")
    for m, number, unit, (_, _, p) in claims:
        if unit in ("%",) or unit.endswith(("fold", "x", "times")) or "-" in unit:
            continue
        if not unit and abs(float(number.replace(",", ""))) < 1000:
            continue
        values = rows_for(data, p)
        if not values:
            continue
        if not matches(number, unit, sentence[:m.start()], values, sentence[m.end():m.end() + 24]):
            label = f"{p[0]}" + (f"-{p[2]:02d}" if p[1] == "m" else f"-Q{p[2]}" if p[1] == "q" else "")
            yield "MISMATCH", f"'{m.group(0).strip()}' not found in the data for {label}"


def check_page(page: Path):
    """Return list of (kind, label, sentence, detail) findings."""
    text = page.read_text()
    parts = text.split("---", 2)
    if len(parts) < 3:
        return []
    fm = yaml.safe_load(parts[1]) or {}
    data = load_data(fm)
    if data is None:
        return []
    has_month = data.month.notna().all()
    last = latest_key(data, has_month)
    findings = []
    for label, sentence in prose(text, fm):
        for kind, detail in check_sentence(sentence, data, has_month, last):
            findings.append((kind, label, sentence, detail))
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pages", nargs="*", help="MDX files (default: all data pages)")
    args = parser.parse_args()

    pages = [Path(p) for p in args.pages] or sorted(CONTENT.glob("*/*.mdx"))
    count = 0
    for page in pages:
        for kind, label, sentence, detail in check_page(page):
            count += 1
            rel = page.resolve().relative_to(ROOT)
            print(f"{kind:8} {rel}  {label}: {detail}\n         \"{sentence[:160]}\"")
    print(f"\n{count} claim problem(s)")
    return 1 if count else 0


if __name__ == "__main__":
    sys.exit(main())
