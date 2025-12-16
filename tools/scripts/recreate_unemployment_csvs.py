#!/usr/bin/env python3
"""
Recreate unemployment CSVs with proper bilingual support.
"""

import pandas as pd
from pathlib import Path

# Paths
DATA_DIR = Path(__file__).parent.parent.parent
SOURCE_EN = DATA_DIR / "data.mn" / "src" / "data" / "datasets" / "nso-0400-049v1-en.csv"
SOURCE_MN = DATA_DIR / "data.mn" / "src" / "data" / "datasets" / "nso-0400-049v1-mn.csv"
OUTPUT_DIR = DATA_DIR / "data.mn" / "public" / "datasets"

# Category translations (EXACT matches from the data)
CATEGORY_MAP = {
    "Total": "Бүгд",
    "Male": "Эрэгтэй",
    "Female": "Эмэгтэй",
    "Urban": "Хот",
    "Rural": "Хөдөө",
    "15-24": "15-24 насны",
    "25-64": "25-64 насны",
    "65+": "65 болон түүнээс дээш насны",
    "Western region": "Баруун бүс",
    "Khangai region": "Хангайн бүс",
    "Central region": "Төвийн бүс",
    "Eastern region": "Зүүн бүс",
    "Ulaanbaatar": "Улаанбаатар",
    "With disabilities": "Хөгжлийн бэрхшээлтэй",
    "No disabilities": "Хөгжлийн бэрхшээлгүй"
}

# Dataset filters (using English category names)
DATASETS = [
    {
        "id": "unemployment-rate-total",
        "filter": {"Category": "Total"}
    },
    {
        "id": "unemployment-rate-by-sex",
        "filter": {"Category": ["Male", "Female"]}
    },
    {
        "id": "unemployment-rate-youth",
        "filter": {"Category": "15-24"}
    },
    {
        "id": "unemployment-rate-by-age",
        "filter": {"Category": ["15-24", "25-64", "65+"]}
    },
    {
        "id": "unemployment-rate-by-location",
        "filter": {"Category": ["Urban", "Rural", "Ulaanbaatar"]}
    },
    {
        "id": "unemployment-rate-by-region",
        "filter": {"Category": ["Central region", "Western region", "Khangai region", "Eastern region"]}
    }
]


def clean_df(df, lang='en'):
    """Clean dataframe and standardize column names."""
    # Rename columns
    if lang == 'en':
        column_map = {'Category': 'category', 'Year': 'year'}
    else:
        column_map = {'Ангилал': 'category', 'Он': 'year'}
    
    df = df.rename(columns=column_map)
    
    # Strip whitespace
    df['category'] = df['category'].str.strip()
    
    return df


def apply_filter_en(df, filter_spec):
    """Apply filter to English dataframe."""
    result = df.copy()
    for column, value in filter_spec.items():
        col_lower = column.lower()
        if isinstance(value, list):
            result = result[result[col_lower].isin(value)]
        else:
            result = result[result[col_lower] == value]
    return result


def apply_filter_mn(df, filter_spec):
    """Apply filter to Mongolian dataframe (translating category values)."""
    result = df.copy()
    for column, value in filter_spec.items():
        col_lower = column.lower()
        if isinstance(value, list):
            # Translate each value to Mongolian
            mn_values = [CATEGORY_MAP[v] for v in value]
            result = result[result[col_lower].isin(mn_values)]
        else:
            # Translate single value to Mongolian
            mn_value = CATEGORY_MAP[value]
            result = result[result[col_lower] == mn_value]
    return result


def main():
    print("=" * 70)
    print("Recreating Unemployment CSV Files")
    print("=" * 70)
    
    # Load source data
    print("\nLoading source data...")
    df_en = pd.read_csv(SOURCE_EN)
    df_mn = pd.read_csv(SOURCE_MN)
    
    df_en = clean_df(df_en, 'en')
    df_mn = clean_df(df_mn, 'mn')
    
    print(f"  English: {len(df_en)} rows")
    print(f"  Mongolian: {len(df_mn)} rows")
    
    # Create parent dataset
    print("\nCreating parent dataset...")
    df_en.to_csv(OUTPUT_DIR / "nso-unemployment-rate-en.csv", index=False)
    df_mn.to_csv(OUTPUT_DIR / "nso-unemployment-rate-mn.csv", index=False)
    print(f"  ✓ nso-unemployment-rate-en.csv ({len(df_en)} rows)")
    print(f"  ✓ nso-unemployment-rate-mn.csv ({len(df_mn)} rows)")
    
    # Create split datasets
    print("\nCreating split datasets...")
    for dataset in DATASETS:
        dataset_id = dataset["id"]
        
        # Apply filter
        df_split_en = apply_filter_en(df_en, dataset["filter"])
        df_split_mn = apply_filter_mn(df_mn, dataset["filter"])
        
        # Save CSVs
        df_split_en.to_csv(OUTPUT_DIR / f"{dataset_id}-en.csv", index=False)
        df_split_mn.to_csv(OUTPUT_DIR / f"{dataset_id}-mn.csv", index=False)
        
        print(f"  ✓ {dataset_id}-en.csv ({len(df_split_en)} rows)")
        print(f"  ✓ {dataset_id}-mn.csv ({len(df_split_mn)} rows)")
        
        # Create XLSX with both languages
        xlsx_path = OUTPUT_DIR / f"{dataset_id}.xlsx"
        with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
            df_split_en.to_excel(writer, sheet_name='English', index=False)
            df_split_mn.to_excel(writer, sheet_name='Mongolian', index=False)
        
        print(f"  ✓ {dataset_id}.xlsx")
    
    print("\n" + "=" * 70)
    print("COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
