#!/usr/bin/env python3
"""
Register trade datasets in the registry database.
"""

import sys
import os
from pathlib import Path

# Add registry module to path
sys.path.insert(0, str(Path(__file__).parent))

from registry import Registry, Dataset

# Initialize registry
reg = Registry()

# Dataset 1: trade-total (parent)
print("Registering trade-total...")
dataset1 = Dataset(
    id='trade-total',
    name_en='Mongolia Total Foreign Trade (1924-2024)',
    name_mn='Монгол Улсын гадаад худалдааны нийт эргэлт (1924-2024)',
    source_id='nso-1212',
    category_en='Economy',
    category_mn='Эдийн засаг',
    definition_path='tools/sources/nso-1212/datasets/DT_NSO_1400_001V1_year.md',
    is_parent=True,
    status='active',
    current_version=1
)
reg.add_dataset(dataset1)

reg.log_activity(
    action='create',
    status='success',
    dataset_id='trade-total',
    message='Created dataset with 101 rows (1924-2024)'
)

# Dataset 2: trade-exports-imports (split)
print("Registering trade-exports-imports...")
dataset2 = Dataset(
    id='trade-exports-imports',
    name_en='Mongolia Exports and Imports (1924-2024)',
    name_mn='Монгол Улсын экспорт, импорт (1924-2024)',
    source_id='nso-1212',
    category_en='Economy',
    category_mn='Эдийн засаг',
    definition_path='tools/sources/nso-1212/datasets/DT_NSO_1400_001V1_year.md',
    is_parent=False,
    parent_id='trade-total',
    split_filter={"indicator": ["Exports", "Imports"]},
    status='active',
    current_version=1
)
reg.add_dataset(dataset2)

reg.log_activity(
    action='create',
    status='success',
    dataset_id='trade-exports-imports',
    message='Created split dataset with 202 rows (1924-2024)'
)

print("\n✅ Datasets registered successfully!")
print("\nSummary:")
print("  trade-total: 101 rows, parent dataset")
print("  trade-exports-imports: 202 rows, split from trade-total")
