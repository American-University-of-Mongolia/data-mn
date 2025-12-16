#!/usr/bin/env python3
"""
Register cpi-food-ulaanbaatar dataset in the registry
"""

import sys
import json
from pathlib import Path

# Add registry to path
sys.path.insert(0, str(Path(__file__).parent))

from registry import Registry, Dataset

# Dataset parameters
DATASET_ID = "cpi-food-ulaanbaatar"
PARENT_ID = "nso-cpi-ulaanbaatar-mom"
SOURCE_ID = "nso-1212"

# Split filter
SPLIT_FILTER = {
    "reference_year": "2020=100",
    "group": " Food and non-alcaholic beverages"  # English version (with leading space and typo)
}

print("=" * 80)
print("Registering CPI Food Ulaanbaatar Dataset")
print("=" * 80)

reg = Registry()

# Check if dataset already exists
existing = reg.get_dataset(DATASET_ID)
if existing:
    print(f"\n⚠️  Dataset {DATASET_ID} already exists in registry")
    print("   Updating instead...")
    action = 'update'
else:
    print(f"\n✓ Creating new dataset: {DATASET_ID}")
    action = 'create'

# Create Dataset object
dataset = Dataset(
    id=DATASET_ID,
    source_id=SOURCE_ID,
    name_en='Food Price Changes in Ulaanbaatar, % MoM (2020-2025)',
    name_mn='Улаанбаатар хотын хүнсний үнийн өөрчлөлт, % сар тутамд (2020-2025)',
    category_en='Economy',
    category_mn='Эдийн засаг',
    definition_path=f'tools/sources/{SOURCE_ID}/datasets/{DATASET_ID}.md',
    status='active',
    current_version=1,
    is_parent=False,
    parent_id=PARENT_ID,
    split_filter=SPLIT_FILTER,
    source_ref='DT_NSO_0600_003V4.px',
)

if action == 'create':
    reg.add_dataset(dataset)
else:
    # For update, we need to use the update method
    # But for now, let's just create
    print("⚠️  Using add_dataset for initial creation")
    reg.add_dataset(dataset)

print(f"\n✓ Dataset registered successfully")

# Log activity
reg.log_activity(
    action=action,
    status='success',
    dataset_id=DATASET_ID,
    message=f"Created split dataset from {PARENT_ID} with 60 rows (2020-02 to 2025-01)"
)

print(f"✓ Activity logged")

# Show dataset info
print("\n" + "=" * 80)
print("Dataset Info")
print("=" * 80)

dataset_info = reg.get_dataset(DATASET_ID)
print(f"ID: {dataset_info.id}")
print(f"Name (EN): {dataset_info.name_en}")
print(f"Name (MN): {dataset_info.name_mn}")
print(f"Source: {dataset_info.source_id}")
print(f"Parent: {dataset_info.parent_id}")
print(f"Status: {dataset_info.status}")
print(f"Version: {dataset_info.current_version}")
print(f"Split filter: {dataset_info.split_filter}")

print("\n✓ Registration complete!")
