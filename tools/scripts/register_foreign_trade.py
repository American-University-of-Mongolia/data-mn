#!/usr/bin/env python3
"""
Register foreign trade datasets in the registry
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add registry to path
sys.path.insert(0, str(Path(__file__).parent.parent / "registry"))
from registry import Registry, Dataset, Source

# Initialize registry
reg = Registry()

# Ensure NSO source exists
source = reg.get_source("nso-1212")
if not source:
    print("Creating NSO source...")
    reg.add_source(Source(
        id="nso-1212",
        name="National Statistics Office of Mongolia",
        name_mn="Үндэсний Статистикийн Хороо",
        type="api",
        base_url="https://data.1212.mn/api/v1",
        definition_path="tools/sources/nso-1212/source.md",
        update_frequency="monthly",
        enabled=True,
        priority=10
    ))

# Dataset definitions
now = datetime.now().isoformat()

# 1. Parent dataset
parent_id = "nso-foreign-trade-yearly"
print(f"\nRegistering parent dataset: {parent_id}")

parent = Dataset(
    id=parent_id,
    source_id="nso-1212",
    name_en="Foreign Trade Yearly (All Indicators)",
    name_mn="Гадаад худалдаа жилээр (Бүх үзүүлэлт)",
    category_en="Trade",
    category_mn="Худалдаа",
    description_en="Complete foreign trade dataset with all indicators (turnover, exports, imports, balance) from 1924-2024",
    description_mn="1924-2024 оны гадаад худалдааны бүх үзүүлэлтүүд (эргэлт, экспорт, импорт, тэнцэл)",
    definition_path=f"tools/sources/nso-1212/datasets/{parent_id}.md",
    is_parent=True,
    status="active",
    current_version=1,
    source_ref="DT_NSO_1400_001V1_year.px",
    data_file=f"public/datasets/{parent_id}.csv",
    source_updated_at="2025-08-04T10:27:10",
    last_fetched_at=now,
    auto_update=True,
    auto_publish=False,  # Parent is not published
)

try:
    reg.add_dataset(parent)
    print(f"✓ Registered: {parent_id}")
except Exception as e:
    print(f"✗ Error registering {parent_id}: {e}")

# 2. Split datasets
splits = [
    {
        "id": "foreign-trade-mongolia",
        "name_en": "Foreign Trade Turnover - Mongolia",
        "name_mn": "Гадаад худалдааны эргэлт - Монгол Улс",
        "description_en": "Total foreign trade turnover (exports + imports) 1924-2024",
        "description_mn": "Нийт гадаад худалдааны эргэлт (экспорт + импорт) 1924-2024",
        "filter": {"main_indicators_of_foreign_trade": "Total turnover"},
        "chart": "foreign-trade-mongolia.json",
        "mdx_en": "en/foreign-trade-mongolia.mdx",
        "mdx_mn": "mn/foreign-trade-mongolia.mdx",
    },
    {
        "id": "exports-mongolia",
        "name_en": "Exports - Mongolia",
        "name_mn": "Экспорт - Монгол Улс",
        "description_en": "Total exports from Mongolia 1924-2024",
        "description_mn": "Монгол Улсын нийт экспорт 1924-2024",
        "filter": {"main_indicators_of_foreign_trade": " Exports"},
        "chart": "exports-mongolia.json",
        "mdx_en": "en/exports-mongolia.mdx",
        "mdx_mn": "mn/exports-mongolia.mdx",
    },
    {
        "id": "imports-mongolia",
        "name_en": "Imports - Mongolia",
        "name_mn": "Импорт - Монгол Улс",
        "description_en": "Total imports into Mongolia 1924-2024",
        "description_mn": "Монгол Улсын нийт импорт 1924-2024",
        "filter": {"main_indicators_of_foreign_trade": " Imports"},
        "chart": "imports-mongolia.json",
        "mdx_en": "en/imports-mongolia.mdx",
        "mdx_mn": "mn/imports-mongolia.mdx",
    },
    {
        "id": "trade-balance-mongolia",
        "name_en": "Trade Balance - Mongolia",
        "name_mn": "Худалдааны тэнцэл - Монгол Улс",
        "description_en": "Trade balance (exports - imports) 1924-2024",
        "description_mn": "Худалдааны тэнцэл (экспорт - импорт) 1924-2024",
        "filter": {"main_indicators_of_foreign_trade": " Balance"},
        "chart": "trade-balance-mongolia.json",
        "mdx_en": "en/trade-balance-mongolia.mdx",
        "mdx_mn": "mn/trade-balance-mongolia.mdx",
    },
]

print("\nRegistering split datasets:")
for split in splits:
    dataset = Dataset(
        id=split["id"],
        source_id="nso-1212",
        parent_id=parent_id,
        name_en=split["name_en"],
        name_mn=split["name_mn"],
        category_en="Trade",
        category_mn="Худалдаа",
        description_en=split["description_en"],
        description_mn=split["description_mn"],
        definition_path=f"tools/sources/nso-1212/datasets/{split['id']}.md",
        is_parent=False,
        split_filter=json.dumps(split["filter"]),
        status="active",
        current_version=1,
        source_ref="DT_NSO_1400_001V1_year.px",
        data_file=f"public/datasets/{split['id']}.csv",
        mdx_file_en=f"src/data/data/{split['mdx_en']}",
        mdx_file_mn=f"src/data/data/{split['mdx_mn']}",
        chart_spec=f"public/charts/{split['chart']}",
        source_updated_at="2025-08-04T10:27:10",
        last_fetched_at=now,
        auto_update=True,
        auto_publish=True,
    )

    try:
        reg.add_dataset(dataset)
        print(f"✓ Registered: {split['id']}")
    except Exception as e:
        print(f"✗ Error registering {split['id']}: {e}")

# Log activity
reg.log_activity(
    action="create",
    status="success",
    dataset_id=None,
    message=f"Created foreign trade datasets: 1 parent + 4 splits"
)

print("\n" + "="*50)
print("Registry update complete!")
print("="*50)
print("\nNext steps:")
print("1. Publish datasets to assign URLs:")
for split in splits:
    print(f"   python -m registry publish {split['id']}")
print("2. Test pages in dev server:")
print("   cd data.mn && npm run dev")
