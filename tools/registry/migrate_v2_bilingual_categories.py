#!/usr/bin/env python3
"""
Migration: Add bilingual category support

This migration:
1. Renames 'category' column to 'category_en'
2. Adds 'category_mn' column
3. Populates category_mn with translations for existing data

Run from: data/tools/registry/
Command: python3 migrate_v2_bilingual_categories.py
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data.db"

# Category translation mapping
CATEGORY_TRANSLATIONS = {
    "Demographics": "Хүн ам зүй",
    "Economy": "Эдийн засаг",
    "Employment": "Хөдөлмөр эрхлэлт",
    "Housing": "Орон сууц",
    "Mining": "Уул уурхай",
    "Finance": "Санхүү",
    "Agriculture": "Хөдөө аж ахуй",
    "Education": "Боловсрол",
    "Health": "Эрүүл мэнд",
    "Trade": "Худалдаа",
    "Energy": "Эрчим хүч",
    "Tourism": "Аялал жуулчлал",
}


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

    if 'category_en' in columns:
        print("Migration already applied (category_en exists). Skipping.")
        conn.close()
        return

    if 'category' not in columns:
        print("No 'category' column found. Database may have different schema.")
        conn.close()
        return

    print("Starting migration...")

    # Step 1: Create new table with updated schema
    print("  1. Creating new table structure...")
    cursor.execute("""
        CREATE TABLE datasets_new (
            id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL,
            parent_id TEXT,
            is_parent INTEGER DEFAULT 0,
            split_filter TEXT,
            name_en TEXT NOT NULL,
            name_mn TEXT,
            description_en TEXT,
            description_mn TEXT,
            category_en TEXT NOT NULL,
            category_mn TEXT,
            tags TEXT,
            keywords_en TEXT,
            keywords_mn TEXT,
            source_ref TEXT,
            source_path TEXT,
            definition_path TEXT NOT NULL,
            source_metadata TEXT,
            current_version INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            data_file TEXT,
            mdx_file_en TEXT,
            mdx_file_mn TEXT,
            chart_spec TEXT,
            data_as_of TEXT,
            source_updated_at TEXT,
            last_checked_at TEXT,
            last_fetched_at TEXT,
            auto_update INTEGER DEFAULT 1,
            auto_publish INTEGER DEFAULT 1,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    # Step 2: Copy data from old table to new table
    print("  2. Copying data with category translations...")
    cursor.execute("SELECT * FROM datasets")
    rows = cursor.fetchall()

    for row in rows:
        category_en = row['category']
        category_mn = CATEGORY_TRANSLATIONS.get(category_en, None)

        if category_mn is None:
            print(f"     Warning: No translation for category '{category_en}' in dataset '{row['id']}'")

        cursor.execute("""
            INSERT INTO datasets_new (
                id, source_id, parent_id, is_parent, split_filter,
                name_en, name_mn, description_en, description_mn,
                category_en, category_mn, tags, keywords_en, keywords_mn,
                source_ref, source_path, definition_path, source_metadata,
                current_version, status, data_file, mdx_file_en, mdx_file_mn,
                chart_spec, data_as_of, source_updated_at, last_checked_at,
                last_fetched_at, auto_update, auto_publish, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row['id'], row['source_id'], row['parent_id'], row['is_parent'],
            row['split_filter'], row['name_en'], row['name_mn'],
            row['description_en'], row['description_mn'],
            category_en, category_mn,
            row['tags'], row['keywords_en'], row['keywords_mn'],
            row['source_ref'], row['source_path'], row['definition_path'],
            row['source_metadata'], row['current_version'], row['status'],
            row['data_file'], row['mdx_file_en'], row['mdx_file_mn'],
            row['chart_spec'], row['data_as_of'], row['source_updated_at'],
            row['last_checked_at'], row['last_fetched_at'],
            row['auto_update'], row['auto_publish'],
            row['created_at'], row['updated_at']
        ))

    # Step 3: Drop old table and rename new one
    print("  3. Replacing old table...")
    cursor.execute("DROP TABLE datasets")
    cursor.execute("ALTER TABLE datasets_new RENAME TO datasets")

    # Step 4: Recreate indexes
    print("  4. Recreating indexes...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_datasets_source ON datasets(source_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_datasets_status ON datasets(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_datasets_category ON datasets(category_en)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_datasets_parent ON datasets(parent_id)")

    # Step 5: Recreate trigger
    print("  5. Recreating triggers...")
    cursor.execute("DROP TRIGGER IF EXISTS update_datasets_timestamp")
    cursor.execute("""
        CREATE TRIGGER update_datasets_timestamp
        AFTER UPDATE ON datasets
        BEGIN
            UPDATE datasets SET updated_at = datetime('now') WHERE id = NEW.id;
        END
    """)

    # Step 6: Update schema version
    print("  6. Updating schema version...")
    cursor.execute("""
        INSERT OR REPLACE INTO schema_version (version, applied_at, description)
        VALUES (2, datetime('now'), 'Add bilingual category support (category_en, category_mn)')
    """)

    conn.commit()
    conn.close()

    print(f"\nMigration complete! Migrated {len(rows)} datasets.")
    print("Category translations applied:")
    for en, mn in CATEGORY_TRANSLATIONS.items():
        print(f"  {en} → {mn}")


def rollback():
    """Rollback the migration (if needed)"""
    print("Rollback not implemented. Restore from backup if needed.")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--rollback':
        rollback()
    else:
        migrate()
