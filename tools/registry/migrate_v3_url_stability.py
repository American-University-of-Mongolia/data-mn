#!/usr/bin/env python3
"""
Migration: Add URL stability support

This migration:
1. Adds URL stability columns to datasets table:
   - canonical_slug, first_published_at, is_published
   - deprecated_at, deprecation_reason, successor_id
2. Creates url_redirects table
3. Creates new indexes
4. Sets canonical_slug = id for existing published datasets

Run from: data/tools/registry/
Command: python3 migrate_v3_url_stability.py

See docs/principles/url-stability.md for full documentation.
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "data.db"


def migrate():
    """Run the migration"""
    print(f"Migrating database: {DB_PATH}")

    if not DB_PATH.exists():
        print("Database does not exist. No migration needed.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Check if migration already applied
    cursor.execute("PRAGMA table_info(datasets)")
    columns = {row['name'] for row in cursor.fetchall()}

    if 'canonical_slug' in columns:
        print("Migration already applied (canonical_slug exists). Skipping column additions.")
    else:
        print("Starting migration...")

        # Step 1: Add new columns to datasets table
        print("  1. Adding URL stability columns to datasets table...")

        new_columns = [
            ("canonical_slug", "TEXT"),
            ("first_published_at", "TEXT"),
            ("is_published", "INTEGER DEFAULT 0"),
            ("deprecated_at", "TEXT"),
            ("deprecation_reason", "TEXT"),
            ("successor_id", "TEXT"),
        ]

        for col_name, col_type in new_columns:
            try:
                cursor.execute(f"ALTER TABLE datasets ADD COLUMN {col_name} {col_type}")
                print(f"     Added column: {col_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"     Column {col_name} already exists, skipping")
                else:
                    raise

    # Step 2: Create url_redirects table
    print("  2. Creating url_redirects table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS url_redirects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            old_slug TEXT NOT NULL UNIQUE,
            target_dataset_id TEXT REFERENCES datasets(id),
            target_url TEXT,
            redirect_type INTEGER DEFAULT 301,
            reason TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            hit_count INTEGER DEFAULT 0,
            last_hit_at TEXT
        )
    """)
    print("     Created url_redirects table")

    # Step 3: Create new indexes
    print("  3. Creating indexes...")
    indexes = [
        ("idx_datasets_canonical_slug", "datasets(canonical_slug)"),
        ("idx_datasets_published", "datasets(is_published)"),
        ("idx_redirects_old_slug", "url_redirects(old_slug)"),
    ]

    for idx_name, idx_def in indexes:
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {idx_def}")
            print(f"     Created index: {idx_name}")
        except sqlite3.OperationalError as e:
            print(f"     Index {idx_name}: {e}")

    # Step 4: Set canonical_slug = id for datasets with MDX files (considered published)
    print("  4. Setting canonical_slug for existing datasets with MDX files...")
    cursor.execute("""
        UPDATE datasets
        SET canonical_slug = id,
            is_published = 1,
            first_published_at = COALESCE(created_at, datetime('now'))
        WHERE mdx_file_en IS NOT NULL
          AND canonical_slug IS NULL
    """)
    updated_count = cursor.rowcount
    print(f"     Updated {updated_count} datasets")

    # Show which datasets were updated
    cursor.execute("""
        SELECT id, canonical_slug, first_published_at
        FROM datasets
        WHERE is_published = 1
        ORDER BY id
    """)
    rows = cursor.fetchall()
    if rows:
        print("\n     Published datasets:")
        for row in rows:
            print(f"       - {row['id']} → /{row['canonical_slug']}")

    # Step 5: Update schema version
    print("\n  5. Updating schema version...")
    cursor.execute("""
        INSERT OR REPLACE INTO schema_version (version, applied_at, description)
        VALUES (3, datetime('now'), 'Add URL stability support (canonical_slug, redirects)')
    """)

    conn.commit()
    conn.close()

    print(f"\nMigration complete!")
    print("\nURL Stability features now available:")
    print("  - python -m registry publish <id>      # Publish a dataset")
    print("  - python -m registry rename <id> <new> # Rename with redirect")
    print("  - python -m registry deprecate <id>    # Mark as deprecated")
    print("  - python -m registry redirects         # List all redirects")
    print("  - python -m registry export-redirects  # Export for Astro")
    print("\nSee docs/principles/url-stability.md for full documentation.")


def show_status():
    """Show current URL stability status"""
    if not DB_PATH.exists():
        print("Database does not exist.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Check schema version
    cursor.execute("SELECT version, description FROM schema_version ORDER BY version DESC LIMIT 1")
    version_row = cursor.fetchone()
    if version_row:
        print(f"Schema version: {version_row['version']} - {version_row['description']}")

    # Check published datasets
    cursor.execute("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN is_published = 1 THEN 1 ELSE 0 END) as published,
               SUM(CASE WHEN deprecated_at IS NOT NULL THEN 1 ELSE 0 END) as deprecated
        FROM datasets
    """)
    stats = cursor.fetchone()
    print(f"\nDatasets: {stats['total']} total, {stats['published']} published, {stats['deprecated']} deprecated")

    # Check redirects
    cursor.execute("SELECT COUNT(*) as count FROM url_redirects")
    redirect_count = cursor.fetchone()['count']
    print(f"Redirects: {redirect_count}")

    conn.close()


def rollback():
    """Rollback the migration (removes columns and table)"""
    print("WARNING: This will remove URL stability data!")
    print("Rollback not recommended. Restore from backup if needed.")

    response = input("Type 'yes' to continue: ")
    if response.lower() != 'yes':
        print("Rollback cancelled.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop url_redirects table
    cursor.execute("DROP TABLE IF EXISTS url_redirects")
    print("Dropped url_redirects table")

    # Note: SQLite doesn't support DROP COLUMN easily
    # Would need to recreate table without those columns
    print("Note: Cannot easily drop columns from datasets table in SQLite.")
    print("The columns will remain but be unused if you restore schema.sql v2.")

    conn.commit()
    conn.close()
    print("Partial rollback complete.")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == '--rollback':
            rollback()
        elif sys.argv[1] == '--status':
            show_status()
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Usage: python3 migrate_v3_url_stability.py [--status|--rollback]")
    else:
        migrate()
