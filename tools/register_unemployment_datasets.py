#!/usr/bin/env python3
"""
Register unemployment datasets in the registry
"""

import sys
import os

# Add tools directory to path
sys.path.insert(0, '/Users/ritz/Insync/robert@aum.edu.mn/Google Drive/data/tools')

from registry import Registry, Dataset

reg = Registry()

print("Registering unemployment datasets...")
print("=" * 50)

# Check if datasets already exist
existing_national = reg.get_dataset('unemployment-rate-national')
existing_sex = reg.get_dataset('unemployment-by-sex')

if existing_national:
    print("⚠️  Dataset 'unemployment-rate-national' already exists")
    print(f"   Status: {existing_national.status}")
else:
    # Register national unemployment dataset
    print("\n1. Registering unemployment-rate-national...")

    dataset_national = Dataset(
        id='unemployment-rate-national',
        source_id='nso-1212',
        name_en='Mongolia National Unemployment Rate (2009-2024)',
        name_mn='Монгол Улсын ажилгүйдлийн түвшин (2009-2024)',
        category_en='Economy',
        category_mn='Эдийн засаг',
        definition_path='sources/nso-1212/DT_NSO_0400_049V1.px',
        is_parent=True,
        status='active',
        current_version=1,
        tags=['mongolia', 'unemployment', 'economy', 'labor', 'labor-market', 'statistics', 'nso'],
        keywords_en=['mongolia unemployment rate', 'labor market', 'jobless rate', 'economy', 'economic indicators'],
        source_ref='DT_NSO_0400_049V1.px',
        source_path='https://data.1212.mn',
        mdx_file_en='src/data/data/en/unemployment-rate-national.mdx',
        mdx_file_mn='src/data/data/mn/unemployment-rate-national.mdx',
        chart_spec='public/charts/unemployment-rate-national-en.json',
        data_file='public/datasets/unemployment-rate-national-en.csv'
    )

    reg.add_dataset(dataset_national)
    print("   ✓ Registered successfully")

    reg.log_activity(
        action='create',
        status='success',
        dataset_id='unemployment-rate-national',
        message='Created national unemployment dataset with 16 rows (2009-2024)'
    )

if existing_sex:
    print("⚠️  Dataset 'unemployment-by-sex' already exists")
    print(f"   Status: {existing_sex.status}")
else:
    # Register unemployment by sex dataset
    print("\n2. Registering unemployment-by-sex...")

    dataset_sex = Dataset(
        id='unemployment-by-sex',
        source_id='nso-1212',
        name_en='Mongolia Unemployment Rate by Sex (2009-2024)',
        name_mn='Монгол Улсын ажилгүйдлийн түвшин хүйсээр (2009-2024)',
        category_en='Economy',
        category_mn='Эдийн засаг',
        definition_path='sources/nso-1212/DT_NSO_0400_049V1.px',
        is_parent=False,
        parent_id='unemployment-rate-national',
        split_filter={'Category': ['Male', 'Female']},
        status='active',
        current_version=1,
        tags=['mongolia', 'unemployment', 'economy', 'labor', 'gender', 'labor-market', 'statistics', 'nso'],
        keywords_en=['mongolia unemployment rate', 'unemployment by sex', 'gender labor market', 'male female unemployment'],
        source_ref='DT_NSO_0400_049V1.px',
        source_path='https://data.1212.mn',
        mdx_file_en='src/data/data/en/unemployment-by-sex.mdx',
        mdx_file_mn='src/data/data/mn/unemployment-by-sex.mdx',
        chart_spec='public/charts/unemployment-by-sex-en.json',
        data_file='public/datasets/unemployment-by-sex-en.csv'
    )

    reg.add_dataset(dataset_sex)
    print("   ✓ Registered successfully")

    reg.log_activity(
        action='create',
        status='success',
        dataset_id='unemployment-by-sex',
        message='Created unemployment by sex dataset with 32 rows (2009-2024)'
    )

print("\n" + "=" * 50)
print("✓ Registration complete!")
print("\nNext step: Publish datasets to assign permanent URLs")
print("  python -m registry publish unemployment-rate-national")
print("  python -m registry publish unemployment-by-sex")
