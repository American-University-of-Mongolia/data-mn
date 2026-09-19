"""
Tests for tools/scripts/diff_registry_db.py.

Run with:
    cd data/tools && ../.venv/bin/python -m pytest tests/test_diff_registry_db.py -v
"""

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from diff_registry_db import diff_dbs  # noqa: E402


def make_db(path: Path, rows: list[tuple]):
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE datasets (id TEXT, status TEXT)")
    conn.executemany("INSERT INTO datasets (id, status) VALUES (?, ?)", rows)
    conn.commit()
    conn.close()


def test_identical_dbs(tmp_path):
    base = tmp_path / "base.db"
    head = tmp_path / "head.db"
    make_db(base, [("a", "active")])
    make_db(head, [("a", "active")])

    changes, report = diff_dbs(base, head, None)
    assert changes == 0
    assert report == ""


def test_modified_row_reported(tmp_path):
    base = tmp_path / "base.db"
    head = tmp_path / "head.db"
    make_db(base, [("a", "error")])
    make_db(head, [("a", "deprecated")])

    changes, report = diff_dbs(base, head, None)
    assert changes == 1
    assert "[datasets]" in report
    assert "id='a'" in report
    assert "status" in report
    assert "error" in report and "deprecated" in report


def test_added_row(tmp_path):
    base = tmp_path / "base.db"
    head = tmp_path / "head.db"
    make_db(base, [("a", "active")])
    make_db(head, [("a", "active"), ("b", "active")])

    changes, report = diff_dbs(base, head, None)
    assert changes == 1
    assert "+ row" in report and "id='b'" in report


def test_removed_row(tmp_path):
    base = tmp_path / "base.db"
    head = tmp_path / "head.db"
    make_db(base, [("a", "active"), ("b", "active")])
    make_db(head, [("a", "active")])

    changes, report = diff_dbs(base, head, None)
    assert changes == 1
    assert "- row" in report and "id='b'" in report


def test_table_filter(tmp_path):
    base = tmp_path / "base.db"
    head = tmp_path / "head.db"
    make_db(base, [("a", "error")])
    make_db(head, [("a", "deprecated")])

    changes, _ = diff_dbs(base, head, ["other_table"])
    assert changes == 0
