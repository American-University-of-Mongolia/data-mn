#!/usr/bin/env python3
"""
Register household income datasets in the registry
"""

import sys
from pathlib import Path

# Add parent directory to path to import registry
sys.path.insert(0, str(Path(__file__).parent.parent))

from registry.registry import Registry, Source, Dataset, Version
from datetime import datetime
import hashlib

def main():
    registry = Registry()

    # First, check if NSO source exists, if not create it
    source = registry.get_source("nso-1212")
    if not source:
        print("Creating NSO source...")
        source = Source(
            id="nso-1212",
            name="National Statistics Office of Mongolia",
            name_mn="Үндэсний Статистикийн Хороо",
            type="API",
            base_url="https://data.1212.mn",
            definition_path="tools/sources/nso-1212/source.md",
            update_frequency="varies",
            enabled=True,
            priority=10
        )
        registry.add_source(source)
        print("✓ NSO source created")
    else:
        print("✓ NSO source already exists")

    # Dataset 1: household-income (total)
    print("\n" + "="*60)
    print("REGISTERING: household-income")
    print("="*60)

    dataset1 = registry.get_dataset("household-income")
    if dataset1:
        print("⚠ Dataset 'household-income' already exists. Updating...")
        registry.update_dataset(
            "household-income",
            status="active",
            current_version=1,
            data_file="data.mn/public/datasets/household-income.csv",
            mdx_file_en="data.mn/src/data/data/en/household-income.mdx",
            mdx_file_mn="data.mn/src/data/data/mn/household-income.mdx",
            chart_spec="data.mn/public/charts/household-income.json",
            data_as_of="2024-12-02",
            source_updated_at="2024-01-01",
            last_fetched_at=datetime.now().isoformat()
        )
        print("✓ Dataset updated")
    else:
        print("Creating household-income dataset...")
        dataset1 = Dataset(
            id="household-income",
            source_id="nso-1212",
            name_en="Mongolia Household Income (1997-2024)",
            name_mn="Монгол Улсын өрхийн орлого (1997-2024)",
            description_en="Monthly average household income in Mongolia from 1997 to 2024",
            description_mn="1997-2024 оны Монгол Улсын өрхийн дундаж сарын орлого",
            category="Economy",
            tags=["household income", "economy", "income", "living standards"],
            keywords_en=["mongolia household income", "household earnings", "average income", "monthly income"],
            keywords_mn=["монгол өрхийн орлого", "өрхийн орлого", "дундаж орлого", "сарын орлого"],
            source_ref="DT_NSO_1900_001V1.px",
            source_path="Society, development / Household income and expenditure",
            definition_path="tools/sources/nso-1212/datasets/household-income.md",
            current_version=1,
            status="active",
            data_file="data.mn/public/datasets/household-income.csv",
            mdx_file_en="data.mn/src/data/data/en/household-income.mdx",
            mdx_file_mn="data.mn/src/data/data/mn/household-income.mdx",
            chart_spec="data.mn/public/charts/household-income.json",
            data_as_of="2024-12-02",
            source_updated_at="2024-01-01",
            last_fetched_at=datetime.now().isoformat(),
            auto_update=True,
            auto_publish=True,
            is_parent=False
        )
        registry.add_dataset(dataset1)
        print("✓ Dataset created")

    # Create version record for dataset 1
    data_file1 = Path(__file__).parent.parent.parent / "data.mn/public/datasets/household-income.csv"
    with open(data_file1, 'rb') as f:
        data_hash1 = hashlib.md5(f.read()).hexdigest()

    version1 = Version(
        id=0,
        dataset_id="household-income",
        version=1,
        data_hash=data_hash1,
        data_path="data.mn/public/datasets/household-income.csv",
        row_count=28,
        column_count=2,
        change_type="initial",
        change_summary="Initial dataset creation with 28 years of household income data (1997-2024)",
        source_updated_at="2024-01-01",
        fetched_at=datetime.now().isoformat()
    )
    registry.add_version(version1)
    print("✓ Version record created")

    # Log activity for dataset 1
    registry.log_activity(
        action="create",
        dataset_id="household-income",
        source_id="nso-1212",
        status="success",
        message="Created household-income dataset with 28 years of data (1997-2024)",
        details={
            "rows": 28,
            "years": "1997-2024",
            "min_income": 56218,
            "max_income": 2567889,
            "latest_income_2024": 2567889
        },
        triggered_by="manual"
    )
    print("✓ Activity logged")

    # Dataset 2: household-income-urban-rural
    print("\n" + "="*60)
    print("REGISTERING: household-income-urban-rural")
    print("="*60)

    dataset2 = registry.get_dataset("household-income-urban-rural")
    if dataset2:
        print("⚠ Dataset 'household-income-urban-rural' already exists. Updating...")
        registry.update_dataset(
            "household-income-urban-rural",
            status="active",
            current_version=1,
            data_file="data.mn/public/datasets/household-income-urban-rural.csv",
            mdx_file_en="data.mn/src/data/data/en/household-income-urban-rural.mdx",
            mdx_file_mn="data.mn/src/data/data/mn/household-income-urban-rural.mdx",
            chart_spec="data.mn/public/charts/household-income-urban-rural.json",
            data_as_of="2024-12-02",
            source_updated_at="2024-01-01",
            last_fetched_at=datetime.now().isoformat()
        )
        print("✓ Dataset updated")
    else:
        print("Creating household-income-urban-rural dataset...")
        dataset2 = Dataset(
            id="household-income-urban-rural",
            source_id="nso-1212",
            name_en="Mongolia Household Income: Urban vs Rural (1997-2024)",
            name_mn="Монгол Улсын өрхийн орлого: Хот ба хөдөө (1997-2024)",
            description_en="Comparison of urban and rural household income in Mongolia from 1997 to 2024",
            description_mn="1997-2024 оны Монгол Улсын хот болон хөдөөгийн өрхийн орлогын харьцуулалт",
            category="Economy",
            tags=["household income", "urban", "rural", "income inequality", "economy"],
            keywords_en=["mongolia urban rural income", "income gap", "urban income", "rural income"],
            keywords_mn=["монгол хот хөдөө орлого", "орлогын зөрүү", "хотын орлого", "хөдөөгийн орлого"],
            source_ref="DT_NSO_1900_001V1.px",
            source_path="Society, development / Household income and expenditure",
            definition_path="tools/sources/nso-1212/datasets/household-income-urban-rural.md",
            current_version=1,
            status="active",
            data_file="data.mn/public/datasets/household-income-urban-rural.csv",
            mdx_file_en="data.mn/src/data/data/en/household-income-urban-rural.mdx",
            mdx_file_mn="data.mn/src/data/data/mn/household-income-urban-rural.mdx",
            chart_spec="data.mn/public/charts/household-income-urban-rural.json",
            data_as_of="2024-12-02",
            source_updated_at="2024-01-01",
            last_fetched_at=datetime.now().isoformat(),
            auto_update=True,
            auto_publish=True,
            is_parent=False
        )
        registry.add_dataset(dataset2)
        print("✓ Dataset created")

    # Create version record for dataset 2
    data_file2 = Path(__file__).parent.parent.parent / "data.mn/public/datasets/household-income-urban-rural.csv"
    with open(data_file2, 'rb') as f:
        data_hash2 = hashlib.md5(f.read()).hexdigest()

    version2 = Version(
        id=0,
        dataset_id="household-income-urban-rural",
        version=1,
        data_hash=data_hash2,
        data_path="data.mn/public/datasets/household-income-urban-rural.csv",
        row_count=56,
        column_count=3,
        change_type="initial",
        change_summary="Initial dataset creation with urban and rural household income comparison (1997-2024)",
        source_updated_at="2024-01-01",
        fetched_at=datetime.now().isoformat()
    )
    registry.add_version(version2)
    print("✓ Version record created")

    # Log activity for dataset 2
    registry.log_activity(
        action="create",
        dataset_id="household-income-urban-rural",
        source_id="nso-1212",
        status="success",
        message="Created household-income-urban-rural dataset with urban/rural comparison (1997-2024)",
        details={
            "rows": 56,
            "years": "1997-2024",
            "areas": ["Urban", "Rural"],
            "latest_urban_2024": 2803740,
            "latest_rural_2024": 2069149,
            "gap_2024": 734591
        },
        triggered_by="manual"
    )
    print("✓ Activity logged")

    # Summary
    print("\n" + "="*60)
    print("REGISTRATION COMPLETE")
    print("="*60)

    print("\n1. household-income")
    print("   Status: active")
    print("   Version: 1")
    print("   Files generated:")
    print("     • data.mn/public/datasets/household-income.csv")
    print("     • data.mn/public/datasets/household-income.xlsx")
    print("     • data.mn/public/charts/household-income.json")
    print("     • data.mn/src/data/data/en/household-income.mdx")
    print("     • data.mn/src/data/data/mn/household-income.mdx")

    print("\n2. household-income-urban-rural")
    print("   Status: active")
    print("   Version: 1")
    print("   Files generated:")
    print("     • data.mn/public/datasets/household-income-urban-rural.csv")
    print("     • data.mn/public/datasets/household-income-urban-rural.xlsx")
    print("     • data.mn/public/charts/household-income-urban-rural.json")
    print("     • data.mn/src/data/data/en/household-income-urban-rural.mdx")
    print("     • data.mn/src/data/data/mn/household-income-urban-rural.mdx")

    # Show registry status
    print("\nRegistry status:")
    status = registry.get_status()
    print(f"  Total datasets: {status['datasets'].get('total', 0)}")
    print(f"  Active: {status['datasets'].get('active', 0)}")

if __name__ == "__main__":
    main()
