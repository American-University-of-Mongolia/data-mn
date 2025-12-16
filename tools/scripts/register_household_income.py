#!/usr/bin/env python3
"""
Register household income datasets in the registry
"""
import sys
from pathlib import Path

# Add parent directory to path to import registry
sys.path.insert(0, str(Path(__file__).parent.parent))

from registry import Registry, Dataset

# Initialize registry
reg = Registry()

# Register household-income-total (parent dataset)
print("Registering household-income-total...")
dataset1 = Dataset(
    id='household-income-total',
    source_id='nso-1212',
    name_en='Mongolia Average Household Monthly Income',
    name_mn='Монгол Улсын өрхийн сарын дундаж орлого',
    category_en='Economy',
    category_mn='Эдийн засаг',
    is_parent=True,
    status='active'
)
reg.add_dataset(dataset1)
print("✓ Registered household-income-total")

# Register household-income-by-location (split dataset)
print("\nRegistering household-income-by-location...")
dataset2 = Dataset(
    id='household-income-by-location',
    source_id='nso-1212',
    name_en='Household Income: Urban vs Rural',
    name_mn='Өрхийн орлого: Хот, хөдөө',
    category_en='Economy',
    category_mn='Эдийн засаг',
    is_parent=False,
    parent_id='household-income-total',
    split_filter='{"Location": ["Urban", "Rural"], "Types of income": "Total income"}',
    status='active'
)
reg.add_dataset(dataset2)
print("✓ Registered household-income-by-location")

# Log activity
reg.log_activity(
    action='create',
    status='success',
    dataset_id='household-income-total',
    message='Created household income datasets with 28 rows (total) and 56 rows (by location)'
)

print("\n✅ Registration complete!")
print("\nNext steps:")
print("  1. Publish datasets: python -m registry publish household-income-total")
print("  2. Publish datasets: python -m registry publish household-income-by-location")
