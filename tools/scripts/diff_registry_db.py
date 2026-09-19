#!/usr/bin/env python3
"""
Diff two registry SQLite files and print human-readable row changes.

The registry database is committed as a binary file, so PRs touching it
are otherwise unreviewable. This script makes the changes visible.

Usage:
    python diff_registry_db.py base.db head.db
    python diff_registry_db.py base.db head.db --tables datasets,activity_log

    # Typical PR review use (from the repo root):
    git show main:tools/registry/data.db > /tmp/base.db
    git show <pr-sha>:tools/registry/data.db > /tmp/head.db
    python tools/scripts/diff_registry_db.py /tmp/base.db /tmp/head.db

Exit code 0 if identical, 1 if any differences are found.
"""

import argparse
import sqlite3
import sys
from pathlib import Path

# Wide/verbose columns trimmed for readability.
MAX_VALUE_LEN = 100


def table_names(conn: sqlite3.Connection) -> list[str]:
    return [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
        " AND name NOT LIKE 'sqlite_%' ORDER BY name")]


def rows_by_rowid(conn: sqlite3.Connection, table: str) -> tuple[list, dict]:
    cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]
    try:
        iterator = conn.execute(f"SELECT rowid, * FROM {table} ORDER BY rowid")
        return cols, {row[0]: row[1:] for row in iterator}
    except sqlite3.OperationalError:
        # WITHOUT ROWID or virtual tables (e.g. FTS): compare by position.
        iterator = conn.execute(f"SELECT * FROM {table}")
        return cols, {f"#{i}": row for i, row in enumerate(iterator)}


def label_for(cols: list, values: tuple) -> str:
    """Short row label, preferring an id-like column."""
    for key in ("id", "old_slug", "dataset_id", "name"):
        if key in cols:
            return f"{key}={values[cols.index(key)]!r}"
    return ""


def short(value) -> str:
    text = "NULL" if value is None else str(value)
    text = text.replace("\n", " ")
    return text if len(text) <= MAX_VALUE_LEN else text[:MAX_VALUE_LEN] + "..."


def diff_table(base: sqlite3.Connection, head: sqlite3.Connection,
               table: str) -> list[str]:
    lines: list[str] = []
    base_cols, base_rows = rows_by_rowid(base, table)
    head_cols, head_rows = rows_by_rowid(head, table)

    if base_cols != head_cols:
        lines.append(f"  schema: {base_cols} -> {head_cols}")
        return lines

    for rowid in sorted(set(base_rows) | set(head_rows)):
        if rowid not in base_rows:
            label = label_for(head_cols, head_rows[rowid])
            lines.append(f"  + row {rowid} {label}".rstrip())
        elif rowid not in head_rows:
            label = label_for(base_cols, base_rows[rowid])
            lines.append(f"  - row {rowid} {label}".rstrip())
        elif base_rows[rowid] != head_rows[rowid]:
            label = label_for(base_cols, base_rows[rowid])
            lines.append(f"  ~ row {rowid} {label}".rstrip())
            for col, old, new in zip(base_cols, base_rows[rowid],
                                     head_rows[rowid]):
                if old != new:
                    lines.append(f"      {col}: {short(old)!r}"
                                 f" -> {short(new)!r}")
    return lines


def diff_dbs(base_path: Path, head_path: Path,
             tables: list[str] | None) -> tuple[int, str]:
    base = sqlite3.connect(base_path)
    head = sqlite3.connect(head_path)
    try:
        base_tables = set(table_names(base))
        head_tables = set(table_names(head))
        wanted = set(tables) if tables else base_tables | head_tables

        out: list[str] = []
        changes = 0
        for table in sorted(wanted):
            if table not in base_tables and table not in head_tables:
                continue  # Unknown --table name; ignore.
            if table not in base_tables:
                out.append(f"[{table}] only in HEAD (new table)")
                changes += 1
            elif table not in head_tables:
                out.append(f"[{table}] only in BASE (dropped table)")
                changes += 1
            else:
                table_lines = diff_table(base, head, table)
                if table_lines:
                    out.append(f"[{table}]")
                    out.extend(table_lines)
                    changes += len([line for line in table_lines
                                    if line.startswith("  +")
                                    or line.startswith("  -")
                                    or line.startswith("  ~")])
        return changes, "\n".join(out)
    finally:
        base.close()
        head.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Diff two registry SQLite files")
    parser.add_argument("base_db", type=Path)
    parser.add_argument("head_db", type=Path)
    parser.add_argument("--tables", default="",
                        help="Comma-separated tables to compare (default: all)")
    args = parser.parse_args()

    tables = [t.strip() for t in args.tables.split(",") if t.strip()] or None
    changes, report = diff_dbs(args.base_db, args.head_db, tables)

    if not changes:
        print("Databases are identical.")
        return 0
    print(report)
    print(f"\n{changes} changed row(s).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
