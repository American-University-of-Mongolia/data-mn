#!/usr/bin/env python3
"""
Fix unemployment-rate-national - it should not be marked as parent
since it has its own MDX pages and is user-facing
"""

import sys
sys.path.insert(0, '/Users/ritz/Insync/robert@aum.edu.mn/Google Drive/data/tools')

from registry import Registry
import sqlite3

reg = Registry()

# Update the dataset to NOT be a parent
conn = reg._get_conn()
conn.execute("""
    UPDATE datasets
    SET is_parent = 0
    WHERE id = 'unemployment-rate-national'
""")
conn.commit()
conn.close()

print("✓ Fixed unemployment-rate-national")
print("  is_parent: True -> False")
print("\nNow you can publish it:")
print("  python -m registry publish unemployment-rate-national")
