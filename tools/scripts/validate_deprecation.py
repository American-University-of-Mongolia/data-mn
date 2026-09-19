#!/usr/bin/env python3
"""
Deprecation Consistency Checks for data.mn.

Validates that deprecated datasets are fully and consistently deprecated
across the registry database and the EN/MN website pages.

Checks (per dataset):
    D1: registry deprecation fields consistent (no stuck status)
    D2: EN page contains DeprecationNotice import + component
    D3: MN page contains DeprecationNotice import + component
    D4: MDX deprecatedAt matches registry deprecated_at (date part)
    D5: MDX successorSlug matches the successor's canonical slug
    D6: successor exists, is active, is published, has EN+MN pages
    D7: MDX DeprecationNotice implies registry status='deprecated' (reverse)
    D8: component lang prop matches the page language

Usage:
    python validate_deprecation.py --all
    python validate_deprecation.py <dataset-id>
    python validate_deprecation.py --all --db tools/registry/data.db \\
        --data-mn data.mn

Exit code 0 if all checks pass, 1 otherwise.
"""

import argparse
import re
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve()
DEFAULT_DB = HERE.parent.parent / "registry" / "data.db"
DEFAULT_DATA_MN = HERE.parent.parent.parent / "data.mn"

NOTICE_IMPORT = "DeprecationNotice"
COMPONENT_RE = re.compile(r"<DeprecationNotice\s(.*?)\s*/?>", re.DOTALL)
PROP_RE = re.compile(r'(\w+)="([^"]*)"')


@dataclass
class DeprecationResult:
    check_id: str
    dataset_id: str
    passed: bool
    reason: str


def parse_notice(body: str) -> dict | None:
    """Extract DeprecationNotice props from MDX body, or None if absent."""
    if NOTICE_IMPORT not in body:
        return None
    match = COMPONENT_RE.search(body)
    if not match:
        return None
    return dict(PROP_RE.findall(match.group(1)))


def get_dataset(conn: sqlite3.Connection, dataset_id: str) -> dict | None:
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT id, status, deprecated_at, deprecation_reason, successor_id,"
        " canonical_slug, is_published FROM datasets WHERE id = ?",
        (dataset_id,),
    ).fetchone()
    return dict(row) if row else None


def validate_dataset(
    dataset_id: str, conn: sqlite3.Connection, data_mn: Path
) -> list[DeprecationResult]:
    results: list[DeprecationResult] = []

    def add(check_id: str, passed: bool, reason: str) -> None:
        results.append(DeprecationResult(check_id, dataset_id, passed, reason))

    row = get_dataset(conn, dataset_id)
    mdx = {
        lang: data_mn / "src" / "data" / "data" / lang / f"{dataset_id}.mdx"
        for lang in ("en", "mn")
    }
    bodies = {lang: p.read_text(encoding="utf-8") if p.exists() else ""
              for lang, p in mdx.items()}
    notices = {lang: parse_notice(body) for lang, body in bodies.items()}

    is_deprecated = bool(row and row["status"] == "deprecated")
    has_notice = any(n is not None for n in notices.values())
    has_deprecated_at = bool(row and row["deprecated_at"])

    if not is_deprecated and not has_notice and not has_deprecated_at:
        return results  # No deprecation involved; nothing to check.

    # D1 (stuck status): deprecated_at set but status never flipped.
    if has_deprecated_at and not is_deprecated:
        add("D1", False,
            f"deprecated_at is set but status is '{row['status']}'"
            f" (expected 'deprecated')")
        return results

    # D7 (reverse): a notice requires registry status='deprecated'.
    if has_notice and not is_deprecated:
        actual = row["status"] if row else "not registered"
        add("D7", False, f"MDX has DeprecationNotice but registry status is '{actual}'")
        return results

    # D1: registry fields complete.
    missing = [c for c in ("deprecated_at", "deprecation_reason")
               if not row[c]]
    add("D1", not missing,
        "deprecated_at and reason set" if not missing
        else f"Missing registry fields: {missing}")

    # D2/D3: notice present in both languages.
    for check_id, lang in (("D2", "en"), ("D3", "mn")):
        if not mdx[lang].exists():
            add(check_id, False, f"Missing {lang.upper()} MDX page")
        elif notices[lang] is None:
            add(check_id, False, f"{lang.upper()} page lacks DeprecationNotice")
        else:
            add(check_id, True, f"{lang.upper()} page has DeprecationNotice")

    # D4: dates match (compare date part; registry stores full ISO timestamp).
    reg_date = str(row["deprecated_at"])[:10]
    for lang in ("en", "mn"):
        if notices[lang] is None:
            continue
        mdx_date = notices[lang].get("deprecatedAt", "")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", mdx_date):
            add("D4", False, f"{lang.upper()} deprecatedAt '{mdx_date}' not YYYY-MM-DD")
        elif mdx_date != reg_date:
            add("D4", False,
                f"{lang.upper()} deprecatedAt {mdx_date} != registry {reg_date}")
        else:
            add("D4", True, f"{lang.upper()} deprecatedAt matches ({reg_date})")

    # D8: lang prop matches page language.
    for lang in ("en", "mn"):
        if notices[lang] is None:
            continue
        actual = notices[lang].get("lang", "")
        add("D8", actual == lang,
            f"{lang.upper()} lang prop ok" if actual == lang
            else f"{lang.upper()} page has lang=\"{actual}\"")

    # D5/D6: successor consistency (only when successor_id is set).
    successor_id = row["successor_id"]
    if successor_id:
        successor = get_dataset(conn, successor_id)
        if successor is None:
            add("D5", False, f"Successor '{successor_id}' not in registry")
            add("D6", False, f"Successor '{successor_id}' not in registry")
            return results
        expected_slug = successor["canonical_slug"] or successor["id"]
        for lang in ("en", "mn"):
            if notices[lang] is None:
                continue
            actual = notices[lang].get("successorSlug", "")
            add("D5", actual == expected_slug,
                f"{lang.upper()} successorSlug ok" if actual == expected_slug
                else f"{lang.upper()} successorSlug '{actual}' != '{expected_slug}'")
        problems = []
        if successor["status"] != "active":
            problems.append(f"status is '{successor['status']}'")
        if not successor["is_published"]:
            problems.append("not published")
        for lang in ("en", "mn"):
            page = data_mn / "src" / "data" / "data" / lang / f"{expected_slug}.mdx"
            if not page.exists():
                problems.append(f"missing {lang.upper()} page")
        add("D6", not problems,
            f"Successor '{successor_id}' active and published" if not problems
            else f"Successor '{successor_id}': {'; '.join(problems)}")

    return results


def find_notice_datasets(data_mn: Path) -> set[str]:
    """Dataset IDs whose EN or MN page contains a DeprecationNotice."""
    found = set()
    for lang in ("en", "mn"):
        for path in (data_mn / "src" / "data" / "data" / lang).glob("*.mdx"):
            if NOTICE_IMPORT in path.read_text(encoding="utf-8"):
                found.add(path.stem)
    return found


def collect_dataset_ids(conn: sqlite3.Connection, data_mn: Path) -> list[str]:
    ids = {r[0] for r in conn.execute(
        "SELECT id FROM datasets WHERE status = 'deprecated'"
        " OR deprecated_at IS NOT NULL")}
    return sorted(ids | find_notice_datasets(data_mn))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate deprecation consistency")
    parser.add_argument("dataset_id", nargs="?",
                        help="Single dataset ID to validate")
    parser.add_argument("--all", action="store_true",
                        help="Validate all deprecated datasets")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB,
                        help="Registry database path")
    parser.add_argument("--data-mn", type=Path, default=DEFAULT_DATA_MN,
                        help="data.mn project directory")
    args = parser.parse_args()

    if not args.dataset_id and not args.all:
        parser.error("Provide a dataset ID or --all")

    conn = sqlite3.connect(args.db)
    try:
        ids = ([args.dataset_id] if args.dataset_id
               else collect_dataset_ids(conn, args.data_mn))
        results: list[DeprecationResult] = []
        for dataset_id in ids:
            results.extend(validate_dataset(dataset_id, conn, args.data_mn))
    finally:
        conn.close()

    if not results:
        print("No deprecated datasets found. Nothing to check.")
        return 0

    failed = 0
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"  [{r.check_id}] {status} {r.dataset_id}: {r.reason}")
        failed += not r.passed

    print(f"\n{len(results) - failed}/{len(results)} deprecation checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
