#!/usr/bin/env python3
"""
Regenerate weekly price datasets with new file patterns:
- Chart CSV: 4-6 representative regions (long form)
- Download CSV: ALL regions (long form)
- Download XLSX: ALL regions (wide/pivot form)
"""

import pandas as pd
import os
from openpyxl.utils import get_column_letter

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(SCRIPT_DIR)  # data/tools
BASE_DIR = os.path.dirname(TOOLS_DIR)     # data/
DATA_MN_DIR = os.path.join(BASE_DIR, "data.mn")
DATASETS_DIR = os.path.join(DATA_MN_DIR, "public", "datasets")
PARENT_DIR = os.path.join(TOOLS_DIR, "versions", "nso-weekly-prices-main-products")

# Load parent data
print("Loading parent data...")
df_en = pd.read_csv(os.path.join(PARENT_DIR, "nso-0300-010v5-en.csv"))
df_mn = pd.read_csv(os.path.join(PARENT_DIR, "nso-0300-010v5-mn.csv"))

print(f"Parent data: {len(df_en)} rows")
print(f"Unique products (EN): {df_en['Products'].nunique()}")
print(f"Unique regions (EN): {df_en['Region'].nunique()}")
print(f"Date range: {df_en['Time'].min()} to {df_en['Time'].max()}")

# Chart subset - 4 representative regions
CHART_REGIONS_EN = ["Darkhan-Uul", "Khovd", "Orkhon", "Umnugovi"]
CHART_REGIONS_MN = ["Дархан-Уул", "Ховд", "Орхон", "Өмнөговь"]

# Product mappings (EN product name -> dataset config)
PRODUCTS = [
    {
        "id": "weekly-beef-prices",
        "filter_en": "Beef",
        "filter_mn": "Үхрийн мах",
    },
    {
        "id": "weekly-mutton-prices",
        "filter_en": "Mutton",
        "filter_mn": "Хонины мах",
    },
    {
        "id": "weekly-flour-prices",
        "filter_en": "Flour",
        "filter_mn": "Гурил",
    },
    {
        "id": "weekly-milk-prices",
        "filter_en": "Milk",
        "filter_mn": "Сүү",
    },
    {
        "id": "weekly-gasoline-prices",
        "filter_en": "Petrol",  # A-92
        "filter_mn": "Аи-92 автобензин",
    },
    {
        "id": "weekly-diesel-prices",
        "filter_en": "Diesel fuel",
        "filter_mn": "Дизелийн түлш",
    },
]

def filter_product(df, product_filter, lang='en'):
    """Filter dataframe to rows containing the product filter string."""
    col = 'Products' if lang == 'en' else 'Бүтээгдэхүүн'
    return df[df[col].str.contains(product_filter, case=False, na=False)].copy()

def clean_columns(df, lang):
    """Rename columns to standard names."""
    if lang == 'en':
        df = df.rename(columns={
            'Products': 'product',
            'Region': 'region',
            'Time': 'date',
            'value': 'price'
        })
    else:
        df = df.rename(columns={
            'Бүтээгдэхүүн': 'product',
            'Бүс': 'region',
            'Хугацаа': 'date',
            'value': 'price'
        })
    return df

def export_xlsx_wide(df, dataset_id, time_col='date', category_col='region', value_col='price'):
    """Export to Excel in wide/pivot format."""
    xlsx_path = os.path.join(DATASETS_DIR, f"{dataset_id}.xlsx")

    # Pivot to wide format
    if category_col and category_col in df.columns:
        wide_df = df.pivot_table(
            index=time_col,
            columns=category_col,
            values=value_col,
            aggfunc='first'
        ).reset_index()
    else:
        wide_df = df.copy()

    # Sort by date descending (newest first)
    wide_df = wide_df.sort_values(time_col, ascending=False)

    # Export with formatting
    with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
        wide_df.to_excel(writer, index=False, sheet_name='Data')

        # Auto-adjust column widths
        worksheet = writer.sheets['Data']
        for idx, col in enumerate(wide_df.columns):
            max_length = max(
                wide_df[col].astype(str).map(len).max(),
                len(str(col))
            ) + 2
            col_letter = get_column_letter(idx + 1)
            worksheet.column_dimensions[col_letter].width = min(max_length, 20)

    return xlsx_path, len(wide_df)

def process_product(product_config):
    """Process a single product and generate all files."""
    dataset_id = product_config['id']
    filter_en = product_config['filter_en']
    filter_mn = product_config['filter_mn']

    print(f"\n{'='*60}")
    print(f"Processing: {dataset_id}")
    print(f"{'='*60}")

    # Filter to this product
    prod_en = filter_product(df_en, filter_en, lang='en')
    prod_mn = filter_product(df_mn, filter_mn, lang='mn')

    print(f"  Filtered rows (EN): {len(prod_en)}")
    print(f"  Filtered rows (MN): {len(prod_mn)}")

    # Clean columns
    prod_en = clean_columns(prod_en, 'en')
    prod_mn = clean_columns(prod_mn, 'mn')

    # Drop product column (now redundant since each file is single product)
    prod_en = prod_en.drop(columns=['product'])
    prod_mn = prod_mn.drop(columns=['product'])

    # Drop rows with missing prices
    prod_en = prod_en.dropna(subset=['price'])
    prod_mn = prod_mn.dropna(subset=['price'])

    # Sort by date, then region
    prod_en = prod_en.sort_values(['date', 'region'])
    prod_mn = prod_mn.sort_values(['date', 'region'])

    print(f"  After cleaning (EN): {len(prod_en)} rows")
    print(f"  Unique regions: {prod_en['region'].nunique()}")

    # 1. Chart CSV (subset of regions)
    chart_en = prod_en[prod_en['region'].isin(CHART_REGIONS_EN)].copy()
    chart_mn = prod_mn[prod_mn['region'].isin(CHART_REGIONS_MN)].copy()

    chart_en_path = os.path.join(DATASETS_DIR, f"{dataset_id}-en.csv")
    chart_mn_path = os.path.join(DATASETS_DIR, f"{dataset_id}-mn.csv")

    chart_en.to_csv(chart_en_path, index=False)
    chart_mn.to_csv(chart_mn_path, index=False)

    print(f"  Chart CSV (EN): {len(chart_en)} rows -> {chart_en_path}")
    print(f"  Chart CSV (MN): {len(chart_mn)} rows -> {chart_mn_path}")

    # 2. Download CSV (ALL regions, long form)
    full_en_path = os.path.join(DATASETS_DIR, f"{dataset_id}-all-en.csv")
    full_mn_path = os.path.join(DATASETS_DIR, f"{dataset_id}-all-mn.csv")

    prod_en.to_csv(full_en_path, index=False)
    prod_mn.to_csv(full_mn_path, index=False)

    print(f"  Full CSV (EN): {len(prod_en)} rows -> {full_en_path}")
    print(f"  Full CSV (MN): {len(prod_mn)} rows -> {full_mn_path}")

    # 3. Download XLSX (ALL regions, wide format) - use English data
    xlsx_path, xlsx_rows = export_xlsx_wide(prod_en, dataset_id)
    print(f"  XLSX (wide): {xlsx_rows} rows x {prod_en['region'].nunique()+1} cols -> {xlsx_path}")

    return {
        'dataset_id': dataset_id,
        'chart_rows': len(chart_en),
        'full_rows': len(prod_en),
        'regions': prod_en['region'].nunique(),
        'dates': prod_en['date'].nunique(),
    }

# Process all products
results = []
for product in PRODUCTS:
    result = process_product(product)
    results.append(result)

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
for r in results:
    print(f"  {r['dataset_id']}: {r['chart_rows']} chart rows, {r['full_rows']} total rows ({r['regions']} regions)")

print("\nDone! Files generated in:", DATASETS_DIR)
print("\nNote: MDX files need to be updated to reference -all-{lang}.csv for downloads.")
