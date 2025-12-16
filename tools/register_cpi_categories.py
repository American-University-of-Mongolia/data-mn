#!/usr/bin/env python3
"""
Register cpi-by-category-ulaanbaatar as a split dataset
"""
import json
import sys
from pathlib import Path

# Add tools directory to path
TOOLS_DIR = Path(__file__).parent
sys.path.insert(0, str(TOOLS_DIR))

from registry import Registry, Dataset

reg = Registry()

# Register the split dataset
dataset_id = 'cpi-by-category-ulaanbaatar'
parent_id = 'nso-cpi-ulaanbaatar-mom'

# Split filter configuration
split_filter = {
    'reference_year': '2023=100',
    'month': 'latest',
    'group': 'NOT Overall index'
}

try:
    # Check if dataset already exists
    existing = reg.get_dataset(dataset_id)

    if existing:
        print(f"Dataset {dataset_id} already exists. Skipping registration.")
        action = 'update'
    else:
        print(f"Creating new dataset {dataset_id}...")

        dataset = Dataset(
            id=dataset_id,
            source_id='nso-1212',
            name_en='CPI by Category in Ulaanbaatar, % (November 2025)',
            category_en='Economy',
            definition_path='tools/sources/nso-1212/datasets/nso-cpi-ulaanbaatar-mom.md',
            name_mn='Улаанбаатар хотын ХҮИ ангиллаар, % (2025 оны 11-р сар)',
            category_mn='Эдийн засаг',
            description_en='Month-on-month consumer price index changes by expenditure category in Ulaanbaatar for November 2025.',
            description_mn='2025 оны 11-р сарын Улаанбаатар хотын хэрэглээний үнийн индексийн сараас сард өөрчлөлт зарлагын бүлгээр.',
            tags=['mongolia', 'cpi', 'inflation', 'prices', 'ulaanbaatar', 'categories', 'consumer-prices'],
            keywords_en=['mongolia cpi', 'inflation categories', 'ulaanbaatar prices', 'consumer price index'],
            source_ref='DT_NSO_0600_003V4.px',
            status='active',
            current_version=1,
            data_file='datasets/cpi-by-category-ulaanbaatar-en.csv',
            mdx_file_en='data/data/en/cpi-by-category-ulaanbaatar.mdx',
            mdx_file_mn='data/data/mn/cpi-by-category-ulaanbaatar.mdx',
            chart_spec='charts/cpi-by-category-ulaanbaatar-en.json',
            is_parent=False,
            parent_id=parent_id,
            split_filter=split_filter
        )

        reg.add_dataset(dataset)
        action = 'create'

    # Log the activity
    reg.log_activity(
        action=action,
        status='success',
        dataset_id=dataset_id,
        message=f"{'Created' if action == 'create' else 'Updated'} split dataset with 13 categories from November 2025 data"
    )

    print(f"\n✅ SUCCESS: Dataset {dataset_id} registered!")
    print(f"   Parent: {parent_id}")
    print(f"   Split filter: {json.dumps(split_filter, indent=2)}")
    print(f"   Status: active")
    print(f"   Version: 1")

    # Show dataset info
    dataset = reg.get_dataset(dataset_id)
    if dataset:
        print(f"\nDataset info:")
        print(f"   ID: {dataset.id}")
        print(f"   Name (EN): {dataset.name_en}")
        print(f"   Name (MN): {dataset.name_mn}")
        print(f"   Source: {dataset.source_id}")
        print(f"   Category: {dataset.category_en}")
        print(f"   Parent: {dataset.parent_id}")
        print(f"   Split filter: {dataset.split_filter}")

except Exception as e:
    print(f"\n❌ ERROR: Failed to register dataset")
    print(f"   {str(e)}")
    import traceback
    traceback.print_exc()
    reg.log_activity(
        action='create',
        status='error',
        dataset_id=dataset_id,
        message=f"Failed to register dataset: {str(e)}"
    )
    sys.exit(1)
