#!/usr/bin/env python3
"""
Fix household-income-total - it's not actually a parent dataset
"""
import sqlite3
from pathlib import Path

# Database path
db_path = Path(__file__).parent.parent / "registry" / "data.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Update household-income-total to not be a parent
cursor.execute("""
    UPDATE datasets
    SET is_parent = 0
    WHERE id = 'household-income-total'
""")

# Update household-income-by-location to not have a parent
cursor.execute("""
    UPDATE datasets
    SET parent_id = NULL,
        split_filter = NULL
    WHERE id = 'household-income-by-location'
""")

conn.commit()
conn.close()

print("✅ Fixed: Both datasets are now standalone (not parent/split)")
