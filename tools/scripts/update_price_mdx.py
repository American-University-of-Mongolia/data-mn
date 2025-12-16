#!/usr/bin/env python3
"""
Update MDX files for price datasets to use new file naming convention:
- CSV download: -all-{lang}.csv (full data)
- Chart: -{lang}.csv (subset)
"""

import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(SCRIPT_DIR)
BASE_DIR = os.path.dirname(TOOLS_DIR)
DATA_MN_DIR = os.path.join(BASE_DIR, "data.mn")
DATASETS_DIR = os.path.join(DATA_MN_DIR, "public", "datasets")

DATASETS = [
    "weekly-beef-prices",
    "weekly-mutton-prices",
    "weekly-flour-prices",
    "weekly-milk-prices",
    "weekly-gasoline-prices",
    "weekly-diesel-prices",
]

def get_file_size(path):
    """Get file size as human-readable string."""
    if not os.path.exists(path):
        return "N/A"
    size = os.path.getsize(path)
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size // 1024} KB"
    else:
        return f"{size // (1024 * 1024)} MB"

def update_mdx_file(mdx_path, dataset_id, lang):
    """Update a single MDX file with new CSV path and sizes."""
    if not os.path.exists(mdx_path):
        print(f"  SKIP: {mdx_path} not found")
        return False

    with open(mdx_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Get new file sizes
    csv_path = os.path.join(DATASETS_DIR, f"{dataset_id}-all-{lang}.csv")
    xlsx_path = os.path.join(DATASETS_DIR, f"{dataset_id}.xlsx")

    csv_size = get_file_size(csv_path)
    xlsx_size = get_file_size(xlsx_path)

    # Update CSV path: change from /{id}-{lang}.csv to /{id}-all-{lang}.csv
    old_csv_pattern = rf'/datasets/{re.escape(dataset_id)}-{lang}\.csv'
    new_csv_path = f'/datasets/{dataset_id}-all-{lang}.csv'

    if re.search(old_csv_pattern, content):
        content = re.sub(old_csv_pattern, new_csv_path, content)
        print(f"  Updated CSV path to {new_csv_path}")
    else:
        print(f"  NOTE: CSV path pattern not found (may already be updated)")

    # Update CSV description
    if lang == 'en':
        content = re.sub(
            r'description: "Download as CSV"',
            'description: "Download as CSV (all regions)"',
            content
        )
    else:
        content = re.sub(
            r'description: "CSV татах"',
            'description: "CSV татах (бүх бүс нутаг)"',
            content
        )

    # Update file sizes in the YAML frontmatter
    # Find and replace size values
    content = re.sub(
        rf'(path: "/datasets/{re.escape(dataset_id)}-all-{lang}\.csv"[\s\S]*?size: ")[^"]*(")',
        rf'\g<1>{csv_size}\g<2>',
        content
    )
    content = re.sub(
        rf'(path: "/datasets/{re.escape(dataset_id)}\.xlsx"[\s\S]*?size: ")[^"]*(")',
        rf'\g<1>{xlsx_size}\g<2>',
        content
    )

    with open(mdx_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  Updated: {mdx_path}")
    print(f"    CSV size: {csv_size}, XLSX size: {xlsx_size}")
    return True

# Process all datasets
for dataset_id in DATASETS:
    print(f"\n{'='*60}")
    print(f"Updating: {dataset_id}")
    print(f"{'='*60}")

    for lang in ['en', 'mn']:
        mdx_path = os.path.join(
            DATA_MN_DIR, "src", "data", "data", lang, f"{dataset_id}.mdx"
        )
        update_mdx_file(mdx_path, dataset_id, lang)

print("\n" + "="*60)
print("Done! MDX files updated.")
print("="*60)
