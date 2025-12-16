#!/usr/bin/env python3
"""
Process Foreign Trade data from NSO 1212.mn
Creates parent dataset and split datasets for each indicator
"""

import pandas as pd
import json
import sys
from pathlib import Path

# Add registry to path
sys.path.insert(0, str(Path(__file__).parent.parent / "registry"))
from registry import Registry, Dataset, Source

# Paths
DATA_DIR = Path(__file__).parent.parent.parent
VERSIONS_DIR = DATA_DIR / "tools" / "versions"
PUBLIC_DATASETS = DATA_DIR / "data.mn" / "public" / "datasets"
PUBLIC_CHARTS = DATA_DIR / "data.mn" / "public" / "charts"
MDX_DIR_EN = DATA_DIR / "data.mn" / "src" / "data" / "data" / "en"
MDX_DIR_MN = DATA_DIR / "data.mn" / "src" / "data" / "data" / "mn"

# Ensure directories exist
PUBLIC_DATASETS.mkdir(parents=True, exist_ok=True)
PUBLIC_CHARTS.mkdir(parents=True, exist_ok=True)
MDX_DIR_EN.mkdir(parents=True, exist_ok=True)
MDX_DIR_MN.mkdir(parents=True, exist_ok=True)

def clean_column_names(df):
    """Standardize column names"""
    df.columns = [c.lower().replace(' ', '_').replace(',', '') for c in df.columns]
    return df

def process_foreign_trade():
    """Process foreign trade data"""

    # Load source data
    source_en = VERSIONS_DIR / "nso-foreign-trade-yearly" / "v1" / "nso-1400-001v1-year-en.csv"
    source_mn = VERSIONS_DIR / "nso-foreign-trade-yearly" / "v1" / "nso-1400-001v1-year-mn.csv"

    df_en = pd.read_csv(source_en)
    df_mn = pd.read_csv(source_mn)

    # Clean column names
    df_en = clean_column_names(df_en)
    df_mn = clean_column_names(df_mn)

    print(f"Loaded {len(df_en)} rows from source data")
    print(f"English columns: {list(df_en.columns)}")
    print(f"Mongolian columns: {list(df_mn.columns)}")
    print(f"\nIndicators in English: {df_en['main_indicators_of_foreign_trade'].unique()}")
    print(f"Indicators in Mongolian: {df_mn['гадаад_худалдааны_үндсэн_үзүүлэлт'].unique()}")

    # Save parent dataset (all data)
    parent_id = "nso-foreign-trade-yearly"
    df_en.to_csv(PUBLIC_DATASETS / f"{parent_id}-en.csv", index=False)
    df_mn.to_csv(PUBLIC_DATASETS / f"{parent_id}-mn.csv", index=False)

    # Create Excel files for parent
    df_en.to_excel(PUBLIC_DATASETS / f"{parent_id}-en.xlsx", index=False, sheet_name='Data')
    df_mn.to_excel(PUBLIC_DATASETS / f"{parent_id}-mn.xlsx", index=False, sheet_name='Data')

    print(f"\nSaved parent dataset: {parent_id}")

    # Define split datasets
    splits = [
        {
            "id": "foreign-trade-mongolia",
            "title_en": "Foreign Trade Turnover - Mongolia",
            "title_mn": "Гадаад худалдаа - Монгол улс",
            "filter_en": "Total turnover",
            "filter_mn": "Нийт эргэлт",
            "description_en": "Total foreign trade turnover of Mongolia from 1924 to present, showing the combined value of exports and imports in million USD.",
            "description_mn": "Монгол улсын 1924 оноос хойшхи нийт гадаад худалдааны эргэлт, экспорт, импортын нийлбэр үнэ дүнг сая ам.доллараар харуулсан.",
        },
        {
            "id": "exports-mongolia",
            "title_en": "Exports - Mongolia",
            "title_mn": "Экспорт - Монгол улс",
            "filter_en": " Exports",
            "filter_mn": "Экспорт",
            "description_en": "Total value of goods exported from Mongolia from 1924 to present in million USD.",
            "description_mn": "Монгол улсаас 1924 оноос хойш экспортолсон нийт бараа бүтээгдэхүүний үнэ дүнг сая ам.доллараар харуулсан.",
        },
        {
            "id": "imports-mongolia",
            "title_en": "Imports - Mongolia",
            "title_mn": "Импорт - Монгол улс",
            "filter_en": " Imports",
            "filter_mn": "Импорт",
            "description_en": "Total value of goods imported into Mongolia from 1924 to present in million USD.",
            "description_mn": "Монгол улс руу 1924 оноос хойш импортолсон нийт бараа бүтээгдэхүүний үнэ дүнг сая ам.доллараар харуулсан.",
        },
        {
            "id": "trade-balance-mongolia",
            "title_en": "Trade Balance - Mongolia",
            "title_mn": "Худалдааны тэнцэл - Монгол улс",
            "filter_en": " Balance",
            "filter_mn": "Тэнцэл",
            "description_en": "Mongolia's trade balance (exports minus imports) from 1924 to present in million USD. Positive values indicate trade surplus, negative values indicate trade deficit.",
            "description_mn": "Монгол улсын 1924 оноос хойшхи худалдааны тэнцэл (экспорт хасах импорт) сая ам.доллараар. Эерэг утга нь худалдааны ашиг, сөрөг утга нь алдагдлыг илэрхийлнэ.",
        },
    ]

    # Process each split
    stats = {}
    for split in splits:
        split_id = split["id"]

        # Filter data - use original column names before cleaning
        # For English
        df_split_en_temp = pd.read_csv(source_en)
        df_split_en_temp = df_split_en_temp[df_split_en_temp['Main indicators of foreign trade'] == split['filter_en']].copy()
        df_split_en = df_split_en_temp[['Year', 'value']].copy()
        df_split_en.columns = ['year', 'value']

        # For Mongolian
        df_split_mn_temp = pd.read_csv(source_mn)
        df_split_mn_temp = df_split_mn_temp[df_split_mn_temp['Гадаад худалдааны үндсэн үзүүлэлт'] == split['filter_mn']].copy()
        df_split_mn = df_split_mn_temp[['Он', 'value']].copy()
        df_split_mn.columns = ['year', 'value']

        # Sort by year
        df_split_en = df_split_en.sort_values('year')
        df_split_mn = df_split_mn.sort_values('year')

        # Save CSV files
        df_split_en.to_csv(PUBLIC_DATASETS / f"{split_id}-en.csv", index=False)
        df_split_mn.to_csv(PUBLIC_DATASETS / f"{split_id}-mn.csv", index=False)

        # Save Excel files
        df_split_en.to_excel(PUBLIC_DATASETS / f"{split_id}-en.xlsx", index=False, sheet_name='Data')
        df_split_mn.to_excel(PUBLIC_DATASETS / f"{split_id}-mn.xlsx", index=False, sheet_name='Data')

        # Calculate stats
        stats[split_id] = {
            "row_count": len(df_split_en),
            "first_year": int(df_split_en['year'].min()),
            "last_year": int(df_split_en['year'].max()),
            "min_value": float(df_split_en['value'].min()),
            "max_value": float(df_split_en['value'].max()),
        }

        print(f"\nSaved split dataset: {split_id}")
        print(f"  Rows: {stats[split_id]['row_count']}")
        print(f"  Years: {stats[split_id]['first_year']} - {stats[split_id]['last_year']}")
        print(f"  Value range: ${stats[split_id]['min_value']:.1f}M - ${stats[split_id]['max_value']:.1f}M")

    return stats, splits

if __name__ == "__main__":
    print("Processing Foreign Trade data...\n")
    stats, splits = process_foreign_trade()

    print("\n" + "="*50)
    print("Processing complete!")
    print("="*50)

    print("\nDatasets created:")
    print("1. Parent: nso-foreign-trade-yearly (404 rows)")
    for i, split in enumerate(splits, 2):
        print(f"{i}. Split: {split['id']} ({stats[split['id']]['row_count']} rows)")
