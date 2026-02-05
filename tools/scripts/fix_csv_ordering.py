#!/usr/bin/env python3
"""
Fix EN/MN CSV row ordering to ensure numeric values align row-by-row.

Both language versions should have identical row order so that numeric
values at each position match. This script:
1. Reads EN and MN CSV pairs
2. Creates a mapping between EN and MN category names
3. Sorts both files using English category names as the key
4. Writes back aligned files
"""

import pandas as pd
import sys
from pathlib import Path

# Datasets that need fixing and their structure
DATASETS = {
    'crop-prices-national': {
        'category_col': 'product',
        'sort_cols': ['date', 'product'],  # After mapping
    },
    'hay-prices-by-region': {
        'category_col': 'product',  # Also has region
        'region_col': 'region',
        'sort_cols': ['date', 'region', 'product'],
    },
    'kindergartens-by-region': {
        'category_col': 'region',
        'sort_cols': ['year', 'region'],
    },
    'sown-area-by-crop-type': {
        'category_col': 'crop_type',
        'sort_cols': ['year', 'crop_type'],
    },
    'sown-area-by-region': {
        'category_col': 'region',
        'sort_cols': ['year', 'region'],
    },
    'wheat-bran-prices': {
        'category_col': 'product',
        'region_col': 'region',
        'sort_cols': ['date', 'region', 'product'],
    },
    'wheat-prices-by-region': {
        'category_col': 'product',
        'region_col': 'region',
        'sort_cols': ['date', 'region', 'product'],
    },
}

# Standard region mappings (EN -> MN)
REGION_MAP = {
    'Arkhangai': 'Архангай',
    'Bayan-Ulgii': 'Баян-Өлгий',
    'Bayankhongor': 'Баянхонгор',
    'Bulgan': 'Булган',
    'Darkhan-Uul': 'Дархан-Уул',
    'Dornod': 'Дорнод',
    'Dornogovi': 'Дорноговь',
    'Dundgovi': 'Дундговь',
    'Govi-Altai': 'Говь-Алтай',
    'Govisumber': 'Говьсүмбэр',
    'Khentii': 'Хэнтий',
    'Khovd': 'Ховд',
    'Khuvsgul': 'Хөвсгөл',
    'Orkhon': 'Орхон',
    'Selenge': 'Сэлэнгэ',
    'Sukhbaatar': 'Сүхбаатар',
    'Tuv': 'Төв',
    'Umnugovi': 'Өмнөговь',
    'Uvs': 'Увс',
    'Uvurkhangai': 'Өвөрхангай',
    'Zavkhan': 'Завхан',
    'Ulaanbaatar': 'Улаанбаатар',
}

# Reverse mapping (MN -> EN)
REGION_MAP_REV = {v: k for k, v in REGION_MAP.items()}

# Product mappings for price datasets (EN -> MN)
PRODUCT_MAP = {
    # crop-prices-national and hay-prices
    'Green feed': 'Ногоон тэжээл',
    'Hay': 'Задгай өвс',
    'Hay bale': 'Боодолтой өвс',
    'Oat': 'Овъёос',
    'Wheat': 'Таваарын буудай',
    'Wheat seed': 'Үрийн буудай',
    # wheat-bran-prices and crop-prices
    'Wheat bran, 25kg': 'Хивэг,25кг',
    'Wheat bran, 50kg': 'Хивэг,50кг',
}

# Reverse product mapping (MN -> EN)
PRODUCT_MAP_REV = {v: k for k, v in PRODUCT_MAP.items()}

# Crop type mappings for sown area
CROP_TYPE_MAP = {
    'Cereals': 'Үр тариа',
    'Industrial crops': 'Техникийн ургамал',
    'Fodder crops': 'Тэжээлийн ургамал',
    'Potatoes': 'Төмс',
    'Vegetables': 'Хүнсний ногоо',
    'Others': 'Бусад',
}

CROP_TYPE_MAP_REV = {v: k for k, v in CROP_TYPE_MAP.items()}


def build_category_mapping(en_df, mn_df, cat_col_en, cat_col_mn):
    """Build a mapping between EN and MN category names based on known mappings."""
    en_cats = set(en_df[cat_col_en].unique())

    # Check if it's a region column - use known mapping
    if all(c in REGION_MAP for c in en_cats):
        return REGION_MAP, REGION_MAP_REV

    # Check if it's a product column - use known mapping
    if all(c in PRODUCT_MAP for c in en_cats):
        return PRODUCT_MAP, PRODUCT_MAP_REV

    # Check if it's a crop type column - use known mapping
    if all(c in CROP_TYPE_MAP for c in en_cats):
        return CROP_TYPE_MAP, CROP_TYPE_MAP_REV

    # Fallback: try to infer from value matching
    # For each date, find pairs with matching numeric values
    print(f"  Warning: No predefined mapping for categories in {cat_col_en}")
    print(f"    EN categories: {en_cats}")

    # Return empty mapping - will fail validation
    return {}, {}


def fix_dataset(base_path, dataset_name, config, fix_all=True):
    """Fix row ordering for a single dataset."""
    print(f"\nProcessing: {dataset_name}")

    # File patterns to process
    patterns = [
        (f'{dataset_name}-en.csv', f'{dataset_name}-mn.csv'),
    ]
    if fix_all:
        patterns.append((f'{dataset_name}-all-en.csv', f'{dataset_name}-all-mn.csv'))

    for en_file, mn_file in patterns:
        en_path = base_path / en_file
        mn_path = base_path / mn_file

        if not en_path.exists() or not mn_path.exists():
            print(f"  Skipping {en_file} - files not found")
            continue

        print(f"  Fixing {en_file} and {mn_file}...")

        # Read CSVs
        en_df = pd.read_csv(en_path)
        mn_df = pd.read_csv(mn_path)

        # Get column names
        en_cols = list(en_df.columns)
        mn_cols = list(mn_df.columns)

        cat_col = config['category_col']
        cat_col_en = cat_col  # EN column name
        cat_col_mn = mn_cols[en_cols.index(cat_col)]  # Corresponding MN column

        # Build category mapping
        cat_map, cat_map_rev = build_category_mapping(en_df, mn_df, cat_col_en, cat_col_mn)

        # Handle region column if present
        if 'region_col' in config:
            reg_col = config['region_col']
            reg_col_en = reg_col
            reg_col_mn = mn_cols[en_cols.index(reg_col)]

        # Add sort key to MN dataframe (mapped to EN values)
        mn_df['_sort_cat'] = mn_df[cat_col_mn].map(cat_map_rev)
        if '_sort_cat' in mn_df.columns and mn_df['_sort_cat'].isna().any():
            # Fall back to original if mapping incomplete
            mn_df['_sort_cat'] = mn_df['_sort_cat'].fillna(mn_df[cat_col_mn])

        if 'region_col' in config:
            mn_df['_sort_reg'] = mn_df[reg_col_mn].map(REGION_MAP_REV)
            if mn_df['_sort_reg'].isna().any():
                mn_df['_sort_reg'] = mn_df['_sort_reg'].fillna(mn_df[reg_col_mn])

        # Determine sort columns
        sort_cols = config['sort_cols']
        en_sort_cols = sort_cols.copy()
        mn_sort_cols = []

        for col in sort_cols:
            if col == cat_col:
                mn_sort_cols.append('_sort_cat')
            elif 'region_col' in config and col == config['region_col']:
                mn_sort_cols.append('_sort_reg')
            else:
                # Map column name to MN
                try:
                    idx = en_cols.index(col)
                    mn_sort_cols.append(mn_cols[idx])
                except ValueError:
                    mn_sort_cols.append(col)

        # Sort both dataframes
        en_df_sorted = en_df.sort_values(by=en_sort_cols).reset_index(drop=True)
        mn_df_sorted = mn_df.sort_values(by=mn_sort_cols).reset_index(drop=True)

        # Drop helper columns
        if '_sort_cat' in mn_df_sorted.columns:
            mn_df_sorted = mn_df_sorted.drop(columns=['_sort_cat'])
        if '_sort_reg' in mn_df_sorted.columns:
            mn_df_sorted = mn_df_sorted.drop(columns=['_sort_reg'])

        # Verify alignment
        # Extract numeric columns and compare (by position, not name)
        en_nums = en_df_sorted.select_dtypes(include=['number']).values
        mn_nums = mn_df_sorted.select_dtypes(include=['number']).values

        if en_nums.shape != mn_nums.shape:
            print(f"    Warning: Shape mismatch after sorting: EN={en_nums.shape}, MN={mn_nums.shape}")
        else:
            # Compare numeric values
            import numpy as np
            if np.allclose(en_nums, mn_nums, equal_nan=True):
                print(f"    Numeric values aligned")
            else:
                # Find first difference
                diff_mask = ~np.isclose(en_nums, mn_nums, equal_nan=True)
                idx = np.argmax(diff_mask.any(axis=1))
                col_idx = np.argmax(diff_mask[idx])
                print(f"    Warning: Numeric values still differ after sorting")
                print(f"      First diff at row {idx}: EN={en_nums[idx, col_idx]}, MN={mn_nums[idx, col_idx]}")

        # Write back
        en_df_sorted.to_csv(en_path, index=False)
        mn_df_sorted.to_csv(mn_path, index=False)
        print(f"    Wrote {en_file} and {mn_file}")


def main():
    base_path = Path('/Users/dlgvnbyr/Documents/internship/data-mn/data.mn/public/datasets')

    if len(sys.argv) > 1:
        # Process specific datasets
        datasets = sys.argv[1:]
    else:
        # Process all failing datasets
        datasets = list(DATASETS.keys())

    for dataset in datasets:
        if dataset not in DATASETS:
            print(f"Unknown dataset: {dataset}")
            continue
        fix_dataset(base_path, dataset, DATASETS[dataset])

    print("\nDone! Run validation to verify fixes.")


if __name__ == '__main__':
    main()
