#!/usr/bin/env python3
"""
Create unemployment rate datasets from NSO data.

This script:
1. Creates parent dataset with raw NSO data
2. Generates filtered split datasets for specific views
3. Creates bilingual CSV/XLSX files
4. Generates Vega-Lite charts
5. Creates bilingual MDX pages
6. Updates the registry
"""

import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

# Add registry to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'registry'))
from registry import Registry, Dataset

# Paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = Path(__file__).parent.parent.parent
TEMP_DIR = DATA_DIR / "temp_unemployment"
PUBLIC_DATASETS = DATA_DIR / "data.mn" / "public" / "datasets"
PUBLIC_CHARTS = DATA_DIR / "data.mn" / "public" / "charts"
MDX_EN = DATA_DIR / "data.mn" / "src" / "data" / "data" / "en"
MDX_MN = DATA_DIR / "data.mn" / "src" / "data" / "data" / "mn"
VERSIONS_DIR = DATA_DIR / "tools" / "versions"

# Source info
SOURCE_ID = "nso-1212"
SOURCE_TABLE_ID = "DT_NSO_0400_049V1.px"
SOURCE_TABLE_NAME = "8.5.2 UNEMPLOYMENT RATE, by sex, age group, persons with disabilities, and by year"

# Dataset definitions
DATASETS = {
    "parent": {
        "id": "nso-unemployment-rate",
        "name_en": "Unemployment Rate by Category and Year",
        "name_mn": "Ажилгүйдлийн түвшин ангилал, жилээр",
        "category_en": "Labor Market",
        "category_mn": "Хөдөлмөрийн зах зээл",
        "is_parent": True,
        "filter": None,
        "description_en": "Unemployment rate in Mongolia broken down by sex, age group, region, urban/rural, and disability status",
        "description_mn": "Монгол улсын ажилгүйдлийн түвшин хүйс, нас, бүс нутаг, хот/хөдөө, хөгжлийн бэрхшээлээр",
    },
    "splits": [
        {
            "id": "unemployment-rate-total",
            "name_en": "Unemployment Rate of Mongolia",
            "name_mn": "Монгол Улсын ажилгүйдлийн түвшин",
            "category_en": "Labor Market",
            "category_mn": "Хөдөлмөрийн зах зээл",
            "filter": {"Category": "Total"},
            "description_en": "Overall unemployment rate in Mongolia",
            "description_mn": "Монгол Улсын нийт ажилгүйдлийн түвшин",
            "chart_type": "line"
        },
        {
            "id": "unemployment-rate-by-sex",
            "name_en": "Unemployment Rate by Sex",
            "name_mn": "Ажилгүйдлийн түвшин хүйсээр",
            "category_en": "Labor Market",
            "category_mn": "Хөдөлмөрийн зах зээл",
            "filter": {"Category": ["Male", "Female"]},
            "description_en": "Unemployment rate in Mongolia by sex (male vs female)",
            "description_mn": "Монгол Улсын ажилгүйдлийн түвшин хүйсээр (эрэгтэй, эмэгтэй)",
            "chart_type": "line_multi"
        },
        {
            "id": "unemployment-rate-youth",
            "name_en": "Youth Unemployment Rate (15-24)",
            "name_mn": "Залуучуудын ажилгүйдлийн түвшин (15-24)",
            "category_en": "Labor Market",
            "category_mn": "Хөдөлмөрийн зах зээл",
            "filter": {"Category": "15-24"},
            "description_en": "Unemployment rate among young people aged 15-24 in Mongolia",
            "description_mn": "15-24 насны залуучуудын ажилгүйдлийн түвшин",
            "chart_type": "line"
        },
        {
            "id": "unemployment-rate-by-age",
            "name_en": "Unemployment Rate by Age Group",
            "name_mn": "Ажилгүйдлийн түвшин насны бүлгээр",
            "category_en": "Labor Market",
            "category_mn": "Хөдөлмөрийн зах зээл",
            "filter": {"Category": ["15-24", "25-64", "65+"]},
            "description_en": "Unemployment rate by age group in Mongolia",
            "description_mn": "Монгол Улсын ажилгүйдлийн түвшин насны бүлгээр",
            "chart_type": "line_multi"
        },
        {
            "id": "unemployment-rate-by-location",
            "name_en": "Unemployment Rate by Location",
            "name_mn": "Ажилгүйдлийн түвшин газар нутгаар",
            "category_en": "Labor Market",
            "category_mn": "Хөдөлмөрийн зах зээл",
            "filter": {"Category": ["Urban", "Rural", "Ulaanbaatar"]},
            "description_en": "Unemployment rate by urban/rural areas and Ulaanbaatar",
            "description_mn": "Ажилгүйдлийн түвшин хот, хөдөө, Улаанбаатар хотоор",
            "chart_type": "line_multi"
        },
        {
            "id": "unemployment-rate-by-region",
            "name_en": "Unemployment Rate by Region",
            "name_mn": "Ажилгүйдлийн түвшин бүс нутгаар",
            "category_en": "Labor Market",
            "category_mn": "Хөдөлмөрийн зах зээл",
            "filter": {"Category": ["Central region", "Western region", "Khangai region", "Eastern region"]},
            "description_en": "Unemployment rate by geographic region in Mongolia",
            "description_mn": "Монгол Улсын ажилгүйдлийн түвшин бүс нутгаар",
            "chart_type": "line_multi"
        },
    ]
}


def clean_column_names(df):
    """Clean and standardize column names"""
    # Rename columns to standard names
    column_map = {
        'Category': 'category',
        'Ангилал': 'category',
        'Year': 'year',
        'Он': 'year',
        'value': 'value'
    }

    # Strip whitespace from category values
    if 'Category' in df.columns:
        df['Category'] = df['Category'].str.strip()
    if 'Ангилал' in df.columns:
        df['Ангилал'] = df['Ангилал'].str.strip()

    df = df.rename(columns=column_map)
    return df


def apply_filter(df, filter_spec):
    """Apply filter to dataframe based on filter specification"""
    if not filter_spec:
        return df

    result = df.copy()
    for column, value in filter_spec.items():
        col_lower = column.lower()
        if isinstance(value, list):
            result = result[result[col_lower].isin(value)]
        else:
            result = result[result[col_lower] == value]

    return result


def create_csv_xlsx(dataset_id, df_en, df_mn):
    """Create bilingual CSV and XLSX files"""
    # Save CSVs
    csv_en = PUBLIC_DATASETS / f"{dataset_id}-en.csv"
    csv_mn = PUBLIC_DATASETS / f"{dataset_id}-mn.csv"

    df_en.to_csv(csv_en, index=False)
    df_mn.to_csv(csv_mn, index=False)

    # Create XLSX with both languages
    xlsx_path = PUBLIC_DATASETS / f"{dataset_id}.xlsx"
    with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
        df_en.to_excel(writer, sheet_name='English', index=False)
        df_mn.to_excel(writer, sheet_name='Mongolian', index=False)

    print(f"  Created: {csv_en.name}, {csv_mn.name}, {xlsx_path.name}")
    return csv_en, csv_mn, xlsx_path


def generate_vega_chart(dataset_id, chart_type, df):
    """Generate Vega-Lite chart specification"""

    # Determine if multi-line chart
    is_multi = chart_type == "line_multi"

    if is_multi:
        # Multi-line chart with category breakdown
        spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "data": {
                "url": f"/datasets/{dataset_id}-en.csv",
                "format": {"type": "csv"}
            },
            "mark": {
                "type": "line",
                "point": True,
                "tooltip": True
            },
            "encoding": {
                "x": {
                    "field": "year",
                    "type": "quantitative",
                    "axis": {"title": "Year", "format": "d"}
                },
                "y": {
                    "field": "value",
                    "type": "quantitative",
                    "axis": {"title": "Unemployment Rate (%)", "format": ".1f"}
                },
                "color": {
                    "field": "category",
                    "type": "nominal",
                    "legend": {"title": "Category"}
                }
            },
            "config": {
                "view": {"strokeWidth": 0},
                "axis": {"labelFontSize": 11, "titleFontSize": 12}
            }
        }
    else:
        # Single line chart
        spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "data": {
                "url": f"/datasets/{dataset_id}-en.csv",
                "format": {"type": "csv"}
            },
            "mark": {
                "type": "line",
                "point": True,
                "tooltip": True
            },
            "encoding": {
                "x": {
                    "field": "year",
                    "type": "quantitative",
                    "axis": {"title": "Year", "format": "d"}
                },
                "y": {
                    "field": "value",
                    "type": "quantitative",
                    "axis": {"title": "Unemployment Rate (%)", "format": ".1f"}
                }
            },
            "config": {
                "view": {"strokeWidth": 0},
                "axis": {"labelFontSize": 11, "titleFontSize": 12}
            }
        }

    chart_path = PUBLIC_CHARTS / f"{dataset_id}.json"
    with open(chart_path, 'w') as f:
        json.dump(spec, f, indent=2)

    print(f"  Created chart: {chart_path.name}")
    return chart_path


def create_mdx_page(dataset_id, name_en, name_mn, description_en, description_mn,
                   category_en, stats, lang='en'):
    """Create MDX page for a dataset"""

    if lang == 'en':
        mdx_dir = MDX_EN
        name = name_en
        description = description_en
        category = category_en
    else:
        mdx_dir = MDX_MN
        name = name_mn
        description = description_mn
        category = category_en  # Use English category for now

    # Get year range
    first_year = stats['first_year']
    last_year = stats['last_year']

    # Create MDX content
    content = f"""---
title: "{name}"
description: "{description}"
category: "{category}"
lastUpdated: {datetime.now().strftime('%Y-%m-%d')}
---

import DatasetPage from '@components/DatasetPage.astro';

<DatasetPage
  datasetId="{dataset_id}"
  chartId="{dataset_id}"
/>

## About this data

{description}

**Data coverage**: {first_year} - {last_year}

**Source**: National Statistical Office of Mongolia (NSO)

**Source table**: {SOURCE_TABLE_NAME}
"""

    mdx_path = mdx_dir / f"{dataset_id}.mdx"
    with open(mdx_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  Created MDX ({lang}): {mdx_path.name}")
    return mdx_path


def main():
    print("=" * 70)
    print("Creating Unemployment Rate Datasets")
    print("=" * 70)

    # Load source data
    print("\n1. Loading source data...")
    df_en = pd.read_csv(TEMP_DIR / "nso-0400-049v1-en.csv")
    df_mn = pd.read_csv(TEMP_DIR / "nso-0400-049v1-mn.csv")

    # Clean column names
    df_en = clean_column_names(df_en)
    df_mn = clean_column_names(df_mn)

    print(f"   Loaded {len(df_en)} rows with categories: {df_en['category'].unique().tolist()}")

    # Initialize registry
    reg = Registry()

    # Create parent dataset
    print("\n2. Creating parent dataset...")
    parent_def = DATASETS["parent"]

    # Save parent data (keep all rows)
    csv_en, csv_mn, xlsx = create_csv_xlsx(parent_def["id"], df_en, df_mn)

    # Calculate stats
    stats = {
        "first_year": int(df_en['year'].min()),
        "last_year": int(df_en['year'].max()),
        "row_count": len(df_en),
        "categories": df_en['category'].nunique()
    }

    # Register parent dataset
    parent_dataset = Dataset(
        id=parent_def["id"],
        source_id=SOURCE_ID,
        name_en=parent_def["name_en"],
        name_mn=parent_def["name_mn"],
        category_en=parent_def["category_en"],
        category_mn=parent_def["category_mn"],
        description_en=parent_def["description_en"],
        description_mn=parent_def["description_mn"],
        is_parent=True,
        source_ref=SOURCE_TABLE_ID,
        definition_path=f"sources/{SOURCE_ID}/datasets/unemployment-rate.md",
        status='active',
        current_version=1,
        auto_update=True,
        auto_publish=True,
        data_file=str(csv_en),
        source_metadata={"table_id": SOURCE_TABLE_ID, "table_name": SOURCE_TABLE_NAME},
        last_fetched_at=datetime.now().isoformat(),
    )

    try:
        reg.add_dataset(parent_dataset)
        print(f"   Registered: {parent_def['id']}")
    except Exception as e:
        print(f"   Warning: Could not register parent dataset: {e}")

    # Create split datasets
    print("\n3. Creating split datasets...")

    for split_def in DATASETS["splits"]:
        print(f"\n   Processing: {split_def['id']}")

        # Apply filter
        df_split_en = apply_filter(df_en, split_def['filter'])
        df_split_mn = apply_filter(df_mn, split_def['filter'])

        if len(df_split_en) == 0:
            print(f"   WARNING: No data after filtering!")
            continue

        print(f"   Filtered to {len(df_split_en)} rows")

        # Create CSV/XLSX
        csv_en, csv_mn, xlsx = create_csv_xlsx(split_def["id"], df_split_en, df_split_mn)

        # Calculate stats
        stats = {
            "first_year": int(df_split_en['year'].min()),
            "last_year": int(df_split_en['year'].max()),
            "row_count": len(df_split_en),
            "min_value": float(df_split_en['value'].min()),
            "max_value": float(df_split_en['value'].max())
        }

        # Generate chart
        chart_path = generate_vega_chart(split_def["id"], split_def["chart_type"], df_split_en)

        # Create MDX pages
        mdx_en = create_mdx_page(
            split_def["id"],
            split_def["name_en"],
            split_def["name_mn"],
            split_def["description_en"],
            split_def["description_mn"],
            split_def["category_en"],
            stats,
            lang='en'
        )

        mdx_mn = create_mdx_page(
            split_def["id"],
            split_def["name_en"],
            split_def["name_mn"],
            split_def["description_en"],
            split_def["description_mn"],
            split_def["category_en"],
            stats,
            lang='mn'
        )

        # Register split dataset
        split_dataset = Dataset(
            id=split_def["id"],
            source_id=SOURCE_ID,
            parent_id=parent_def["id"],
            is_parent=False,
            split_filter=split_def["filter"],
            name_en=split_def["name_en"],
            name_mn=split_def["name_mn"],
            category_en=split_def["category_en"],
            category_mn=split_def["category_mn"],
            description_en=split_def["description_en"],
            description_mn=split_def["description_mn"],
            source_ref=SOURCE_TABLE_ID,
            definition_path=f"sources/{SOURCE_ID}/datasets/unemployment-rate.md",
            status='active',
            current_version=1,
            auto_update=True,
            auto_publish=True,
            data_file=str(csv_en),
            chart_spec=str(chart_path),
            mdx_file_en=str(mdx_en),
            mdx_file_mn=str(mdx_mn),
            source_metadata={"table_id": SOURCE_TABLE_ID, "table_name": SOURCE_TABLE_NAME},
            last_fetched_at=datetime.now().isoformat(),
        )

        try:
            reg.add_dataset(split_dataset)
            print(f"   Registered: {split_def['id']}")
        except Exception as e:
            print(f"   Warning: Could not register split dataset: {e}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Parent dataset: {parent_def['id']}")
    print(f"Split datasets: {len(DATASETS['splits'])}")
    print(f"\nFiles generated:")
    print(f"  - CSV files: {(len(DATASETS['splits']) + 1) * 2}")
    print(f"  - XLSX files: {len(DATASETS['splits']) + 1}")
    print(f"  - Chart files: {len(DATASETS['splits'])}")
    print(f"  - MDX pages: {len(DATASETS['splits']) * 2}")
    print("\nNext steps:")
    print("  1. Validate charts: cd data.mn && python3 ../tools/scripts/validate_vega.py --all")
    print("  2. Publish datasets: cd tools && python -m registry publish <dataset-id>")
    print("  3. Test locally: cd data.mn && npm run dev")
    print("=" * 70)


if __name__ == '__main__':
    main()
