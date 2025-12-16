#!/usr/bin/env python3
"""
Register inflation rate dataset in the registry
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

    # Check if dataset already exists
    dataset = registry.get_dataset("inflation-rate")
    if dataset:
        print("⚠ Dataset 'inflation-rate' already exists. Updating...")
        # Update the dataset
        registry.update_dataset(
            "inflation-rate",
            status="active",
            current_version=1,
            data_file="data.mn/public/datasets/inflation-rate.csv",
            mdx_file_en="data.mn/src/data/data/en/inflation-rate.mdx",
            mdx_file_mn="data.mn/src/data/data/mn/inflation-rate.mdx",
            chart_spec="data.mn/public/charts/inflation-rate.json",
            data_as_of="2024-12-02",
            source_updated_at="2024-01-10",
            last_fetched_at=datetime.now().isoformat()
        )
        print("✓ Dataset updated")
    else:
        print("Creating inflation-rate dataset...")
        dataset = Dataset(
            id="inflation-rate",
            source_id="nso-1212",
            name_en="Mongolia Inflation Rate (1991-2024)",
            name_mn="Монгол Улсын инфляцийн түвшин (1991-2024)",
            description_en="Annual inflation rate in Mongolia from 1991 to 2024",
            description_mn="1991-2024 оны Монгол Улсын жилийн инфляцийн түвшин",
            category="Economy",
            tags=["inflation", "economy", "cpi", "prices"],
            keywords_en=["mongolia inflation rate", "inflation", "consumer price index", "cpi"],
            keywords_mn=["монгол инфляц", "инфляцийн түвшин", "үнийн өсөлт"],
            source_ref="DT_NSO_0600_013V2.px",
            source_path="Economy, environment / Consumer Price Index",
            definition_path="tools/sources/nso-1212/datasets/inflation-rate.md",
            current_version=1,
            status="active",
            data_file="data.mn/public/datasets/inflation-rate.csv",
            mdx_file_en="data.mn/src/data/data/en/inflation-rate.mdx",
            mdx_file_mn="data.mn/src/data/data/mn/inflation-rate.mdx",
            chart_spec="data.mn/public/charts/inflation-rate.json",
            data_as_of="2024-12-02",
            source_updated_at="2024-01-10",
            last_fetched_at=datetime.now().isoformat(),
            auto_update=True,
            auto_publish=True,
            is_parent=False
        )
        registry.add_dataset(dataset)
        print("✓ Dataset created")

    # Create version record
    print("\nCreating version record...")

    # Calculate hash of data file
    data_file = Path(__file__).parent.parent.parent / "data.mn/public/datasets/inflation-rate.csv"
    with open(data_file, 'rb') as f:
        data_hash = hashlib.md5(f.read()).hexdigest()

    version = Version(
        id=0,  # Will be auto-assigned
        dataset_id="inflation-rate",
        version=1,
        data_hash=data_hash,
        data_path="data.mn/public/datasets/inflation-rate.csv",
        row_count=34,
        column_count=2,
        change_type="initial",
        change_summary="Initial dataset creation with 34 years of inflation data (1991-2024)",
        source_updated_at="2024-01-10",
        fetched_at=datetime.now().isoformat()
    )

    registry.add_version(version)
    print("✓ Version record created")

    # Log activity
    registry.log_activity(
        action="create",
        dataset_id="inflation-rate",
        source_id="nso-1212",
        status="success",
        message="Created inflation-rate dataset with 34 years of data (1991-2024)",
        details={
            "rows": 34,
            "years": "1991-2024",
            "min_inflation": 1.3,
            "max_inflation": 325.5
        },
        triggered_by="manual"
    )
    print("✓ Activity logged")

    print("\n" + "="*60)
    print("REGISTRATION COMPLETE")
    print("="*60)
    print("\nDataset ID: inflation-rate")
    print("Status: active")
    print("Version: 1")
    print("Files generated:")
    print("  • data.mn/public/datasets/inflation-rate.csv")
    print("  • data.mn/public/datasets/inflation-rate.xlsx")
    print("  • data.mn/public/charts/inflation-rate.json")
    print("  • data.mn/src/data/data/en/inflation-rate.mdx")
    print("  • data.mn/src/data/data/mn/inflation-rate.mdx")

    # Show registry status
    print("\nRegistry status:")
    status = registry.get_status()
    print(f"  Total datasets: {status['datasets'].get('total', 0)}")
    print(f"  Active: {status['datasets'].get('active', 0)}")

if __name__ == "__main__":
    main()
