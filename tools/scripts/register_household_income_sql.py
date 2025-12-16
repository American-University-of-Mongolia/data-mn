#!/usr/bin/env python3
"""
Register household income datasets directly via SQL
"""
import sqlite3
from datetime import datetime
from pathlib import Path

# Database path
db_path = Path(__file__).parent.parent / "registry" / "data.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if datasets already exist
cursor.execute("SELECT id FROM datasets WHERE id IN ('household-income-total', 'household-income-by-location')")
existing = cursor.fetchall()
if existing:
    print(f"⚠️  Datasets already exist: {[row[0] for row in existing]}")
    print("Skipping registration.")
    conn.close()
    exit(0)

now = datetime.now().isoformat()

# Insert household-income-total (parent dataset)
print("Registering household-income-total...")
cursor.execute("""
    INSERT INTO datasets (
        id, source_id, name_en, name_mn, category_en, category_mn,
        is_parent, definition_path, status, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    'household-income-total',
    'nso-1212',
    'Mongolia Average Household Monthly Income',
    'Монгол Улсын өрхийн сарын дундаж орлого',
    'Economy',
    'Эдийн засаг',
    1,  # is_parent
    'sources/nso-1212/datasets/household-income.md',
    'active',
    now,
    now
))
print("✓ Registered household-income-total")

# Insert household-income-by-location (split dataset)
print("\nRegistering household-income-by-location...")
cursor.execute("""
    INSERT INTO datasets (
        id, source_id, parent_id, name_en, name_mn, category_en, category_mn,
        is_parent, split_filter, definition_path, status, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    'household-income-by-location',
    'nso-1212',
    'household-income-total',
    'Household Income: Urban vs Rural',
    'Өрхийн орлого: Хот, хөдөө',
    'Economy',
    'Эдийн засаг',
    0,  # is_parent
    '{"Location": ["Urban", "Rural"], "Types of income": "Total income"}',
    'sources/nso-1212/datasets/household-income.md',
    'active',
    now,
    now
))
print("✓ Registered household-income-by-location")

# Log activity
cursor.execute("""
    INSERT INTO activity_log (timestamp, action, status, dataset_id, message)
    VALUES (?, ?, ?, ?, ?)
""", (
    now,
    'create',
    'success',
    'household-income-total',
    'Created household income datasets with 28 rows (total) and 56 rows (by location)'
))

# Commit changes
conn.commit()
conn.close()

print("\n✅ Registration complete!")
print("\nNext steps:")
print("  1. Publish: cd /Users/ritz/Insync/robert@aum.edu.mn/Google Drive/data/tools && python -m registry publish household-income-total")
print("  2. Publish: cd /Users/ritz/Insync/robert@aum.edu.mn/Google Drive/data/tools && python -m registry publish household-income-by-location")
