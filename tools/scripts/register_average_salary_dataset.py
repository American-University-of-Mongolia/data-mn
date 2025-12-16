#!/usr/bin/env python3
"""
Register average salary dataset in the registry
"""

import sys
from pathlib import Path

# Add parent directory to path to import registry
sys.path.insert(0, str(Path(__file__).parent.parent))

from registry.registry import Registry, Source, Dataset, Version
from datetime import datetime

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
    dataset = registry.get_dataset("average-salary")
    if dataset:
        print("⚠ Dataset 'average-salary' already exists. Updating...")
        # Update the dataset
        registry.update_dataset(
            "average-salary",
            status="active",
            current_version=1,
            data_file="data.mn/public/datasets/average-salary.csv",
            mdx_file_en="data.mn/src/data/data/en/average-salary.mdx",
            mdx_file_mn="data.mn/src/data/data/mn/average-salary.mdx",
            chart_spec="data.mn/src/data/charts/average-salary.json",
            data_as_of="2024-12-02",
            source_updated_at="2025-08-13",
            last_fetched_at=datetime.now().isoformat()
        )
        print("✓ Dataset updated")
    else:
        print("Creating average-salary dataset...")
        dataset = Dataset(
            id="average-salary",
            source_id="nso-1212",
            name_en="Mongolia Average Monthly Salary (1995-2024)",
            name_mn="Монгол Улсын дундаж сарын цалин (1995-2024)",
            description_en="National average monthly nominal wages from 1995 to 2024",
            description_mn="1995-2024 оны үндэсний дундаж сарын нэрлэсэн цалин",
            category="Economy",
            tags=["salary", "wages", "labour", "income", "economy"],
            keywords_en=["mongolia average salary", "salary", "wages", "income", "labour market"],
            keywords_mn=["монгол дундаж цалин", "цалин", "хөлс", "орлого", "хөдөлмөрийн зах зээл"],
            source_ref="DT_NSO_0400_021V1.px",
            source_path="Labour, business / Wages / MONTHLY AVERAGE NOMINAL WAGES, by region, aimags and the Capital, by gender",
            definition_path="tools/sources/nso-1212/datasets/average-salary.md",
            current_version=1,
            status="active",
            data_file="data.mn/public/datasets/average-salary.csv",
            mdx_file_en="data.mn/src/data/data/en/average-salary.mdx",
            mdx_file_mn="data.mn/src/data/data/mn/average-salary.mdx",
            chart_spec="data.mn/src/data/charts/average-salary.json",
            data_as_of="2024-12-02",
            source_updated_at="2025-08-13",
            last_fetched_at=datetime.now().isoformat()
        )
        registry.add_dataset(dataset)
        print("✓ Dataset created")

    # Create version 1
    versions = registry.get_versions("average-salary")
    if not versions or not any(v.version == 1 for v in versions):
        print("Creating version 1...")
        version = Version(
            id=None,  # Will be auto-generated
            dataset_id="average-salary",
            version=1,
            data_hash="",  # Could compute hash if needed
            data_path="data.mn/public/datasets/average-salary.csv",
            row_count=30,
            column_count=2,
            change_type="initial",
            change_summary="Initial version with data from 1995-2024",
            fetched_at=datetime.now().isoformat()
        )
        registry.add_version(version)
        print("✓ Version 1 created")
    else:
        print("✓ Version 1 already exists")

    # Log activity
    registry.log_activity(
        dataset_id="average-salary",
        action="create",
        status="success",
        message="Dataset created with 30 years of average salary data (1995-2024)"
    )

    print("\n" + "="*60)
    print("✓ Registration complete!")
    print("="*60)
    print("\nDataset ID: average-salary")
    print("Source: NSO 1212.mn")
    print("Coverage: 1995-2024 (30 years)")
    print("Status: active")
    print("\nFiles created:")
    print("  - data.mn/public/datasets/average-salary.csv")
    print("  - data.mn/public/datasets/average-salary.xlsx")
    print("  - data.mn/src/data/charts/average-salary.json")
    print("  - data.mn/src/data/data/en/average-salary.mdx")
    print("  - data.mn/src/data/data/mn/average-salary.mdx")

if __name__ == "__main__":
    main()
