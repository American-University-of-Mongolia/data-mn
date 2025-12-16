#!/usr/bin/env python3
"""
Generate bilingual MDX pages for foreign trade datasets
"""

import os
from pathlib import Path
from datetime import datetime

# Paths
DATA_DIR = Path(__file__).parent.parent.parent
PUBLIC_DATASETS = DATA_DIR / "data.mn" / "public" / "datasets"
MDX_DIR_EN = DATA_DIR / "data.mn" / "src" / "data" / "data" / "en"
MDX_DIR_MN = DATA_DIR / "data.mn" / "src" / "data" / "data" / "mn"

def format_size(size_bytes):
    """Format file size in KB or MB"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def get_file_size(filename):
    """Get file size formatted"""
    path = PUBLIC_DATASETS / filename
    if path.exists():
        return format_size(path.stat().st_size)
    return "Unknown"

# Dataset definitions
datasets = [
    {
        "id": "foreign-trade-mongolia",
        "title_en": "Foreign Trade Turnover - Mongolia",
        "title_mn": "Гадаад худалдааны эргэлт - Монгол Улс",
        "excerpt_en": "Mongolia's total foreign trade turnover from 1924 to 2024, showing the combined value of exports and imports in million USD.",
        "excerpt_mn": "Монгол Улсын 1924 оноос 2024 он хүртэлх гадаад худалдааны нийт эргэлт, экспорт болон импортын нийлбэр үнэ дүнг сая ам.доллараар харуулав.",
        "category_en": "Trade",
        "category_mn": "Худалдаа",
        "tags": ["mongolia", "foreign trade", "trade turnover", "exports imports"],
        "keywords": ["mongolia foreign trade", "trade turnover", "exports imports combined", "international trade mongolia"],
    },
    {
        "id": "exports-mongolia",
        "title_en": "Exports - Mongolia",
        "title_mn": "Экспорт - Монгол Улс",
        "excerpt_en": "Total value of goods exported from Mongolia from 1924 to 2024 in million USD, reflecting the country's mining-driven export economy.",
        "excerpt_mn": "Монгол Улсаас 1924 оноос 2024 он хүртэл экспортолсон нийт бараа бүтээгдэхүүний үнэ дүнг сая ам.доллараар харуулсан нь уул уурхайн салбарт түшиглэсэн экспортыг илэрхийлнэ.",
        "category_en": "Trade",
        "category_mn": "Худалдаа",
        "tags": ["mongolia", "exports", "international trade", "mining"],
        "keywords": ["mongolia exports", "export value", "international exports", "mining exports mongolia"],
    },
    {
        "id": "imports-mongolia",
        "title_en": "Imports - Mongolia",
        "title_mn": "Импорт - Монгол Улс",
        "excerpt_en": "Total value of goods imported into Mongolia from 1924 to 2024 in million USD, showing the country's reliance on imported goods.",
        "excerpt_mn": "Монгол Улс руу 1924 оноос 2024 он хүртэл импортолсон нийт бараа бүтээгдэхүүний үнэ дүнг сая ам.доллараар харуулсан нь улс орны импортод хамаарлыг илэрхийлнэ.",
        "category_en": "Trade",
        "category_mn": "Худалдаа",
        "tags": ["mongolia", "imports", "international trade"],
        "keywords": ["mongolia imports", "import value", "international imports", "imported goods mongolia"],
    },
    {
        "id": "trade-balance-mongolia",
        "title_en": "Trade Balance - Mongolia",
        "title_mn": "Худалдааны тэнцэл - Монгол Улс",
        "excerpt_en": "Mongolia's trade balance (exports minus imports) from 1924 to 2024 in million USD, with positive values indicating trade surplus and negative values indicating trade deficit.",
        "excerpt_mn": "Монгол Улсын 1924 оноос 2024 он хүртэлх худалдааны тэнцэл (экспорт хасах импорт) сая ам.доллараар, эерэг утга нь худалдааны ашиг, сөрөг утга нь алдагдлыг илэрхийлнэ.",
        "category_en": "Trade",
        "category_mn": "Худалдаа",
        "tags": ["mongolia", "trade balance", "trade surplus", "trade deficit"],
        "keywords": ["mongolia trade balance", "trade surplus deficit", "balance of trade", "net exports mongolia"],
    },
]

# Source information
source_en = "National Statistics Office of Mongolia"
source_mn = "Үндэсний Статистикийн Хороо"
source_url = "https://data.1212.mn"
table_id = "DT_NSO_1400_001V1_year.px"

publish_date = datetime.now().strftime("%Y-%m-%d")

# Generate MDX files
for dataset in datasets:
    dataset_id = dataset["id"]

    # Get file sizes
    csv_size_en = get_file_size(f"{dataset_id}-en.csv")
    xlsx_size_en = get_file_size(f"{dataset_id}-en.xlsx")
    csv_size_mn = get_file_size(f"{dataset_id}-mn.csv")
    xlsx_size_mn = get_file_size(f"{dataset_id}-mn.xlsx")

    # Format tags and keywords for frontmatter
    tags_str = str(dataset["tags"]).replace("'", '"')
    keywords_str = str(dataset["keywords"]).replace("'", '"')

    # English MDX
    mdx_en = f'''---
title: "{dataset["title_en"]}"
publishDate: {publish_date}
excerpt: "{dataset["excerpt_en"]}"
category: "{dataset["category_en"]}"
tags: {tags_str}
keywords: {keywords_str}
dataFiles:
  - path: "/datasets/{dataset_id}-en.csv"
    format: "csv"
    size: "{csv_size_en}"
    description: "Download as CSV"
  - path: "/datasets/{dataset_id}-en.xlsx"
    format: "xlsx"
    size: "{xlsx_size_en}"
    description: "Open in Excel"
source:
  name: "{source_en}"
  url: "{source_url}"
  tableId: "{table_id}"
---

import VegaChart from '~/components/ui/VegaChart.astro';

{dataset["excerpt_en"]}

<VegaChart
  spec="/charts/{dataset_id}.json"
  title="{dataset["title_en"]}"
/>
'''

    # Mongolian MDX
    mdx_mn = f'''---
title: "{dataset["title_mn"]}"
publishDate: {publish_date}
excerpt: "{dataset["excerpt_mn"]}"
category: "{dataset["category_mn"]}"
tags: {tags_str}
keywords: {keywords_str}
dataFiles:
  - path: "/datasets/{dataset_id}-mn.csv"
    format: "csv"
    size: "{csv_size_mn}"
    description: "CSV татах"
  - path: "/datasets/{dataset_id}-mn.xlsx"
    format: "xlsx"
    size: "{xlsx_size_mn}"
    description: "Excel татах"
source:
  name: "{source_mn}"
  url: "{source_url}"
  tableId: "{table_id}"
---

import VegaChart from '~/components/ui/VegaChart.astro';

{dataset["excerpt_mn"]}

<VegaChart
  spec="/charts/{dataset_id}.json"
  title="{dataset["title_mn"]}"
/>
'''

    # Write files
    en_path = MDX_DIR_EN / f"{dataset_id}.mdx"
    mn_path = MDX_DIR_MN / f"{dataset_id}.mdx"

    with open(en_path, 'w', encoding='utf-8') as f:
        f.write(mdx_en)

    with open(mn_path, 'w', encoding='utf-8') as f:
        f.write(mdx_mn)

    print(f"Generated: {dataset_id}")
    print(f"  EN: {en_path}")
    print(f"  MN: {mn_path}")
    print()

print("All MDX files generated successfully!")
