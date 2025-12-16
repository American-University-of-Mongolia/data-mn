#!/usr/bin/env python3
"""
Fix unemployment dataset charts and MDX pages.

This script:
1. Creates bilingual chart versions (-en.json and -mn.json)
2. Regenerates MDX pages with proper format
"""

import json
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.generate_mdx import generate_mdx_pages

# Paths
DATA_DIR = Path(__file__).parent.parent.parent
CHARTS_DIR = DATA_DIR / "data.mn" / "public" / "charts"

# Dataset definitions with metadata
DATASETS = [
    {
        "id": "unemployment-rate-total",
        "title_en": "Mongolia Unemployment Rate, % (2009-2024)",
        "title_mn": "Монгол Улсын ажилгүйдлийн түвшин, хувь (2009-2024)",
        "excerpt_en": "Overall unemployment rate in Mongolia from 2009 to 2024, showing labor market trends.",
        "excerpt_mn": "Монгол Улсын нийт ажилгүйдлийн түвшин 2009-2024 онд, хөдөлмөрийн зах зээлийн чиг хандлагыг харуулсан.",
        "tags": ["mongolia", "unemployment", "economy", "labor", "labor market"],
        "keywords_en": ["mongolia unemployment rate", "jobless rate", "labor market", "employment"],
        "chart_type": "line",
        "y_title_en": "Unemployment Rate (%)",
        "y_title_mn": "Ажилгүйдлийн түвшин (%)"
    },
    {
        "id": "unemployment-rate-by-sex",
        "title_en": "Mongolia Unemployment Rate by Sex, % (2009-2024)",
        "title_mn": "Ажилгүйдлийн түвшин хүйсээр, хувь (2009-2024)",
        "excerpt_en": "Unemployment rate in Mongolia by sex (male vs female) from 2009 to 2024.",
        "excerpt_mn": "Монгол Улсын ажилгүйдлийн түвшин хүйсээр (эрэгтэй, эмэгтэй) 2009-2024 онд.",
        "tags": ["mongolia", "unemployment", "economy", "labor", "gender"],
        "keywords_en": ["unemployment by sex", "gender gap", "male unemployment", "female unemployment"],
        "chart_type": "line_multi",
        "y_title_en": "Unemployment Rate (%)",
        "y_title_mn": "Ажилгүйдлийн түвшин (%)"
    },
    {
        "id": "unemployment-rate-youth",
        "title_en": "Youth Unemployment Rate (15-24), % (2009-2024)",
        "title_mn": "Залуучуудын ажилгүйдлийн түвшин (15-24), хувь (2009-2024)",
        "excerpt_en": "Unemployment rate among young people aged 15-24 in Mongolia from 2009 to 2024.",
        "excerpt_mn": "15-24 насны залуучуудын ажилгүйдлийн түвшин 2009-2024 онд.",
        "tags": ["mongolia", "unemployment", "youth", "labor"],
        "keywords_en": ["youth unemployment", "young people", "15-24", "labor market"],
        "chart_type": "line",
        "y_title_en": "Unemployment Rate (%)",
        "y_title_mn": "Ажилгүйдлийн түвшин (%)"
    },
    {
        "id": "unemployment-rate-by-age",
        "title_en": "Unemployment Rate by Age Group, % (2009-2024)",
        "title_mn": "Ажилгүйдлийн түвшин насны бүлгээр, хувь (2009-2024)",
        "excerpt_en": "Unemployment rate by age group in Mongolia (15-24, 25-64, 65+) from 2009 to 2024.",
        "excerpt_mn": "Монгол Улсын ажилгүйдлийн түвшин насны бүлгээр (15-24, 25-64, 65+) 2009-2024 онд.",
        "tags": ["mongolia", "unemployment", "age", "labor"],
        "keywords_en": ["unemployment by age", "age groups", "labor market"],
        "chart_type": "line_multi",
        "y_title_en": "Unemployment Rate (%)",
        "y_title_mn": "Ажилгүйдлийн түвшин (%)"
    },
    {
        "id": "unemployment-rate-by-location",
        "title_en": "Unemployment Rate by Location, % (2009-2024)",
        "title_mn": "Ажилгүйдлийн түвшин газар нутгаар, хувь (2009-2024)",
        "excerpt_en": "Unemployment rate by urban/rural areas and Ulaanbaatar from 2009 to 2024.",
        "excerpt_mn": "Ажилгүйдлийн түвшин хот, хөдөө, Улаанбаатар хотоор 2009-2024 онд.",
        "tags": ["mongolia", "unemployment", "geography", "urban", "rural"],
        "keywords_en": ["unemployment by location", "urban unemployment", "rural unemployment", "Ulaanbaatar"],
        "chart_type": "line_multi",
        "y_title_en": "Unemployment Rate (%)",
        "y_title_mn": "Ажилгүйдлийн түвшин (%)"
    },
    {
        "id": "unemployment-rate-by-region",
        "title_en": "Unemployment Rate by Region, % (2009-2024)",
        "title_mn": "Ажилгүйдлийн түвшин бүс нутгаар, хувь (2009-2024)",
        "excerpt_en": "Unemployment rate by geographic region in Mongolia (Central, Western, Khangai, Eastern) from 2009 to 2024.",
        "excerpt_mn": "Монгол Улсын ажилгүйдлийн түвшин бүс нутгаар (Төв, Баруун, Хангай, Зүүн) 2009-2024 онд.",
        "tags": ["mongolia", "unemployment", "region", "geography"],
        "keywords_en": ["unemployment by region", "regional unemployment", "geographic distribution"],
        "chart_type": "line_multi",
        "y_title_en": "Unemployment Rate (%)",
        "y_title_mn": "Ажилгүйдлийн түвшин (%)"
    }
]


def create_bilingual_charts():
    """Create -en.json and -mn.json versions from existing chart specs."""
    print("Creating bilingual chart versions...")
    
    for dataset in DATASETS:
        dataset_id = dataset["id"]
        old_chart_path = CHARTS_DIR / f"{dataset_id}.json"
        
        if not old_chart_path.exists():
            print(f"  WARNING: {old_chart_path.name} not found, skipping")
            continue
        
        # Load existing chart
        with open(old_chart_path, 'r') as f:
            spec = json.load(f)
        
        # Create English version
        spec_en = spec.copy()
        spec_en['data']['url'] = f"/datasets/{dataset_id}-en.csv"
        spec_en['encoding']['y']['axis']['title'] = dataset['y_title_en']
        
        chart_en_path = CHARTS_DIR / f"{dataset_id}-en.json"
        with open(chart_en_path, 'w') as f:
            json.dump(spec_en, f, indent=2)
        
        # Create Mongolian version
        spec_mn = spec.copy()
        spec_mn['data']['url'] = f"/datasets/{dataset_id}-mn.csv"
        spec_mn['encoding']['y']['axis']['title'] = dataset['y_title_mn']
        
        chart_mn_path = CHARTS_DIR / f"{dataset_id}-mn.json"
        with open(chart_mn_path, 'w') as f:
            json.dump(spec_mn, f, indent=2)
        
        print(f"  ✓ Created: {chart_en_path.name}, {chart_mn_path.name}")
        
        # Remove old chart
        old_chart_path.unlink()
        print(f"  ✓ Removed: {old_chart_path.name}")


def regenerate_mdx_pages():
    """Regenerate MDX pages with proper format."""
    print("\nRegenerating MDX pages...")
    
    for dataset in DATASETS:
        print(f"\n  Processing: {dataset['id']}")
        
        result = generate_mdx_pages(
            dataset_id=dataset["id"],
            title_en=dataset["title_en"],
            title_mn=dataset["title_mn"],
            excerpt_en=dataset["excerpt_en"],
            excerpt_mn=dataset["excerpt_mn"],
            category_en="Economy",
            category_mn="Эдийн засаг",
            tags=dataset["tags"],
            keywords_en=dataset["keywords_en"],
            source_table_id="DT_NSO_0400_049V1.px",
            base_dir=str(DATA_DIR / "data.mn"),
        )


def main():
    print("=" * 70)
    print("Fixing Unemployment Dataset Charts and MDX Pages")
    print("=" * 70)
    
    create_bilingual_charts()
    regenerate_mdx_pages()
    
    print("\n" + "=" * 70)
    print("COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Validate charts: cd data.mn && python3 ../tools/scripts/validate_vega.py --all")
    print("  2. Validate MDX: cd tools && python3 scripts/validate_dataset.py --all <dataset-id>")
    print("  3. Publish datasets: cd tools && python -m registry publish <dataset-id>")
    print("=" * 70)


if __name__ == '__main__':
    main()
