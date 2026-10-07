"""Protect the wage snapshot and additive, pending-only registration workflow."""

import hashlib
import json
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/scripts"))
from build_real_wage_index import SLUG, VERSION, national_rows
from register_real_wage_index import register


@pytest.fixture
def db(tmp_path):
    target = tmp_path / "registry.db"
    shutil.copyfile(ROOT / "tools/registry/data.db", target)
    with sqlite3.connect(target) as conn:
        for table in ("versions", "activity_log"):
            conn.execute(f"DELETE FROM {table} WHERE dataset_id = ?", (SLUG,))
        conn.execute("DELETE FROM datasets WHERE id = ?", (SLUG,))
    return target


def rows(db, table):
    with sqlite3.connect(db) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute(f"SELECT * FROM {table}")]


def test_preserved_national_snapshot():
    manifest = json.loads((VERSION / "raw/manifest.json").read_text())
    for name, digest in manifest["files"].items():
        assert hashlib.sha256((VERSION / "raw" / name).read_bytes()).hexdigest() == digest
    en = national_rows("en")
    assert en == national_rows("mn")
    assert [year for year, _ in en] == list(range(1992, 2026))
    assert dict(en)[2023] == 100
    assert dict(en)[2024] == 116.7
    assert dict(en)[2025] == 125.6
    assert all(isinstance(value, (int, float)) and value > 0 for _, value in en)


def test_registration_is_additive_and_repairs_matching_pending_metadata(db):
    tables = ("datasets", "versions", "activity_log", "sources")
    before = {table: rows(db, table) for table in tables}
    register(db)
    for table in tables:
        after = rows(db, table)
        assert all(row in after for row in before[table])
        assert len(after) == len(before[table]) + (0 if table == "sources" else 1)
    with sqlite3.connect(db) as conn:
        conn.execute("UPDATE datasets SET data_file=NULL, data_as_of=NULL, current_version=0 WHERE id=?", (SLUG,))
    register(db)
    for table in ("versions", "activity_log"):
        assert len(rows(db, table)) == len(before[table]) + 1
    ds = next(row for row in rows(db, "datasets") if row["id"] == SLUG)
    assert ds["status"] == "pending"
    assert ds["current_version"] == 1
    assert not any(ds[key] for key in ("auto_update", "auto_publish", "is_published"))
    for key in ("data_file", "mdx_file_en", "mdx_file_mn", "chart_spec"):
        assert (ROOT / ds[key]).is_file()
    assert ds["data_as_of"] == "2025-12-31"
    assert ds["source_updated_at"] == "2026-04-21T00:00:00Z"
    assert ds["last_fetched_at"] == "2026-09-30T02:05:34.799971+00:00"
    assert json.loads(ds["coverage_geography"]) == ["national"]
    assert json.loads(ds["source_metadata"])["non_comparable_years"] == [2025]


@pytest.mark.parametrize("mutation", [
    "UPDATE datasets SET is_published=1 WHERE id=?",
    "UPDATE datasets SET auto_publish=1 WHERE id=?",
    "UPDATE datasets SET auto_update=1 WHERE id=?",
    "UPDATE datasets SET status='active' WHERE id=?",
    "UPDATE datasets SET current_version=2 WHERE id=?",
    "UPDATE versions SET data_hash='changed' WHERE dataset_id=?",
    "UPDATE versions SET version=2 WHERE dataset_id=?",
])
def test_registration_refuses_changed_or_active_records(db, mutation):
    register(db)
    with sqlite3.connect(db) as conn:
        conn.execute(mutation, (SLUG,))
    before = db.read_bytes()
    with pytest.raises(ValueError, match="review instead of overwriting"):
        register(db)
    assert db.read_bytes() == before
