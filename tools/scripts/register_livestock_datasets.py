#!/usr/bin/env python3
"""
Register livestock datasets in the registry
"""

import sys
from pathlib import Path

# Add parent directory to path to import registry
sys.path.insert(0, str(Path(__file__).parent.parent))

from registry.registry import Registry, Source, Dataset, Version
from datetime import datetime
import hashlib
import pandas as pd

def main():
    registry = Registry()

    # Ensure NSO source exists
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

    # Base paths
    base_path = Path(__file__).parent.parent.parent

    # Dataset 1: livestock-total
    print("\n" + "="*60)
    print("Registering livestock-total dataset...")
    print("="*60)

    dataset_id = "livestock-total"
    dataset = registry.get_dataset(dataset_id)

    if dataset:
        print(f"⚠ Dataset '{dataset_id}' already exists. Updating...")
        registry.update_dataset(
            dataset_id,
            status="active",
            current_version=1,
            data_file="data.mn/public/datasets/livestock-total.csv",
            mdx_file_en="data.mn/src/data/data/en/livestock-total.mdx",
            mdx_file_mn="data.mn/src/data/data/mn/livestock-total.mdx",
            chart_spec="data.mn/public/charts/livestock-total.json",
            data_as_of="2024-09-29",
            source_updated_at="2024-09-29",
            last_fetched_at=datetime.now().isoformat()
        )
        print("✓ Dataset updated")
    else:
        print(f"Creating {dataset_id} dataset...")
        dataset = Dataset(
            id=dataset_id,
            source_id="nso-1212",
            name_en="Mongolia Total Livestock Count (1970-2024)",
            name_mn="Монгол Улсын нийт мал сүргийн тоо (1970-2024)",
            description_en="Total livestock population in Mongolia from 1970 to 2024",
            description_mn="1970-2024 оны Монгол Улсын нийт мал сүргийн тоо",
            category="Agriculture",
            tags=["livestock", "agriculture", "animals", "pastoral"],
            keywords_en=["mongolia livestock", "total livestock", "animal husbandry", "pastoral economy"],
            keywords_mn=["монгол мал", "мал сүрэг", "малчин эдийн засаг"],
            source_ref="DT_NSO_1001_021V1.px",
            source_path="Industry, service / Livestock",
            definition_path="tools/sources/nso-1212/datasets/livestock-total.md",
            current_version=1,
            status="active",
            data_file="data.mn/public/datasets/livestock-total.csv",
            mdx_file_en="data.mn/src/data/data/en/livestock-total.mdx",
            mdx_file_mn="data.mn/src/data/data/mn/livestock-total.mdx",
            chart_spec="data.mn/public/charts/livestock-total.json",
            data_as_of="2024-09-29",
            source_updated_at="2024-09-29",
            last_fetched_at=datetime.now().isoformat(),
            auto_update=True,
            auto_publish=True,
            is_parent=False
        )
        registry.add_dataset(dataset)
        print("✓ Dataset created")

    # Create version record
    data_file = base_path / "data.mn/public/datasets/livestock-total.csv"
    df = pd.read_csv(data_file)
    with open(data_file, 'rb') as f:
        data_hash = hashlib.md5(f.read()).hexdigest()

    version = Version(
        id=0,
        dataset_id=dataset_id,
        version=1,
        data_hash=data_hash,
        data_path="data.mn/public/datasets/livestock-total.csv",
        row_count=len(df),
        column_count=len(df.columns),
        change_type="initial",
        change_summary=f"Initial dataset creation with {len(df)} rows covering 1970-2024",
        source_updated_at="2024-09-29",
        fetched_at=datetime.now().isoformat()
    )
    registry.add_version(version)
    print("✓ Version record created")

    # Log activity
    registry.log_activity(
        action="create",
        dataset_id=dataset_id,
        source_id="nso-1212",
        status="success",
        message=f"Created {dataset_id} dataset with {len(df)} years of data (1970-2024)",
        details={
            "rows": len(df),
            "years": "1970-2024",
            "min_livestock": float(df['total_livestock'].min()),
            "max_livestock": float(df['total_livestock'].max())
        },
        triggered_by="manual"
    )
    print("✓ Activity logged")

    # Dataset 2: livestock-by-type
    print("\n" + "="*60)
    print("Registering livestock-by-type dataset...")
    print("="*60)

    dataset_id = "livestock-by-type"
    dataset = registry.get_dataset(dataset_id)

    if dataset:
        print(f"⚠ Dataset '{dataset_id}' already exists. Updating...")
        registry.update_dataset(
            dataset_id,
            status="active",
            current_version=1,
            data_file="data.mn/public/datasets/livestock-by-type.csv",
            mdx_file_en="data.mn/src/data/data/en/livestock-by-type.mdx",
            mdx_file_mn="data.mn/src/data/data/mn/livestock-by-type.mdx",
            chart_spec="data.mn/public/charts/livestock-by-type.json",
            data_as_of="2024-09-29",
            source_updated_at="2024-09-29",
            last_fetched_at=datetime.now().isoformat()
        )
        print("✓ Dataset updated")
    else:
        print(f"Creating {dataset_id} dataset...")
        dataset = Dataset(
            id=dataset_id,
            source_id="nso-1212",
            name_en="Mongolia Livestock by Type (1970-2024)",
            name_mn="Монгол Улсын мал сүрэг төрлөөр (1970-2024)",
            description_en="Livestock population breakdown by type (Horse, Cattle, Camel, Sheep, Goat) from 1970 to 2024",
            description_mn="1970-2024 оны мал сүргийн тоо төрлөөр (Адуу, Үхэр, Тэмээ, Хонь, Ямаа)",
            category="Agriculture",
            tags=["livestock", "agriculture", "animals", "sheep", "goat", "five animals"],
            keywords_en=["mongolia livestock types", "sheep goat", "horses cattle", "five animals", "tabun khoshuu mal"],
            keywords_mn=["монгол мал төрөл", "хонь ямаа", "адуу үхэр", "табан хошуу мал"],
            source_ref="DT_NSO_1001_021V1.px",
            source_path="Industry, service / Livestock",
            definition_path="tools/sources/nso-1212/datasets/livestock-by-type.md",
            current_version=1,
            status="active",
            data_file="data.mn/public/datasets/livestock-by-type.csv",
            mdx_file_en="data.mn/src/data/data/en/livestock-by-type.mdx",
            mdx_file_mn="data.mn/src/data/data/mn/livestock-by-type.mdx",
            chart_spec="data.mn/public/charts/livestock-by-type.json",
            data_as_of="2024-09-29",
            source_updated_at="2024-09-29",
            last_fetched_at=datetime.now().isoformat(),
            auto_update=True,
            auto_publish=True,
            is_parent=False
        )
        registry.add_dataset(dataset)
        print("✓ Dataset created")

    # Create version record
    data_file = base_path / "data.mn/public/datasets/livestock-by-type.csv"
    df = pd.read_csv(data_file)
    with open(data_file, 'rb') as f:
        data_hash = hashlib.md5(f.read()).hexdigest()

    version = Version(
        id=0,
        dataset_id=dataset_id,
        version=1,
        data_hash=data_hash,
        data_path="data.mn/public/datasets/livestock-by-type.csv",
        row_count=len(df),
        column_count=len(df.columns),
        change_type="initial",
        change_summary=f"Initial dataset creation with {len(df)} rows covering 1970-2024",
        source_updated_at="2024-09-29",
        fetched_at=datetime.now().isoformat()
    )
    registry.add_version(version)
    print("✓ Version record created")

    # Log activity
    livestock_types = df['livestock_type'].unique()
    registry.log_activity(
        action="create",
        dataset_id=dataset_id,
        source_id="nso-1212",
        status="success",
        message=f"Created {dataset_id} dataset with {len(df)} rows (1970-2024)",
        details={
            "rows": len(df),
            "years": "1970-2024",
            "livestock_types": list(livestock_types)
        },
        triggered_by="manual"
    )
    print("✓ Activity logged")

    # Summary
    print("\n" + "="*60)
    print("REGISTRATION COMPLETE")
    print("="*60)
    print("\nDatasets registered:")
    print("  1. livestock-total")
    print("  2. livestock-by-type")
    print("\nFiles generated:")
    print("  • data.mn/public/datasets/livestock-total.csv")
    print("  • data.mn/public/datasets/livestock-total.xlsx")
    print("  • data.mn/public/charts/livestock-total.json")
    print("  • data.mn/src/data/data/en/livestock-total.mdx")
    print("  • data.mn/src/data/data/mn/livestock-total.mdx")
    print()
    print("  • data.mn/public/datasets/livestock-by-type.csv")
    print("  • data.mn/public/datasets/livestock-by-type.xlsx")
    print("  • data.mn/public/charts/livestock-by-type.json")
    print("  • data.mn/src/data/data/en/livestock-by-type.mdx")
    print("  • data.mn/src/data/data/mn/livestock-by-type.mdx")

    # Show registry status
    print("\nRegistry status:")
    status = registry.get_status()
    print(f"  Total datasets: {status['datasets'].get('total', 0)}")
    print(f"  Active: {status['datasets'].get('active', 0)}")

if __name__ == "__main__":
    main()
