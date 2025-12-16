#!/usr/bin/env python3
"""
Register cpi-monthly-ulaanbaatar dataset in the registry
"""

import sys
import json
from pathlib import Path

# Add registry module to path
sys.path.insert(0, str(Path(__file__).parent))

from registry import Registry, Dataset

# Initialize registry
reg = Registry()

DATASET_ID = "cpi-monthly-ulaanbaatar"
PARENT_ID = "nso-cpi-ulaanbaatar-mom"
SOURCE_ID = "nso-1212"

# Split filter
SPLIT_FILTER = {
    "reference_year": "2020=100",
    "group": "Overall index"
}

print(f"Registering dataset: {DATASET_ID}")
print(f"  Parent: {PARENT_ID}")
print(f"  Filter: {SPLIT_FILTER}")

# Check if dataset already exists
existing = reg.get_dataset(DATASET_ID)

if existing:
    print(f"\n⚠️  Dataset {DATASET_ID} already exists. Skipping...")
    action = 'exists'
else:
    print(f"\n✓ Creating new dataset {DATASET_ID}")

    # Create dataset object
    dataset = Dataset(
        id=DATASET_ID,
        source_id=SOURCE_ID,
        name_en='Monthly Inflation in Ulaanbaatar, % (2020-2025)',
        name_mn='Улаанбаатар хотын сарын инфляци, % (2020-2025)',
        category_en='Economy',
        category_mn='Эдийн засаг',
        definition_path=f'tools/sources/{SOURCE_ID}/datasets/{DATASET_ID}.md',
        status='active',
        current_version=1,
        is_parent=False,
        parent_id=PARENT_ID,
        split_filter=SPLIT_FILTER,
        source_ref='DT_NSO_0600_003V4.px',
        mdx_file_en=f'data.mn/src/data/data/en/{DATASET_ID}.mdx',
        mdx_file_mn=f'data.mn/src/data/data/mn/{DATASET_ID}.mdx',
        chart_spec=f'data.mn/public/charts/{DATASET_ID}-en.json',
        data_file=f'data.mn/public/datasets/{DATASET_ID}-en.csv'
    )

    reg.add_dataset(dataset)
    action = 'create'

# Log activity
if action != 'exists':
    reg.log_activity(
        action=action,
        status='success',
        dataset_id=DATASET_ID,
        message=f"Created dataset with 60 rows (Feb 2020 - Jan 2025)"
    )

print("\n✓ Registry updated successfully!")
print(f"\nDataset info:")
dataset_info = reg.get_dataset(DATASET_ID)
if dataset_info:
    print(f"  ID: {dataset_info.id}")
    print(f"  EN: {dataset_info.name_en}")
    print(f"  MN: {dataset_info.name_mn}")
    print(f"  Status: {dataset_info.status}")
    print(f"  Parent: {dataset_info.parent_id}")
    print(f"  Version: {dataset_info.current_version}")
