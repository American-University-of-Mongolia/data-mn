"""
Tests for tools/scripts/validate_deprecation.py.

Run with:
    cd data/tools && ../.venv/bin/python -m pytest tests/test_deprecation.py -v
    (or: conda run -n datamn pytest tests/test_deprecation.py -v)
"""

import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from validate_deprecation import (  # noqa: E402
    collect_dataset_ids,
    validate_dataset,
)

SCHEMA = """
CREATE TABLE datasets (
    id TEXT PRIMARY KEY,
    status TEXT DEFAULT 'pending',
    deprecated_at TEXT,
    deprecation_reason TEXT,
    successor_id TEXT,
    canonical_slug TEXT,
    is_published INTEGER DEFAULT 0
)
"""

NOTICE_EN = """---
title: Test
---

import VegaChart from '~/components/ui/VegaChart.astro';
import DeprecationNotice from '~/components/ui/DeprecationNotice.astro';

<DeprecationNotice
  lang="en"
  deprecatedAt="2026-09-08"
  reason="Source retired."
  successorSlug="new-data"
  successorTitle="New Data"
/>
"""

NOTICE_MN = NOTICE_EN.replace('lang="en"', 'lang="mn"')
PLAIN_MDX = "---\ntitle: Test\n---\n\nBody text.\n"


@pytest.fixture
def mini_site(tmp_path):
    """A minimal (db, data.mn dir) pair. Tests populate both."""
    db_path = tmp_path / "data.db"
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    data_mn = tmp_path / "data.mn"
    for lang in ("en", "mn"):
        (data_mn / "src" / "data" / "data" / lang).mkdir(parents=True)
    yield conn, data_mn
    conn.close()


def add_dataset(conn, dataset_id, **kwargs):
    defaults = {"status": "active", "canonical_slug": dataset_id,
                "is_published": 1}
    defaults.update(kwargs)
    cols = ", ".join(defaults)
    conn.execute(f"INSERT INTO datasets (id, {cols}) VALUES (?, "
                 + ", ".join("?" * len(defaults)) + ")",
                 (dataset_id, *defaults.values()))
    conn.commit()


def write_mdx(data_mn, dataset_id, lang, body):
    path = data_mn / "src" / "data" / "data" / lang / f"{dataset_id}.mdx"
    path.write_text(body, encoding="utf-8")


def by_id(results):
    out = {}
    for r in results:
        out.setdefault(r.check_id, []).append(r)
    return out


def test_fully_deprecated_passes(mini_site):
    conn, data_mn = mini_site
    add_dataset(conn, "old-data", status="deprecated",
                deprecated_at="2026-09-08T12:00:00",
                deprecation_reason="Retired", successor_id="new-data")
    add_dataset(conn, "new-data")
    write_mdx(data_mn, "old-data", "en", NOTICE_EN)
    write_mdx(data_mn, "old-data", "mn", NOTICE_MN)
    write_mdx(data_mn, "new-data", "en", PLAIN_MDX)
    write_mdx(data_mn, "new-data", "mn", PLAIN_MDX)

    results = validate_dataset("old-data", conn, data_mn)
    assert results, "Expected deprecation checks to run"
    assert all(r.passed for r in results), \
        [f"{r.check_id}: {r.reason}" for r in results if not r.passed]


def test_active_dataset_without_notice_runs_no_checks(mini_site):
    conn, data_mn = mini_site
    add_dataset(conn, "new-data")
    write_mdx(data_mn, "new-data", "en", PLAIN_MDX)
    write_mdx(data_mn, "new-data", "mn", PLAIN_MDX)

    assert validate_dataset("new-data", conn, data_mn) == []


def test_missing_mn_notice_fails_d3(mini_site):
    conn, data_mn = mini_site
    add_dataset(conn, "old-data", status="deprecated",
                deprecated_at="2026-09-08T12:00:00",
                deprecation_reason="Retired")
    write_mdx(data_mn, "old-data", "en", NOTICE_EN)
    write_mdx(data_mn, "old-data", "mn", PLAIN_MDX)

    failed = [r for r in validate_dataset("old-data", conn, data_mn)
              if not r.passed]
    assert any(r.check_id == "D3" for r in failed)


def test_date_mismatch_fails_d4(mini_site):
    conn, data_mn = mini_site
    add_dataset(conn, "old-data", status="deprecated",
                deprecated_at="2026-09-08T12:00:00",
                deprecation_reason="Retired")
    write_mdx(data_mn, "old-data", "en",
               NOTICE_EN.replace("2026-09-08", "2026-01-01"))
    write_mdx(data_mn, "old-data", "mn", NOTICE_MN)

    failed = [r for r in validate_dataset("old-data", conn, data_mn)
              if not r.passed]
    assert any(r.check_id == "D4" and "en" in r.reason.lower()
               for r in failed)


def test_wrong_lang_prop_fails_d8(mini_site):
    conn, data_mn = mini_site
    add_dataset(conn, "old-data", status="deprecated",
                deprecated_at="2026-09-08T12:00:00",
                deprecation_reason="Retired")
    write_mdx(data_mn, "old-data", "en", NOTICE_EN)
    write_mdx(data_mn, "old-data", "mn", NOTICE_EN)  # EN props on MN page

    failed = [r for r in validate_dataset("old-data", conn, data_mn)
              if not r.passed]
    assert any(r.check_id == "D8" for r in failed)


def test_missing_successor_fails_d5_d6(mini_site):
    conn, data_mn = mini_site
    add_dataset(conn, "old-data", status="deprecated",
                deprecated_at="2026-09-08T12:00:00",
                deprecation_reason="Retired", successor_id="ghost")
    write_mdx(data_mn, "old-data", "en", NOTICE_EN)
    write_mdx(data_mn, "old-data", "mn", NOTICE_MN)

    failed_ids = {r.check_id for r in
                  validate_dataset("old-data", conn, data_mn)
                  if not r.passed}
    assert {"D5", "D6"} <= failed_ids


def test_inactive_successor_fails_d6(mini_site):
    conn, data_mn = mini_site
    add_dataset(conn, "old-data", status="deprecated",
                deprecated_at="2026-09-08T12:00:00",
                deprecation_reason="Retired", successor_id="new-data")
    add_dataset(conn, "new-data", status="error", is_published=0)
    write_mdx(data_mn, "old-data", "en", NOTICE_EN)
    write_mdx(data_mn, "old-data", "mn", NOTICE_MN)

    failed = [r for r in validate_dataset("old-data", conn, data_mn)
              if not r.passed]
    assert any(r.check_id == "D6" for r in failed)


def test_notice_without_registry_status_fails_d7(mini_site):
    conn, data_mn = mini_site
    add_dataset(conn, "old-data", status="error")  # never deprecated
    write_mdx(data_mn, "old-data", "en", NOTICE_EN)
    write_mdx(data_mn, "old-data", "mn", NOTICE_MN)

    failed = [r for r in validate_dataset("old-data", conn, data_mn)
              if not r.passed]
    assert any(r.check_id == "D7" for r in failed)


def test_stuck_status_fails_d1(mini_site):
    conn, data_mn = mini_site
    add_dataset(conn, "old-data", status="error",
                deprecated_at="2026-09-08T12:00:00",
                deprecation_reason="Retired")
    write_mdx(data_mn, "old-data", "en", PLAIN_MDX)
    write_mdx(data_mn, "old-data", "mn", PLAIN_MDX)

    failed = [r for r in validate_dataset("old-data", conn, data_mn)
              if not r.passed]
    assert any(r.check_id == "D1" and "error" in r.reason
               for r in failed)


def test_collect_finds_deprecated_and_notice_datasets(mini_site):
    conn, data_mn = mini_site
    add_dataset(conn, "old-data", status="deprecated",
                deprecated_at="2026-09-08T12:00:00",
                deprecation_reason="Retired")
    add_dataset(conn, "rogue", status="active")
    write_mdx(data_mn, "rogue", "en", NOTICE_EN)

    assert collect_dataset_ids(conn, data_mn) == ["old-data", "rogue"]
