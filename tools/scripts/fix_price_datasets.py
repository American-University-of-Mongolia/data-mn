#!/usr/bin/env python3
"""
Fix price datasets by aligning EN and MN versions.

Uses MN as authoritative source for prices (NSO's native language),
then creates matching EN version with translated labels but same prices.
"""

import pandas as pd
from pathlib import Path

# Region mappings (MN -> EN)
REGION_MAP = {
    'Архангай': 'Arkhangai', 'Баян-Өлгий': 'Bayan-Ulgii', 'Баянхонгор': 'Bayankhongor',
    'Булган': 'Bulgan', 'Дархан-Уул': 'Darkhan-Uul', 'Дорнод': 'Dornod',
    'Дорноговь': 'Dornogovi', 'Дундговь': 'Dundgovi', 'Говь-Алтай': 'Govi-Altai',
    'Говьсүмбэр': 'Govisumber', 'Хэнтий': 'Khentii', 'Ховд': 'Khovd',
    'Хөвсгөл': 'Khuvsgul', 'Орхон': 'Orkhon', 'Сэлэнгэ': 'Selenge',
    'Сүхбаатар': 'Sukhbaatar', 'Төв': 'Tuv', 'Өмнөговь': 'Umnugovi',
    'Увс': 'Uvs', 'Өвөрхангай': 'Uvurkhangai', 'Завхан': 'Zavkhan',
    'Улаанбаатар': 'Ulaanbaatar',
}

# Product mappings (MN -> EN)
PRODUCT_MAP = {
    # Hay/fodder products
    'Ногоон тэжээл': 'Green feed',
    'Задгай өвс': 'Hay',
    'Боодолтой өвс': 'Hay bale',
    # Grain products
    'Овъёос': 'Oat',
    'Таваарын буудай': 'Wheat',
    'Үрийн буудай': 'Wheat seed',
    # Wheat bran
    'Хивэг,25кг': 'Wheat bran, 25kg',
    'Хивэг,50кг': 'Wheat bran, 50kg',
}


def fix_dataset(base_path, dataset_name):
    """Fix a price dataset by using MN as authoritative source."""
    print(f"\n=== Fixing {dataset_name} ===")

    mn_path = base_path / f'{dataset_name}-mn.csv'
    en_path = base_path / f'{dataset_name}-en.csv'

    if not mn_path.exists():
        print(f"  MN file not found: {mn_path}")
        return False

    # Read MN file (authoritative source for prices)
    mn_df = pd.read_csv(mn_path)
    print(f"  MN rows: {len(mn_df)}")

    # MN file has columns: product, region, date, price
    # Values are in Mongolian for product/region

    # Create EN version by translating product/region from MN
    en_df = mn_df.copy()
    en_df['product'] = mn_df['product'].map(PRODUCT_MAP)
    en_df['region'] = mn_df['region'].map(REGION_MAP)

    # Check for unmapped values
    unmapped_products = mn_df[en_df['product'].isna()]['product'].unique()
    unmapped_regions = mn_df[en_df['region'].isna()]['region'].unique()

    if len(unmapped_products) > 0:
        print(f"  Warning: Unmapped products: {list(unmapped_products)}")
        # Keep original MN value if no mapping
        en_df['product'] = en_df['product'].fillna(mn_df['product'])

    if len(unmapped_regions) > 0:
        print(f"  Warning: Unmapped regions: {list(unmapped_regions)}")
        en_df['region'] = en_df['region'].fillna(mn_df['region'])

    # Sort both by a consistent key (date, then EN region, then EN product)
    # For MN, we need to map to EN equivalents for sorting
    mn_df['_sort_region'] = mn_df['region'].map(REGION_MAP).fillna(mn_df['region'])
    mn_df['_sort_product'] = mn_df['product'].map(PRODUCT_MAP).fillna(mn_df['product'])

    mn_df = mn_df.sort_values(by=['date', '_sort_region', '_sort_product']).reset_index(drop=True)
    mn_df = mn_df.drop(columns=['_sort_region', '_sort_product'])

    en_df = en_df.sort_values(by=['date', 'region', 'product']).reset_index(drop=True)

    # Verify numeric alignment
    import numpy as np
    en_prices = en_df['price'].values
    mn_prices = mn_df['price'].values

    if np.allclose(en_prices, mn_prices, equal_nan=True):
        print(f"  ✅ Numeric values aligned ({len(en_df)} rows)")
    else:
        diff_count = np.sum(~np.isclose(en_prices, mn_prices, equal_nan=True))
        print(f"  ❌ Warning: {diff_count} values still differ")

    # Save both files
    en_df.to_csv(en_path, index=False)
    mn_df.to_csv(mn_path, index=False)
    print(f"  Saved {en_path.name}")
    print(f"  Saved {mn_path.name}")

    return True


def main():
    base_path = Path('/Users/dlgvnbyr/Documents/internship/data-mn/data.mn/public/datasets')

    datasets = [
        'hay-prices-by-region',
        'wheat-bran-prices',
        'wheat-prices-by-region',
    ]

    for dataset in datasets:
        fix_dataset(base_path, dataset)

    print("\n" + "="*50)
    print("Verification:")
    print("="*50)

    # Verify all datasets
    for dataset in datasets:
        en_path = base_path / f'{dataset}-en.csv'
        mn_path = base_path / f'{dataset}-mn.csv'

        en_df = pd.read_csv(en_path)
        mn_df = pd.read_csv(mn_path)

        # Compare price columns
        import numpy as np
        en_prices = en_df['price'].values
        mn_prices = mn_df.iloc[:, 3].values

        if len(en_prices) == len(mn_prices) and np.allclose(en_prices, mn_prices, equal_nan=True):
            print(f"  ✅ {dataset}: {len(en_df)} rows, prices match")
        else:
            print(f"  ❌ {dataset}: EN={len(en_df)}, MN={len(mn_df)} rows, prices differ")


if __name__ == '__main__':
    main()
