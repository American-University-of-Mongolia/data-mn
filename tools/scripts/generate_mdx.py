#!/usr/bin/env python3
"""
MDX Page Generator for data.mn

Generates bilingual (EN/MN) MDX pages with consistent formatting.
This ensures all dataset pages follow the exact same structure and
pass Astro content collection validation.

Usage:
    python generate_mdx.py \
        --dataset-id population-total \
        --title-en "Total Population of Mongolia" \
        --title-mn "Монгол Улсын нийт хүн ам" \
        --excerpt-en "Mongolia's population reached 3.5 million in 2024." \
        --excerpt-mn "Монгол Улсын хүн ам 2024 онд 3.5 сая хүрэв." \
        --category-en Demographics \
        --category-mn "Хүн ам зүй" \
        --source-name "National Statistics Office of Mongolia" \
        --source-url "https://data.1212.mn" \
        --source-table-id "DT_NSO_0300_003V1.px"

Or use as a Python module:
    from generate_mdx import generate_mdx_pages
    generate_mdx_pages(config)
"""

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path
from typing import Optional


# Default paths
DEFAULT_BASE_DIR = "data/data.mn"
DEFAULT_MDX_EN_DIR = "src/data/data/en"
DEFAULT_MDX_MN_DIR = "src/data/data/mn"
DEFAULT_DATASETS_DIR = "public/datasets"
DEFAULT_CHARTS_DIR = "public/charts"


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes // 1024} KB"
    else:
        return f"{size_bytes // (1024 * 1024)} MB"


def get_file_size(file_path: str) -> str:
    """Get file size as formatted string, or default if file doesn't exist."""
    if os.path.exists(file_path):
        return format_file_size(os.path.getsize(file_path))
    return "1 KB"  # Default


def generate_mdx_content(
    lang: str,
    dataset_id: str,
    title: str,
    excerpt: str,
    category: str,
    tags: list[str],
    keywords: list[str],
    source_name: str,
    source_url: str,
    source_table_id: Optional[str] = None,
    csv_size: str = "1 KB",
    xlsx_size: str = "5 KB",
    chart_title: Optional[str] = None,
    publish_date: Optional[str] = None,
    data_version: int = 1,
    author: str = "Data.mn",
) -> str:
    """
    Generate MDX content for a single language.

    This produces YAML frontmatter that exactly matches the Astro
    content collection schema defined in content/config.ts.
    """
    if publish_date is None:
        publish_date = date.today().isoformat()

    if chart_title is None:
        chart_title = title

    # Language-specific file suffixes
    lang_suffix = f"-{lang}"

    # Determine download button text
    if lang == "mn":
        csv_desc = "CSV татах"
        xlsx_desc = "Excel татах"
    else:
        csv_desc = "Download as CSV"
        xlsx_desc = "Open in Excel"

    # Format tags and keywords as JSON arrays
    tags_json = json.dumps(tags, ensure_ascii=False)
    keywords_json = json.dumps(keywords, ensure_ascii=False)

    # Build the MDX content with proper YAML formatting
    # CRITICAL: Use exactly 2 spaces for indentation, no tabs
    mdx = f'''---
title: "{title}"
publishDate: {publish_date}
excerpt: "{excerpt}"
category: "{category}"
tags: {tags_json}
keywords: {keywords_json}
author: "{author}"
dataVersion: {data_version}
dataDate: {publish_date}
dataFiles:
  - path: "/datasets/{dataset_id}{lang_suffix}.csv"
    format: "csv"
    size: "{csv_size}"
    description: "{csv_desc}"
  - path: "/datasets/{dataset_id}.xlsx"
    format: "xlsx"
    size: "{xlsx_size}"
    description: "{xlsx_desc}"
source:
  name: "{source_name}"
  url: "{source_url}"
'''

    # Add optional tableId if provided
    if source_table_id:
        mdx += f'  tableId: "{source_table_id}"\n'

    # Close frontmatter and add body
    mdx += f'''---

import VegaChart from '~/components/ui/VegaChart.astro';

<VegaChart
  spec="/charts/{dataset_id}{lang_suffix}.json"
  title="{chart_title}"
/>
'''

    return mdx


def generate_mdx_pages(
    dataset_id: str,
    title_en: str,
    title_mn: str,
    excerpt_en: str,
    excerpt_mn: str,
    category_en: str,
    category_mn: str,
    tags: list[str],
    keywords_en: list[str],
    keywords_mn: Optional[list[str]] = None,
    source_name_en: str = "National Statistics Office of Mongolia",
    source_name_mn: str = "Үндэсний Статистикийн Хороо",
    source_url: str = "https://data.1212.mn",
    source_table_id: Optional[str] = None,
    chart_title_en: Optional[str] = None,
    chart_title_mn: Optional[str] = None,
    base_dir: str = DEFAULT_BASE_DIR,
    publish_date: Optional[str] = None,
    data_version: int = 1,
    dry_run: bool = False,
) -> dict:
    """
    Generate both English and Mongolian MDX pages for a dataset.

    Returns dict with paths to created files and their content.
    """
    if keywords_mn is None:
        keywords_mn = keywords_en

    # Calculate file sizes
    csv_en_path = os.path.join(base_dir, DEFAULT_DATASETS_DIR, f"{dataset_id}-en.csv")
    csv_mn_path = os.path.join(base_dir, DEFAULT_DATASETS_DIR, f"{dataset_id}-mn.csv")
    xlsx_path = os.path.join(base_dir, DEFAULT_DATASETS_DIR, f"{dataset_id}.xlsx")

    csv_en_size = get_file_size(csv_en_path)
    csv_mn_size = get_file_size(csv_mn_path)
    xlsx_size = get_file_size(xlsx_path)

    # Generate content for both languages
    content_en = generate_mdx_content(
        lang="en",
        dataset_id=dataset_id,
        title=title_en,
        excerpt=excerpt_en,
        category=category_en,
        tags=tags,
        keywords=keywords_en,
        source_name=source_name_en,
        source_url=source_url,
        source_table_id=source_table_id,
        csv_size=csv_en_size,
        xlsx_size=xlsx_size,
        chart_title=chart_title_en or title_en,
        publish_date=publish_date,
        data_version=data_version,
    )

    content_mn = generate_mdx_content(
        lang="mn",
        dataset_id=dataset_id,
        title=title_mn,
        excerpt=excerpt_mn,
        category=category_mn,
        tags=tags,
        keywords=keywords_mn,
        source_name=source_name_mn,
        source_url=source_url,
        source_table_id=source_table_id,
        csv_size=csv_mn_size,
        xlsx_size=xlsx_size,
        chart_title=chart_title_mn or title_mn,
        publish_date=publish_date,
        data_version=data_version,
    )

    # Define output paths
    path_en = os.path.join(base_dir, DEFAULT_MDX_EN_DIR, f"{dataset_id}.mdx")
    path_mn = os.path.join(base_dir, DEFAULT_MDX_MN_DIR, f"{dataset_id}.mdx")

    result = {
        "dataset_id": dataset_id,
        "files": {
            "en": {"path": path_en, "content": content_en},
            "mn": {"path": path_mn, "content": content_mn},
        },
        "dry_run": dry_run,
    }

    if not dry_run:
        # Create directories if needed
        os.makedirs(os.path.dirname(path_en), exist_ok=True)
        os.makedirs(os.path.dirname(path_mn), exist_ok=True)

        # Write files
        with open(path_en, 'w', encoding='utf-8') as f:
            f.write(content_en)

        with open(path_mn, 'w', encoding='utf-8') as f:
            f.write(content_mn)

        result["status"] = "created"
        print(f"✅ Created: {path_en}")
        print(f"✅ Created: {path_mn}")
    else:
        result["status"] = "dry_run"
        print(f"[DRY RUN] Would create: {path_en}")
        print(f"[DRY RUN] Would create: {path_mn}")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Generate bilingual MDX pages for data.mn datasets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate pages for a population dataset
  python generate_mdx.py \\
      --dataset-id population-total \\
      --title-en "Total Population of Mongolia" \\
      --title-mn "Монгол Улсын нийт хүн ам" \\
      --excerpt-en "Mongolia's population reached 3.5 million in 2024." \\
      --excerpt-mn "Монгол Улсын хүн ам 2024 онд 3.5 сая хүрэв." \\
      --category-en Demographics \\
      --category-mn "Хүн ам зүй" \\
      --tags mongolia population demographics

  # Dry run to preview output
  python generate_mdx.py --dataset-id test --dry-run ...
        """
    )

    # Required arguments
    parser.add_argument('--dataset-id', required=True, help='Unique dataset identifier')
    parser.add_argument('--title-en', required=True, help='English title')
    parser.add_argument('--title-mn', required=True, help='Mongolian title')
    parser.add_argument('--excerpt-en', required=True, help='English excerpt/description')
    parser.add_argument('--excerpt-mn', required=True, help='Mongolian excerpt/description')
    parser.add_argument('--category-en', required=True, help='English category')
    parser.add_argument('--category-mn', required=True, help='Mongolian category')

    # Optional arguments
    parser.add_argument('--tags', nargs='+', default=[], help='Tags (space-separated)')
    parser.add_argument('--keywords-en', nargs='+', default=[], help='English keywords')
    parser.add_argument('--keywords-mn', nargs='+', default=None, help='Mongolian keywords')
    parser.add_argument('--source-name-en', default='National Statistics Office of Mongolia')
    parser.add_argument('--source-name-mn', default='Үндэсний Статистикийн Хороо')
    parser.add_argument('--source-url', default='https://data.1212.mn')
    parser.add_argument('--source-table-id', default=None, help='Source table ID (e.g., DT_NSO_xxx)')
    parser.add_argument('--chart-title-en', default=None, help='Chart title (EN), defaults to title')
    parser.add_argument('--chart-title-mn', default=None, help='Chart title (MN), defaults to title')
    parser.add_argument('--base-dir', default=DEFAULT_BASE_DIR, help='Base directory for data.mn')
    parser.add_argument('--publish-date', default=None, help='Publish date (YYYY-MM-DD)')
    parser.add_argument('--data-version', type=int, default=1, help='Data version number')
    parser.add_argument('--dry-run', action='store_true', help='Preview without writing files')
    parser.add_argument('--json', action='store_true', help='Output result as JSON')

    args = parser.parse_args()

    # Use title-based tags if none provided
    if not args.tags:
        args.tags = ["mongolia"]

    # Use tags as keywords if none provided
    if not args.keywords_en:
        args.keywords_en = args.tags

    result = generate_mdx_pages(
        dataset_id=args.dataset_id,
        title_en=args.title_en,
        title_mn=args.title_mn,
        excerpt_en=args.excerpt_en,
        excerpt_mn=args.excerpt_mn,
        category_en=args.category_en,
        category_mn=args.category_mn,
        tags=args.tags,
        keywords_en=args.keywords_en,
        keywords_mn=args.keywords_mn,
        source_name_en=args.source_name_en,
        source_name_mn=args.source_name_mn,
        source_url=args.source_url,
        source_table_id=args.source_table_id,
        chart_title_en=args.chart_title_en,
        chart_title_mn=args.chart_title_mn,
        base_dir=args.base_dir,
        publish_date=args.publish_date,
        data_version=args.data_version,
        dry_run=args.dry_run,
    )

    if args.json:
        # Remove content from JSON output (too verbose)
        output = {
            "dataset_id": result["dataset_id"],
            "status": result["status"],
            "files": {
                lang: {"path": info["path"]}
                for lang, info in result["files"].items()
            }
        }
        print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
